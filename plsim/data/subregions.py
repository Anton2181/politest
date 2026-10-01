"""Sub-regions: splitting voivodeships along county lines.

Some scenarios need units smaller than a voivodeship: an autonomy, a canton
or the later Curzon line can cut through one.  A split is defined by lists
of county seats (the anchors of ``data.geography``).  Every place is assigned
to the sub-region of its nearest county seat in the parent voivodeship, a
Voronoi approximation of the county borders.

Sub-region codes are ``PARENT.CHILD``.  Settings given for the parent apply
to the children unless overridden (``params.region_lookup``).

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

import numpy as np

from .geography import ANCHORS, haversine_matrix

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


def assign(parent: str, lat, lon, child_codes=None) -> np.ndarray:
    """Sub-region code of each place (nearest seat; weighted by county area
    when the county table provides areas)."""
    anc = seat_table(parent, child_codes)
    D = haversine_matrix(np.atleast_1d(np.asarray(lat, float)), np.atleast_1d(np.asarray(lon, float)),
                         np.array([a[0] for a in anc]), np.array([a[1] for a in anc]))
    return np.array([anc[k][2] for k in D.argmin(axis=1)])
