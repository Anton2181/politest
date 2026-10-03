"""Spatial downscaling of the regional projection to a ~3.5 km grid (maps).

The cohort-component model works with 23 regions x rural/urban.  For maps,
each region's population and languages are placed on grid cells and towns
and carried forward year by year.  At every step the cells of a region add
up exactly to the main model's regional figures.  The spatial layer adds
geography, not new demography.

Initial state (1932)
--------------------
This is spatial microsimulation by iterative proportional fitting (IPF;
Ballas et al. 2005, Lovelace & Dumont 2016).

* Rural population is spread in proportion to cell area times a terrain
  factor (thin Polesie marshes and Carpathians).
* A seed of language shares is interpolated from the 1931 county anchors
  in ``data.geography`` with a Gaussian kernel.
* The seed is fitted by IPF to the cell totals and to the region x
  language totals of the main model.
* Towns (the transport-network nodes) start from the regional urban mix,
  tilted toward the languages of their hinterland.  The remaining urban
  population (small towns not in the network) is spread over cells.

Yearly update, for each region and rural/urban stratum
------------------------------------------------------
1. Unit totals.  Towns follow the network model.  Rural cells grow with
   their region, plus a small premium for being near growing towns
   (suburbanisation, depopulation of remote countryside).
2. Language shift.  The region's net shift (vertical and horizontal,
   recorded by the main model) is placed with a neighbourhood rule after
   Prochazka & Vogl (2017, PNAS 114:4365).  Their result: the most important
   factor in a speaker's shift is how many speakers of each language live
   in the village and its Gaussian neighbourhood.
   * Losses: the per-capita chance that a speaker of a losing language
     shifts at a place is ``kappa0 + G^a``, where ``G`` is the local
     neighbourhood share of the gaining languages, ``a`` is the
     Abrams-Strogatz exponent, and ``kappa0`` is a neighbourhood-free part
     (schooling, church, the state).
   * Gains: these go to the gaining languages in proportion to
     ``(kappa0 + K_l)^a``.
   * Towns enter the neighbourhood with a kernel that widens with town
     size: hierarchical, town-to-hinterland diffusion (Trudgill 1974).
3. IPF to the new unit totals and to the region x language totals.
   Differences in fertility, mortality and migration between language
   groups are therefore applied uniformly within each stratum, while
   shift is placed where contact happens.  Language islands erode first
   and contact zones move as fronts (Patriarca & Heinsalu 2009; Isern &
   Fort 2014; Burridge 2017).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import sparse
from scipy.spatial import cKDTree

from .data.geography import ANCHORS, Grid, build_grid, haversine_matrix
from .data.languages import GROUPS, LANG_INDEX, NL
from .params import DEFAULTS

GROUP_LANG = np.array([LANG_INDEX[l] for _, l in GROUPS])


def lang_totals(x: np.ndarray) -> np.ndarray:
    """Sum the trailing group axis into languages: (..., G) -> (..., NL)."""
    out = np.zeros(x.shape[:-1] + (NL,))
    for g, l in enumerate(GROUP_LANG):
        out[..., l] += x[..., g]
    return out


def _xy_km(lat, lon, lon0: float = 22.0) -> np.ndarray:
    """Sinusoidal projection in km (good to a few % over the domain)."""
    lat = np.asarray(lat, float)
    lon = np.asarray(lon, float)
    return np.column_stack([(lon - lon0) * 111.32 * np.cos(np.radians(lat)), lat * 111.32])


def _indicator(key: np.ndarray, n_keys: int) -> sparse.csr_matrix:
    return sparse.csr_matrix((np.ones(len(key)), (key, np.arange(len(key)))), shape=(n_keys, len(key)))


def ipf(seed: np.ndarray, row_tot: np.ndarray, A: sparse.csr_matrix, key: np.ndarray, col_tot: np.ndarray,
        n_iter: int = 40, tol: float = 1e-6) -> np.ndarray:
    """Iterative proportional fitting of ``seed`` (units x languages) to unit
    totals and to stratum x language totals (``A`` aggregates units to strata).
    Stops once every stratum x language total is within ``tol`` (relative)."""
    X = seed.copy()
    for _ in range(n_iter):
        cs = A @ X
        f = np.where(cs > 0, col_tot / np.maximum(cs, 1e-30), 0.0)
        live = cs > 1e-9
        if live.any() and np.abs(f[live] - 1.0).max() < tol:
            break
        X *= f[key]
        rs = X.sum(axis=1)
        X *= np.where(rs > 0, row_tot / np.maximum(rs, 1e-30), 0.0)[:, None]
    return X


@dataclass
class SpatialResult:
    grid: Grid
    years: list
    cells: np.ndarray        # (T, Nc, NL) rural + small-town population by language
    towns: np.ndarray        # (T, Nt, NL) network towns
    town_names: list
    town_lat: np.ndarray
    town_lon: np.ndarray
    town_region: np.ndarray
    region_codes: list
    params: dict

    def frame(self, year: int) -> int:
        return self.years.index(year)

    def town_spread(self, j: int) -> sparse.csr_matrix:
        """Cells x towns weights drawing each town as an area at urban density."""
        rho = self.params["urban_density"]
        g = self.grid
        pop = self.towns[j].sum(axis=1)
        r_km = np.sqrt(pop / rho / np.pi)
        s = np.maximum(r_km / 1.5, 2.5)
        cell_xy = _xy_km(g.lat, g.lon)
        town_xy = _xy_km(self.town_lat, self.town_lon)
        tree = cKDTree(cell_xy)
        rows, cols, vals = [], [], []
        for n in range(len(pop)):
            idx = tree.query_ball_point(town_xy[n], r=max(3 * s[n], 6.0))
            if not idx:
                idx = [int(tree.query(town_xy[n])[1])]
            d2 = ((cell_xy[idx] - town_xy[n]) ** 2).sum(axis=1)
            w = np.exp(-d2 / (2 * s[n] ** 2))
            w /= w.sum()
            rows += list(idx)
            cols += [n] * len(idx)
            vals += list(w)
        return sparse.csr_matrix((vals, (rows, cols)), shape=(len(g.lat), len(pop)))

    def display(self, j: int) -> np.ndarray:
        """(Nc, NL) persons per cell with towns drawn as areas."""
        return self.cells[j] + self.town_spread(j) @ self.towns[j]

    def density(self, j: int) -> np.ndarray:
        return self.display(j).sum(axis=1) / self.grid.cell_km2


class Downscaler:
    def __init__(self, res, sp: dict | None = None, grid: Grid | None = None):
        self.res = res
        self.p = dict(DEFAULTS["spatial"])
        self.p.update((res.params or {}).get("spatial", {}))
        if sp:
            self.p.update(sp)
        self.codes = list(res.region_codes)
        self.R = len(self.codes)
        self.grid = grid or build_grid(self.codes)
        g = self.grid
        self.Nc = len(g.lat)
        node_region = np.array(res.node_region)
        self.town_idx = np.where(node_region >= 0)[0]
        self.Nt = len(self.town_idx)
        self.town_region = node_region[self.town_idx]
        self.town_lat = np.array(res.node_lat)[self.town_idx]
        self.town_lon = np.array(res.node_lon)[self.town_idx]
        self.town_names = [res.node_names[i] for i in self.town_idx]
        self.cell_xy = _xy_km(g.lat, g.lon)
        self.town_xy = _xy_km(self.town_lat, self.town_lon)
        tree = cKDTree(self.cell_xy)
        self.town_cell = tree.query(self.town_xy)[1]
        # units: rural cells | small-town urban cells | towns
        Nc, Nt = self.Nc, self.Nt
        self.N = 2 * Nc + Nt
        self.unit_region = np.concatenate([g.region, g.region, self.town_region])
        self.unit_u = np.concatenate([np.zeros(Nc, int), np.ones(Nc, int), np.ones(Nt, int)])
        self.unit_cell = np.concatenate([np.arange(Nc), np.arange(Nc), self.town_cell])
        self.key = 2 * self.unit_region + self.unit_u
        self.A = _indicator(self.key, 2 * self.R)
        # neighbourhood kernel between cells
        sig = self.p["sigma_km"]
        pairs = tree.query_pairs(r=self.p["cutoff_sigmas"] * sig, output_type="ndarray")
        d2 = ((self.cell_xy[pairs[:, 0]] - self.cell_xy[pairs[:, 1]]) ** 2).sum(axis=1)
        w = np.exp(-d2 / (2 * sig ** 2))
        W = sparse.coo_matrix((np.concatenate([w, w, np.ones(Nc)]),
                               (np.concatenate([pairs[:, 0], pairs[:, 1], np.arange(Nc)]),
                                np.concatenate([pairs[:, 1], pairs[:, 0], np.arange(Nc)]))), shape=(Nc, Nc))
        self.W = W.tocsr()
        D_ct = np.sqrt(((self.cell_xy[:, None, :] - self.town_xy[None, :, :]) ** 2).sum(axis=2))   # (Nc,Nt)
        self.E_pull = np.exp(-D_ct / self.p["pull_km"])                                       # town potential
        # cell-town pairs within the largest town-influence radius any town reaches
        tp_max = np.array([res.town_pop0] + list(res.town_pop), float)[:, self.town_idx].max(axis=0) * 1000.0
        s_max = self.p["town_sigma_km"] * np.maximum(1.0, tp_max / 20000.0) ** self.p["town_sigma_exp"]
        ci, ti = np.nonzero(D_ct <= self.p["cutoff_sigmas"] * s_max[None, :])
        self._ct = (ci, ti, D_ct[ci, ti])
        del D_ct
        self.WT = None
        # yearly regional targets
        self.years = [res.params["start_year"]] + list(res.years)
        pops = [res.pop0] + list(res.pop)
        self.T = np.array([lang_totals(np.asarray(p, float)) for p in pops])          # (T,R,2,NL)
        self.shift = np.array([np.asarray(s, float) for s in res.shift_net])          # (T-1,R,2,NL)
        self.town_pop = np.array([res.town_pop0] + list(res.town_pop), float)[:, self.town_idx] * 1000.0

    # ------------------------------------------------------------------ helpers
    def _town_kernel(self, town_pop: np.ndarray) -> sparse.csr_matrix:
        s = self.p["town_sigma_km"] * np.maximum(1.0, town_pop / 20000.0) ** self.p["town_sigma_exp"]
        ci, ti, d = self._ct
        k = np.exp(-d ** 2 / (2 * s[ti] ** 2)) * (d <= self.p["cutoff_sigmas"] * s[ti]) * self.p["town_weight"]
        return sparse.csr_matrix((k, (ci, ti)), shape=(self.Nc, self.Nt))

    def neighbourhood(self, C: np.ndarray) -> np.ndarray:
        """Kernel-smoothed language shares around every unit: (N, NL)."""
        Nc = self.Nc
        cellpop = C[:Nc] + C[Nc:2 * Nc]
        np.add.at(cellpop, self.town_cell, C[2 * Nc:])
        num = self.W @ cellpop + self.WT @ C[2 * Nc:]
        den = num.sum(axis=1, keepdims=True)
        K = np.where(den > 0, num / np.maximum(den, 1e-30), 0.0)
        return K[self.unit_cell]

    def _pull(self, town_pop: np.ndarray) -> np.ndarray:
        return self.E_pull @ town_pop + 1.0

    def _targets(self, t: int):
        """Unit totals for year index t (rural cells need the previous state)."""
        T = self.T[t]                                                   # (R,2,NL)
        urban = T[:, 1].sum(axis=1)
        tp = self.town_pop[t].copy()
        tsum = np.bincount(self.town_region, weights=tp, minlength=self.R)
        scale = np.where(tsum > urban, urban / np.maximum(tsum, 1e-9), 1.0)
        tp *= scale[self.town_region]
        tsum = np.bincount(self.town_region, weights=tp, minlength=self.R)
        return T, tp, np.maximum(urban - tsum, 0.0)

    def _anchor_seed(self) -> np.ndarray:
        g = self.grid
        F = np.full((self.Nc, NL), np.nan)
        sig = self.p["anchor_sigma_km"]
        for r, code in enumerate(self.codes):
            cells = np.where(g.region == r)[0]
            anc = [a for a in ANCHORS if a.region == code.split(".")[0]]
            if not anc or not len(cells):
                continue
            D = haversine_matrix(g.lat[cells], g.lon[cells], np.array([a.lat for a in anc]),
                                 np.array([a.lon for a in anc]))
            D2 = D ** 2 - (D ** 2).min(axis=1, keepdims=True)
            Kw = np.exp(-D2 / (2 * sig ** 2))
            Kw /= Kw.sum(axis=1, keepdims=True)
            for l in sorted({l for a in anc for l in a.shares}):
                F[cells, LANG_INDEX[l]] = Kw @ np.array([a.shares.get(l, 0.0) for a in anc])
        return F

    # ------------------------------------------------------------------ run
    def initial_state(self) -> np.ndarray:
        g, p = self.grid, self.p
        Nc = self.Nc
        T, tp, small_urban = self._targets(0)
        pull = self._pull(tp)
        # rural totals
        w = g.terrain * g.cell_km2 * (pull / pull.mean()) ** 0.1
        wsum = np.bincount(g.region, weights=w, minlength=self.R)
        rural_tot = T[:, 0].sum(axis=1)
        D = w / np.maximum(wsum[g.region], 1e-30) * rural_tot[g.region]
        # language seed: anchor field, uniform regional share, dominant remainder
        F = self._anchor_seed()
        share_r = T[:, 0] / np.maximum(T[:, 0].sum(axis=1, keepdims=True), 1e-30)
        uni = share_r[g.region]
        home = (lambda c: "lt" if c.startswith("LT") else "be" if c.startswith(("BY_", "RU_"))
                else "lv" if c.startswith("LV_") else "pl")
        dom = np.array([LANG_INDEX[home(c)] for c in self.codes])[g.region]
        seed = np.where(np.isnan(F), uni, F)
        seed[np.arange(Nc), dom] = 0.0
        seed[np.arange(Nc), dom] = np.maximum(0.02, 1.0 - seed.sum(axis=1))
        seed = seed * D[:, None] + p["seed_floor"] * 0.01 * D[:, None] * uni
        rural = ipf(seed, D, _indicator(g.region, self.R), g.region, T[:, 0])
        # urban: towns and small towns, regional mix tilted toward the hinterland
        rshare = rural / np.maximum(rural.sum(axis=1, keepdims=True), 1e-30)
        cell_urb_w = D / np.maximum(np.bincount(g.region, weights=D, minlength=self.R)[g.region], 1e-30)
        U = cell_urb_w * small_urban[g.region]
        ushare = T[:, 1] / np.maximum(T[:, 1].sum(axis=1, keepdims=True), 1e-30)
        tilt = (p["town_seed_floor"] + np.concatenate([rshare, rshare[self.town_cell]])) ** p["town_seed_exp"]
        ureg = np.concatenate([g.region, self.town_region])
        useed = ushare[ureg] * tilt
        utot = np.concatenate([U, tp])
        useed = useed / np.maximum(useed.sum(axis=1, keepdims=True), 1e-30) * utot[:, None]
        urban = ipf(useed + 1e-9 * utot[:, None], utot, _indicator(ureg, self.R), ureg, T[:, 1])
        return np.concatenate([rural, urban[:Nc], urban[Nc:]])

    def step(self, C: np.ndarray, t: int) -> np.ndarray:
        """Advance from year index t-1 to t."""
        p, g = self.p, self.grid
        Nc = self.Nc
        T, tp, small_urban = self._targets(t)
        # 1. unit totals
        tot = C.sum(axis=1)
        pull = np.log(self._pull(tp))
        new_tot = np.empty(self.N)
        for part, total_r, beta in ((slice(0, Nc), T[:, 0].sum(axis=1), p["beta_access"]),
                                    (slice(Nc, 2 * Nc), small_urban, 2 * p["beta_access"])):
            x = tot[part]
            wsum = np.bincount(g.region, weights=x, minlength=self.R)
            mean = np.bincount(g.region, weights=x * pull, minlength=self.R) / np.maximum(wsum, 1e-30)
            gw = x * np.exp(beta * np.clip(pull - mean[g.region], -3, 3))
            gsum = np.bincount(g.region, weights=gw, minlength=self.R)
            fallback = g.cell_km2 * g.terrain
            fsum = np.bincount(g.region, weights=fallback, minlength=self.R)
            new_tot[part] = np.where(gsum[g.region] > 0, gw / np.maximum(gsum[g.region], 1e-30),
                                     fallback / np.maximum(fsum[g.region], 1e-30)) * total_r[g.region]
        new_tot[2 * Nc:] = tp
        # carry the composition forward
        share = C / np.maximum(tot, 1e-30)[:, None]
        empty = tot <= 0
        if empty.any():
            reg_share = (self.A @ C) / np.maximum((self.A @ C).sum(axis=1, keepdims=True), 1e-30)
            share[empty] = reg_share[self.key[empty]]
        S = share * new_tot[:, None]
        # 2. language shift with the neighbourhood rule
        if t - 1 < len(self.shift):
            delta = self.shift[t - 1].reshape(2 * self.R, NL)
            S = self._shift(S, self.neighbourhood(C), delta)
        # 3. fit to the main model
        col = T.reshape(2 * self.R, NL)
        stratum_share = col / np.maximum(col.sum(axis=1, keepdims=True), 1e-30)
        S = S + p["seed_floor"] * 0.01 * new_tot[:, None] * stratum_share[self.key]
        return ipf(S, new_tot, self.A, self.key, col)

    def _shift(self, S: np.ndarray, K: np.ndarray, delta: np.ndarray) -> np.ndarray:
        a, k0 = self.p["a"], self.p["kappa0"]
        key, A = self.key, self.A
        need = np.maximum(-delta, 0.0)                                  # (2R, NL)
        gain_mask = delta > 0
        G = (K * gain_mask[key]).sum(axis=1)
        lam = S * (k0 + G ** a)[:, None]
        cap = 0.95 * S
        x = np.zeros_like(S)
        for _ in range(6):
            remaining = np.maximum(need - A @ x, 0.0)
            if remaining.max() < 1.0:
                break
            lam_f = lam * (x < cap - 1e-9)
            lsum = A @ lam_f
            add = lam_f * (remaining / np.maximum(lsum, 1e-30))[key]
            x = np.minimum(x + add, cap)
        L = x.sum(axis=1)
        lost = (A @ x).sum(axis=1)                                      # realised losses per stratum
        gneed = np.maximum(delta, 0.0)
        gneed *= (lost / np.maximum(gneed.sum(axis=1), 1e-30))[:, None]
        seed = L[:, None] * (k0 + K) ** a * gain_mask[key] + 1e-12 * gain_mask[key]
        y = ipf(seed, L, A, key, gneed, n_iter=20)
        return S - x + y

    def run(self, frame_years=None, verbose: bool = False) -> SpatialResult:
        Nc = self.Nc
        frame_years = list(frame_years) if frame_years is not None else list(self.years)
        C = self.initial_state()
        cells, towns, yrs = [], [], []
        last = max(frame_years) if frame_years else None
        for t, year in enumerate(self.years):
            if last is not None and year > last:
                break
            if t > 0:
                if self.WT is None or (year - self.years[0]) % 5 == 0:
                    self.WT = self._town_kernel(self.town_pop[t - 1])
                C = self.step(C, t)
            elif self.WT is None:
                self.WT = self._town_kernel(self.town_pop[0])
            if year in frame_years:
                cells.append((C[:Nc] + C[Nc:2 * Nc]).astype(np.float32))
                towns.append(C[2 * Nc:].astype(np.float32))
                yrs.append(year)
            if verbose and year % 10 == 0:
                print(year, f"{C.sum() / 1e6:.2f} M")
        return SpatialResult(grid=self.grid, years=yrs, cells=np.array(cells), towns=np.array(towns),
                             town_names=self.town_names, town_lat=self.town_lat, town_lon=self.town_lon,
                             town_region=self.town_region, region_codes=self.codes, params=self.p)


def downscale(res, sp: dict | None = None, frame_years=None, verbose: bool = False) -> SpatialResult:
    return Downscaler(res, sp).run(frame_years=frame_years, verbose=verbose)
