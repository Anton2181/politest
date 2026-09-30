"""Monte-Carlo ensembles: parameter uncertainty + stochastic shocks.

Each member re-draws the parameters listed in ``plsim.params.UNCERTAINTY``
(TFR transition shape and post-transition level, mortality catch-up speed,
convergence speed and shock volatility, emigration propensity and the
position of the migration hump, the Abrams-Strogatz exponent and key
shift propensities, network appraisal parameters) and uses its own random
seed for economic, mortality, fertility and town-growth shocks.

Results are condensed into a compact summary per member and reported as
quantiles (5, 25, 50, 75, 95 %).
"""
from __future__ import annotations

import copy
import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from .data.languages import COMMUNITIES, GROUPS, LANG_INDEX, LANGUAGES, NC, NL
from .language import CENSUS_CATEGORIES, REGIMES
from .model import Simulation
from .params import UNCERTAINTY, get_path, set_path

QUANTILES = [5, 25, 50, 75, 95]
KM_KEYS = ["rail_nar", "rail_sec", "rail_main", "rail_main_el", "rail_hsr",
           "road_dirt", "road_gravel", "road_paved", "road_express", "road_motorway"]


def draw_params(base: dict, rng: np.random.Generator) -> dict:
    p = copy.deepcopy(base)
    for path, (dist, a, b) in UNCERTAINTY.items():
        try:
            get_path(p, path)
        except (KeyError, IndexError, TypeError):
            continue
        if dist == "uniform":
            v = float(rng.uniform(a, b))
        elif dist == "normal":
            v = float(rng.normal(a, b))
        else:
            raise ValueError(dist)
        set_path(p, path, v)
    return p


def summarise(res) -> dict:
    A = res.arrays()
    gl = np.array([LANG_INDEX[l] for _, l in GROUPS])
    gc = np.array([[c.code for c in COMMUNITIES].index(c) for c, _ in GROUPS])
    pop = A["pop"]                                     # (T,R,2,G)
    bil = A["bil"]
    T = pop.shape[0]
    pop_lang = np.zeros((T, NL))
    bil_lang = np.zeros((T, NL))
    pop_comm = np.zeros((T, NC))
    for g in range(len(GROUPS)):
        pop_lang[:, gl[g]] += pop[:, :, :, g].sum(axis=(1, 2))
        bil_lang[:, gl[g]] += bil[:, :, :, g].sum(axis=(1, 2))
        pop_comm[:, gc[g]] += pop[:, :, :, g].sum(axis=(1, 2))
    w = pop.sum(axis=(2, 3))                           # (T,R)
    tot = w.sum(axis=1)
    lt_mask = np.array([c.startswith("LT") for c in res.region_codes])
    region_lang = np.zeros((T, len(res.region_codes), NL))
    for g in range(len(GROUPS)):
        region_lang[:, :, gl[g]] += pop[:, :, :, g].sum(axis=2)
    snap_years = sorted(y for (_r, y) in res.census.keys())
    snap_years = sorted(set(snap_years))
    census = np.zeros((len(snap_years), len(REGIMES), len(CENSUS_CATEGORIES)))
    for i, y in enumerate(snap_years):
        for j, rg in enumerate(REGIMES):
            census[i, j] = res.census[(rg, y)].sum(axis=0)
    return {
        "years": np.array(res.years),
        "region_codes": np.array(res.region_codes),
        "pop_total": tot,
        "pop_pl": w[:, ~lt_mask].sum(axis=1),
        "pop_lt": w[:, lt_mask].sum(axis=1),
        "pop_region": w,
        "urban_share": pop[:, :, 1].sum(axis=(1, 2)) / tot,
        "pop_lang": pop_lang,
        "bil_lang": bil_lang,
        "pop_comm": pop_comm,
        "region_lang": region_lang,
        "tfr": (A["tfr"] * w).sum(axis=1) / tot,
        "e0": (A["e0"] * w[:, :, None]).sum(axis=1) / tot[:, None],
        "births": A["births"].sum(axis=1),
        "deaths": A["deaths"].sum(axis=1),
        "emig": A["emig"].sum(axis=(1, 2)),
        "immig": A["immig"].sum(axis=(1, 2)),
        "internal": A["internal"].sum(axis=(1, 2)),
        "y_nat": np.array([e["y_nat"] for e in res.econ]),
        "y_frontier": np.array([e["y_frontier"] for e in res.econ]),
        "vehicles": np.array([e["vehicles_per_1000"] for e in res.econ]),
        "km": np.array([[k[x] for x in KM_KEYS] for k in res.km]),
        "census_years": np.array(snap_years),
        "census": census,
    }


def _run_member(args):
    params, seed = args
    p = copy.deepcopy(params)
    p["seed"] = int(seed)
    sim = Simulation(p)
    res = sim.run()
    return summarise(res)


def run_ensemble(base: dict, n: int = 24, seed: int = 7, workers: int | None = None,
                 vary_params: bool = True) -> dict:
    rng = np.random.default_rng(seed)
    members = []
    for i in range(n):
        p = draw_params(base, rng) if vary_params else copy.deepcopy(base)
        members.append((p, int(rng.integers(1, 2**31 - 1))))
    workers = workers or max(1, min(os.cpu_count() or 1, n))
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            outs = list(ex.map(_run_member, members))
    else:
        outs = [_run_member(m) for m in members]
    return stack(outs)


def stack(outs: list[dict]) -> dict:
    keys = [k for k in outs[0] if k not in ("years", "region_codes", "census_years")]
    st = {k: np.stack([o[k] for o in outs]) for k in keys}
    st["years"] = outs[0]["years"]
    st["region_codes"] = outs[0]["region_codes"]
    st["census_years"] = outs[0]["census_years"]
    return st


def quantiles(ens: dict, key: str) -> np.ndarray:
    return np.percentile(ens[key], QUANTILES, axis=0)


def save(ens: dict, path: str) -> None:
    np.savez_compressed(path, **ens)


def load(path: str) -> dict:
    z = np.load(path, allow_pickle=False)
    return {k: z[k] for k in z.files}


LANG_CODES = [l.code for l in LANGUAGES]
