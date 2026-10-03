"""Simulation engine: an annual, multi-regional, multi-group cohort-component
projection coupled to language dynamics, migration, the economy and an
evolving transport network.

State array ``P[r, u, g, b, s, a]``:
    r  region (17 Polish units + 6 Lithuanian units)
    u  0 rural / 1 urban
    g  (community, home language) group
    b  0 monolingual / 1 competent in the region's dominant language
    s  0 male / 1 female
    a  single year of age 0..100+

Order of events within year t (state at 1 Jan t -> 1 Jan t+1):
    economy -> network (times, demand, investment) -> vital rates ->
    births with intergenerational language transmission -> survival & ageing ->
    horizontal language processes -> rural-urban, inter-regional and
    international migration -> bookkeeping and recording.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field

import numpy as np

from .data.census1931 import bilingual_share, build_initial_composition
from .data.languages import COMM_INDEX, COMMUNITIES, GROUP_INDEX, GROUPS, LANG_INDEX, LANGUAGES, NC, NG, NL
from .data.regions import select_regions
from .demography import (FertilitySchedule, MortalityModel, alkema_decrement, catchup_rate,
                         frontier_e0_female, mean_age_childbearing, sex_gap, stable_age_distribution, target_gap)
from .economy import Economy, piecewise
from .infrastructure import Network
from .params import region_lookup, region_match, resolve_governorates
from .identity import IDENTITY_REGIMES, IdentityModel, identity_census
from .language import CENSUS_CATEGORIES, LANGUAGE_REGIMES, LanguageModel, census_view
from .migration import MigrationModel

_MORT_CACHE: dict = {}


def _mortality() -> MortalityModel:
    if "m" not in _MORT_CACHE:
        _MORT_CACHE["m"] = MortalityModel()
    return _MORT_CACHE["m"]


def _lang_totals(comp: np.ndarray) -> np.ndarray:
    """(R, NL) speakers of each home language from a (R, 2, G) composition."""
    out = np.zeros((comp.shape[0], NL))
    np.add.at(out, (slice(None), np.array([LANG_INDEX[l] for _, l in GROUPS])), comp.sum(axis=1))
    return out


def _dominant(params: dict, regions, comp: np.ndarray) -> list[str]:
    """Contact language per region; "auto:a,b,c" picks the listed language
    with the most 1931 speakers in the region ("b+d": b, counting d's
    speakers with it)."""
    out = []
    L = _lang_totals(comp)
    for i, r in enumerate(regions):
        v = region_lookup(params["dominant_language"], r.code, "pl")
        if isinstance(v, str) and v.startswith("auto"):
            # "auto:pl,be+pls": Belarusian counts West Polesian speakers too
            cand = v.split(":", 1)[1].split(",") if ":" in v else ["pl", "uk", "be", "lt"]
            v = max(cand, key=lambda c: sum(L[i, LANG_INDEX[l]] for l in c.split("+"))).split("+")[0]
        out.append(v)
    return out


def _official(params: dict, regions, dominant: list[str]) -> list[list[str]]:
    """Official languages per region (the contact language is always one)."""
    out = []
    for r, d in zip(regions, dominant):
        v = region_lookup(params.get("official_languages") or {}, r.code, None)
        if v == "all":
            v = [lg.code for lg in LANGUAGES]
        langs = list(dict.fromkeys([d] + list(v or [])))
        out.append(langs)
    return out


BILING_AGE = np.ones(101)
BILING_AGE[:7] = 0.25
BILING_AGE[7:15] = 0.9
BILING_AGE[15:30] = 1.15
BILING_AGE[50:65] = 0.85
BILING_AGE[65:] = 0.7


@dataclass
class Results:
    params: dict
    region_codes: list[str]
    region_names: list[str]
    years: list[int] = field(default_factory=list)
    pop: list = field(default_factory=list)          # (R,2,G) per year
    bil: list = field(default_factory=list)          # (R,2,G) with b=1
    births: list = field(default_factory=list)       # (R,)
    deaths: list = field(default_factory=list)       # (R,)
    tfr: list = field(default_factory=list)          # (R,)
    e0: list = field(default_factory=list)           # (R,2) m,f
    imr: list = field(default_factory=list)          # (R,)
    emig: list = field(default_factory=list)         # (R,G)
    immig: list = field(default_factory=list)        # (R,G)
    internal: list = field(default_factory=list)     # (R,R)
    rural_urban: list = field(default_factory=list)  # (R,)
    shifts: list = field(default_factory=list)       # (NL_from, NL_to) births raised in another language
    shift_net: list = field(default_factory=list)    # (R,2,NL) net language shift (vertical + horizontal)
    econ: list = field(default_factory=list)         # dict per year
    rel_income: list = field(default_factory=list)   # (R,)
    km: list = field(default_factory=list)           # dict per year
    town_pop: list = field(default_factory=list)     # (N,)
    access: list = field(default_factory=list)       # (R,) market access index
    pyramids: dict = field(default_factory=dict)     # year -> (NL, S, A)
    census: dict = field(default_factory=dict)       # (regime, year) -> (R, n_cat)
    network_snapshots: dict = field(default_factory=dict)
    project_log: list = field(default_factory=list)
    node_names: list = field(default_factory=list)
    node_lat: list = field(default_factory=list)
    node_lon: list = field(default_factory=list)
    node_region: list = field(default_factory=list)
    national: list = field(default_factory=list)     # dict per year
    members: list = field(default_factory=list)      # federal member state of each region
    dominant: list = field(default_factory=list)     # contact language of each region
    official: list = field(default_factory=list)     # official languages of each region
    exchange: dict = field(default_factory=dict)     # population exchange (plsim.exchange), if any
    identity: list = field(default_factory=list)     # (R,NI) national identity per year (plsim.identity)
    identity0: np.ndarray | None = None              # (R,NI) at the start
    identity_lang: dict = field(default_factory=dict)  # snapshot year -> (R,NL,NI) identity by home language
    pop0: np.ndarray | None = None                   # (R,2,G) initial state (start_year)
    town_pop0: np.ndarray | None = None              # (N,) initial town populations

    def arrays(self) -> dict:
        return {k: np.array(getattr(self, k)) for k in
                ["pop", "bil", "births", "deaths", "tfr", "e0", "imr", "emig", "immig", "internal",
                 "rural_urban", "shifts", "shift_net", "rel_income", "town_pop", "access", "identity"]}


class Simulation:
    def __init__(self, params: dict):
        self.params = copy.deepcopy(params)
        p = self.params
        # Independent random streams per component ("common random numbers"):
        # scenarios that share a seed share their economic, demographic and
        # network shocks, so scenario differences are not sampling noise.
        ss = np.random.SeedSequence(p.get("seed", 0))
        econ_ss, demo_ss, net_ss = ss.spawn(3)
        self.rng = np.random.default_rng(demo_ss)
        self.econ_rng = np.random.default_rng(econ_ss)
        self.net_rng = np.random.default_rng(net_ss)
        self.regions = select_regions(p["include_lithuania"], p.get("include_belarus", False),
                                      p.get("include_krai_east", False))
        self._comp = None
        node_region = {}
        if p.get("partition") or p.get("governorates"):
            from .partition import apply_partition
            self.regions, self._comp, node_region, labels = apply_partition(self.regions, p)
            if p.get("governorates"):
                resolve_governorates(p, labels)
        if self._comp is None:
            self._comp = build_initial_composition(self.regions, p["census_variant"], p["lt_variant"]).pop
        if p.get("exclude"):
            # regions left out of the state: their people, towns and land are foreign
            keep = [i for i, r in enumerate(self.regions)
                    if not any(region_match(r.code, e) for e in p["exclude"])]
            self.regions = [self.regions[i] for i in keep]
            self._comp = self._comp[keep]
        self.codes = [r.code for r in self.regions]
        self.R = len(self.regions)
        # Regional noise is drawn per 1931 voivodeship and shared by its
        # sub-regions, so a county run uses the same random numbers as the
        # voivodeship run (and the national shocks stay in step).
        parents = list(dict.fromkeys(c.split(".")[0] for c in self.codes))
        self.parent_idx = np.array([parents.index(c.split(".")[0]) for c in self.codes])
        self.n_parent = len(parents)
        self.dominant = _dominant(p, self.regions, self._comp)
        self.official = _official(p, self.regions, self.dominant)
        self.dom_idx = np.array([LANG_INDEX[d] for d in self.dominant])
        self.mort = _mortality()
        self.fsched = FertilitySchedule()
        self.group_comm = np.array([COMM_INDEX[c] for c, _ in GROUPS])
        self.group_lang = np.array([LANG_INDEX[l] for _, l in GROUPS])
        self.econ = Economy(p["economy"], self.regions, self.econ_rng)
        self.lang = LanguageModel(p["language"], self.regions, self.dominant, self.official)
        self.mig = MigrationModel(p["migration"], self.regions, self.dominant)
        self.member = [region_lookup(p["members"], c, "PL") for c in self.codes]
        self.mig.member = np.array(self.member)
        # separate states (two sovereign states in one run): their own economy
        sep = list(p.get("separate_states") or [])
        self.state = np.array([1 + sep.index(m) if m in sep else 0 for m in self.member])
        kby = p["economy"].get("kappa_by_state") or {}
        self.econ.set_states(self.state, np.array([r.pop_1931 for r in self.regions]),
                             [None] + [kby.get(m) for m in sep])
        infra_p = copy.deepcopy(p["infrastructure"])
        infra_p["node_region"] = node_region
        infra_p["region_seats"] = [(r.lat, r.lon) for r in self.regions]
        self.net = Network(infra_p, self.codes, federation=p["federation"] and p["include_lithuania"], rng=self.net_rng)
        self._init_population()
        self.ident = IdentityModel(p["identity"], self.codes, self.dominant, self.P.sum(axis=(3, 4, 5)))
        if len({c.split(".")[0] for c in self.codes}) < self.R:
            self.lang.nest_concentration(self.P, self.codes)
        self._init_vital_rates()
        # town share of urban population (towns in the node list vs all urban places)
        urb_k = self.P[:, 1].sum(axis=(1, 2, 3, 4)) / 1000.0
        share = np.zeros(self.R)
        for r in range(self.R):
            share[r] = min(1.0, self.net.pop[self.net.region == r].sum() / max(urb_k[r], 1e-9))
        self.net.p["town_share_of_urban"] = share
        self.year = p["start_year"]
        self.res = Results(params=self.params, region_codes=self.codes,
                           region_names=[r.name for r in self.regions])
        self.res.node_names = list(self.net.names)
        self.res.node_lat = self.net.lat.tolist()
        self.res.node_lon = self.net.lon.tolist()
        self.res.node_region = self.net.region.tolist()
        self.res.members = list(self.member)
        self.res.dominant = list(self.dominant)
        self.res.official = [list(o) for o in self.official]
        self.res.pop0 = self.P.sum(axis=(3, 4, 5)).astype(np.float32)
        self.res.identity0 = self.ident.by_region().astype(np.float32)
        self.res.town_pop0 = self.net.pop.copy()
        self._last_log_ma = None
        self._d_log_ma = np.zeros(self.R)
        self._shift_acc = np.zeros((NL, NL))

    # ------------------------------------------------------------------ initialisation
    def _init_population(self):
        p = self.params
        comp = self._comp if self._comp is not None else \
            build_initial_composition(self.regions, p["census_variant"], p["lt_variant"]).pop
        fert = p["fertility"]
        mort = p["mortality"]
        R = self.R
        self.P = np.zeros((R, 2, NG, 2, 2, 101))
        for r, reg in enumerate(self.regions):
            for u in (0, 1):
                for c in range(NC):
                    gs = [g for g in range(NG) if self.group_comm[g] == c and comp[r, u, g] > 0]
                    if not gs:
                        continue
                    cc = COMMUNITIES[c].code
                    tfr = (reg.tfr_urban if u else reg.tfr_rural) * fert["community_mult"].get(cc, 1.0)
                    e0f = reg.e0_female + (mort["urban_e0_adj"] if (u and reg.code != "WAW") else 0.0) + \
                        mort["community_e0_adj"].get(cc, 0.0)
                    e0m = e0f - piecewise(1931, mort["sex_gap"])
                    # Age structures reflect the higher fertility of the preceding
                    # decades (and urban in-migration of young adults), so the stable
                    # population is built on a blend of current and pre-war fertility.
                    tfr_struct = fert["struct_weight_current"] * tfr + \
                        (1 - fert["struct_weight_current"]) * fert["struct_tfr_past"]
                    old = stable_age_distribution(tfr_struct, e0f, e0m, self.mort, reg.partition)
                    new = stable_age_distribution(tfr * fert["tfr_scale"], e0f, e0m, self.mort, reg.partition)
                    # the youngest cohorts reflect current fertility (scaled to the same
                    # number of women aged 15-49), older ones the past
                    wa = np.clip((np.arange(101) - 2) / 10.0, 0, 1)
                    k_old = old[1, 15:50].sum() / max(new[1, 15:50].sum(), 1e-12)
                    ages = new * k_old * (1 - wa) + old * wa
                    ages /= ages.sum()
                    for g in gs:
                        grp = GROUPS[g]
                        bsh = bilingual_share(grp, self.dominant[r], u)
                        bage = np.clip(bsh * BILING_AGE, 0, 0.98) if bsh < 1 else np.ones(101)
                        tot = comp[r, u, g]
                        for s in (0, 1):
                            self.P[r, u, g, 1, s] = tot * ages[s] * bage
                            self.P[r, u, g, 0, s] = tot * ages[s] * (1 - bage)
        self.mig.reset_competence(self.P)

    def _init_vital_rates(self):
        p = self.params
        fert, mort = p["fertility"], p["mortality"]
        R = self.R
        self.tfr = np.zeros((R, 2, NC))
        self.e0f = np.zeros((R, 2, NC))
        self.e0_adj0 = np.zeros((R, 2, NC))
        for r, reg in enumerate(self.regions):
            for u in (0, 1):
                for c in range(NC):
                    cc = COMMUNITIES[c].code
                    self.tfr[r, u, c] = (reg.tfr_urban if u else reg.tfr_rural) * fert["community_mult"].get(cc, 1.0) \
                        * fert["tfr_scale"]
                    adj = (mort["urban_e0_adj"] if (u and reg.code != "WAW") else 0.0) + \
                        mort["community_e0_adj"].get(cc, 0.0)
                    self.e0f[r, u, c] = reg.e0_female + adj
                    self.e0_adj0[r, u, c] = mort["community_e0_adj"].get(cc, 0.0)
        self.U = np.maximum(self.tfr, fert["pretransition_U"])
        self.phase3 = np.zeros((R, 2, NC), dtype=bool)
        mu = fert["phase3_mu"]
        self.mu3 = np.array([mu.get(c.code, mu["default"]) for c in COMMUNITIES])
        self.group_fert = np.array([fert["group_mult"].get(f"{c}:{l}", 1.0) for c, l in GROUPS])
        self.group_e0 = np.array([mort["group_e0_adj"].get(f"{c}:{l}", 0.0) for c, l in GROUPS])
        self.pace_c = np.array([fert["community_pace"].get(c.code, 1.0) for c in COMMUNITIES])

    # ------------------------------------------------------------------ helpers
    def urban_share(self) -> np.ndarray:
        tot = self.P.sum(axis=(2, 3, 4, 5))
        return tot[:, 1] / np.clip(tot.sum(axis=1), 1e-9, None)

    def region_pop(self) -> np.ndarray:
        return self.P.sum(axis=(1, 2, 3, 4, 5))

    # ------------------------------------------------------------------ network
    def _network_step(self, year: int):
        ip = self.net.p
        net = self.net
        net.inject_dated_projects(year, ip["enable_planned"], ip["planned_delay"])
        net.open_pending(year)
        veh = self.econ.vehicles_per_1000
        net.travel_times(year, veh)
        # node incomes (relative)
        rel = np.ones(net.N)
        yreg = self.econ.region_income()
        ybar = self.econ.y_nat
        for r in range(self.R):
            rel[net.region == r] = yreg[r] / ybar
        masses = net.masses(rel)
        total_pop_k = self.region_pop().sum() / 1000.0
        net.demand(masses, piecewise(year, ip["trip_rate"]), total_pop_k)
        ma = net.market_access(masses)
        # regional market access (population weighted over towns)
        reg_ma = np.zeros(self.R)
        caps = net.region_capital_nodes()
        acc = net.region_access_hours(year)
        for r in range(self.R):
            idx = net.region == r
            if idx.any():
                reg_ma[r] = (ma[idx] * net.pop[idx]).sum() / max(net.pop[idx].sum(), 1e-9)
            else:       # a county without a modelled town: access through the nearest one
                reg_ma[r] = ma[caps[r]] * np.exp(-ip["ma_theta"] * acc[r])
        log_ma = np.log(reg_ma)
        if self._last_log_ma is not None:
            self._d_log_ma = log_ma - self._last_log_ma
        self._last_log_ma = log_ma
        self.reg_ma = reg_ma
        if not hasattr(self, "_ma_ref"):
            self._ma_ref = reg_ma.copy()
        # investment
        if (year - self.params["start_year"]) % ip["appraisal_interval"] == 0:
            budget = self.econ.infra_budget(year, self.region_pop().sum()) * ip["appraisal_interval"]
            vot = rel * self.econ.y_nat / 2000.0 * ip["vot_share"]
            ew = piecewise(year, ip["equity_weight"])
            equity = np.clip(1.0 / np.clip(rel, 0.2, None), 0.2, 5.0) ** ew
            equity[net.foreign] = 0.5
            # rural hinterland population attached to each town (persons)
            rural = self.P[:, 0].sum(axis=(1, 2, 3, 4))
            hinter = np.zeros(net.N)
            for r in range(self.R):
                idx = np.where(net.region == r)[0]
                if len(idx):
                    hinter[idx] += rural[r] / len(idx) + net.pop[idx] * 1000.0 * 0.3
                else:
                    hinter[caps[r]] += rural[r]
            if len(self.econ.y_state) == 1:
                net.invest(year, budget, veh, vot, equity, ip["bcr_threshold"], hinter)
            else:            # separate states: each builds on its own territory from its own GDP
                budgets = self.econ.infra_budgets(year, self.region_pop()) * ip["appraisal_interval"]
                for k, b in enumerate(budgets):
                    nodes = {i for i in range(net.N) if net.region[i] >= 0 and self.state[net.region[i]] == k}
                    net.invest(year, float(b), veh, vot, equity, ip["bcr_threshold"], hinter, nodes=nodes, key=k)
        net.rationalise(year, veh)
        # towns
        urb_k = self.P[:, 1].sum(axis=(1, 2, 3, 4)) / 1000.0
        net.update_towns(urb_k, year)
        # region-to-region travel times through capitals
        self.t_reg = net.D[np.ix_(caps, caps)] + acc[:, None] + acc[None, :]

    # ------------------------------------------------------------------ vital rates
    def _update_mortality(self, year: int, M: np.ndarray):
        mp = self.params["mortality"]
        front = frontier_e0_female(year, mp["frontier_slope"], mp["frontier_slope_post2000"])
        ycell = self.econ.cell_income(self.urban_share())                     # (R,2)
        yrel = ycell / self.econ.y_frontier
        gap = target_gap(yrel, mp["gap_min"], mp["gap_max"], mp["gap_power"])  # (R,2)
        decay = 0.5 ** ((year - self.params["start_year"]) / mp["adj_halflife"])
        target = front - gap[:, :, None] + self.e0_adj0 * decay
        lam = catchup_rate(year, mp["catchup_pre"], mp["catchup_post"])
        shock = self.rng.normal(0, mp["shock_sd"])
        noise = self.rng.normal(0, 0.1, (self.n_parent,) + self.e0f.shape[1:])[self.parent_idx]
        self.e0f += lam * (target - self.e0f) + shock + noise
        self.e0f = np.minimum(self.e0f, front + 1.0)

    def _update_fertility(self, year: int, M: np.ndarray):
        fp = self.params["fertility"]
        pace = np.clip((M - fp["pace_M0"]) / (fp["pace_M1"] - fp["pace_M0"]), fp["pace_min"], fp["pace_max"])
        d = fp["d_max"] * pace[:, :, None] * self.pace_c[None, None, :]
        dec = alkema_decrement(self.tfr, self.U, d, fp["D1"], fp["D3"], fp["D4"]) / 5.0
        f2 = np.where(self.phase3, self.tfr, self.tfr - dec)
        # phase III
        enter = (~self.phase3) & (f2 <= fp["D4"] + fp["phase3_entry_margin"])
        self.phase3 |= enter
        mu = np.broadcast_to(self.mu3[None, None, :], self.tfr.shape)
        rho = fp["phase3_rho"]
        noise = self.rng.normal(0, fp["phase3_sd"], (self.n_parent,) + self.tfr.shape[1:])[self.parent_idx]
        ph3 = mu + rho * (self.tfr - mu) + noise
        self.tfr = np.where(self.phase3 & ~enter, ph3, f2)
        # Haredi: slow drift towards their own long-run mean instead of the Alkema curve
        jh = COMM_INDEX["JH"]
        self.tfr[:, :, jh] = self.mu3[jh] + 0.98 * (self.tfr[:, :, jh] - self.mu3[jh])
        self.tfr = np.clip(self.tfr, 0.8, 8.0)

    def _period_factor(self, year: int) -> float:
        fp = self.params["fertility"]
        f = piecewise(year, fp["period"])
        bb = fp["baby_boom"]
        f *= 1 + bb["amplitude"] * np.exp(-0.5 * ((year - bb["centre"]) / bb["width"]) ** 2)
        f *= np.exp(self.rng.normal(0, fp["period_sd"]))
        return f

    # ------------------------------------------------------------------ one year
    def step(self):
        year = self.year
        p = self.params
        R = self.R
        ex = p.get("population_exchange") or {}
        if ex.get("plan") and year == ex["year"]:
            from .exchange import apply_exchange, apply_exchange_identity
            if ex["plan"].get("by") == "identity":          # identity moves with its people
                self.res.exchange = apply_exchange_identity(self.P, self.ident.I, self.codes, ex["plan"])
                self.mig.reset_competence(self.P)
            else:
                before_x = self.P.sum(axis=(3, 4, 5))
                self.res.exchange = apply_exchange(self.P, self.codes, ex["plan"])
                self.mig.reset_competence(self.P)
                self.ident.reconcile(before_x, self.P.sum(axis=(3, 4, 5)))
        P = self.P
        pop_r = self.region_pop()
        self.econ.step(year, self._d_log_ma, pop_r)
        U = self.urban_share()
        M = self.econ.modernisation(U)
        self._network_step(year)
        ma_norm = np.log(self.reg_ma / self._ma_ref.mean())
        ma_norm = np.clip(ma_norm - ma_norm.mean(), -1, 1)
        self._update_mortality(year, M)
        self._update_fertility(year, M)
        fp = p["fertility"]
        period = self._period_factor(year)
        # ---- births
        post = fp["postponement"]
        postpone = min(post["max"], max(0.0, year - post["start"]) * post["rate"]) * self.phase3
        mac = mean_age_childbearing(self.tfr, postpone)
        sched = self.fsched.schedule(mac)                                   # (R,2,C,35)
        asfr = sched * (self.tfr * period)[..., None]                       # (R,2,C,35)
        asfr_g = asfr[:, :, self.group_comm] * self.group_fert[None, None, :, None]   # (R,2,G,35)
        women = P[:, :, :, :, 1, 15:50]                                     # (R,2,G,B,35)
        births_gb = (women * asfr_g[:, :, :, None, :]).sum(axis=4)          # (R,2,G,B)
        # Haredi exit at birth
        ex, en = self.lang.haredi_exit(year)
        jh = [g for g in range(NG) if GROUPS[g][0] == "JH"]
        for g in jh:
            tgt = GROUP_INDEX.get(("JW", GROUPS[g][1]))
            if tgt is not None:
                moved = births_gb[:, :, g] * ex
                births_gb[:, :, g] -= moved
                births_gb[:, :, tgt] += moved
        jwyi, jhyi = GROUP_INDEX[("JW", "yi")], GROUP_INDEX[("JH", "yi")]
        back = births_gb[:, :, jwyi] * en
        births_gb[:, :, jwyi] -= back
        births_gb[:, :, jhyi] += back
        # intergenerational language transmission
        p_shift, dist, frac, mod, pol, omega = self.lang.transmission(year, P, M, ma_norm)
        shifted = births_gb * p_shift                                       # (R,2,G,B)
        stay = births_gb - shifted
        child = stay.sum(axis=3)                                            # (R,2,G)
        child_from_shift = np.einsum("rugk,rug->ruk", dist, shifted.sum(axis=3))
        newborns = child + child_from_shift                                 # (R,2,G)
        births_id = self.ident.birth_counts(child, shifted.sum(axis=3), dist)   # (R,2,G,NI)
        # record shift matrix by language
        flows = np.einsum("rugk,rug->gk", dist, shifted.sum(axis=3))
        for g in range(NG):
            for k in np.nonzero(flows[g] > 0)[0]:
                self._shift_acc[self.group_lang[g], self.group_lang[k]] += flows[g, k]
        fl_ru = dist * shifted.sum(axis=3)[..., None]                        # (R,2,G,G)
        shift_net = self._lang_ru(fl_ru.sum(axis=2)) - self._lang_ru(fl_ru.sum(axis=3))
        # ---- mortality & ageing
        e0f_g = self.e0f[:, :, self.group_comm] + self.group_e0[None, None, :]      # (R,2,G)
        gap = sex_gap(year, p["mortality"]["sex_gap"])
        e0m_g = e0f_g - gap
        s_f = self.mort.survival(e0f_g, 1)                                   # (R,2,G,101)
        s_m = self.mort.survival(e0m_g, 0)
        surv = np.stack([s_m, s_f], axis=3)                                  # (R,2,G,S,101)
        before = P.sum(axis=(1, 2, 3, 4, 5))
        before_g = P.sum(axis=(3, 4, 5))
        Pn = np.zeros_like(P)
        Pn[..., 1:100] = P[..., 0:99] * surv[:, :, :, None, :, 0:99]
        Pn[..., 100] = P[..., 99] * surv[:, :, :, None, :, 99] + P[..., 100] * surv[:, :, :, None, :, 100]
        srb = fp["srb"]
        pm = srb / (1 + srb)
        sb_m = self.mort.birth_survival(e0m_g, 0)
        sb_f = self.mort.birth_survival(e0f_g, 1)
        Pn[:, :, :, 0, 0, 0] = newborns * pm * sb_m
        Pn[:, :, :, 0, 1, 0] = newborns * (1 - pm) * sb_f
        births_r = newborns.sum(axis=(1, 2))
        deaths_r = before + births_r - Pn.sum(axis=(1, 2, 3, 4, 5))
        infant_deaths = (newborns * pm * (1 - sb_m) + newborns * (1 - pm) * (1 - sb_f)).sum(axis=(1, 2))
        self.ident.vital(Pn[..., 1:].sum(axis=(3, 4, 5)), before_g, births_id, Pn[..., 0].sum(axis=(3, 4)))
        self.P = P = Pn
        self.mig.reset_competence(P)
        # ---- horizontal language processes
        before_l = self._lang_ru(P.sum(axis=(3, 4, 5)))
        hz = self.lang.horizontal(year, P, self.econ.enrollment, M, ma_norm)
        self.ident.switch(hz["flows"])
        shift_net += self._lang_ru(P.sum(axis=(3, 4, 5))) - before_l
        # ---- migration
        before_m = P.sum(axis=(3, 4, 5))
        ur = self.mig.urbanisation(P, self.econ.urban_target(), year, self.t_reg)
        x_lang = self.lang.competence_shares(P)
        settle = p["migration"].get("settlement")
        flows_int = self.mig.interregional(P, self.t_reg, self.econ.region_income(), x_lang, year, settle,
                                           y_dest=self.econ.cell_income(self.urban_share())[:, 1])
        intl = self.mig.international(P, year, self.econ.y_of_region(), self.econ.y_frontier,
                                      self.econ.region_income(), self.econ.state)
        self.mig.reset_competence(P)
        np.maximum(P, 0.0, out=P)
        self.ident.reconcile(before_m, P.sum(axis=(3, 4, 5)))
        # ---- national identity: nation-building and the pull of the state nation
        self.ident.drift(M, self.lang.pressure(year))
        # ---- vital-rate diagnostics
        women_tot = P[:, :, :, :, 1, 15:50].sum(axis=3)                      # (R,2,G,35)
        w_c = np.zeros((R, 2, NC, 35))
        np.add.at(w_c, (slice(None), slice(None), self.group_comm), women_tot)
        # TFR by region = sum over ages of population-weighted ASFR
        asfr_r = (asfr * w_c).sum(axis=(1, 2)) / np.clip(w_c.sum(axis=(1, 2)), 1e-9, None)   # (R,35)
        tfr_r = asfr_r.sum(axis=1)
        wpop = P.sum(axis=(3, 4, 5))                                          # (R,2,G)
        wpop_c = np.zeros((R, 2, NC))
        np.add.at(wpop_c, (slice(None), slice(None), self.group_comm), wpop)
        e0f_r = (self.e0f * wpop_c).sum(axis=(1, 2)) / np.clip(wpop_c.sum(axis=(1, 2)), 1e-9, None)
        e0_r = np.stack([e0f_r - gap, e0f_r], axis=1)
        # ---- record (state at 1 Jan year+1, flows during year)
        res = self.res
        res.years.append(year + 1)
        res.pop.append(P.sum(axis=(3, 4, 5)).astype(np.float32))
        res.bil.append(P[:, :, :, 1].sum(axis=(3, 4)).astype(np.float32))
        res.births.append(births_r)
        res.deaths.append(deaths_r)
        res.tfr.append(tfr_r)
        res.e0.append(e0_r)
        res.imr.append(infant_deaths / np.clip(births_r, 1e-9, None))
        res.emig.append(intl["emigrants"].astype(np.float32))
        res.immig.append(intl["immigrants"].astype(np.float32))
        res.internal.append(flows_int.astype(np.float32))
        res.rural_urban.append(ur["rural_urban"])
        res.shifts.append(self._shift_acc.copy())
        res.shift_net.append(shift_net.astype(np.float32))
        res.identity.append(self.ident.by_region().astype(np.float32))
        self._shift_acc[:] = 0
        res.econ.append({"y_nat": self.econ.y_nat, "y_frontier": self.econ.y_frontier,
                         "y_state": [float(v) for v in self.econ.y_state],
                         "vehicles_per_1000": self.econ.vehicles_per_1000,
                         "literacy": float((self.econ.literacy * pop_r).sum() / pop_r.sum()),
                         "infra_account": self.net.account})
        res.rel_income.append(self.econ.rel.copy())
        res.km.append(self.net.km_by_class())
        res.town_pop.append(self.net.pop.copy())
        res.access.append(self.reg_ma.copy())
        if (year + 1) in p["snapshot_years"]:
            self._snapshot(year + 1)
        self.year += 1

    def _lang_ru(self, x: np.ndarray) -> np.ndarray:
        """Sum a (R,2,G) array over groups into languages: (R,2,NL)."""
        out = np.zeros(x.shape[:2] + (NL,))
        np.add.at(out, (slice(None), slice(None), self.group_lang), x)
        return out

    def _snapshot(self, year: int):
        P = self.P
        pyr = np.zeros((NL, 2, 101))
        by_g = P.sum(axis=(0, 1, 3))                                          # (G,S,A)
        np.add.at(pyr, self.group_lang, by_g)
        self.res.pyramids[year] = pyr
        rugb = P.sum(axis=(4, 5))
        for regime in LANGUAGE_REGIMES:
            self.res.census[(regime, year)] = census_view(rugb, regime, self.codes)
        for regime in IDENTITY_REGIMES:      # nationality censuses record identity
            self.res.census[(regime, year)] = identity_census(self.ident.I, regime, self.codes, CENSUS_CATEGORIES)
        self.res.identity_lang[year] = self.ident.by_language().astype(np.float32)
        self.res.network_snapshots[year] = self.net.snapshot()

    def run(self, verbose: bool = False) -> Results:
        self._snapshot(self.year)
        end = self.params["end_year"]
        while self.year < end:
            self.step()
            if verbose and self.year % 10 == 0:
                tot = self.P.sum() / 1e6
                print(f"{self.year}: {tot:.2f} M")
        self.res.project_log = list(self.net.log)
        return self.res


def run_scenario(params: dict, verbose: bool = False) -> Results:
    return Simulation(params).run(verbose=verbose)
