"""Governorates of 1897, for scenarios drawn on the old imperial borders.

``governorates_1897.json`` (built by ``tools/build_governorates.py`` from the
RISTAT 1897 layer, CC0) holds the seven governorates the scenarios name,
each with a one-letter code:

    V Vilna   K Kovno   G Grodno   M Minsk   O Mogilev   T Vitebsk   S Suwałki

Every other place has the code ``x``.

A scenario's ``governorates`` setting names groups of governorates (for
example the Northwestern Krai: Vilna, Kovno, Grodno, Minsk, Mogilev,
Vitebsk). ``partition`` cuts a county that straddles the edge of a group
into pieces (see ``plsim.partition``). A piece's code is the county's code
plus ``~`` and the letters it covers (``BIA.bialystok~x``; ``LT_KAU.~S`` for
a unit that is not divided into counties); the largest piece covers every
letter the others do not. So the cells of every piece follow from the codes
alone (``data.geography.build_grid``).
"""
from __future__ import annotations

import json
import os

import numpy as np
from matplotlib.path import Path

HERE = os.path.dirname(os.path.abspath(__file__))
LETTERS = "VKGMOTS"
_DATA = None


def _load():
    global _DATA
    if _DATA is None:
        with open(os.path.join(HERE, "governorates_1897.json"), encoding="utf-8") as fh:
            d = json.load(fh)
        _DATA = [(g["code"], g["name"], [[Path(np.asarray(r, float)) for r in poly] for poly in g["rings"]])
                 for g in d["governorates"]]
    return _DATA


NAMES = {"V": "Vilna", "K": "Kovno", "G": "Grodno", "M": "Minsk", "O": "Mogilev", "T": "Vitebsk", "S": "Suwałki"}
CODE_OF = {v: k for k, v in NAMES.items()} | {"Suwalki": "S"}


def letters_of(names) -> str:
    """Canonical letter string of a list of governorate names."""
    return "".join(c for c in LETTERS if c in {CODE_OF[n] for n in names})


def letter(lat, lon) -> np.ndarray:
    """Governorate letter of each place ('x' outside the seven)."""
    lat, lon = np.atleast_1d(np.asarray(lat, float)), np.atleast_1d(np.asarray(lon, float))
    out = np.full(len(lat), "x", dtype="<U1")
    pts = np.column_stack([lon, lat])
    for code, _, polys in _load():
        free = np.where(out == "x")[0]
        if not len(free):
            break
        m = np.zeros(len(free), dtype=bool)
        for rings in polys:
            a = rings[0].contains_points(pts[free])
            for hole in rings[1:]:
                a &= ~hole.contains_points(pts[free])
            m |= a
        out[free[m]] = code
    return out


def piece_letters(groups: dict) -> dict:
    """{group: letters} for a scenario's ``governorates`` setting, plus the
    pseudo-group ``None`` for the rest (every other letter and ``x``)."""
    out = {g: letters_of(names) for g, names in groups.items()}
    used = "".join(out.values())
    out[None] = "".join(c for c in LETTERS if c not in used) + "x"
    return out


def split_code(code: str) -> tuple[str, str]:
    """('BIA.bialystok', 'x') for 'BIA.bialystok~x', ('LT_KAU', 'S') for the
    piece 'LT_KAU.~S' of an undivided unit; (code, '') for a whole unit."""
    base, _, lets = code.partition("~")
    return base.rstrip("."), lets


def piece_code(base: str, lets: str) -> str:
    """Code of the piece of ``base`` covering ``lets`` (a '.' keeps the
    parent of an undivided unit's piece readable as ``code.split('.')[0]``)."""
    return f"{base}~{lets}" if "." in base else f"{base}.~{lets}"
