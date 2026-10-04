"""Fit the county Voronoi weights to the census areas of the powiaty.

Reads plsim/data/county_areas_1931.csv and writes plsim/data/county_weights.json:
one additive weight per county (km), so that the cells of the model grid that
``data.subregions.assign`` gives each county add up to its census area. Targets
are relative: each voivodeship's cells are shared in proportion to the areas of
its counties (towns with county rights print no area and are small). Powiaty
merged in 1932 are printed with one area, which their members share as the
unweighted diagram does. With additive weights (distance less weight) every
county keeps its seat and is star-shaped around it (``data.subregions``). Run
from the repository root:  python tools/build_county_weights.py
"""
from __future__ import annotations

import csv
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plsim.data import subregions  # noqa: E402
from plsim.data.geography import build_grid  # noqa: E402
from plsim.data.regions import select_regions  # noqa: E402

HERE = os.path.join(os.path.dirname(__file__), "..", "plsim", "data")


def targets() -> dict:
    out = {}
    with open(os.path.join(HERE, "county_areas_1931.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(l for l in fh if not l.startswith("#")):
            out[tuple(r["county"].split("+"))] = float(r["area_km2"])
    return out


def fit(n_iter: int = 700):
    codes = [r.code for r in select_regions(True)]
    g = build_grid(codes)
    tg = targets()
    weights, report = {}, {}
    for i, par in enumerate(codes):
        cells = np.where(g.region == i)[0]
        kids = subregions.children(par, "county") if len(subregions.county_seats(par)) > 1 else []
        units = [u for u in tg if u[0].split(".")[0] == par]
        if not len(cells) or not units:
            continue
        km2 = g.cell_km2[cells]
        total = km2.sum()
        tsum = sum(tg[u] for u in units)
        goal = {u: tg[u] / tsum * total for u in units}
        # a 1932 group is printed with one area: its members split it as the unweighted diagram does
        base = subregions.assign(par, g.lat[cells], g.lon[cells], kids, weights={})
        for u in [u for u in units if len(u) > 1]:
            a = {m: km2[base == m].sum() for m in u}
            for m in u:
                goal[(m,)] = goal[u] * a[m] / max(sum(a.values()), 1.0)
            del goal[u]
        units = list(goal)
        w = {k: 0.0 for k in kids}
        step = 0.5 * np.sqrt(total / len(units))     # km of weight per unit of relative error
        for it in range(n_iter):
            child = subregions.assign(par, g.lat[cells], g.lon[cells], kids, weights=w)
            for u in units:
                a = km2[np.isin(child, u)].sum()
                d = float(np.clip(1.0 - a / goal[u], -1.0, 1.0)) * step * (0.99 ** it + 0.02)
                for m in u:
                    if m in w:
                        w[m] += d
        child = subregions.assign(par, g.lat[cells], g.lon[cells], kids, weights=w)
        err = {"+".join(u): round(km2[np.isin(child, u)].sum() / goal[u] - 1, 3) for u in units}
        report[par] = (max(abs(v) for v in err.values()), err)
        weights.update({k: round(v, 1) for k, v in w.items()})
    return weights, report


if __name__ == "__main__":
    weights, report = fit()
    with open(os.path.join(HERE, "county_weights.json"), "w", encoding="utf-8") as fh:
        json.dump({"source": "tools/build_county_weights.py from county_areas_1931.csv", "weights": weights}, fh,
                  indent=1, sort_keys=True, ensure_ascii=False)
    for par, (worst, err) in report.items():
        bad = {k: v for k, v in err.items() if abs(v) > 0.05}
        print(f"{par}: worst {worst:+.1%}  {bad if bad else ''}")
