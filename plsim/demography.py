"""Demographic components: mortality, fertility and initial age structures.

Mortality
---------
Age pattern: a three-component (Siler 1979-type) hazard

    mu(x) = A exp(-B x) + C + D exp(G x)

(infant/child, background, senescent).  A single "health progress" index
``k`` lowers the components at different speeds (child mortality fastest,
senescent slowest), which reproduces the rectangularisation seen in
twentieth-century European life tables: at e0(f) = 51.5 the model gives
IMR = 120-140 per 1000 and e65 = 12.8 (Poland 1931-32: e0 m 48.2 / f 51.4),
at e0(f) = 74 it gives IMR ~ 16 and e65 ~ 17, at 85 IMR ~ 1 and e65 ~ 23.
Any target e0 is converted into a full life table by inverting e0(k).

Level: a best-practice-gap model.  Following Oeppen & Vaupel (2002) the
record female life expectancy rises ~0.243 years per calendar year; each
population closes its gap to a Preston-curve-style income-dependent target
gap at a rate that jumps after 1945 (sulphonamides, penicillin,
streptomycin, DDT, mass vaccination - the "mortality revolution" that lifted
southern and eastern Europe from e0 ~ 50 to ~ 65-70 within 15 years).
Compare Torri & Vaupel (2012) and Raftery et al. (2013, Demography), whose
Bayesian double-logistic gain model yields similar gain-vs-level profiles.

Fertility
---------
TFR follows the three-phase model of Alkema et al. (2011, Demography) used by
the UN (bayesTFR): a pre-transition plateau, a Phase-II decline whose 5-year
decrement is a double-logistic function of the current level, and a Phase-III
AR(1) recovery/fluctuation around a long-run mean.  Here the Phase-II pace is
modulated by a modernisation index (literacy, urbanisation, income), echoing
the Princeton European Fertility Project finding that declines diffused
along cultural-linguistic lines (Coale & Watkins 1986; Lesthaeghe 1977).
Age schedules: normalised gamma densities (Hoem et al. 1981) whose mean
tracks TFR (high-parity regimes have old schedules) and later postponement.
"""
from __future__ import annotations

import numpy as np

AGES = np.arange(101)
NA = 101
FERT_AGES = np.arange(15, 50)

# ---------------------------------------------------------------------------------
# Mortality
# ---------------------------------------------------------------------------------
_SILER = {
    # sex: A0, B, C0, D0, G
    0: (0.26, 1.3, 0.0056, 8.0e-5, 0.095),   # male
    1: (0.22, 1.3, 0.0048, 5.5e-5, 0.095),   # female
}
_SPEED = (1.05, 0.95, 0.25)  # d ln A / dk, d ln C / dk, d ln D / dk


def _life_table(k: float, sex: int, sub: int = 8):
    A0, B, C0, D0, G = _SILER[sex]
    A = A0 * np.exp(-_SPEED[0] * k)
    C = C0 * np.exp(-_SPEED[1] * k)
    D = D0 * np.exp(-_SPEED[2] * k)
    xs = AGES[:, None] + (np.arange(sub)[None, :] + 0.5) / sub
    mu = A * np.exp(-B * xs) + C + D * np.exp(G * xs)
    q = 1 - np.exp(-mu.mean(axis=1))
    q[-1] = 1.0
    l = np.ones(NA + 1)
    for x in range(NA):
        l[x + 1] = l[x] * (1 - q[x])
    L = (l[:-1] + l[1:]) / 2
    mu_open = A * np.exp(-B * 100.5) + C + D * np.exp(G * 100.5)
    L[-1] = l[-2] / mu_open
    return q, l, L


class MortalityModel:
    """Precomputed life tables on an e0 grid; returns survival ratios."""

    def __init__(self, e0_min: float = 20.0, e0_max: float = 95.0, step: float = 0.05):
        ks = np.linspace(-2.5, 8.0, 800)
        self.grid = np.arange(e0_min, e0_max + 1e-9, step)
        self.surv = np.zeros((2, len(self.grid), NA))
        self.surv_birth = np.zeros((2, len(self.grid)))
        self.Lx = np.zeros((2, len(self.grid), NA))
        for sex in (0, 1):
            e0s = np.array([_life_table(k, sex)[2].sum() for k in ks])
            kgrid = np.interp(self.grid, e0s, ks)
            for j, k in enumerate(kgrid):
                _q, l, L = _life_table(k, sex)
                s = np.empty(NA)
                s[:-2] = L[1:-1] / L[:-2]
                # open interval 100+: s(99) uses the one-year L(100); the open
                # group survives at exp(-mu_100+)
                s_open = np.exp(-l[100] / L[100])
                s[-2] = l[100] * (1 + s_open) / 2 / L[99]
                s[-1] = s_open
                self.surv[sex, j] = s
                self.surv_birth[sex, j] = L[0]
                self.Lx[sex, j] = L
        self.step = step
        self.e0_min = e0_min

    def _idx(self, e0: np.ndarray):
        x = (np.clip(e0, self.grid[0], self.grid[-1]) - self.e0_min) / self.step
        i0 = np.floor(x).astype(int)
        i0 = np.clip(i0, 0, len(self.grid) - 2)
        w = x - i0
        return i0, w

    def survival(self, e0: np.ndarray, sex: int) -> np.ndarray:
        """Annual survival ratios s(x) for arrays of e0; returns e0.shape + (101,)."""
        i0, w = self._idx(np.asarray(e0, dtype=float))
        s = self.surv[sex]
        return s[i0] * (1 - w)[..., None] + s[i0 + 1] * w[..., None]

    def birth_survival(self, e0: np.ndarray, sex: int) -> np.ndarray:
        i0, w = self._idx(np.asarray(e0, dtype=float))
        s = self.surv_birth[sex]
        return s[i0] * (1 - w) + s[i0 + 1] * w

    def person_years(self, e0: np.ndarray, sex: int) -> np.ndarray:
        i0, w = self._idx(np.asarray(e0, dtype=float))
        L = self.Lx[sex]
        return L[i0] * (1 - w)[..., None] + L[i0 + 1] * w[..., None]


def frontier_e0_female(year: float, slope: float = 0.243, slope_post2000: float = 0.20) -> float:
    """Best-practice female life expectancy (Oeppen & Vaupel 2002 trend)."""
    base = 67.1 + slope * (min(year, 2000) - 1931)
    if year > 2000:
        base += slope_post2000 * (year - 2000)
    return base


def target_gap(y_rel: np.ndarray, gmin: float, gmax: float, power: float = 1.5) -> np.ndarray:
    """Income-dependent gap (years) to the best-practice frontier (Preston curve)."""
    y = np.clip(y_rel, 0.0, 1.0)
    return gmin + (gmax - gmin) * (1 - y) ** power


def catchup_rate(year: float, pre: float, post: float, start: float = 1945.0, end: float = 1951.0) -> float:
    if year <= start:
        return pre
    if year >= end:
        return post
    return pre + (post - pre) * (year - start) / (end - start)


def sex_gap(year: float, schedule: list[list[float]]) -> float:
    ys = [p[0] for p in schedule]
    vs = [p[1] for p in schedule]
    return float(np.interp(year, ys, vs))


# ---------------------------------------------------------------------------------
# Fertility
# ---------------------------------------------------------------------------------
LN9 = np.log(9.0)


def alkema_decrement(f: np.ndarray, U: np.ndarray, d: np.ndarray, D1: float, D3: float, D4: np.ndarray) -> np.ndarray:
    """Expected 5-year TFR decrement (Alkema et al. 2011, eq. 2)."""
    t1 = -d / (1 + np.exp(-(2 * LN9 / D1) * (f - U + 0.5 * D1)))
    t2 = d / (1 + np.exp(-(2 * LN9 / D3) * (f - D4 - 0.5 * D3)))
    return np.maximum(t1 + t2, 0.0)


class FertilitySchedule:
    """Gamma-shaped age-specific fertility schedules indexed by mean age."""

    def __init__(self, shape: float = 6.0, mac_min: float = 23.0, mac_max: float = 34.0, step: float = 0.05):
        self.macs = np.arange(mac_min, mac_max + 1e-9, step)
        self.step = step
        self.mac_min = mac_min
        x = FERT_AGES + 0.5 - 14.5
        tab = np.zeros((len(self.macs), len(FERT_AGES)))
        for j, m in enumerate(self.macs):
            theta = (m - 14.5) / shape
            dens = x ** (shape - 1) * np.exp(-x / theta)
            tab[j] = dens / dens.sum()
        self.tab = tab

    def schedule(self, mac: np.ndarray) -> np.ndarray:
        x = (np.clip(mac, self.macs[0], self.macs[-1]) - self.mac_min) / self.step
        i0 = np.clip(np.floor(x).astype(int), 0, len(self.macs) - 2)
        w = x - i0
        return self.tab[i0] * (1 - w)[..., None] + self.tab[i0 + 1] * w[..., None]


def mean_age_childbearing(tfr: np.ndarray, postponement: np.ndarray | float) -> np.ndarray:
    """High-parity regimes have late schedules; transition compresses them,
    post-transition postponement pushes them back up."""
    return np.clip(26.5 + 1.1 * (tfr - 2.0), 25.3, 30.5) + postponement


# ---------------------------------------------------------------------------------
# Initial age structure
# ---------------------------------------------------------------------------------
# Relative size of cohorts born during WW1 / the Polish-Soviet war (age in Dec 1931).
WW1_COHORT_FACTORS = {
    "RU": {16: 0.72, 15: 0.52, 14: 0.50, 13: 0.55, 12: 0.72, 11: 0.85},
    "AT": {16: 0.78, 15: 0.58, 14: 0.55, 13: 0.60, 12: 0.78, 11: 0.92},
    "DE": {16: 0.78, 15: 0.60, 14: 0.58, 13: 0.62, 12: 0.85, 11: 0.97},
}
WW1_MALE_FACTOR = 0.92  # males aged 32-55 in 1931 (military deaths 1914-1920)


def stable_age_distribution(tfr: float, e0f: float, e0m: float, mort: MortalityModel,
                            partition: str = "RU") -> np.ndarray:
    """Return (2, 101) age-sex shares for a stable population with the given
    vital rates, adjusted for the WW1 birth deficit and male war losses."""
    Lf = mort.person_years(np.array(e0f), 1)
    Lm = mort.person_years(np.array(e0m), 0)
    mac = float(mean_age_childbearing(np.array(tfr), 0.0))
    srb = 1.06
    pf = 1 / (1 + srb)
    nrr = tfr * pf * np.interp(mac, AGES, Lf)
    gen = mac
    r = np.log(max(nrr, 0.2)) / gen
    disc = np.exp(-r * (AGES + 0.5))
    fem = Lf * disc * pf
    mal = Lm * disc * (1 - pf)
    fac = WW1_COHORT_FACTORS.get(partition, WW1_COHORT_FACTORS["RU"])
    for age, f in fac.items():
        fem[age] *= f
        mal[age] *= f
    mal[32:56] *= WW1_MALE_FACTOR
    out = np.stack([mal, fem])
    return out / out.sum()
