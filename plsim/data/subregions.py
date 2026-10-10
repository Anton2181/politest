"""Sub-regions: splitting voivodeships along county lines.

Some scenarios need units smaller than a voivodeship: an autonomy, a canton
or the later Curzon line can cut through one.  A split is defined by lists
of county seats (the anchors of ``data.geography``).  Every place is assigned
to the sub-region of its nearest county seat in the parent voivodeship, a
Voronoi approximation of the county borders.

Sub-region codes are ``PARENT.CHILD``.  Settings given for the parent apply
to the children unless overridden (``params.region_lookup``).

County areas.  The 1931 census prints the area of every powiat
(``data/county_areas_1931.csv``).  A place goes to the county with the least
distance to its seat less the county's weight (an additively weighted
Voronoi diagram; ``data/county_weights.json``, fitted by
``tools/build_county_weights.py`` on the model grid), so that each county's
land matches its census area. Such a diagram can meet any set of areas, and
every county holds its seat and is star-shaped around it: if a seat i fell in
county j (w_j - w_i > d_ij), every place would be nearer j, and i would have
no land. A power diagram (squared distance less the weight) fits the areas
too, but put the seats of Katowice, Grudziądz and Mińsk Mazowiecki in their
neighbours.

Real county borders.  When ``data/powiaty_1931.geojson`` exists (polygon
features with a ``plsim_code`` property naming the county, e.g. digitised
from the MPIDR Population History GIS Collection, which holds the 1931
powiaty), places inside a county's polygon go to that county and the
Voronoi rule only fills the gaps.  ``tools/match_powiaty.py`` adds the
codes to a GeoJSON by county name.

Splits
------
``BIA``  west of the Curzon line (Białystok, Bielsk, Sokółka, Suwałki,
         Augustów, Łomża ...) | east: the Grodno and Wołkowysk counties.
``WIL``  west (Wilno-Troki, Oszmiana, Święciany, Ejszyszki: Polish and
         Lithuanian plurality) | east (Mołodeczno, Wilejka, Dzisna,
         Głębokie, Postawy, Brasław: Belarusian plurality).
``NOW``  west (Lida, Szczuczyn) | east (Nowogródek, Baranowicze, Nieśwież,
         Stołpce, Wołożyn, Słonim).
``LWO``  west of the San ethnographic line (Rzeszów, Jarosław, Przemyśl,
         Sanok, Krosno, Jasło, the Lemko districts ...) | east, with Lwów.
"""
from __future__ import annotations

import json
import os

import numpy as np
from matplotlib.path import Path

from .geography import ANCHORS, GOV_ALLOWED, gov_constrain, haversine_matrix

POWIAT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "powiaty_1931.geojson")
WEIGHT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "county_weights.json")
_POLYS: dict | None = None
_WEIGHTS: dict | None = None
_LATTICE: dict = {}


def county_weights(kind: str = "model") -> dict:
    """{county code: additive weight, km} fitted to the census areas (0 if
    absent). ``kind="map"``: the weights the maps use, fitted with every
    county joined into one piece (``geography.build_grid(connected=True)``);
    the model's when none are stored."""
    global _WEIGHTS
    if _WEIGHTS is None:
        _WEIGHTS = {"model": {}, "map": {}}
        if os.path.exists(WEIGHT_FILE):
            with open(WEIGHT_FILE, encoding="utf-8") as fh:
                d = json.load(fh)
            _WEIGHTS = {"model": d.get("weights", {}), "map": d.get("map_weights") or d.get("weights", {})}
    return _WEIGHTS[kind]


def assign_connected(parent: str, lat, lon, child_codes, dlat: float, dlon: float,
                     weights: dict | None = None, gov_cut: bool = False) -> np.ndarray:
    """County of each place for the maps: an additively weighted Voronoi
    diagram like ``assign``, but with distances measured along the ground
    inside the voivodeship (over the grid of places, 8 neighbours), and, where
    the 1931 powiaty kept the uezd borders of 1897, inside the governorate.
    Every county is then in one piece: a place on the shortest path from a
    seat to a place of its county is nearer that seat still. The weights are
    ``county_weights("map")``, fitted to the census areas on these distances.
    Places no seat reaches (pieces of the voivodeship cut off by the state
    border) take the plain rule."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import dijkstra
    anc = seat_table(parent, child_codes)
    lat, lon = np.asarray(lat, float), np.asarray(lon, float)
    n, K = len(lat), len(anc)
    wt = county_weights("map") if weights is None else weights
    w = np.array([wt.get(a[2], 0.0) for a in anc])
    key = (parent, n, round(float(lat.sum()), 6), round(float(lon.sum()), 6), dlat, dlon, tuple(a[2] for a in anc),
           gov_cut)
    if key not in _LATTICE:
        r = np.round((lat - lat.min()) / dlat).astype(int)
        c = np.round((lon - lon.min()) / dlon).astype(int)
        at = {(i, j): k for k, (i, j) in enumerate(zip(r, c))}
        gov = seat_gov = None
        if (gov_cut and len(GOV_ALLOWED.get(parent, "x")) > 1 and n
                and not parent.startswith(("LT", "BY_", "LV_", "RU_"))):
            from .governorates import letter
            gov = np.asarray(letter(lat, lon))
            seat_gov = np.asarray(letter([a[0] for a in anc], [a[1] for a in anc]))
        km_lat = 111.32 * dlat
        src, dst, ln = [], [], []
        for di, dj in ((0, 1), (1, 0), (1, 1), (1, -1)):
            for k in range(n):
                m = at.get((r[k] + di, c[k] + dj))
                if m is None or (gov is not None and gov[k] != gov[m]):
                    continue
                km_lon = 111.32 * dlon * np.cos(np.radians((lat[k] + lat[m]) / 2))
                d = float(np.hypot(di * km_lat, dj * km_lon))
                src += [k, m]; dst += [m, k]; ln += [d, d]
        # each seat joins the grid at its nearest place (of its governorate)
        D0 = haversine_matrix(np.array([a[0] for a in anc]), np.array([a[1] for a in anc]), lat, lon)   # (K, n)
        entry = []
        for q in range(K):
            d = D0[q] if gov is None else np.where(gov == seat_gov[q], D0[q], np.inf)
            if not np.isfinite(d).any():
                d = D0[q]
            k = int(np.argmin(d))
            entry.append((k, float(d[k])))
        _LATTICE[key] = (src, dst, ln, entry)
    src, dst, ln, entry = _LATTICE[key]
    # node n: the source; n+1 ... n+K: the seats, at a start of (largest weight - weight)
    top = w.max() if K else 0.0
    s2, d2, l2 = list(src), list(dst), list(ln)
    for q, (k, dk) in enumerate(entry):
        s2 += [n, n + 1 + q]; d2 += [n + 1 + q, k]; l2 += [top - w[q] + 1e-9, dk + 1e-6]
    G = coo_matrix((l2, (s2, d2)), shape=(n + 1 + K, n + 1 + K)).tocsr()
    dist, pred = dijkstra(G, indices=n, return_predecessors=True)
    lab = np.full(n + 1 + K, -1)
    lab[n + 1:] = np.arange(K)
    for v in np.argsort(dist[:n], kind="stable"):
        if np.isfinite(dist[v]):
            u, chain = v, []
            while lab[u] < 0 and pred[u] >= 0:
                chain.append(u)
                u = pred[u]
            for x in chain:
                lab[x] = lab[u]
    out = np.array([anc[k][2] if k >= 0 else "" for k in lab[:n]], dtype=object)
    lost = lab[:n] < 0
    if lost.any():
        out[lost] = assign(parent, lat[lost], lon[lost], child_codes, weights=wt)
    return out.astype(str)


def county_polygons() -> dict:
    """{county code: [[outer ring, hole, ...], ...]} as matplotlib Paths from
    ``POWIAT_FILE``; {} when the file is absent."""
    global _POLYS
    if _POLYS is None:
        _POLYS = {}
        if os.path.exists(POWIAT_FILE):
            with open(POWIAT_FILE, encoding="utf-8") as fh:
                gj = json.load(fh)
            for f in gj.get("features", []):
                code = (f.get("properties") or {}).get("plsim_code")
                geom = f.get("geometry") or {}
                if not code:
                    continue
                polys = [geom["coordinates"]] if geom.get("type") == "Polygon" else \
                    geom.get("coordinates", []) if geom.get("type") == "MultiPolygon" else []
                for poly in polys:
                    _POLYS.setdefault(code, []).append([Path(np.asarray(r, float)[:, :2]) for r in poly])
        # the uezds of Latgale and the Nevel lands are their counties' borders (data.krai_east)
        from .geography import load_borders
        for piece in load_borders().get("XK_units", []):
            if "." in piece["unit"]:
                for poly in piece["rings"]:
                    _POLYS.setdefault(piece["unit"], []).append([Path(np.asarray(r, float)) for r in poly])
    return _POLYS

SPLITS: dict[str, dict] = {
    "BIA": {"default": "BIA.W", "BIA.E": ["Grodno", "Wołkowysk"]},
    "WIL": {"default": "WIL.W", "WIL.E": ["Mołodeczno", "Wilejka", "Dzisna", "Głębokie", "Postawy", "Brasław"]},
    "NOW": {"default": "NOW.E", "NOW.W": ["Lida", "Szczuczyn"]},
    "LWO": {"default": "LWO.E",
            "LWO.W": ["Jarosław", "Przemyśl", "Brzozów", "Sanok", "Komańcza (Lemko)", "Dukla (Lemko)", "Krosno",
                      "Jasło", "Rzeszów", "Łańcut", "Przeworsk", "Tarnobrzeg", "Nisko", "Kolbuszowa"]},
}

NAMES: dict[str, str] = {
    "BIA.W": "białostockie (west)", "BIA.E": "Grodno–Wołkowysk",
    "WIL.W": "Wilno lands", "WIL.E": "wileńskie (east)",
    "NOW.W": "Lida–Szczuczyn", "NOW.E": "nowogródzkie (east)",
    "LWO.W": "lwowskie (west of the San)", "LWO.E": "lwowskie (east, with Lwów)",
}


_TRANS = str.maketrans("ąćęłńóśźżĄĆĘŁŃÓŚŹŻėęįšųūžčĖĮŠŲŪŽČ", "acelnoszzACELNOSZZeeisuuzcEISUUZC")


def slug(name: str) -> str:
    base = name.split("(")[0].strip().translate(_TRANS).lower()
    return "".join(ch for ch in base if ch.isalnum())[:14]


def county_seats(parent: str) -> list[tuple]:
    """(code, name, lat, lon) of the counties of a voivodeship or Lithuanian unit.
    Uses the 1931 county table when it covers the parent, else the anchors."""
    try:
        from .counties import COUNTIES
    except ImportError:          # county table not available
        COUNTIES = []
    rows = [c for c in COUNTIES if c.parent == parent]
    if rows:
        return [(c.code, c.name, c.lat, c.lon) for c in rows]
    out, seen = [], set()
    for a in ANCHORS:
        if a.region != parent:
            continue
        code = f"{parent}.{slug(a.name)}"
        if code in seen:
            continue
        seen.add(code)
        out.append((code, a.name.split("(")[0].strip(), a.lat, a.lon))
    return out


def children(parent: str, mode: str = "named") -> list[str]:
    if mode == "county":
        return [c[0] for c in county_seats(parent)]
    spec = SPLITS[parent]
    out = [spec["default"]] + [k for k in spec if k != "default"]
    return sorted(set(out), key=out.index)


def child_name(code: str) -> str:
    if code in NAMES:
        return NAMES[code]
    parent = code.split(".")[0]
    for c, name, _, _ in county_seats(parent):
        if c == code:
            return name
    return code


def seat_table(parent: str, child_codes=None) -> list[tuple]:
    """(lat, lon, child) seats for the Voronoi assignment.  Named splits use
    all county seats labelled with their sub-region; county splits use one
    seat per county."""
    if parent in SPLITS and (child_codes is None or set(child_codes) <= set(children(parent))):
        spec = SPLITS[parent]
        named = {n: c for c, names in spec.items() if c != "default" for n in names}
        return [(a.lat, a.lon, named.get(a.name, spec["default"])) for a in ANCHORS if a.region == parent]
    seats = county_seats(parent)
    if child_codes is not None:
        seats = [s for s in seats if s[0] in set(child_codes)]
    return [(la, lo, code) for code, _, la, lo in seats]


def assign(parent: str, lat, lon, child_codes=None, weights: dict | None = None) -> np.ndarray:
    """Sub-region code of each place: the nearest seat, the distance less the
    county's weight (``county_weights``; or ``weights`` when fitting)."""
    anc = seat_table(parent, child_codes)
    lat, lon = np.atleast_1d(np.asarray(lat, float)), np.atleast_1d(np.asarray(lon, float))
    D = D0 = haversine_matrix(lat, lon, np.array([a[0] for a in anc]), np.array([a[1] for a in anc]))
    named = parent in SPLITS and (child_codes is None or set(child_codes) <= set(children(parent)))
    if not named:
        # additively weighted Voronoi: distance less the county's weight (km), fitted to the census areas
        wt = county_weights() if weights is None else weights
        D = D - np.array([wt.get(a[2], 0.0) for a in anc])[None, :]
    if (len(GOV_ALLOWED.get(parent, "x")) > 1 and not named and len(lat)
            and not parent.startswith(("LT", "BY_", "LV_", "RU_"))):
        # the 1931 powiaty of the formerly Russian north-east kept the uezd
        # borders of 1897: a place goes to a county of its own governorate
        # (Lithuanian apskritys and Soviet okrugs did cross them, and are cut)
        from .governorates import letter
        gl = letter(lat, lon)
        sl = letter([a[0] for a in anc], [a[1] for a in anc])
        D = gov_constrain(D, gl[:, None] != sl[None, :], raw=D0)
    out = np.array([anc[k][2] for k in D.argmin(axis=1)], dtype=object)
    polys = county_polygons()
    if polys:
        pts = np.column_stack([lon, lat])
        for code in dict.fromkeys(a[2] for a in anc):
            inside = np.zeros(len(pts), dtype=bool)
            for rings in polys.get(code, []):
                m = rings[0].contains_points(pts)
                for hole in rings[1:]:
                    m &= ~hole.contains_points(pts)
                inside |= m
            out[inside] = code
    return out.astype(str)
