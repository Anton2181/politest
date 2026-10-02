"""History matching of the language-shift module on documented cases.

Why analogues
-------------
The model starts in December 1931 and cannot be run backwards, and the two
Polish comparisons that come to mind cannot be used directly:

* **1921 -> 1931.** The 1921 census asked nationality, the 1931 census
  mother tongue and religion. The difference between them (e.g. 1.06 M
  Belarusians in 1921 against 0.99 M Belarusian speakers plus 0.71 M
  "tutejszy" in 1931; 3.9 M Ukrainians against 4.4 M Ukrainian and
  "Ruthenian" speakers) measures the change of question and of the
  enumerators' practice, not ten years of language shift.
* **1897 -> 1931.** The imperial "native language" of 1897 and the Polish
  mother tongue of 1931 are separated by the 1915 evacuation (bieżeństwo:
  well over a million people from the Grodno, Vilna and Minsk governorates,
  many of whom never returned), the wars of 1918-21, the departure of
  Russian officials and garrisons, emigration and, again, a different
  question. ``census_view(..., "imperial_1897")`` shows the 1931 start
  through the 1897 lens as a check of the observation model, not of the
  dynamics.

So the shift rates are matched to cases where the same kind of minority
language under the same kind of state language was counted in the same way
at both ends, with little else changing.

Cases (targets)
---------------
* **Masuria 1890 -> 1910** (Prussian censuses; Polish/Masurian speakers by
  district): Johannisburg 78.8 -> 68.0 %, Lyck 66.6 -> 51 %, Neidenburg
  75.6 -> 66.6 %, Oletzko 47.7 -> 29.6 %. A same-faith vernacular without
  its own schools under a modern state language: the analogue of the
  Catholic Belarusian speakers (sigma0 ``RC:be``). The faster loss where the
  share was smaller is the Abrams-Strogatz frequency effect.
* **Carinthian Slovenes 1880 -> 1910** (Austrian "Umgangssprache"):
  91,927 = 26.4 % of 348,730 in 1880; 74,210-82,212 (18.7-20.7 %, sources
  differ) of 396,200 in 1910, a share ratio of 0.71-0.79. A standardised,
  same-faith national language with partly own-language schooling
  (utraquist schools): the analogue of ``RC:lt``.
* **Wales 1921 -> 1951** (census, ability to speak Welsh, aged 3+): 37.1 %
  -> 28.9 % (ratio 0.78; home language falls faster than ability, so the
  target is set a little lower), monolingual Welsh 6.3 % -> 1.7 % of the
  population, i.e. 17 % -> 6 % of Welsh speakers.
* **Prussian Poles (province of Posen) 1871 -> 1910**: the Polish share
  rose slightly despite Germanisation; with German out-migration removed,
  language shift of Catholic Poles under a Protestant German state was close
  to nil. A different-faith national minority with strong institutions:
  the analogue of ``GC:uk`` / ``OR:uk``.
* **Second generation in a diaspora** (Alba, Logan, Lutz & Stults 2002;
  Portes & Rumbaut 2001): 40 % (Indian) to 76 % (Filipino) of children of
  immigrants spoke only English at home in 1990, 60-70 % of the third
  generation of Hispanic origin. Target: 40-80 % of the children born to an
  urban immigrant group (3 % of the town) over 25 years are raised in the
  majority language.

Method
------
History matching (Craig et al. 1997; Vernon, Goldstein & Bower 2010;
Andrianakis et al. 2015). Each case is run with the model's own
``LanguageModel`` (vertical transmission, acquisition, re-identification)
on a stylised one-region population with a stable age structure, the case's
setting (status, own schooling, institutions, pressure, modernisation,
clustering) and the same demography for minority and majority, so that
only shift moves the shares. Parameters are drawn by Latin hypercube; a
draw is ruled out when any target's implausibility

    I = |simulated - observed| / sqrt(sd_obs^2 + sd_discrepancy^2)

exceeds 3 (Pukelsheim's three-sigma rule). The discrepancy term covers the
cases' migration, the census definitions and the stylised settings. The
not-ruled-out-yet (NROY) set is written out. A second wave samples the box
around the first wave's NROY draws. The defaults are moved to the NROY
median of each parameter the cases constrain (checked to be NROY itself);
parameters they do not constrain keep their values. The ensemble draws its
language parameters jointly from the NROY set.

Limits. The cases constrain classes of minorities, not each group; the
settings of each case (status, schooling, clustering) are judgements; and
the model's frequency effect is weaker than the Masurian districts show
(the share fell fastest where it was smallest, which the Abrams-Strogatz
term reproduces only in part, perhaps because German settlers and the
Masurians' own departure for the Ruhr concentrated there too).
"""
from __future__ import annotations

import copy
import csv
import os
from dataclasses import dataclass, field

import numpy as np

from .data.languages import GROUP_INDEX, NG
from .demography import FertilitySchedule, MortalityModel
from .language import LanguageModel
from .params import DEFAULTS

HERE = os.path.dirname(os.path.abspath(__file__))
NROY_PATH = os.path.join(HERE, "data", "nroy_language.csv")


@dataclass
class Target:
    kind: str           # share | ratio | mono | births_shifted
    obs: float
    sd_obs: float
    sd_disc: float


@dataclass
class Case:
    key: str
    label: str
    group: str          # model group standing for the minority (carrier)
    years: int
    x0: float           # initial minority share
    mono0: float        # initial monolingual share of minority speakers aged 3+
    urban: float
    M: tuple            # modernisation index (rural, urban), as plsim.economy
    enrol: float
    status: float       # status of the minority language (state language = 1)
    own: float          # own-language schooling
    inst: float         # institutional maintenance (church, press, associations)
    pressure: float
    conc: float         # clustering: local own share = conc x share
    tfr: float
    e0: float
    targets: list = field(default_factory=list)
    immigrant: bool = False
    source: str = ""


def _masuria(key, name, x0, x1):
    return Case(key, f"Masuria, {name} district 1890-1910", "RC:be", 20, x0, 0.30, 0.10, (0.45, 0.75), 0.95,
                0.10, 0.0, 0.10, 1.0, 1.15, 4.8, 42.0,
                [Target("share", x1, 0.03, 0.03)],
                source="Prussian censuses 1890, 1910 (district language statistics)")


CASES = [
    _masuria("mas_joh", "Johannisburg", 0.788, 0.680),
    _masuria("mas_lyc", "Lyck", 0.666, 0.510),
    _masuria("mas_nei", "Neidenburg", 0.756, 0.666),
    _masuria("mas_ole", "Oletzko", 0.477, 0.296),
    Case("carinthia", "Carinthian Slovenes 1880-1910", "RC:lt", 30, 0.264, 0.45, 0.15, (0.40, 0.70), 0.80,
         0.25, 0.30, 0.15, 1.0, 2.5, 4.3, 40.0,
         [Target("ratio", 0.75, 0.04, 0.05)],
         source="Austrian censuses 1880-1910 (Umgangssprache)"),
    Case("wales", "Wales 1921-1951", "RC:cs", 30, 0.371, 0.17, 0.55, (0.57, 0.85), 1.0,
         0.30, 0.10, 0.30, 1.0, 1.6, 2.4, 58.0,
         [Target("ratio", 0.74, 0.04, 0.05), Target("mono", 0.06, 0.015, 0.02)],
         source="Censuses of England and Wales 1921, 1951"),
    Case("posen", "Poles in the province of Posen 1871-1910", "GC:uk", 39, 0.60, 0.80, 0.20, (0.35, 0.65), 0.85,
         0.35, 0.10, 0.40, 1.2, 1.2, 5.0, 38.0,
         [Target("ratio", 0.99, 0.015, 0.015)],
         source="Prussian censuses (Polish share 1871-1910, net of migration)"),
    Case("diaspora", "Immigrants in a modern city (second generation)", "OR:uk", 25, 0.03, 0.70, 1.0, (0.98, 0.98),
         1.0, 0.20, 0.05, 0.10, 1.0, 2.0, 2.0, 75.0,
         [Target("births_shifted", 0.60, 0.10, 0.05)], immigrant=True,
         source="Alba et al. 2002; Portes & Rumbaut 2001"),
]

# Calibrated parameters: name -> (where in the language parameters, low, high)
PARAMS = {
    "sigma_vern": ("sigma0.RC:be", 0.10, 1.20),
    "sigma_nat": ("sigma0.RC:lt", 0.02, 0.50),
    "sigma_nat_distinct": ("sigma0.GC:uk", 0.0, 0.25),
    "a": ("a", 1.0, 1.6),
    "m_mono": ("m_mono", 0.05, 0.40),
    "h0": ("h0", 0.0, 0.012),
    "completeness_share": ("completeness_share", 0.10, 0.50),
    "sigma_diaspora": ("sigma_diaspora", 0.0, 0.80),
    "acq_adult": ("acq_adult", 0.004, 0.030),
    "acq_school": ("acq_school", 0.10, 0.40),
}
# Groups whose sigma0 moves with each calibrated class (by the same factor).
CLASS_GROUPS = {
    "sigma_vern": ["RC:be", "RC:pls", "RC:csb"],
    "sigma_nat": ["RC:lt", "RC:uk", "RC:de", "RC:cs", "RC:lv"],
    "sigma_nat_distinct": ["GC:uk", "OR:uk", "GC:rue", "OR:rue", "PR:de", "PR:lt", "PR:lv", "PR:cs"],
}
# carrier groups of the cases take the class value directly
CARRIER_CLASS = {"RC:be": "sigma_vern", "RC:lt": "sigma_nat", "RC:cs": "sigma_nat",
                 "GC:uk": "sigma_nat_distinct", "OR:uk": "sigma_nat_distinct"}


def default_theta(lang: dict | None = None) -> dict:
    lang = lang or DEFAULTS["language"]
    out = {}
    for k, (path, _lo, _hi) in PARAMS.items():
        if path.startswith("sigma0."):
            out[k] = float(lang["sigma0"].get(path[7:], lang["sigma0"]["default"]))
        else:
            out[k] = float(lang.get(path, 0.0))
    return out


def apply_theta(lang: dict, theta: dict, scale_classes: bool = True) -> dict:
    """Language parameters with theta applied. With ``scale_classes`` every
    group of a calibrated class moves by the factor of its anchor group."""
    out = copy.deepcopy(lang)
    s0 = out["sigma0"]
    for k, (path, _lo, _hi) in PARAMS.items():
        if k not in theta:
            continue
        v = float(theta[k])
        if path.startswith("sigma0."):
            anchor = path[7:]
            old = lang["sigma0"].get(anchor, lang["sigma0"]["default"])
            groups = CLASS_GROUPS[k] if scale_classes else [anchor]
            for g in groups:
                g_old = lang["sigma0"].get(g, lang["sigma0"]["default"])
                s0[g] = v if g == anchor else (g_old * v / old if old > 0 else v)
        else:
            out[path] = v
    return out


class _Region:
    def __init__(self, code):
        self.code = code


_MORT: dict = {}


def _mort() -> MortalityModel:
    if "m" not in _MORT:
        _MORT["m"] = MortalityModel()
    return _MORT["m"]


def simulate(theta: dict, cases: list[Case] = CASES, lang: dict | None = None) -> dict:
    """Run every case with the language parameters ``theta``; return
    {(case key, target index): simulated value}."""
    lang = lang or DEFAULTS["language"]
    lp = apply_theta(lang, theta, scale_classes=False)
    R = len(cases)
    codes = [f"CAL{i}" for i in range(R)]
    lp["status_regions"] = {}
    lp["own_schooling_regions"] = {}
    lp["pressure"] = {"default": 1.0}
    lp["institutional"] = dict(lp["institutional"])
    for code, c in zip(codes, cases):
        comm, lng = c.group.split(":")
        lp["sigma0"][c.group] = float(theta.get(CARRIER_CLASS[c.group], lp["sigma0"].get(c.group, 0.2)))
        lp["status_regions"][code] = {lng: c.status}
        lp["own_schooling_regions"][code] = {c.group: c.own}
        lp["pressure"][code] = c.pressure
        lp["institutional"][c.group] = c.inst
    lm = LanguageModel(lp, [_Region(c) for c in codes], ["pl"] * R)
    gi = np.array([GROUP_INDEX[tuple(c.group.split(":"))] for c in cases])
    di = np.array([GROUP_INDEX[(c.group.split(":")[0], "pl")] for c in cases])
    for r, c in enumerate(cases):
        lm.conc[r, gi[r]] = c.conc

    mort = _mort()
    e0 = np.array([c.e0 for c in cases])
    s_f = mort.survival(e0 + 1.5, 1)                     # (R,101)
    s_m = mort.survival(e0 - 1.5, 0)
    sb_f = mort.birth_survival(e0 + 1.5, 1)
    sb_m = mort.birth_survival(e0 - 1.5, 0)
    # stable age structure, 1 % growth
    lx = np.cumprod(np.concatenate([np.ones((R, 1)), 0.5 * (s_f + s_m)[:, :-1]], axis=1), axis=1)
    age_w = lx * np.exp(-0.01 * np.arange(101))[None, :]
    age_w /= age_w.sum(axis=1, keepdims=True)
    P = np.zeros((R, 2, NG, 2, 2, 101))
    for r, c in enumerate(cases):
        u = np.array([1 - c.urban, c.urban]) * 1e5
        if c.immigrant:
            mig = np.zeros(101)
            mig[20:41] = 1.0
            mig /= mig.sum()
            minority = mig
        else:
            minority = age_w[r]
        # bilingual from age 7 so that the 3+ monolingual share is mono0
        a3 = minority[3:].sum()
        a7 = minority[7:].sum()
        bil7 = np.clip((1 - c.mono0) * a3 / max(a7, 1e-12), 0, 1)
        bil = np.where(np.arange(101) >= 7, bil7, 0.0)
        for uu in (0, 1):
            for s in (0, 1):
                P[r, uu, gi[r], 1, s] = 0.5 * u[uu] * c.x0 * minority * bil
                P[r, uu, gi[r], 0, s] = 0.5 * u[uu] * c.x0 * minority * (1 - bil)
                P[r, uu, di[r], 0, s] = 0.5 * u[uu] * (1 - c.x0) * age_w[r]
    x_start = P[np.arange(R), :, gi].sum(axis=(1, 2, 3, 4)) / P.sum(axis=(1, 2, 3, 4, 5))
    M = np.array([c.M for c in cases], dtype=float)
    enrol = np.array([c.enrol for c in cases])
    ma0 = np.zeros(R)
    fs = FertilitySchedule()
    asfr = fs.schedule(np.full(R, 28.0)) * np.array([c.tfr for c in cases])[:, None]      # (R,35)
    pm = 1.06 / 2.06
    out: dict = {}
    born = np.zeros(R)
    born_shift = np.zeros(R)
    for t in range(1, max(c.years for c in cases) + 1):
        women = P[:, :, :, :, 1, 15:50]
        births = (women * asfr[:, None, None, None, :]).sum(axis=4)          # (R,2,G,B)
        p_shift, dist, *_ = lm.transmission(1931, P, M, ma0)
        shifted = births * p_shift
        newborns = (births - shifted).sum(axis=3) + np.einsum("rugk,rug->ruk", dist, shifted.sum(axis=3))
        born += births[np.arange(R), :, gi].sum(axis=(1, 2))
        born_shift += shifted[np.arange(R), :, gi].sum(axis=(1, 2))
        surv = np.stack([s_m, s_f], axis=1)                                  # (R,2,101)
        Pn = np.zeros_like(P)
        Pn[..., 1:100] = P[..., 0:99] * surv[:, None, None, None, :, 0:99]
        Pn[..., 100] = P[..., 99] * surv[:, None, None, None, :, 99] + P[..., 100] * surv[:, None, None, None, :, 100]
        Pn[:, :, :, 0, 0, 0] = newborns * pm * sb_m[:, None, None]
        Pn[:, :, :, 0, 1, 0] = newborns * (1 - pm) * sb_f[:, None, None]
        P = Pn
        lm.horizontal(1931, P, enrol, M, ma0)
        for r, c in enumerate(cases):
            if t != c.years:
                continue
            tot = P[r].sum()
            share = P[r, :, gi[r]].sum() / tot
            for j, tg in enumerate(c.targets):
                if tg.kind == "share":
                    v = share
                elif tg.kind == "ratio":
                    v = share / x_start[r]
                elif tg.kind == "mono":
                    sp = P[r, :, gi[r], :, :, 3:]
                    v = sp[:, 0].sum() / max(sp.sum(), 1e-12)
                elif tg.kind == "births_shifted":
                    v = born_shift[r] / max(born[r], 1e-12)
                else:
                    raise ValueError(tg.kind)
                out[(c.key, j)] = float(v)
    return out


def implausibility(sim: dict, cases: list[Case] = CASES) -> dict:
    out = {}
    for c in cases:
        for j, tg in enumerate(c.targets):
            out[(c.key, j)] = abs(sim[(c.key, j)] - tg.obs) / np.sqrt(tg.sd_obs ** 2 + tg.sd_disc ** 2)
    return out


def lhs(n: int, seed: int = 1931, bounds: dict | None = None) -> list[dict]:
    rng = np.random.default_rng(seed)
    names = list(PARAMS)
    bounds = bounds or {k: PARAMS[k][1:] for k in names}
    k = len(names)
    u = (np.argsort(rng.random((k, n)), axis=1).T + rng.random((n, k))) / n
    return [{names[j]: bounds[names[j]][0] + u[i, j] * (bounds[names[j]][1] - bounds[names[j]][0])
             for j in range(k)} for i in range(n)]


def _eval(theta):
    sim = simulate(theta)
    imp = implausibility(sim)
    return theta, sim, imp


def _sig2(x: float) -> float:
    return float(f"{x:.2g}")


def history_match(n: int = 2000, seed: int = 1931, workers: int = 1, cutoff: float = 3.0, waves: int = 2) -> dict:
    """Waves of Latin-hypercube draws; each wave after the first samples the
    box around the draws not ruled out by the previous ones."""
    names = list(PARAMS)
    keys = [(c.key, j) for c in CASES for j in range(len(c.targets))]
    span = np.array([PARAMS[k][2] - PARAMS[k][1] for k in names])
    bounds = None
    rows: list = []
    for w in range(waves):
        thetas = lhs(n, seed + w, bounds)
        if workers > 1:
            from concurrent.futures import ProcessPoolExecutor
            with ProcessPoolExecutor(max_workers=workers) as ex:
                rows += list(ex.map(_eval, thetas, chunksize=16))
        else:
            rows += [_eval(t) for t in thetas]
        X = np.array([[r[0][k] for k in names] for r in rows])
        I = np.array([[r[2][k] for k in keys] for r in rows])
        ok = I.max(axis=1) <= cutoff
        if not ok.any():
            break
        lo = np.maximum(X[ok].min(axis=0) - 0.05 * span, [PARAMS[k][1] for k in names])
        hi = np.minimum(X[ok].max(axis=0) + 0.05 * span, [PARAMS[k][2] for k in names])
        bounds = {k: (lo[j], hi[j]) for j, k in enumerate(names)}
    X = np.array([[r[0][k] for k in names] for r in rows])
    I = np.array([[r[2][k] for k in keys] for r in rows])
    imax = I.max(axis=1)
    nroy = imax <= cutoff
    d0 = default_theta()
    dsim = simulate(d0)
    dimp = implausibility(dsim)
    hm = {"names": names, "keys": keys, "X": X, "I": I, "imax": imax, "nroy": nroy,
          "default": d0, "default_sim": dsim, "default_imp": dimp, "sims": [r[1] for r in rows]}
    hm.update(adopt(hm, cutoff))
    return hm


def adopt(hm: dict, cutoff: float = 3.0) -> dict:
    """The adopted parameters: the NROY median of each parameter the cases
    constrain; parameters they do not constrain (NROY 5-95 % range over 70 %
    of the prior range, with the default inside it) keep their defaults. If
    that vector were ruled out, the best-fitting NROY draw is taken instead."""
    names, X, I, nroy, d0 = hm["names"], hm["X"], hm["I"], hm["nroy"], hm["default"]
    span = np.array([PARAMS[k][2] - PARAMS[k][1] for k in names])
    pool = X[nroy] if nroy.any() else X
    q = np.percentile(pool, [5, 50, 95], axis=0)
    unconstrained = {k for j, k in enumerate(names)
                     if (q[2, j] - q[0, j]) > 0.7 * span[j] and q[0, j] <= d0[k] <= q[2, j]}
    adopted = {k: (d0[k] if k in unconstrained else _sig2(q[1, j])) for j, k in enumerate(names)}
    asim = simulate(adopted)
    aimp = implausibility(asim)
    rule = "median"
    if max(aimp.values()) > cutoff:
        score = np.where(nroy, (I ** 2).sum(axis=1), np.inf)
        best = int(np.argmin(score)) if nroy.any() else int(np.argmin(hm["imax"]))
        adopted = {k: _sig2(X[best, j]) for j, k in enumerate(names)}
        unconstrained, rule = set(), "best fit"
        asim = simulate(adopted)
        aimp = implausibility(asim)
    return {"adopted": adopted, "adopted_sim": asim, "adopted_imp": aimp, "unconstrained": sorted(unconstrained),
            "rule": rule}


def write_outputs(hm: dict, outdir: str) -> None:
    os.makedirs(outdir, exist_ok=True)
    names, keys = hm["names"], hm["keys"]
    with open(os.path.join(outdir, "samples.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(names + [f"I_{k}_{j}" for k, j in keys] + ["I_max", "nroy"])
        for x, i, m, n in zip(hm["X"], hm["I"], hm["imax"], hm["nroy"]):
            w.writerow([f"{v:.5g}" for v in x] + [f"{v:.3f}" for v in i] + [f"{m:.3f}", int(n)])
    write_nroy(hm, os.path.join(outdir, "nroy.csv"))
    with open(os.path.join(outdir, "parameters.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["parameter", "previous", "nroy_p5", "nroy_p50", "nroy_p95", "adopted", "constrained"])
        X = hm["X"][hm["nroy"]] if hm["nroy"].any() else hm["X"]
        q = np.percentile(X, [5, 50, 95], axis=0)
        for j, k in enumerate(names):
            w.writerow([k, hm["default"][k], f"{q[0, j]:.4g}", f"{q[1, j]:.4g}", f"{q[2, j]:.4g}",
                        hm["adopted"][k], int(k not in hm["unconstrained"])])
    with open(os.path.join(outdir, "targets.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["case", "label", "measure", "observed", "sd", "previous", "I_previous", "adopted", "I_adopted",
                    "source"])
        for c in CASES:
            for j, tg in enumerate(c.targets):
                k = (c.key, j)
                w.writerow([c.key, c.label, tg.kind, tg.obs, f"{np.hypot(tg.sd_obs, tg.sd_disc):.3f}",
                            f"{hm['default_sim'][k]:.3f}", f"{hm['default_imp'][k]:.2f}",
                            f"{hm['adopted_sim'][k]:.3f}", f"{hm['adopted_imp'][k]:.2f}", c.source])


def write_nroy(hm: dict, path: str = NROY_PATH) -> None:
    names = hm["names"]
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(names)
        for x, n in zip(hm["X"], hm["nroy"]):
            if n:
                w.writerow([f"{v:.5g}" for v in x])


def load_nroy(path: str = NROY_PATH) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, newline="") as fh:
        r = csv.DictReader(fh)
        return [{k: float(v) for k, v in row.items()} for row in r]


def summary(hm: dict) -> str:
    names = hm["names"]
    X, nroy = hm["X"], hm["nroy"]
    lines = [f"History matching: {len(X)} draws in two waves, {int(nroy.sum())} not ruled out "
             f"(every target within 3 standard deviations)", ""]
    lines.append(f"{'parameter':22} {'previous':>9} {'NROY 5%':>9} {'median':>9} {'95%':>9} {'adopted':>9}")
    for j, k in enumerate(names):
        col = X[nroy, j] if nroy.any() else X[:, j]
        q = np.percentile(col, [5, 50, 95])
        flag = "  (not constrained; kept)" if k in hm["unconstrained"] else ""
        lines.append(f"{k:22} {hm['default'][k]:9.4g} {q[0]:9.4g} {q[1]:9.4g} {q[2]:9.4g} "
                     f"{hm['adopted'][k]:9.4g}{flag}")
    lines += ["", f"adopted: {hm.get('rule', 'median')} of the NROY draws; I = implausibility", "",
              f"{'target':30} {'observed':>9} {'previous':>9} {'I':>6} {'adopted':>9} {'I':>6}"]
    for c in CASES:
        for j, tg in enumerate(c.targets):
            k = (c.key, j)
            lines.append(f"{c.key + ' ' + tg.kind:30} {tg.obs:9.3f} {hm['default_sim'][k]:9.3f} "
                         f"{hm['default_imp'][k]:6.2f} {hm['adopted_sim'][k]:9.3f} {hm['adopted_imp'][k]:6.2f}")
    return "\n".join(lines)


def figure(hm: dict, path: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    names = hm["names"]
    X, nroy = hm["X"], hm["nroy"]
    fig, axes = plt.subplots(2, (len(names) + 1) // 2, figsize=(14, 5.6))
    for ax, j in zip(axes.flat, range(len(names))):
        lo, hi = PARAMS[names[j]][1:]
        bins = np.linspace(lo, hi, 21)
        ax.hist(X[:, j], bins=bins, color="#ccc", label="all draws")
        ax.hist(X[nroy, j], bins=bins, color="#2b6cb0", label="not ruled out")
        ax.axvline(hm["default"][names[j]], color="#c53030", lw=1.5, label="previous default")
        ax.axvline(hm["adopted"][names[j]], color="#2f855a", lw=1.5, ls="--", label="adopted")
        ax.set_title(names[j], fontsize=9)
        ax.tick_params(labelsize=7)
        ax.set_yticks([])
    axes.flat[0].legend(fontsize=7, frameon=False)
    for ax in list(axes.flat)[len(names):]:
        ax.axis("off")
    fig.suptitle("History matching of the language-shift parameters on documented cases", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
