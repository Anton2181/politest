"""Governorates of 1897 for the scenarios drawn on the old imperial borders.

    python tools/build_governorates.py /path/to/history_stats/data/out/boundaries

Reads the RISTAT layers of 1897 (``provinces_1897.geojson`` and
``districts_1897.geojson``: Electronic Repository of Russian Historical
Statistics, "Russian Empire Historical GIS Maps (1897)", IISG Dataverse
hdl:10622/DN9QDM, CC0; as republished in the GeoJSON set of
github.com/Baushkiner/history_stats) and writes

* ``plsim/data/governorates_1897.json``: the seven governorates the
  scenarios name (Vilna, Kovno, Grodno, Minsk, Mogilev, Vitebsk, Suwałki),
  simplified to about 300 m, with their one-letter codes;
* the key ``XK`` of ``plsim/data/borders_1932.json``: the lands of the six
  north-western governorates outside Poland, Lithuania and the BSSR of 1932
  (Latgale; Nevel, Sebezh and Velizh; the eastern edge of the Mogilev
  governorate), with the uezd each piece belongs to, and the outlines of
  the state combinations that include it.

Needs ``shapely``.
"""
from __future__ import annotations

import argparse
import json
import math
import os

from shapely.geometry import Polygon, shape
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "plsim", "data")

GOVS = {"Vilna governorate": ("V", "Vilna"), "Kovno governorate": ("K", "Kovno"),
        "Grodno governorate": ("G", "Grodno"), "Minsk governorate": ("M", "Minsk"),
        "Mogilev governorate": ("O", "Mogilev"), "Vitebsk governorate": ("T", "Vitebsk"),
        "Suwałki governorate": ("S", "Suwałki")}
# uezds of the land outside the 1932 territory -> unit of data.krai_east
UEZD_UNIT = {"Dvinskii": "LV_LAT.dyneburg", "Drissenskii": "LV_LAT.dyneburg",
             "Rezhitskii": "LV_LAT.rzezyca", "Liutsinskii": "LV_LAT.lucyn", "Kuprovskii": "LV_LAT.lucyn",
             "Nevelskii": "RU_VIT.newel", "Gorodokskii": "RU_VIT.newel", "Sebezhskii": "RU_VIT.siebiez",
             "Velizhskii": "RU_VIT.wieliz",
             "Mstislavskii": "RU_MOH", "Orshanskii": "RU_MOH", "Klimovichskii": "RU_MOH",
             "Goretskii": "RU_MOH", "Gomelskii": "RU_MOH", "Rogachevskii": "RU_MOH"}
MIN_KM2 = 150.0          # smaller pieces outside the 1932 territory are border slivers


def km2(g) -> float:
    return 0.0 if g.is_empty else g.area * 111.2 ** 2 * math.cos(math.radians(g.centroid.y))


def rings(g, nd=4) -> list:
    out = []
    for p in getattr(g, "geoms", [g]):
        if p.geom_type != "Polygon" or p.is_empty:
            continue
        out.append([[[round(x, nd), round(y, nd)] for x, y in p.exterior.coords]]
                   + [[[round(x, nd), round(y, nd)] for x, y in r.coords] for r in p.interiors])
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("boundaries", help="directory with provinces_1897.geojson and districts_1897.geojson")
    a = ap.parse_args(argv)
    with open(os.path.join(a.boundaries, "provinces_1897.geojson"), encoding="utf-8") as fh:
        prov = json.load(fh)
    with open(os.path.join(a.boundaries, "districts_1897.geojson"), encoding="utf-8") as fh:
        dist = json.load(fh)
    govs = {}
    for f in prov["features"]:
        n = f["properties"]["prov_ENG"]
        if n in GOVS:
            govs[GOVS[n][0]] = shape(f["geometry"]).buffer(0).simplify(0.003, preserve_topology=True)
    out = {"source": "RISTAT, Russian Empire Historical GIS Maps (1897), IISG Dataverse hdl:10622/DN9QDM (CC0), "
                     "via github.com/Baushkiner/history_stats; simplified to about 300 m",
           "governorates": [{"code": c, "name": nm, "rings": rings(govs[c])}
                            for c, (_, nm) in sorted(((v[0], v) for v in GOVS.values()), key=lambda t: "VKGMOTS".index(t[0]))]}
    with open(os.path.join(DATA, "governorates_1897.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
    print("governorates:", {c: round(km2(g)) for c, g in govs.items()})

    # the krai's land outside the 1932 territory
    path = os.path.join(DATA, "borders_1932.json")
    with open(path, encoding="utf-8") as fh:
        b = json.load(fh)

    def poly(rl):
        return unary_union([Polygon(r[0], r[1:]) for r in rl]).buffer(0)
    PL, LT, BY = poly(b["PL"]), poly(b["LT"]), poly(b["BY"])
    terr = unary_union([PL, LT, BY])
    krai = unary_union([govs[c] for c in "VKGMOT"])
    rest = krai.difference(terr)
    keep = [p for p in getattr(rest, "geoms", [rest]) if km2(p) >= MIN_KM2]
    XK = unary_union(keep).buffer(0)
    pieces = []
    for f in dist["features"]:
        name = f["properties"]["Name_ENG"]
        if name not in UEZD_UNIT:
            continue
        g = shape(f["geometry"]).buffer(0).intersection(XK)
        if km2(g) >= 20:
            pieces.append({"uezd": name, "unit": UEZD_UNIT[name], "km2": round(km2(g)), "rings": rings(g)})
    b["XK"] = rings(XK)
    b["XK_units"] = pieces
    b["source_XK"] = ("RISTAT 1897 governorates (CC0): the Vilna, Kovno, Grodno, Minsk, Mogilev and Vitebsk "
                      "governorates minus Poland, Lithuania and the BSSR of 1932; pieces under 150 km² dropped")
    shared = BY.boundary.intersection(XK.buffer(0.01))
    b["BY_XK"] = [[[round(x, 4), round(y, 4)] for x, y in ln.coords]
                  for ln in getattr(shared, "geoms", [shared]) if ln.geom_type == "LineString" and len(ln.coords) > 1]
    b.setdefault("outlines", {})
    for key, parts in {"PL+LT+BY": [PL, LT, BY], "PL+LT+BY+XK": [PL, LT, BY, XK], "PL+BY+XK": [PL, BY, XK]}.items():
        u = unary_union([p.buffer(0.002) for p in parts]).buffer(-0.002)
        b["outlines"][key] = [[[round(x, 4), round(y, 4)] for x, y in p.exterior.coords]
                              for p in getattr(u, "geoms", [u]) if km2(p) > 50]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(b, fh, ensure_ascii=False, separators=(",", ":"))
    print("XK:", round(km2(XK)), "km2;", {p["uezd"]: p["km2"] for p in pieces})
    print("bounds:", [round(v, 2) for v in XK.bounds])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
