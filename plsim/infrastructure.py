"""Endogenous growth of the rail and road networks.

Model
-----
The network is a multimodal graph over ~170 towns.  Each year:

1. Generalised travel times ``t_ij`` are computed by Dijkstra over the current
   graph; edge speeds depend on class, calendar era (steam -> diesel/electric ->
   high speed) and, for roads, on motorisation (buses/carts early on, cars later).
2. Interaction demand follows a gravity model
   ``T_ij = tau * m_i m_j exp(-beta t_ij)`` (Zipf 1946; Wilson 1971), with
   masses = population x income and ``tau`` normalised to a per-capita trip
   rate that rises with income.  Cross-border pairs carry a McCallum (1995)
   border penalty.
3. Candidate projects (new links on the Delaunay/Gabriel proximity graph,
   gauge conversion, double-tracking, electrification, high-speed lines, road
   surfacing, expressways/motorways) are appraised by consumer surplus
   (rule-of-half time savings valued at a share of income) over a 40-year life,
   optionally equity-weighted towards poor regions (the 1939-54 plan's aim of
   erasing Poland A/B).  The exact post-project travel times are obtained
   cheaply because lowering a single edge weight w_uv -> w'_uv gives
   ``d'_ij = min(d_ij, d_iu + w' + d_vj, d_iv + w' + d_uj)``.
4. Projects are chosen greedily by benefit-cost ratio under a budget that is
   a share of GDP (with a capped multi-year account for large works).
   Dated historical and planned projects are injected exogenously.
5. After mass motorisation, lightly used narrow-gauge and secondary lines are
   closed with a small hazard ("Beeching"-type rationalisation).

This cost-benefit growth rule is in the family of Yerra & Levinson (2005),
Xie & Levinson (2009, 2011) and Louf, Jensen & Barthelemy (2013, PNAS), whose
models reproduce the emergence of hierarchy (trunks vs branches) in road and
rail networks.  Market access ``MA_i = sum_j m_j exp(-theta t_ij)`` (Harris
1954; Donaldson & Hornbeck 2016) feeds back to regional growth and town size.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path
from scipy.spatial import Delaunay

from .data.network import NODES, PAVED_ROADS_1931, PROJECTS, RAIL_1931, RAIL_1931_BY, RAIL_1931_XK
from .economy import piecewise

RAIL_CLASSES = ["nar", "sec", "main", "main_el", "hsr"]
ROAD_CLASSES = ["dirt", "gravel", "paved", "express", "motorway"]
TERRAIN_COST = {"flat": 1.0, "marsh": 1.45, "hill": 1.3, "mountain": 2.2}

RAIL_SPEED = {  # km/h commercial speed schedules
    "nar": [[1931, 18], [1970, 25], [2000, 30]],
    "sec": [[1931, 36], [1960, 50], [1990, 70], [2020, 85]],
    "main": [[1931, 52], [1960, 75], [1990, 100], [2020, 115]],
    "main_el": [[1931, 58], [1960, 90], [1990, 125], [2020, 150]],
    "hsr": [[1960, 180], [1980, 210], [2000, 250], [2020, 280]],
}
ROAD_FAST = {  # km/h for motor vehicles
    "dirt": [[1931, 22], [2000, 35]],
    "gravel": [[1931, 35], [1970, 55], [2000, 60]],
    "paved": [[1931, 50], [1970, 70], [2000, 80]],
    "express": [[1931, 80], [1970, 95], [2000, 105]],
    "motorway": [[1931, 95], [1970, 115], [2000, 125]],
}
ROAD_SLOW = {"dirt": 5.0, "gravel": 7.0, "paved": 8.5, "express": 8.5, "motorway": 8.5}
# Limited-access classes: built as new carriageways next to the old road, which
# keeps most local traffic; only the share ``local_share_limited`` of the
# farm-to-market (hinterland) benefit is counted for them.
LIMITED_ACCESS = ("express", "motorway")

# Upgrade paths: (mode, from_class) -> (to_class, cost per km [M 1990 GK$], first year)
UPGRADES = {
    ("rail", "nar"): ("sec", 0.45, 1931),
    ("rail", "sec"): ("main", 0.60, 1931),
    ("rail", "main"): ("main_el", 0.50, 1946),
    ("rail", "main_el"): ("hsr", 14.0, 1975),
    ("road", "dirt"): ("gravel", 0.10, 1931),
    ("road", "gravel"): ("paved", 0.20, 1931),
    ("road", "paved"): ("express", 1.60, 1950),
    ("road", "express"): ("motorway", 2.40, 1955),
}
NEW_RAIL_COST = 0.85  # M per km, single-track secondary
MODE = {"rail": 0, "road": 1}


def haversine(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = p2 - p1
    dl = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


@dataclass
class Project:
    kind: str           # 'new' | 'upgrade'
    mode: str
    a: int
    b: int
    new_class: str
    length: float
    cost: float
    edge: int = -1
    label: str = ""


def _exists(optional, have: set) -> bool:
    """Whether an optional town exists in a run with the optional lands ``have``
    (see ``data.network.Node.optional``)."""
    if not optional:
        return True
    need, _, unless = ("BY" if optional is True else optional).partition("-")
    return (not need or need in have) and (not unless or unless not in have)


class Network:
    def __init__(self, params: dict, region_codes: list[str], federation: bool, rng: np.random.Generator):
        self.p = params
        self.rng = rng
        self.region_codes = region_codes
        reg_idx = {c: i for i, c in enumerate(region_codes)}
        self.names = [n.name for n in NODES]
        self.N = len(NODES)
        self.lat = np.array([n.lat for n in NODES])
        self.lon = np.array([n.lon for n in NODES])
        override = params.get("node_region", {})          # towns of split voivodeships
        self.region = np.array([reg_idx.get(override.get(n.name, n.region), -1) for n in NODES])
        self.foreign = self.region < 0
        # towns and gateways of Soviet Belarus exist only when it is part of the state
        self.with_by = any(c.startswith("BY_") for c in region_codes)
        self.with_xk = any(c.startswith(("LV_", "RU_")) for c in region_codes)
        have = {k for k, on in (("BY", self.with_by), ("XK", self.with_xk)) if on}
        self.dormant = np.array([not _exists(n.optional, have) for n in NODES])
        self.pop = np.array([0.0 if d else n.pop_1931 for n, d in zip(NODES, self.dormant)])  # thousands (urban)
        self.base_pop = self.pop.copy()
        self.terrain = np.array([TERRAIN_COST.get(n.terrain, 1.0) for n in NODES])
        self.federation = federation
        self.name_idx = {n: i for i, n in enumerate(self.names)}
        # Edge arrays.
        self.eu: list[int] = []
        self.ev: list[int] = []
        self.emode: list[int] = []
        self.ecls: list[str] = []
        self.elen: list[float] = []
        self.eyear: list[int] = []
        self.eactive: list[bool] = []
        self.pending: list[tuple[int, Project]] = []  # (opening year, project)
        self.account = 0.0
        self.accounts: dict[str, float] = {}
        self.log: list[dict] = []
        self._build_initial()
        self._build_candidates()
        self.T = None
        self.ma = None
        self.ma0 = None

    # ------------------------------------------------------------------ building
    def _add_edge(self, a: int, b: int, mode: str, cls: str, year: int = 1931) -> int:
        d = float(haversine(self.lat[a], self.lon[a], self.lat[b], self.lon[b]))
        detour = 1.15 if mode == "rail" else 1.22
        self.eu.append(a)
        self.ev.append(b)
        self.emode.append(MODE[mode])
        self.ecls.append(cls)
        self.elen.append(d * detour)
        self.eyear.append(year)
        self.eactive.append(True)
        return len(self.eu) - 1

    def _edge_open(self, a: int, b: int) -> bool:
        """Links between two sovereign-foreign nodes are dropped; links across the
        Polish-Lithuanian demarcation line are closed outside the federation."""
        if (self.foreign[a] and self.foreign[b]) or self.dormant[a] or self.dormant[b]:
            return False
        ra, rb = NODES[a].region, NODES[b].region
        la, lb = ra.startswith("LT"), rb.startswith("LT")
        if not self.federation and (la != lb) and ra != "EXT" and rb != "EXT":
            return False
        return True

    def _build_initial(self):
        for a, b, cls in RAIL_1931 + (RAIL_1931_BY if self.with_by else []) + (RAIL_1931_XK if self.with_xk else []):
            ia, ib = self.name_idx[a], self.name_idx[b]
            if self._edge_open(ia, ib):
                self._add_edge(ia, ib, "rail", cls)
        # Road skeleton: Delaunay triangulation (of the towns that exist), pruned by length.
        live = np.where(~self.dormant)[0]
        xy = np.column_stack([self.lon[live] * np.cos(np.radians(52)), self.lat[live]]) * 111.0
        tri = Delaunay(xy)
        pairs = set()
        for s in tri.simplices:
            for i in range(3):
                a, b = int(live[s[i]]), int(live[s[(i + 1) % 3]])
                pairs.add((min(a, b), max(a, b)))
        paved = {tuple(sorted((self.name_idx[a], self.name_idx[b]))) for a, b in PAVED_ROADS_1931
                 if a in self.name_idx and b in self.name_idx}
        pairs |= paved
        self.delaunay_pairs = []
        for a, b in sorted(pairs):
            d = haversine(self.lat[a], self.lon[a], self.lat[b], self.lon[b])
            if d > 130 and (a, b) not in paved:
                continue
            if not self._edge_open(a, b):
                continue
            self.delaunay_pairs.append((a, b))
            if (a, b) in paved:
                cls = "paved"
            else:
                regs = {NODES[a].region, NODES[b].region}
                poor = regs & {"POL", "NOW", "WOL", "LT_NEA", "WIL", "BY_WIT", "BY_MIN", "BY_MOH", "BY_HOM"}
                cls = "dirt" if poor and min(self.pop[a], self.pop[b]) < 20 else "gravel"
            self._add_edge(a, b, "road", cls)

    def _build_candidates(self):
        rail_pairs = {(min(u, v), max(u, v)) for u, v, m in zip(self.eu, self.ev, self.emode) if m == 0}
        self.new_rail_candidates = [p for p in self.delaunay_pairs if p not in rail_pairs
                                    and not (self.foreign[p[0]] or self.foreign[p[1]])
                                    and haversine(self.lat[p[0]], self.lon[p[0]], self.lat[p[1]], self.lon[p[1]]) < 150]

    # ------------------------------------------------------------------ speeds
    def road_access(self, year: int, vehicles_per_1000: float) -> float:
        """Share of road trips made by motor vehicle (buses first, then cars)."""
        return min(1.0, piecewise(year, self.p["bus_access"]) + vehicles_per_1000 / 250.0)

    def edge_times(self, year: int, vehicles_per_1000: float) -> np.ndarray:
        access = self.road_access(year, vehicles_per_1000)
        t = np.full(len(self.eu), np.inf)
        cache = {}
        for e in range(len(self.eu)):
            if not self.eactive[e]:
                continue
            key = (self.emode[e], self.ecls[e])
            if key not in cache:
                if self.emode[e] == 0:
                    v = piecewise(year, RAIL_SPEED[self.ecls[e]])
                    cache[key] = (v, 0.06)
                else:
                    vf = piecewise(year, ROAD_FAST[self.ecls[e]])
                    vs = ROAD_SLOW[self.ecls[e]]
                    # harmonic mix: share `access` travels at motor speed
                    v = 1.0 / (access / vf + (1 - access) / vs) if access < 1 else vf
                    v = max(v, vs)
                    cache[key] = (v, 0.0)
            v, pen = cache[key]
            t[e] = self.elen[e] / v + pen
        return t

    def _adjacency(self, times: np.ndarray):
        best = {}
        for e in range(len(self.eu)):
            if not np.isfinite(times[e]):
                continue
            a, b = self.eu[e], self.ev[e]
            k = (a, b) if a < b else (b, a)
            if times[e] < best.get(k, (np.inf, -1))[0]:
                best[k] = (times[e], e)
        rows, cols, vals = [], [], []
        for (a, b), (w, _e) in best.items():
            rows += [a, b]
            cols += [b, a]
            vals += [w, w]
        return csr_matrix((vals, (rows, cols)), shape=(self.N, self.N)), best

    def travel_times(self, year: int, vehicles: float) -> np.ndarray:
        self._times = self.edge_times(year, vehicles)
        adj, self._best = self._adjacency(self._times)
        d = shortest_path(adj, method="D", directed=False)
        d[~np.isfinite(d)] = 99.0
        np.fill_diagonal(d, 0.3)
        self.D = d
        return d

    # ------------------------------------------------------------------ demand
    def masses(self, rel_income_node: np.ndarray) -> np.ndarray:
        m = self.pop * np.sqrt(np.clip(rel_income_node, 0.05, None))
        m = np.where(self.foreign, m * self.p["border_factor"], m)
        return m

    def demand(self, masses: np.ndarray, trips_per_capita: float, total_pop_k: float) -> np.ndarray:
        beta = self.p["gravity_beta"]
        K = np.outer(masses, masses) * np.exp(-beta * self.D)
        np.fill_diagonal(K, 0.0)
        scale = trips_per_capita * total_pop_k * 1000.0 / K.sum()
        self.T = K * scale
        return self.T

    def market_access(self, masses: np.ndarray) -> np.ndarray:
        theta = self.p["ma_theta"]
        self.ma = (masses[None, :] * np.exp(-theta * self.D)).sum(axis=1)
        if self.ma0 is None:
            self.ma0 = self.ma.copy()
        return self.ma

    # ------------------------------------------------------------------ projects
    def _cost_factor(self, a: int, b: int) -> float:
        return 0.5 * (self.terrain[a] + self.terrain[b])

    def candidates(self, year: int) -> list[Project]:
        out: list[Project] = []
        busy = {pr.edge for _y, pr in self.pending if pr.edge >= 0}
        busy_pairs = {(pr.a, pr.b) for _y, pr in self.pending}
        for e in range(len(self.eu)):
            if not self.eactive[e] or e in busy:
                continue
            mode = "rail" if self.emode[e] == 0 else "road"
            up = UPGRADES.get((mode, self.ecls[e]))
            if up is None or year < up[2]:
                continue
            new_cls, ckm, _y0 = up
            a, b = self.eu[e], self.ev[e]
            if new_cls == "hsr" and min(self.pop[a], self.pop[b]) < self.p["hsr_min_town_k"] and \
                    max(self.pop[a], self.pop[b]) < 400:
                continue
            if new_cls in ("express", "motorway") and min(self.pop[a], self.pop[b]) < 8:
                continue
            L = self.elen[e]
            out.append(Project("upgrade", mode, a, b, new_cls, L, L * ckm * self._cost_factor(a, b), edge=e))
        existing_rail = {(min(u, v), max(u, v)) for u, v, m, act in
                         zip(self.eu, self.ev, self.emode, self.eactive) if m == 0 and act}
        for a, b in self.new_rail_candidates:
            if (a, b) in existing_rail or (a, b) in busy_pairs:
                continue
            L = float(haversine(self.lat[a], self.lon[a], self.lat[b], self.lon[b])) * 1.15
            out.append(Project("new", "rail", a, b, "sec", L, L * NEW_RAIL_COST * self._cost_factor(a, b)))
        return out

    def _new_time(self, pr: Project, year: int, vehicles: float) -> float:
        if pr.mode == "rail":
            v = piecewise(year + 1, RAIL_SPEED[pr.new_class])
            return pr.length / v + 0.06
        access = self.road_access(year + 1, vehicles)
        vf = piecewise(year + 1, ROAD_FAST[pr.new_class])
        vs = ROAD_SLOW[pr.new_class]
        v = 1.0 / (access / vf + (1 - access) / vs) if access < 1 else vf
        return pr.length / max(v, vs)

    def appraise(self, projects: list[Project], year: int, vehicles: float, vot: np.ndarray,
                 equity: np.ndarray, hinterland: np.ndarray | None = None) -> np.ndarray:
        """Benefit-cost ratios.

        Network benefit: rule-of-half consumer surplus of gravity trips whose
        shortest path improves (exact single-edge update of all-pairs times).
        Local benefit (roads only): farm-to-market and local trips of the
        rural hinterland along the improved link, which inter-town gravity
        flows do not capture (all-weather surfacing was the main gain of
        interwar and post-war road programmes); for expressways and
        motorways only the share of local traffic that leaves the old road.
        Costs: construction plus the present value of operation and
        maintenance (``om_share`` of the capital cost per year).
        vot: (N,) value of time per hour at nodes; equity: (N,) welfare weights."""
        D = self.D.astype(np.float32)
        np.fill_diagonal(D, 0.0)       # true path lengths (the 0.3 h self-time is for demand only)
        T = self.T
        beta = self.p["gravity_beta"]
        V = 0.5 * (vot[:, None] + vot[None, :]) * np.sqrt(np.outer(equity, equity))
        W = (T * V).astype(np.float32)
        annuity = (1 - (1 + self.p["discount"]) ** -self.p["life"]) / self.p["discount"]
        growth = self.p["demand_growth_factor"]
        freight = 1.0 + self.p["freight_uplift"]
        local_rate = piecewise(year, self.p["local_trip_rate"])
        om = self.p.get("om_share", {})
        local_limited = self.p.get("local_share_limited", {})
        bcr = np.zeros(len(projects))
        cur_t = self._times
        for k, pr in enumerate(projects):
            w_new = self._new_time(pr, year, vehicles)
            a, b = pr.a, pr.b
            cur = D[a, b]
            local = 0.0
            if pr.mode == "road" and pr.edge >= 0 and hinterland is not None:
                dt_edge = max(cur_t[pr.edge] - w_new, 0.0)
                local = local_rate * (hinterland[a] + hinterland[b]) * 0.5 * dt_edge * \
                    0.5 * (vot[a] * equity[a] + vot[b] * equity[b]) * \
                    (local_limited.get(pr.new_class, 0.0) if pr.new_class in LIMITED_ACCESS else 1.0)
            if w_new >= cur - 1e-6 and local <= 0:
                continue
            benefit = local
            if w_new < cur - 1e-6:
                via = np.minimum(D[:, a][:, None] + w_new + D[b, :][None, :],
                                 D[:, b][:, None] + w_new + D[a, :][None, :])
                saving = D - via
                np.maximum(saving, 0.0, out=saving)
                induced = np.exp(beta * saving)
                benefit += float((W * saving * 0.5 * (1 + induced)).sum()) * freight
            cost = pr.cost * (1 + om.get(pr.new_class, 0.0) * annuity)
            bcr[k] = benefit * annuity * growth / max(cost * 1e6, 1.0)
        return bcr

    def invest(self, year: int, budget: float, vehicles: float, vot: np.ndarray, equity: np.ndarray,
               threshold: float, hinterland: np.ndarray | None = None, nodes: set | None = None,
               key: int = 0) -> list[Project]:
        """Separate rail and road programmes (as with PKP vs. the 1931 Road
        Fund), each with a capped multi-year account; greedy by BCR. With
        ``nodes`` (the towns of one of several states in the run), only links
        within that state (or to a foreign gateway) are built, from its own
        accounts (``key``)."""
        rail_share = piecewise(year, self.p["rail_budget_share"])
        chosen: list[Project] = []
        all_cands = self.candidates(year)
        if nodes is not None:
            all_cands = [c for c in all_cands if (c.a in nodes or c.b in nodes)
                         and all(x in nodes or self.foreign[x] for x in (c.a, c.b))]
        for mode, share in (("rail", rail_share), ("road", 1 - rail_share)):
            mode_key = mode if not key else f"{key}:{mode}"
            acc = self.accounts.get(mode_key, 0.0)
            acc = min(acc + budget * share, budget * share * self.p["account_cap_years"])
            cands = [c for c in all_cands if c.mode == mode]
            if cands:
                bcr = self.appraise(cands, year, vehicles, vot, equity, hinterland)
                order = np.argsort(-bcr)
                used_edges = set()
                used_pairs = set()
                for k in order:
                    if bcr[k] < threshold:
                        break
                    pr = cands[k]
                    if pr.edge >= 0 and pr.edge in used_edges:
                        continue
                    if (pr.a, pr.b) in used_pairs:
                        continue
                    if pr.cost * 1e6 > acc:
                        continue
                    acc -= pr.cost * 1e6
                    build = max(1, int(math.ceil(pr.length / (120 if pr.mode == "road" else 80))))
                    if pr.new_class in ("hsr", "motorway"):
                        build += 2
                    self.pending.append((year + build, pr))
                    if pr.edge >= 0:
                        used_edges.add(pr.edge)
                    used_pairs.add((pr.a, pr.b))
                    chosen.append(pr)
                    self.log.append({"year": year, "open": year + build, "kind": pr.kind, "mode": pr.mode,
                                     "from": self.names[pr.a], "to": self.names[pr.b], "class": pr.new_class,
                                     "km": round(pr.length, 1), "cost_M": round(float(pr.cost), 1),
                                     "bcr": round(float(bcr[k]), 2), "source": "appraisal"})
            self.accounts[mode_key] = acc
        self.account = sum(self.accounts.values())
        return chosen

    def open_pending(self, year: int) -> None:
        still = []
        for y, pr in self.pending:
            if y > year:
                still.append((y, pr))
                continue
            if pr.kind == "upgrade" and pr.edge >= 0:
                cur = self.ecls[pr.edge]
                order = RAIL_CLASSES if pr.mode == "rail" else ROAD_CLASSES
                if order.index(pr.new_class) > order.index(cur):
                    self.ecls[pr.edge] = pr.new_class
            else:
                self._add_edge(pr.a, pr.b, pr.mode, pr.new_class, year)
        self.pending = still

    def inject_dated_projects(self, year: int, enable_planned: bool, planned_delay: int) -> None:
        for a, b, mode, cls, y, label, status in PROJECTS:
            if status == "planned":
                if not enable_planned:
                    continue
                y = y + planned_delay
            if status == "federation" and not self.federation:
                continue
            if y != year or a not in self.name_idx or b not in self.name_idx:
                continue
            ia, ib = self.name_idx[a], self.name_idx[b]
            if not self._edge_open(ia, ib) and status != "federation":
                continue
            # Upgrade an existing parallel edge if one exists, else add.
            done = False
            order = RAIL_CLASSES if mode == "rail" else ROAD_CLASSES
            for e in range(len(self.eu)):
                if {self.eu[e], self.ev[e]} == {ia, ib} and self.emode[e] == MODE[mode] and self.eactive[e]:
                    if order.index(cls) > order.index(self.ecls[e]):
                        self.ecls[e] = cls
                    done = True
                    break
            if not done:
                self._add_edge(ia, ib, mode, cls, year)
            self.log.append({"year": year, "open": year, "kind": "dated", "mode": mode, "from": a, "to": b,
                             "class": cls, "km": None, "cost_M": None, "bcr": None, "source": status + ": " + label})

    def rationalise(self, year: int, vehicles: float) -> int:
        """Close lightly used narrow/secondary rail links after mass motorisation."""
        if vehicles < self.p["closure_motorisation"]:
            return 0
        rate = self.p["closure_rate"]
        closed = 0
        road_best = {}
        for e in range(len(self.eu)):
            if self.emode[e] == 1 and self.eactive[e]:
                k = (min(self.eu[e], self.ev[e]), max(self.eu[e], self.ev[e]))
                road_best[k] = max(road_best.get(k, 0), ROAD_CLASSES.index(self.ecls[e]))
        for e in range(len(self.eu)):
            if self.emode[e] != 0 or not self.eactive[e] or self.ecls[e] not in ("nar", "sec"):
                continue
            a, b = self.eu[e], self.ev[e]
            if min(self.pop[a], self.pop[b]) > 25:
                continue
            k = (min(a, b), max(a, b))
            if road_best.get(k, 0) < ROAD_CLASSES.index("paved"):
                continue
            p = rate * (2.0 if self.ecls[e] == "nar" else 1.0)
            if self.rng.random() < p:
                self.eactive[e] = False
                closed += 1
                self.log.append({"year": year, "open": year, "kind": "closure", "mode": "rail",
                                 "from": self.names[a], "to": self.names[b], "class": self.ecls[e],
                                 "km": round(self.elen[e], 1), "cost_M": None, "bcr": None, "source": "rationalisation"})
        return closed

    # ------------------------------------------------------------------ towns
    def update_towns(self, urban_by_region_k: np.ndarray, year: int) -> None:
        """Distribute each region's urban population over its towns with
        Gibrat growth plus a market-access premium."""
        eta = self.p["town_ma_elasticity"]
        if self.ma is not None and self.ma0 is not None:
            lma = np.log(self.ma / self.ma0)
        else:
            lma = np.zeros(self.N)
        # one draw per town that exists (dormant towns of Soviet Belarus take none)
        noise = np.zeros(self.N)
        noise[~self.dormant] = self.rng.normal(0, self.p["town_noise"], int((~self.dormant).sum()))
        bonus = np.zeros(self.N)
        for name, sched in self.p.get("town_bonus", {}).items():
            if name in self.name_idx:
                bonus[self.name_idx[name]] = piecewise(year, sched)
        R = len(self.region_codes)
        for r in range(R):
            idx = np.where(self.region == r)[0]
            if len(idx) == 0:
                continue
            w = self.pop[idx].copy()
            rel = lma[idx] - (w * lma[idx]).sum() / w.sum()
            w = w * np.exp(eta * rel * 0.1 + noise[idx] + bonus[idx])
            # primacy premium for capitals (Warsaw, Kaunas) is implicit in their own region
            self.pop[idx] = w / w.sum() * urban_by_region_k[r] * self.p["town_share_of_urban"][r]

    # ------------------------------------------------------------------ reporting
    def km_by_class(self) -> dict[str, float]:
        out = {f"rail_{c}": 0.0 for c in RAIL_CLASSES}
        out.update({f"road_{c}": 0.0 for c in ROAD_CLASSES})
        for e in range(len(self.eu)):
            if not self.eactive[e]:
                continue
            if self.foreign[self.eu[e]] or self.foreign[self.ev[e]]:
                continue
            key = ("rail_" if self.emode[e] == 0 else "road_") + self.ecls[e]
            out[key] += self.elen[e]
        return out

    def snapshot(self) -> list[tuple]:
        return [(self.eu[e], self.ev[e], self.emode[e], self.ecls[e]) for e in range(len(self.eu)) if self.eactive[e]]

    def region_capital_nodes(self) -> np.ndarray:
        """Largest town of each region; a region without a modelled town
        (a small county) uses the nearest domestic town."""
        R = len(self.region_codes)
        caps = np.zeros(R, dtype=int)
        seats = self.p.get("region_seats")
        dom = np.where(~self.foreign)[0]
        for r in range(R):
            idx = np.where(self.region == r)[0]
            if len(idx):
                caps[r] = idx[np.argmax(self.base_pop[idx])]
            else:
                la, lo = seats[r]
                caps[r] = dom[np.argmin(haversine(self.lat[dom], self.lon[dom], la, lo))]
        return caps

    def region_access_hours(self, year: int) -> np.ndarray:
        """Road time from the seat of a region without its own town to the
        town it uses (zero for regions with towns)."""
        R = len(self.region_codes)
        seats = self.p.get("region_seats")
        out = np.zeros(R)
        if seats is None:
            return out
        caps = self.region_capital_nodes()
        speed = piecewise(year, [[1931, 22.0], [1960, 40.0], [1990, 60.0], [2030, 70.0]])
        for r in range(R):
            if not (self.region == r).any():
                la, lo = seats[r]
                out[r] = haversine(self.lat[caps[r]], self.lon[caps[r]], la, lo) * 1.3 / speed
        return out
