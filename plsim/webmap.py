"""Data export for the interactive atlas (``outputs/atlas``).

Each scenario becomes one file, ``data/<scenario>.txt``, holding the base64
text of gzip-compressed quantised frames (base64 because artifact hosting
serves text but not arbitrary binary):

* ``shares``: (F, N, 8) uint8, the share x 255 of the first eight map
  categories (``maps.CATS``); "other" is the remainder;
* ``dens``: (F, N) uint8, ``round(log10(persons/km2) / 4.5 * 254) + 1``,
  where 0 means no data (cell outside the state in this scenario).

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

from .data.geography import BBOX, build_grid, load_base_geography
from .data.languages import LANG_INDEX
from .data.regions import REGIONS
from .maps import CAT_COLOR, CAT_LABEL, CATS, LABEL_TOWNS, REGIONAL, display_shares
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


def encode_frames(sr, full, frames=FRAMES) -> bytes:
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
    return gzip.compress(sh.tobytes() + dn.tobytes(), compresslevel=9, mtime=0)


def national_series(res) -> dict:
    years = [res.params["start_year"]] + list(res.years)
    pops = [np.asarray(res.pop0, float)] + [np.asarray(p, float) for p in res.pop]
    rows, urban = [], []
    for p in pops:
        L = lang_totals(p.sum(axis=1).sum(axis=0))                     # (NL,)
        row = [L[LANG_INDEX[c]] for c in CATS[:7]]
        row.append(sum(L[LANG_INDEX[c]] for c in REGIONAL))
        row.append(L.sum() - sum(row))
        rows.append([round(v / 1000.0, 1) for v in row])
        urban.append(round(float(p[:, 1].sum() / p.sum()), 4))
    return {"years": years, "cats": rows, "urban": urban}


def town_series(sr, frames=FRAMES) -> list:
    out = []
    for i, n in enumerate(sr.town_names):
        if n in LABEL_TOWNS:
            out.append({"name": n, "lat": round(float(sr.town_lat[i]), 3), "lon": round(float(sr.town_lon[i]), 3),
                        "pop": [int(sr.towns[sr.frame(y)][i].sum()) for y in frames]})
    return out


def grid_payload(full) -> dict:
    row, col = _rc(full)
    H = int(np.round((BBOX[3] - BBOX[1]) / full.dlat))
    W = int(np.round((BBOX[2] - BBOX[0]) / full.dlon))
    region = full.region.astype(np.uint8)
    blob = np.stack([row.astype(np.uint8), col.astype(np.uint8), region], axis=1).tobytes()
    return {"W": W, "H": H, "N": len(full.lat), "bbox": list(BBOX), "dlat": full.dlat, "dlon": full.dlon,
            "cells": base64.b64encode(blob).decode(), "km2": [round(float(a), 2) for a in full.cell_km2[:1]],
            "lat0": float(BBOX[1] + full.dlat / 2),
            "regions": [{"code": r.code, "name": r.name} for r in REGIONS]}


def geo_payload(ndigits: int = 2) -> dict:
    geo = load_base_geography()

    def rnd(lines, min_pts=2):
        return [[[round(x, ndigits), round(y, ndigits)] for x, y in ln] for ln in lines if len(ln) >= min_pts]
    return {"land": rnd(geo["land"], 3), "lakes": rnd(geo["lakes"], 3), "rivers": rnd(geo["rivers"])}


def legend_payload() -> list:
    return [{"code": c, "label": CAT_LABEL[c], "color": CAT_COLOR[c]} for c in CATS]


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
    meta = {"frames": FRAMES, "densScale": DENS_SCALE, "cats": legend_payload(), "grid": grid_payload(full),
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
                 "GD-B": "Grand Duchy: Belarusian canton"}
LOG_KINDS = {"new", "dated", "closure"}
LOG_UPGRADES = {"hsr", "motorway"}


def network_payload(res, frames=FRAMES) -> dict:
    """Edges active in any frame, their class in each frame (0 = absent;
    rail 1-5, road 1-5 in ``RAIL_CLS``/``ROAD_CLS`` order), km by class, and the
    notable openings and closures."""
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
    log = []
    for p in res.project_log:
        if p["kind"] in LOG_KINDS or (p["kind"] == "upgrade" and p["class"] in LOG_UPGRADES):
            log.append([int(p["open"]), p["kind"], p["mode"], p["class"], p["from"], p["to"]])
    log.sort(key=lambda r: r[0])
    return {"e": edges, "c": base64.b64encode(cls_arr.tobytes()).decode(), "km": km, "log": log}


def geometry_payload(res, sr, full) -> dict:
    """Regions and federal members of a scenario, mapped onto the full grid."""
    idx = cell_map(full, sr.grid)
    cellreg = np.full(len(full.lat), 255, dtype=np.uint8)
    ok = idx >= 0
    cellreg[idx[ok]] = sr.grid.region[ok].astype(np.uint8)
    members = list(getattr(res, "members", []) or ["LT" if c.startswith("LT") else "PL" for c in res.region_codes])
    from .data.counties import BY_CODE
    parent_name = {r.code: r.name for r in REGIONS}
    labels = []
    for code, name in zip(res.region_codes, res.region_names):
        par = code.split(".")[0]
        if code in BY_CODE and not par.startswith("LT"):
            labels.append(f"pow. {name} · woj. {parent_name.get(par, par)}")
        elif code in BY_CODE:
            labels.append(f"{name} · {parent_name.get(par, par)}")
        elif "." in code or par.startswith("LT") or code == "WAW":
            labels.append(name)
        else:
            labels.append(f"woj. {name}")
    return {"codes": list(res.region_codes), "names": list(res.region_names), "labels": labels,
            "members": [MEMBER_LABELS.get(m, m) for m in members],
            "dominant": list(getattr(res, "dominant", []) or []),
            "cellreg": base64.b64encode(cellreg.tobytes()).decode()}


def nodes_payload(res) -> list:
    return [[round(a, 3), round(b, 3)] for a, b in zip(res.node_lat, res.node_lon)]
