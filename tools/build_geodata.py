"""Rebuild the geographic data files in plsim/data (run by hand; not needed
to run the model).

* ``geo_base.json``: land, lakes and rivers from GSHHS / World Data Bank II at
  intermediate resolution, as shipped in the ``basemap-data`` 2.0 wheel,
  clipped to the map box ``plsim.data.geography.BBOX``.
* ``borders_1932.json``, Soviet Belarus: the 1932 Byelorussian SSR, taken as
  modern Belarus (Natural Earth 1:10m admin-0, v5) minus Poland and
  Lithuania on 1 January 1932 (CShapes 2.0). Belarus's borders with Russia,
  Ukraine and Latvia are those the BSSR had from December 1926; the result
  covers 125,900 km² against the 126,800 km² of the 1926 census. Also the
  Polish-Soviet Belarusian border and the outer outlines of every
  combination of states.

Needs ``shapely`` and the two downloads::

    pip download basemap-data==2.0.0 --no-deps -d /tmp/bmd && unzip -o /tmp/bmd/*.whl -d /tmp/bmd
    curl -o /tmp/ne10_admin0.geojson https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_0_countries.geojson
    python tools/build_geodata.py /tmp/bmd/mpl_toolkits/basemap_data /tmp/ne10_admin0.geojson
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from shapely.geometry import LineString, Polygon, box, shape
from shapely.ops import linemerge, unary_union

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plsim", "data")
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from plsim.data.geography import BBOX  # noqa: E402

LAKE_MIN_AREA = 100.0       # km², GSHHS level-2 polygons kept as lakes
LAND_MIN_KM2 = 200.0        # islands smaller than this are dropped
RIVER_MIN_PTS = 6           # shorter river pieces are dropped


def _segments(bmd: str, name: str):
    raw = open(os.path.join(bmd, f"{name}_i.dat"), "rb").read()
    for line in open(os.path.join(bmd, f"{name}meta_i.dat")):
        f = line.split()
        level, area = int(f[0]), float(f[1])
        lat0, lat1, off, cnt = float(f[3]), float(f[4]), int(f[5]), int(f[6])
        if lat1 < BBOX[1] or lat0 > BBOX[3]:
            continue
        xy = np.frombuffer(raw[off:off + cnt], "<f4").reshape(-1, 2).astype(float)
        if xy[:, 0].max() < BBOX[0] or xy[:, 0].min() > BBOX[2]:
            continue
        yield level, area, xy


def _km2(ring) -> float:
    p = Polygon(ring)
    return p.area * 111.2 ** 2 * np.cos(np.radians(p.centroid.y))


def _rings(geom, nd=3):
    polys = [geom] if geom.geom_type == "Polygon" else [g for g in getattr(geom, "geoms", []) if g.geom_type == "Polygon"]
    return [[[round(x, nd), round(y, nd)] for x, y in p.exterior.coords] for p in polys if not p.is_empty]


def _lines(geom, nd=3):
    if geom.is_empty:
        return []
    parts = [geom] if geom.geom_type != "MultiLineString" and not hasattr(geom, "geoms") else list(geom.geoms)
    return [[[round(x, nd), round(y, nd)] for x, y in p.coords] for p in parts if p.geom_type == "LineString"]


def build_geo_base(bmd: str) -> dict:
    frame = box(*BBOX)
    land, lakes, rivers = [], [], []
    for level, area, xy in _segments(bmd, "gshhs"):
        p = Polygon(xy).buffer(0)
        clip = p.intersection(frame)
        if clip.is_empty:
            continue
        if level == 1:
            land += [r for r in _rings(clip) if _km2(r) >= LAND_MIN_KM2]
        elif level == 2 and area >= LAKE_MIN_AREA:
            lakes += _rings(clip)
    for _, _, xy in _segments(bmd, "rivers"):
        rivers += [r for r in _lines(LineString(xy).intersection(frame)) if len(r) >= RIVER_MIN_PTS]
    return {"land": land, "lakes": lakes, "rivers": rivers,
            "source": "GSHHS/World Data Bank II via basemap-data 2.0 (intermediate resolution), clipped to "
                      f"{BBOX[0]}-{BBOX[2]}E, {BBOX[1]}-{BBOX[3]}N"}


def add_belarus(borders: dict, ne_path: str) -> dict:
    ne = json.load(open(ne_path))
    blr = shape(next(f for f in ne["features"] if f["properties"].get("ADM0_A3") == "BLR")["geometry"])
    poly = lambda rl: unary_union([Polygon(r[0], r[1:]) for r in rl])  # noqa: E731
    PL, LT = poly(borders["PL"]), poly(borders["LT"])
    by = blr.difference(PL).difference(LT)
    if by.geom_type == "MultiPolygon":                     # keep the body; drop slivers
        by = max(by.geoms, key=lambda g: g.area)
    by = by.simplify(0.002)
    borders["BY"] = [[[[round(x, 4), round(y, 4)] for x, y in by.exterior.coords]]]
    states = {"PL": PL, "LT": LT, "BY": Polygon(borders["BY"][0][0])}
    # the Polish-Soviet Belarusian border (the 1921 Riga line), as a line
    shared = states["PL"].boundary.intersection(states["BY"].buffer(0.01))
    merged = linemerge(shared) if shared.geom_type == "MultiLineString" else shared
    borders["PL_BY"] = _lines(merged, 4)
    # outer outline of Poland together with Soviet Belarus (Poland alone and
    # Poland-Lithuania use the CShapes rings and "outline")
    u = unary_union([states["PL"], states["BY"]])
    parts = [u] if u.geom_type == "Polygon" else sorted(u.geoms, key=lambda g: -g.area)
    outlines = {"PL+BY": [[[round(x, 4), round(y, 4)] for x, y in p.exterior.coords]
                          for p in parts if p.area > 1e-4]}
    borders["outlines"] = outlines
    borders["neighbours"]["BY"] = ["Latvia", "Poland", "Russia (Soviet Union)", "Ukraine (Soviet Union)"]
    borders["source_BY"] = ("Natural Earth 1:10m admin-0 countries (v5): Belarus, minus Poland and Lithuania of "
                            "1 Jan 1932 (CShapes 2.0) = the Byelorussian SSR of Dec 1926-Sep 1939")
    return borders


if __name__ == "__main__":
    bmd, ne_path = sys.argv[1], sys.argv[2]
    geo = build_geo_base(bmd)
    with open(os.path.join(HERE, "geo_base.json"), "w") as fh:
        json.dump(geo, fh, separators=(",", ":"))
    path = os.path.join(HERE, "borders_1932.json")
    borders = add_belarus(json.load(open(path)), ne_path)
    with open(path, "w") as fh:
        json.dump(borders, fh, separators=(",", ":"))
    print("land", len(geo["land"]), "lakes", len(geo["lakes"]), "rivers", len(geo["rivers"]))
