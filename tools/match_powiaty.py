"""Add ``plsim_code`` to a GeoJSON of 1931 county (powiat) polygons, so that
``plsim.data.subregions`` uses the real borders instead of Voronoi cells.

    python tools/match_powiaty.py powiaty.geojson --name-field NAME \\
        --out plsim/data/powiaty_1931.geojson

The polygons must be in longitude/latitude (EPSG:4326). Each feature's name
(e.g. "Tarnopol", "powiat tarnopolski", "Brzeżany") is matched to the
counties of ``plsim.data.counties`` by seat or by county name, ignoring
diacritics, case and the words "powiat"/"pow."; a voivodeship field
(``--voiv-field``, matched to the region names of ``plsim.data.regions``)
resolves seat names that occur in two voivodeships. Unmatched features
are listed and left without a code (their land keeps the Voronoi rule).
Cities with county rights should be merged into their surrounding powiat
first, as in ``data.counties``.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plsim.data.counties import COUNTIES, _slug  # noqa: E402
from plsim.data.regions import REGIONS  # noqa: E402

DROP = ("powiat", "pow", "grodzki", "ziemski")


def key(text: str) -> str:
    words = [w for w in str(text).replace(".", " ").split() if w.lower() not in DROP]
    return _slug(" ".join(words))


def stem(text: str) -> str:
    """'tarnopolski' -> 'tarnopol' (adjectival county names)."""
    k = key(text)
    for suf in ("ski", "cki", "zki"):
        if k.endswith(suf) and len(k) > 5:
            return k[: -len(suf)]
    return k


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("geojson")
    ap.add_argument("--name-field", default="name")
    ap.add_argument("--voiv-field")
    ap.add_argument("--out", default=os.path.join("plsim", "data", "powiaty_1931.geojson"))
    a = ap.parse_args(argv)
    with open(a.geojson, encoding="utf-8") as fh:
        gj = json.load(fh)
    voiv = {_slug(r.name): r.code for r in REGIONS}
    index: dict[str, list] = {}
    for c in COUNTIES:
        for k in {key(c.seat), key(c.name), stem(c.name), stem(c.seat)}:
            index.setdefault(k, []).append(c)
    missing = []
    for f in gj["features"]:
        props = f.setdefault("properties", {})
        name = props.get(a.name_field, "")
        cands = index.get(key(name)) or index.get(stem(name)) or []
        if a.voiv_field and len(cands) > 1:
            par = voiv.get(_slug(str(props.get(a.voiv_field, ""))))
            cands = [c for c in cands if c.parent == par] or cands
        if len({c.code for c in cands}) == 1:
            props["plsim_code"] = cands[0].code
        else:
            missing.append(name)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(gj, fh, ensure_ascii=False)
    print(f"matched {len(gj['features']) - len(missing)} of {len(gj['features'])} features -> {a.out}")
    if missing:
        print("unmatched or ambiguous:", ", ".join(sorted(map(str, missing))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
