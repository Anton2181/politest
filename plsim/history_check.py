"""The historical scenario against what happened (calibration targets).

``historical`` (scenarios/historical.yaml) replays the war, the border change
of 1945 and People's Poland. This module compares Poland within each year's
borders (the regions of state PL at 1 January of the year) with:

* population: the census of 14 February 1946 (23.93 M), the censuses of
  1950 (25.01 M), 1960 (29.80 M), 1970 (32.64 M), 1978 (35.06 M), 1988
  (37.88 M), 2002 (38.23 M), 2011 (38.51 M) and 2021 (38.04 M);
* the Recovered Territories (German land and Danzig): 8.86 M in 1939
  (incl. Danzig), 5.02 M in 1946, 5.94 M in 1950; Germans counted in
  1946: 2.29 M, with 0.42 M more awaiting "verification";
* urban share: 36.9 % (1950), 48.3 % (1960), 52.3 % (1970), 61.0 % (1988),
  61.8 % (2002), 60.2 % (2021);
* total fertility: 3.71 (1950), 2.98 (1960), 2.20 (1970), 2.28 (1980),
  2.04 (1990), 1.37 (2000), 1.38 (2010), 1.39 (2020);
* life expectancy (men, women): 58.6/64.2 (1952-53), 64.8/70.5 (1960-61),
  66.8/73.8 (1970-72), 66.2/75.2 (1990), 69.6/78.0 (2000), 72.1/80.6
  (2010), 74.1/81.8 (2019);
* national identity in the 2002 census (single answer; thousands):
  Silesian 173, German 153, Belarusian 49, Ukrainian 31, Lemko 6,
  Lithuanian 6, Kashubian 5, Jewish 1; and home language: German 205,
  Belarusian 40, Ukrainian 23, Kashubian 53, Lemko 6, Lithuanian 6;
* home language in the 2011 census (up to two answers; thousands; table 33
  of "Struktura narodowo-etniczna, językowa i wyznaniowa"): German 96.5,
  Belarusian 26.4, Ukrainian 24.5, Kashubian 108.1, Lemko 6.3,
  Lithuanian 5.3. The two censuses asked differently: German halves and
  Kashubian doubles between them, a measure of how loose these counts are.

Sources: GUS (Rocznik Demograficzny; the census reports of 1946-2021);
GUS life tables; the 2002 census report "Ludność według narodowości i
języka"; Kosiński (1960) for the Recovered Territories.
"""
from __future__ import annotations

import os

import numpy as np

from .data.languages import LANG_INDEX, NL, GROUPS
from .history import members_at
from .identity import ID_INDEX

POP = {1946: 23.93, 1950: 25.01, 1960: 29.80, 1970: 32.64, 1978: 35.06, 1988: 37.88, 2002: 38.23, 2011: 38.51,
       2021: 38.04}
URBAN = {1950: 36.9, 1960: 48.3, 1970: 52.3, 1988: 61.0, 2002: 61.8, 2021: 60.2}
TFR = {1950: 3.71, 1960: 2.98, 1970: 2.20, 1980: 2.28, 1990: 2.04, 2000: 1.37, 2010: 1.38, 2020: 1.39}
E0 = {1953: (58.6, 64.2), 1961: (64.8, 70.5), 1971: (66.8, 73.8), 1990: (66.2, 75.2), 2000: (69.6, 78.0),
      2010: (72.1, 80.6), 2019: (74.1, 81.8)}
RT = {1939: 8.86, 1946: 5.02, 1950: 5.94}
IDENT_2002 = {"sil": 173, "de": 153, "be": 49, "uk": 31, "rue": 6, "lt": 6, "csb": 5, "jw": 1}
LANG_2002 = {"de": 205, "be": 40, "uk": 23, "csb": 53, "rue": 6, "lt": 6}
LANG_2011 = {"de": 96.5, "be": 26.4, "uk": 24.5, "csb": 108.1, "rue": 6.3, "lt": 5.3}


def _year_index(res, year: int) -> int | None:
    """Index of the state at 1 January ``year`` in ``res.pop`` (None before the start)."""
    ys = list(res.years)
    if year in ys:
        return ys.index(year)
    return None


def poland_mask(res, year: int) -> np.ndarray:
    return np.array([m == "PL" for m in members_at(res, year)])


def _flow_index(res, year: int) -> int | None:
    """Index of the flows recorded during ``year`` (``res.years`` holds year + 1)."""
    return _year_index(res, year + 1)


def series(res) -> dict:
    """Poland (within each year's borders) by year: population (M), urban
    share (%), TFR, e0 (m, f), Recovered Territories population (M)."""
    pop = np.array(res.pop)                                   # (T,R,2,G)
    out = {"year": [], "pop": [], "urban": [], "tfr": [], "e0m": [], "e0f": [], "rt": []}
    rt = np.array([c[:3] in ("DE_", "DZ_") for c in res.region_codes])
    tfr = np.array(res.tfr)
    births = np.array(res.births)
    e0 = np.array(res.e0)
    for t, y in enumerate(res.years):
        m = poland_mask(res, y)
        P = pop[t][m]
        out["year"].append(y)
        out["pop"].append(P.sum() / 1e6)
        out["urban"].append(P[:, 1].sum() / max(P.sum(), 1e-9) * 100)
        out["rt"].append(pop[t][rt].sum() / 1e6)
        # flows of year y - 1 (the step that ended at 1 January y), in its borders
        mf = poland_mask(res, y - 1)
        b = births[t][mf]
        f = tfr[t][mf]
        out["tfr"].append(b.sum() / max((b / np.maximum(f, 1e-9)).sum(), 1e-9))
        w = pop[t][mf].sum(axis=(1, 2))
        out["e0m"].append(float((e0[t][mf, 0] * w).sum() / w.sum()))
        out["e0f"].append(float((e0[t][mf, 1] * w).sum() / w.sum()))
    return {k: np.array(v) for k, v in out.items()}


def identity_2002(res, year: int = 2002) -> dict:
    """Thousands of people in Poland by identity and by home language."""
    t = _year_index(res, year)
    m = poland_mask(res, year)
    I = np.array(res.identity)[t][m].sum(axis=0)
    pop = np.array(res.pop)[t][m]
    lang = np.zeros(NL)
    for g, (_, l) in enumerate(GROUPS):
        lang[LANG_INDEX[l]] += pop[:, :, g].sum()
    ident = {k: I[ID_INDEX[k]] / 1e3 for k in IDENT_2002}
    langs = {k: lang[LANG_INDEX[k]] / 1e3 for k in LANG_2002}
    return {"identity": ident, "language": langs}


def checks(res) -> list[tuple]:
    """(measure, year, model, target) rows."""
    s = series(res)
    at = {int(y): i for i, y in enumerate(s["year"])}
    rows = []
    for y, v in POP.items():
        if y in at:
            rows.append(("population (M)", y, s["pop"][at[y]], v))
    for y, v in RT.items():
        if y in at:
            rows.append(("Recovered Territories (M)", y, s["rt"][at[y]], v))
    for y, v in URBAN.items():
        if y in at:
            rows.append(("urban (%)", y, s["urban"][at[y]], v))
    for y, v in TFR.items():
        if y + 1 in at:
            rows.append(("TFR", y, s["tfr"][at[y + 1]], v))
    for y, (vm, vf) in E0.items():
        if y + 1 in at:
            rows.append(("e0 men", y, s["e0m"][at[y + 1]], vm))
            rows.append(("e0 women", y, s["e0f"][at[y + 1]], vf))
    if 2002 in at:
        d = identity_2002(res)
        for k, v in IDENT_2002.items():
            rows.append((f"identity {k} (k)", 2002, d["identity"][k], v))
        for k, v in LANG_2002.items():
            rows.append((f"home language {k} (k)", 2002, d["language"][k], v))
    if 2011 in at:
        d = identity_2002(res, 2011)
        for k, v in LANG_2011.items():
            rows.append((f"home language {k} (k)", 2011, d["language"][k], v))
    return rows


def write_report(res, outdir: str) -> str:
    """CSV and chart of the checks (outputs/history)."""
    os.makedirs(outdir, exist_ok=True)
    rows = checks(res)
    path = os.path.join(outdir, "historical_checks.csv")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("measure,year,model,observed\n")
        for m, y, a, b in rows:
            fh.write(f"{m},{y},{a:.3f},{b}\n")
    try:
        _chart(res, os.path.join(outdir, "historical_checks.png"))
    except Exception as exc:                                  # charts are a convenience
        print("chart failed:", exc)
    return path


def _chart(res, path: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from .report import INK, SLOTS, _save
    s = series(res)
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5))
    y = s["year"]
    ax = axes[0, 0]
    ax.plot(y, s["pop"], color=SLOTS[0], label="model: Poland in each year's borders")
    ax.scatter(list(POP), list(POP.values()), color=INK, s=14, zorder=5, label="census")
    ax.plot(y, s["rt"], color=SLOTS[1], label="model: German land and Danzig")
    ax.scatter(list(RT), list(RT.values()), color=INK, marker="x", s=18, zorder=5)
    ax.set_title("Population (M)")
    ax.legend(fontsize=7, frameon=False)
    ax = axes[0, 1]
    ax.plot(y - 1, s["tfr"], color=SLOTS[0])
    ax.scatter(list(TFR), list(TFR.values()), color=INK, s=14, zorder=5)
    ax.set_title("Total fertility")
    ax.set_xlim(1931, 2032)
    ax = axes[1, 0]
    ax.plot(y - 1, s["e0m"], color=SLOTS[2], label="men")
    ax.plot(y - 1, s["e0f"], color=SLOTS[3], label="women")
    ax.scatter(list(E0), [v[0] for v in E0.values()], color=SLOTS[2], edgecolor=INK, s=16, zorder=5)
    ax.scatter(list(E0), [v[1] for v in E0.values()], color=SLOTS[3], edgecolor=INK, s=16, zorder=5)
    ax.set_title("Life expectancy at birth")
    ax.legend(fontsize=7, frameon=False)
    ax = axes[1, 1]
    ax.plot(y, s["urban"], color=SLOTS[4])
    ax.scatter(list(URBAN), list(URBAN.values()), color=INK, s=14, zorder=5)
    ax.set_title("Urban share (%)")
    for a in axes.ravel():
        a.set_xlim(1931, 2032)
    fig.suptitle("Historical scenario against the censuses (points)", x=0.01, ha="left", fontweight="bold")
    fig.tight_layout()
    _save(fig, path)
