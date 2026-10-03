"""Macro-regional economic drivers (deliberately light-weight).

The economy is not the object of study, but demography, migration, language
contact and network investment all respond to income, so a transparent
reduced-form growth model supplies those drivers:

* National income per head converges towards a fraction ``kappa`` of a
  western-European frontier with the "2 % iron law" speed of conditional
  beta-convergence (Barro 1991; Barro & Sala-i-Martin 1992).  ``kappa`` is the
  main counterfactual lever: ~0.85 is a Finnish path, ~0.6 a southern European
  (Spain/Portugal/Greece) path, ~0.45 a Latin-American/Argentine path.
* Regional relative incomes converge slowly (regional beta ~1.5 %/yr) to
  partially persistent targets (Poland A/B), receive transport market-access
  effects (Donaldson & Hornbeck 2016 market-access elasticity) and explicit
  development programmes (Central Industrial District 1936-, the 1939-54
  Fifteen-Year Plan's goal of erasing the A/B divide).
* Motorisation follows the Gompertz income-saturation curve of Dargay &
  Gately (1999) / Dargay, Gately & Sommer (2007) with partial adjustment,
  calibrated to Poland's ~44 k motor vehicles on 1 Jan 1938.
* Urbanisation targets rise logistically with income (Davis & Henderson 2003)
  and are used by the migration module (Lewis 1954 / Harris-Todaro 1970 logic:
  rural-urban moves respond to the urban-rural income gap).

Separate states. A scenario may hold two states in one run (``separate_states``:
the members that are sovereign, e.g. the Northwestern Krai beside Poland).
Each then has its own national income, starting from its regions' 1931
income level and converging to its own ``kappa`` (by default the same) with
the same shocks; relative incomes are normalised within each state, and each
state has its own infrastructure budget (``infra_budgets``).

All money is in 1990 Geary-Khamis dollars (Maddison convention).
"""
from __future__ import annotations

import numpy as np

from .params import region_lookup


def piecewise(year: float, schedule, kind: str = "linear") -> float:
    """Evaluate a [[year, value], ...] schedule (linear interpolation, or step)."""
    ys = np.array([p[0] for p in schedule], dtype=float)
    vs = np.array([p[1] for p in schedule], dtype=float)
    if kind == "step":
        idx = np.searchsorted(ys, year, side="right") - 1
        return float(vs[max(idx, 0)])
    return float(np.interp(year, ys, vs))


class Economy:
    def __init__(self, params: dict, regions, rng: np.random.Generator):
        self.p = params
        self.regions = regions
        self.rng = rng
        R = len(regions)
        self.y_frontier = params["frontier_1931"]
        self.y_nat = params["y0_1931"]
        rel0 = np.array([r.income_index for r in regions], dtype=float)
        lt_rel = params.get("lithuania_rel", 0.95)
        for i, r in enumerate(regions):
            if r.country == "LT":
                rel0[i] *= lt_rel
        self.rel0 = rel0.copy()
        self.rel = rel0.copy()
        self.literacy = np.array([r.literacy_1931 for r in regions], dtype=float)
        self.enrollment = np.clip(self.literacy + 0.08, 0.0, 0.98)
        self.vehicles_per_1000 = params["vehicles_1938_per_1000"] * 0.95
        self.urban_rural_ratio = piecewise(1931, params["urban_rural_ratio"])
        self.history: dict[str, list] = {"y_nat": [], "y_frontier": [], "vehicles": []}
        self.program_bonus = np.zeros(R)
        self.state = np.zeros(R, dtype=int)          # 0: the main state; 1, 2 ...: separate states
        self.y_state = np.array([self.y_nat])
        self.kappa_state: list = [None]

    def set_states(self, state: np.ndarray, pop: np.ndarray, kappa: list | None = None) -> None:
        """Give separate states (``state`` > 0) their own national income. Each
        starts at its regions' share of the 1931 income, so that regional
        incomes are unchanged at the start."""
        self.state = np.asarray(state, dtype=int)
        S = int(self.state.max()) + 1
        if S == 1:
            return
        pop = np.asarray(pop, float)
        overall = (pop * self.rel0).sum() / pop.sum()
        self.y_state = np.array([self.y_nat * (pop * self.rel0)[self.state == k].sum()
                                 / max(pop[self.state == k].sum(), 1e-9) / overall for k in range(S)])
        self.y_nat = float(self.y_state[0])
        self.kappa_state = list(kappa or [None] * S)

    def y_of_region(self) -> np.ndarray:
        """National income of each region's state."""
        return self.y_state[self.state] if len(self.y_state) > 1 else np.full(len(self.rel), self.y_nat)

    # ------------------------------------------------------------------ incomes
    def region_income(self) -> np.ndarray:
        return self.y_of_region() * self.rel

    def cell_income(self, urban_share: np.ndarray) -> np.ndarray:
        """(R, 2) income per head for rural / urban parts."""
        ratio = self.urban_rural_ratio
        y = self.region_income()
        # y_r = U*y_u + (1-U)*y_rural,  y_u = ratio*y_rural
        yr = y / (urban_share * ratio + (1 - urban_share))
        return np.stack([yr, yr * ratio], axis=1)

    def modernisation(self, urban_share: np.ndarray) -> np.ndarray:
        """(R, 2) modernisation index in [0, 1] (literacy, urbanity, income)."""
        yc = self.cell_income(urban_share)
        inc = np.clip(np.log(yc / 800.0) / np.log(30000 / 800.0), 0, 1)
        lit = self.literacy[:, None]
        urb = np.array([0.0, 1.0])[None, :]
        return np.clip(0.45 * lit + 0.25 * urb + 0.30 * inc, 0, 1)

    def urban_target(self) -> np.ndarray:
        p = self.p["urbanisation"]
        y = self.region_income()
        return p["u_max"] / (1 + np.exp(-p["slope"] * (np.log(y) - np.log(p["y50"]))))

    # ------------------------------------------------------------------- update
    def step(self, year: int, d_log_ma: np.ndarray | None, pop_by_region: np.ndarray) -> None:
        p = self.p
        # Frontier growth.
        gF = piecewise(year, p["frontier_growth"], kind="step")
        self.y_frontier *= np.exp(gF)
        # National income.
        hist = p.get("historical_growth", {})
        if str(year) in hist or year in hist:
            g = np.full(len(self.y_state), hist.get(str(year), hist.get(year)))
        else:
            beta = p["convergence_beta"]
            kappa = np.array([piecewise(year, k if k is not None else p["kappa"]) for k in self.kappa_state])
            g = gF + beta * np.log(kappa * self.y_frontier / self.y_state)
            g += self.rng.normal(0, p["shock_sd"])                       # one shock for all states
            # crises shift timing, not the long-run level: mean-corrected
            g -= p["crisis_prob"] * p["crisis_size"]
            if self.rng.random() < p["crisis_prob"]:
                g += p["crisis_size"]
        self.y_state = self.y_state * np.exp(g)
        self.y_nat = float(self.y_state[0])
        # Regional relative incomes.
        target = self.rel0 ** p["regional_persistence"]
        drel = -p["regional_beta"] * (np.log(self.rel) - np.log(target))
        if d_log_ma is not None:
            drel += p["ma_elasticity"] * d_log_ma
        bonus = np.zeros(len(self.regions))
        progs = p.get("regional_programmes", {})
        for i, r in enumerate(self.regions):
            sched = region_lookup(progs, r.code)
            if sched is not None:
                bonus[i] += piecewise(year, sched)
        # Poland A/B equalisation policy: extra convergence for poor regions.
        eq = piecewise(year, p["equalisation"])
        drel += eq * np.maximum(0, -np.log(self.rel))
        self.rel *= np.exp(drel + bonus)
        # Renormalise to population-weighted mean of one (within each state).
        for k in range(len(self.y_state)):
            m = self.state == k
            w = pop_by_region[m] / pop_by_region[m].sum()
            self.rel[m] /= (w * self.rel[m]).sum()
        # Literacy / schooling (illiteracy closes at a fixed hazard + cohort replacement).
        lr = p["literacy_rate"]
        self.literacy += (1 - self.literacy) * lr
        self.enrollment += (0.99 - self.enrollment) * p["enrollment_rate"]
        # Motorisation (Gompertz with partial adjustment).
        g_ = p["gompertz"]
        vstar = g_["gamma"] * np.exp(g_["alpha"] * np.exp(g_["beta"] * self.y_nat / 1000.0))
        self.vehicles_per_1000 += g_["adjust"] * (vstar - self.vehicles_per_1000)
        self.urban_rural_ratio = piecewise(year, p["urban_rural_ratio"])
        self.history["y_nat"].append(self.y_nat)
        self.history.setdefault("y_state", []).append(self.y_state.copy())
        self.history["y_frontier"].append(self.y_frontier)
        self.history["vehicles"].append(self.vehicles_per_1000)

    def infra_budget(self, year: int, total_pop: float) -> float:
        share = piecewise(year, self.p["infra_share_gdp"])
        return share * self.y_nat * total_pop

    def infra_budgets(self, year: int, pop_by_region: np.ndarray) -> np.ndarray:
        """Infrastructure budget of each state (its own GDP)."""
        share = piecewise(year, self.p["infra_share_gdp"])
        return np.array([share * self.y_state[k] * pop_by_region[self.state == k].sum()
                         for k in range(len(self.y_state))])
