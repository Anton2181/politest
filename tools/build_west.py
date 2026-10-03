"""German, Danzig and Czechoslovak lands for the scenarios that redraw the
western and southern borders (run by hand; not needed to run the model).

    python tools/build_west.py /path/to/cshapes_2_gw.topojson

Reads CShapes 2.0 (Schvitz et al. 2022; ``cshapes_2_gw.topojson`` from the R
package cshapes 2.0, ``inst/extdata``) and adds to
``plsim/data/borders_1932.json``:

* ``DE``: the German land that Poland held after 1945, i.e. Germany on
  1 January 1932 intersected with Poland of 1946-2019 (Silesia and
  Pomerania east of the Oder and Lusatian Neisse, the Neumark, the
  Grenzmark, Stettin and Swinemünde, southern East Prussia);
* ``DZ``: the Free City of Danzig;
* ``CS``: the Czechoslovak lands of the 1920 plebiscite areas: the
  Czechoslovak part of Cieszyn Silesia (west of the Olza, east of the
  Ostravice: the Fryštát, Český Těšín and Frýdek districts) and of northern
  Spiš and Orava (Zamagurie and Upper Orava). The two outlines are drawn by
  hand to about 3 km on their inner sides (the Ostravice; the Orava,
  Ľubovňa and Tatra edges) and clipped to Czechoslovakia in 1932, so the
  border with Poland is CShapes';
* ``PL1946``: Poland on its post-war borders (for the border change of 1945);
* ``inner``: the borders between these states and Poland, as lines;
* ``outlines``: the outer outline of every combination of states the
  scenarios use.

Needs ``shapely``.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
from shapely.geometry import Polygon
from shapely.ops import linemerge, unary_union

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plsim", "data")

# Hand-drawn outlines (lon, lat) of the Czechoslovak parts of the plebiscite
# areas; the sides facing Poland run past the border and are clipped to it.
TESIN = [(18.27, 49.85), (18.33, 49.90), (18.36, 49.935), (18.42, 49.99), (19.2, 49.99), (19.2, 49.515),
         (18.85, 49.515), (18.75, 49.505), (18.62, 49.49), (18.53, 49.47), (18.46, 49.47), (18.40, 49.53),
         (18.37, 49.60), (18.36, 49.66), (18.33, 49.72), (18.30, 49.78), (18.28, 49.82)]
ORAVA = [(19.30, 49.40), (19.36, 49.52), (19.42, 49.62), (19.60, 49.62), (19.95, 49.45), (19.80, 49.30),
         (19.62, 49.29), (19.48, 49.31), (19.38, 49.33)]
SPIS = [(20.05, 49.22), (20.02, 49.30), (20.10, 49.36), (20.30, 49.45), (20.50, 49.42), (20.56, 49.36),
        (20.52, 49.26), (20.40, 49.20), (20.30, 49.19), (20.15, 49.19)]

COMBOS = ["PL+DE+DZ", "PL+LT+DE+DZ+CS", "PL+DE+DZ+CS", "PL+LT+DE+DZ"]


def topo_polys(t: dict, name: str, date: str):
    arcs = t["arcs"]

    def arc(i):
        return arcs[i] if i >= 0 else arcs[~i][::-1]

    def ring(idx):
        pts = []
        for i in idx:
            a = arc(i)
            pts.extend(a if not pts else a[1:])
        return pts
    for g in t["objects"]["cshapes_2_gw"]["geometries"]:
        p = g["properties"]
        if p["country_name"] == name and p["start"] <= date <= p["end"]:
            parts = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"]
            return unary_union([Polygon(ring(r[0]), [ring(h) for h in r[1:]]).buffer(0) for r in parts])
    raise KeyError((name, date))


def km2(g) -> float:
    return g.area * 111.2 ** 2 * math.cos(math.radians(g.centroid.y))


def rings(g, nd=4, min_km2=1.0) -> list:
    out = []
    for p in getattr(g, "geoms", [g]):
        if p.geom_type != "Polygon" or p.is_empty or km2(p) < min_km2:
            continue
        out.append([[[round(x, nd), round(y, nd)] for x, y in p.exterior.coords]]
                   + [[[round(x, nd), round(y, nd)] for x, y in r.coords] for r in p.interiors])
    return out


def lines(g, nd=4) -> list:
    if g.is_empty:
        return []
    if g.geom_type == "MultiLineString":
        g = linemerge(g)
    parts = list(getattr(g, "geoms", [g]))
    return [[[round(x, nd), round(y, nd)] for x, y in p.coords] for p in parts if p.geom_type == "LineString"
            and p.length > 0.005]


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    t = json.load(open(argv[0]))
    date = "1932-01-01"
    de32 = topo_polys(t, "Germany (Prussia)", date)
    dz = topo_polys(t, "Danzig", date)
    cs32 = topo_polys(t, "Czechoslovakia", date)
    pl46 = topo_polys(t, "Poland", "1946-01-01")
    # the German land held by Poland after 1945 (slivers along the river borders dropped)
    de = de32.intersection(pl46).buffer(0)
    de = unary_union([p for p in getattr(de, "geoms", [de]) if p.geom_type == "Polygon" and km2(p) > 20])
    de = de.simplify(0.002, preserve_topology=True)
    cs = unary_union([Polygon(TESIN), Polygon(ORAVA), Polygon(SPIS)]).intersection(cs32).buffer(0)
    cs = unary_union([p for p in getattr(cs, "geoms", [cs]) if p.geom_type == "Polygon" and km2(p) > 20])
    dz = dz.simplify(0.001, preserve_topology=True)
    path = os.path.join(HERE, "borders_1932.json")
    b = json.load(open(path))
    poly = lambda rl: unary_union([Polygon(r[0], r[1:]) for r in rl]).buffer(0)  # noqa: E731
    PL, LT = poly(b["PL"]), poly(b["LT"])
    b["DE"], b["DZ"], b["CS"] = rings(de), rings(dz), rings(cs)
    b["PL1946"] = rings(pl46.simplify(0.002, preserve_topology=True), min_km2=50)
    states = {"PL": PL, "LT": LT, "DE": poly(b["DE"]), "DZ": poly(b["DZ"]), "CS": poly(b["CS"])}
    inner = {}
    for a, c in [("PL", "DE"), ("PL", "DZ"), ("DE", "DZ"), ("PL", "CS"), ("LT", "DE")]:
        shared = states[a].boundary.intersection(states[c].buffer(0.01))
        ln = lines(shared)
        if ln:
            inner[f"{a}|{c}"] = ln
    b["inner"] = inner
    # coastlines: the parts of the DE and DZ outlines along no other state of 1932
    others = unary_union([de32.difference(states["DE"]).buffer(0), PL, LT, cs32, dz]).buffer(0.01)
    b["coast"]["DE"] = lines(states["DE"].boundary.difference(others))
    b["coast"]["DZ"] = lines(states["DZ"].boundary.difference(
        unary_union([de32, PL]).buffer(0.01)))
    outl = b.setdefault("outlines", {})
    for key in COMBOS:
        u = unary_union([states[s].buffer(0.002) for s in key.split("+")]).buffer(-0.002)
        parts = sorted(getattr(u, "geoms", [u]), key=lambda g: -g.area)
        outl[key] = [[[round(x, 4), round(y, 4)] for x, y in p.exterior.coords] for p in parts if km2(p) > 30]
    b["source_west"] = ("CShapes 2.0: Germany and the Free City of Danzig on 1 Jan 1932; DE = Germany 1932 "
                        "intersected with Poland 1946-2019; CS = Czechoslovakia 1932 within hand-drawn outlines of "
                        "the Czechoslovak parts of the Cieszyn, Spiš and Orava plebiscite areas (tools/build_west.py)")
    with open(path, "w") as fh:
        json.dump(b, fh, separators=(",", ":"))
    for k, g in [("DE", states["DE"]), ("DZ", states["DZ"]), ("CS", states["CS"]), ("PL1946", pl46)]:
        print(k, round(km2(g)), "km2", len(getattr(g, "geoms", [g])), "parts")
    for nm, pg in [("Tesin", TESIN), ("Orava", ORAVA), ("Spis", SPIS)]:
        print(nm, round(km2(Polygon(pg).intersection(cs32))), "km2")
    print({k: len(v) for k, v in inner.items()}, "coast", len(b["coast"]["DE"]), len(b["coast"]["DZ"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
