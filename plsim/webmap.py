"""Data export for the interactive atlas (``outputs/atlas``).

Each scenario becomes one file, ``data/<scenario>.txt``, holding the base64
text of gzip-compressed quantised frames (base64 because artifact hosting
serves text but not arbitrary binary):

* ``shares``: (F, N, 8) uint8, the share x 255 of the first eight map
  categories (``maps.CATS``); "other" is the remainder;
* ``dens``: (F, N) uint8, ``round(log10(persons/km2) / 4.5 * 254) + 1``,
  where 0 means no data (cell outside the state in this scenario);
* ``ident``: (F, R, 8) uint8, the share x 255 of the first eight national
  identity categories (``maps.IDCATS``) in each of the scenario's R regions
  (identity is tracked by county, not by cell);
* ``uncert`` (baseline, when an ensemble was run): for each ensemble year,
  (N,) uint8 the most likely leading map category and (N,) uint8 the share
  x 250 of runs in which it leads (255 = no data).

N indexes the cells of the full grid, which includes Lithuania, so all
scenarios share one geometry.  Small series (national language totals,
town populations) and the grid itself travel as JSON inside the page.
"""
from __future__ import annotations

import base64
import gzip
import json
import os

import numpy as np

from .data.geography import BBOX, build_grid, load_base_geography, load_borders
from .data.languages import LANG_INDEX
from .data.regions import REGIONS
from .maps import (CAT_COLOR, CAT_LABEL, CATS, IDCAT_LABEL, IDCATS, LABEL_TOWNS, REGIONAL, display_shares,
                   identity_at, identity_shares)
from .spatial import lang_totals

FRAMES = [1932] + list(range(1935, 2031, 5)) + [2032]
DENS_SCALE = 4.5


def full_grid():
    return build_grid([r.code for r in REGIONS])


def _rc(grid):
    row = np.round((grid.lat - (BBOX[1] + grid.dlat / 2)) / grid.dlat).astype(int)
    col = np.round((grid.lon - (BBOX[0] + grid.dlon / 2)) / grid.dlon).astype(int)
    return row, col


def cell_map(full, grid) -> np.ndarray:
    """Index of each cell of ``grid`` in the full grid."""
    fr, fc = _rc(full)
    lookup = {(r, c): i for i, (r, c) in enumerate(zip(fr, fc))}
    gr, gc = _rc(grid)
    return np.array([lookup.get((r, c), -1) for r, c in zip(gr, gc)])


def identity_frames(res, frames=FRAMES) -> np.ndarray:
    """(F, R, 9) identity shares of each region in IDCATS order."""
    return np.stack([identity_shares(identity_at(res, y)) for y in frames])


def identity_series(res, frames=FRAMES) -> dict:
    """National identity totals (thousands) per frame, for the legend."""
    def tot(y):
        I = identity_at(res, y)[_poland_mask(res, y)]
        return (identity_shares(I) * I.sum(axis=1, keepdims=True)).sum(axis=0)
    return {"years": list(frames), "cats": [[round(float(v) / 1000, 1) for v in tot(y)] for y in frames]}


def encode_uncert(prob: dict, grid, full) -> bytes:
    """Most likely leading category and its probability per cell of the full grid."""
    idx = cell_map(full, grid)
    ok = idx >= 0
    N = len(full.lat)
    out = b""
    for y in sorted(prob):
        P = prob[y]
        top = np.full(N, 255, np.uint8)
        pr = np.full(N, 255, np.uint8)
        top[idx[ok]] = P[ok].argmax(axis=1).astype(np.uint8)
        pr[idx[ok]] = np.round(P[ok].max(axis=1) * 250).astype(np.uint8)
        out += top.tobytes() + pr.tobytes()
    return out


def encode_frames(sr, full, frames=FRAMES, ident: np.ndarray | None = None, uncert: bytes = b"") -> bytes:
    idx = cell_map(full, sr.grid)
    ok = idx >= 0
    N = len(full.lat)
    sh = np.zeros((len(frames), N, 8), dtype=np.uint8)
    dn = np.zeros((len(frames), N), dtype=np.uint8)
    for f, y in enumerate(frames):
        X = sr.display(sr.frame(y))
        s = display_shares(X)[:, :8]
        d = X.sum(axis=1) / sr.grid.cell_km2
        sh[f, idx[ok]] = np.round(s[ok] * 255).astype(np.uint8)
        q = np.round(np.log10(np.clip(d, 1.0, 10 ** DENS_SCALE)) / DENS_SCALE * 254).astype(int) + 1
        dn[f, idx[ok]] = q[ok].astype(np.uint8)
    extra = b""
    if ident is not None:
        extra = np.round(ident[:, :, :8] * 255).astype(np.uint8).tobytes()
    return gzip.compress(sh.tobytes() + dn.tobytes() + extra + uncert, compresslevel=9, mtime=0)


def _poland_mask(res, year: int) -> np.ndarray:
    """Regions counted in the national series: all, or, in a run with border
    changes (the historical scenario), the regions of Poland at 1 January of
    ``year``."""
    if not getattr(res, "border_changes", None):
        return np.ones(len(res.region_codes), dtype=bool)
    from .history import members_at
    return np.array([m == "PL" for m in members_at(res, year)])


def national_series(res) -> dict:
    years = [res.params["start_year"]] + list(res.years)
    pops = [np.asarray(res.pop0, float)] + [np.asarray(p, float) for p in res.pop]
    rows, urban = [], []
    for y, p in zip(years, pops):
        p = p[_poland_mask(res, y)]
        L = lang_totals(p.sum(axis=1).sum(axis=0))                     # (NL,)
        row = [L[LANG_INDEX[c]] for c in CATS[:7]]
        row.append(sum(L[LANG_INDEX[c]] for c in REGIONAL))
        row.append(L.sum() - sum(row))
        rows.append([round(v / 1000.0, 1) for v in row])
        urban.append(round(float(p[:, 1].sum() / p.sum()), 4))
    return {"years": years, "cats": rows, "urban": urban}


def town_series(sr, frames=FRAMES) -> list:
    """Every modelled town of the scenario; ``major`` towns are labelled first."""
    out = []
    for i, n in enumerate(sr.town_names):
        out.append({"name": n, "lat": round(float(sr.town_lat[i]), 3), "lon": round(float(sr.town_lon[i]), 3),
                    "major": int(n in LABEL_TOWNS), "pop": [int(sr.towns[sr.frame(y)][i].sum()) for y in frames]})
    return out


def grid_payload(full) -> dict:
    row, col = _rc(full)
    H = int(np.round((BBOX[3] - BBOX[1]) / full.dlat))
    W = int(np.round((BBOX[2] - BBOX[0]) / full.dlon))
    # rows (uint16) | columns (uint16) | voivodeship (uint8), little-endian
    blob = row.astype("<u2").tobytes() + col.astype("<u2").tobytes() + full.region.astype(np.uint8).tobytes()
    return {"W": W, "H": H, "N": len(full.lat), "bbox": list(BBOX), "dlat": full.dlat, "dlon": full.dlon,
            "cells": base64.b64encode(blob).decode(), "km2": [round(float(a), 2) for a in full.cell_km2[:1]],
            "lat0": float(BBOX[1] + full.dlat / 2),
            "regions": [{"code": r.code, "name": r.name} for r in REGIONS]}


def geo_payload(ndigits: int = 2) -> dict:
    geo = load_base_geography()

    def rnd(lines, min_pts=2):
        return [[[round(x, ndigits), round(y, ndigits)] for x, y in ln] for ln in lines if len(ln) >= min_pts]
    b = load_borders()                    # 1932 state borders, to about 100 m

    def r3(lines):
        return [[[round(x, 3), round(y, 3)] for x, y in ln] for ln in lines]
    states = {"PL": r3([p[0] for p in b["PL"]]), "LT": r3([p[0] for p in b["LT"]]),
              "BY": r3([p[0] for p in b["BY"]]), "outline": r3(b["outline"]), "plLt": r3(b["PL_LT"]),
              "plBy": r3(b["PL_BY"]), "outlines": {k: r3(v) for k, v in b["outlines"].items()},
              "XK": r3([p[0] for p in b.get("XK", [])]), "byXk": r3(b.get("BY_XK", [])),
              "DE": r3([p[0] for p in b.get("DE", [])]), "DZ": r3([p[0] for p in b.get("DZ", [])]),
              "CS": r3([p[0] for p in b.get("CS", [])]),
              "inner": {k: r3(v) for k, v in b.get("inner", {}).items()},
              "pl1946": r3([p[0] for p in b.get("PL1946", [])])}
    return {"land": rnd(geo["land"], 3), "lakes": rnd(geo["lakes"], 3), "rivers": rnd(geo["rivers"]), "states": states}


def legend_payload() -> list:
    return [{"code": c, "label": CAT_LABEL[c], "color": CAT_COLOR[c]} for c in CATS]


def identity_legend_payload() -> list:
    return [{"code": i, "label": IDCAT_LABEL[i], "color": CAT_COLOR[c]} for c, i in zip(CATS, IDCATS)]


def write_data(outdir: str, name: str, blob: bytes) -> str:
    os.makedirs(os.path.join(outdir, "data"), exist_ok=True)
    path = os.path.join(outdir, "data", f"{name}.txt")
    with open(path, "w", encoding="ascii") as fh:
        fh.write(base64.b64encode(blob).decode())
    return path


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def build_atlas(atlasdir: str) -> list[str]:
    """Assemble the atlas page from the template, the scenario JSON and the
    baseline frames (embedded so the first view needs no fetch)."""
    with open(os.path.join(atlasdir, "scenarios.json"), encoding="utf-8") as fh:
        entries = json.load(fh)
    with open(os.path.join(atlasdir, "data", "baseline.txt"), encoding="ascii") as fh:
        base_b64 = fh.read().strip()
    full = full_grid()
    from .data.network import NODES
    meta = {"frames": FRAMES, "densScale": DENS_SCALE, "cats": legend_payload(), "idcats": identity_legend_payload(),
            "grid": grid_payload(full),
            "geo": geo_payload(), "scenarios": entries,
            "nodes": [[round(n.lat, 3), round(n.lon, 3)] for n in NODES],
            "rail": RAIL_CLS, "road": ROAD_CLS}
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "atlas_template.html"), encoding="utf-8") as fh:
        tpl = fh.read()
    body = tpl.replace("/*__META__*/null", dumps(meta)).replace("__BASELINE_B64__", base_b64)
    frag = os.path.join(atlasdir, "atlas.html")
    with open(frag, "w", encoding="utf-8") as fh:
        fh.write(body)
    page = os.path.join(atlasdir, "index.html")
    with open(page, "w", encoding="utf-8") as fh:
        fh.write('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
                 '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
                 "</head><body>\n" + body + "\n</body></html>\n")
    return [frag, page]


# ---------------------------------------------------------------------------------
# Transport network and political geometry (per scenario)
# ---------------------------------------------------------------------------------
RAIL_CLS = ["nar", "sec", "main", "main_el", "hsr"]
ROAD_CLS = ["dirt", "gravel", "paved", "express", "motorway"]
MEMBER_LABELS = {"PL": "Poland", "LT": "Lithuania", "UA": "Ukrainian autonomy",
                 "GD-L": "Grand Duchy: Lithuanian canton", "GD-P": "Grand Duchy: Polish canton",
                 "GD-B": "Grand Duchy: Belarusian canton", "GD": "Grand Duchy of Lithuania (autonomous)",
                 "NWK": "Northwestern Krai (separate state)", "LB": "Lit-Bel (separate state)",
                 "DE": "Germany", "DZ": "Free City of Danzig", "SU": "Soviet Union"}


def network_payload(res, frames=FRAMES) -> dict:
    """Edges active in any frame, their class in each frame (0 = absent;
    rail 1-5, road 1-5 in ``RAIL_CLS``/``ROAD_CLS`` order) and km by class; the
    projects themselves are in ``infra_payload``."""
    snaps = res.network_snapshots
    years = sorted(snaps)
    key_idx, edges = {}, []
    cls = []
    for f, y in enumerate(frames):
        sy = max([s for s in years if s <= y] or [years[0]])
        for u, v, m, c in snaps[sy]:
            k = (min(u, v), max(u, v), int(m))
            if k not in key_idx:
                key_idx[k] = len(edges)
                edges.append(list(k))
                cls.append([0] * len(frames))
            order = RAIL_CLS if m == 0 else ROAD_CLS
            cls[key_idx[k]][f] = order.index(c) + 1
    cls_arr = np.array(cls, dtype=np.uint8).reshape(len(edges), len(frames))
    ry = list(res.years)
    km = []
    for y in frames:
        j = min(range(len(ry)), key=lambda i: abs(ry[i] - y))
        d = res.km[j]
        km.append([round(d[f"rail_{c}"]) for c in RAIL_CLS] + [round(d[f"road_{c}"]) for c in ROAD_CLS])
    return {"e": edges, "c": base64.b64encode(cls_arr.tobytes()).decode(), "km": km}


def infra_payload(res) -> dict:
    """Every project of a run, with the reasons it was built or closed, for the
    atlas's infrastructure panel (loaded on demand from ``data/<name>.infra.json``).
    Rows: y (year decided), o (year opened), k (new | upgrade | dated |
    closure), m (rail | road), c (class built), a, b (node indices), f, t
    (town names), s (appraisal | historical | planned | federation |
    rationalisation), km, cost (million 1990 $), bcr, label (dated projects)
    and w (the appraisal or closure details logged by ``plsim.infrastructure``)."""
    idx = {n: i for i, n in enumerate(res.node_names)}
    rows = []
    for p in res.project_log:
        src, _, label = p["source"].partition(": ")
        r = {"y": int(p["year"]), "o": int(p["open"]), "k": p["kind"], "m": p["mode"], "c": p["class"],
             "a": idx.get(p["from"], -1), "b": idx.get(p["to"], -1), "f": p["from"], "t": p["to"], "s": src}
        for k_out, k_in in (("km", "km"), ("cost", "cost_M"), ("bcr", "bcr")):
            if p.get(k_in) is not None:
                r[k_out] = p[k_in]
        if label:
            r["label"] = label
        if p.get("why"):
            r["w"] = p["why"]
        rows.append(r)
    rows.sort(key=lambda r: (r["o"], r["y"]))
    return {"p": rows}


def write_json(outdir: str, name: str, obj) -> str:
    os.makedirs(os.path.join(outdir, "data"), exist_ok=True)
    path = os.path.join(outdir, "data", name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(dumps(obj))
    return path


def geometry_payload(res, sr, full) -> dict:
    """Regions and federal members of a scenario, mapped onto the full grid."""
    idx = cell_map(full, sr.grid)
    # 16 bits: county runs have more than 255 regions; 65535 = no region
    cellreg = np.full(len(full.lat), 65535, dtype="<u2")
    ok = idx >= 0
    assert len(res.region_codes) < 65535
    cellreg[idx[ok]] = sr.grid.region[ok].astype("<u2")
    members = list(getattr(res, "members", []) or ["LT" if c.startswith("LT") else "PL" for c in res.region_codes])
    from .data.counties import BY_CODE
    parent_name = {r.code: r.name for r in REGIONS}
    labels = []
    for code, name in zip(res.region_codes, res.region_names):
        par = code.split(".")[0]
        if code in BY_CODE and par.startswith("BY_"):          # Soviet Belarus: the 1926 okrugs
            labels.append(f"{name} · woj. {parent_name.get(par, par)}")
        elif code in BY_CODE and not par.startswith("LT"):
            labels.append(f"pow. {name} · woj. {parent_name.get(par, par)}")
        elif code in BY_CODE:
            labels.append(f"{name} · {parent_name.get(par, par)}")
        elif "." in code or par.startswith("LT") or code == "WAW":
            labels.append(name)
        else:
            labels.append(f"woj. {name}")
    # label point of each region: the cell nearest the centroid of its cells
    pts = []
    for k in range(len(res.region_codes)):
        m = np.where(sr.grid.region == k)[0]
        if not len(m):
            pts.append(None)
            continue
        la, lo = sr.grid.lat[m].mean(), sr.grid.lon[m].mean()
        j = m[np.argmin((sr.grid.lat[m] - la) ** 2 + ((sr.grid.lon[m] - lo) * 0.6) ** 2)]
        pts.append([round(float(sr.grid.lat[j]), 3), round(float(sr.grid.lon[j]), 3)])
    return {"codes": list(res.region_codes), "names": list(res.region_names), "labels": labels, "seats": pts,
            "members": [MEMBER_LABELS.get(m, m) for m in members],
            "dominant": list(getattr(res, "dominant", []) or []),
            "official": [list(o) for o in (getattr(res, "official", None) or [[d] for d in res.dominant])],
            # border changes (plsim.history): from 1 January after ``year``, the regions ``idx`` are in ``member``
            "changes": [{"year": ch["year"], "member": MEMBER_LABELS.get(ch["member"], ch["member"]),
                         "idx": [res.region_codes.index(c) for c in ch["codes"]],
                         "dominant": ch.get("dominant")}
                        for ch in (getattr(res, "border_changes", None) or []) if ch.get("member")],
            "cellreg": base64.b64encode(cellreg.tobytes()).decode()}


def curzon_payload(lines: list[dict], count: str = "language") -> dict:
    """Equal-exchange Curzon line of each frame (``plsim.curzon``): the line and,
    in thousands, [Poles, counted, Polish side, its Poles, its others, other side's Poles,
    its others, not counted]; ``by`` says whether Poles are counted by home
    language or by identity."""
    keys = ["poles", "people", "west", "west_poles", "west_others", "east_poles", "east_others", "excluded"]
    hist = ["hist_west_poles", "hist_west_others", "hist_east_poles", "hist_east_others"]
    from .curzon import HISTORICAL_LINE
    return {"by": count,
            "lines": [[[[round(float(x), 3), round(float(y), 3)] for x, y in ln] for ln in s["lines"]] for s in lines],
            "stats": [[round(s[k] / 1e3) for k in keys] for s in lines],
            "hist": [[round(s[k] / 1e3) for k in hist] for s in lines],
            "histLine": [[round(float(lon), 3), round(float(lat), 3)] for lat, lon in HISTORICAL_LINE]}


def nodes_payload(res) -> list:
    return [[round(a, 3), round(b, 3)] for a, b in zip(res.node_lat, res.node_lon)]
