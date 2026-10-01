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


def children(parent: str) -> list[str]:
    spec = SPLITS[parent]
    out = [spec["default"]] + [k for k in spec if k != "default"]
    return sorted(set(out), key=out.index)


def anchor_child(parent: str) -> list[tuple]:
    """(lat, lon, child) for every county seat of the parent voivodeship."""
    spec = SPLITS[parent]
    named = {n: c for c, names in spec.items() if c != "default" for n in names}
    return [(a.lat, a.lon, named.get(a.name, spec["default"])) for a in ANCHORS if a.region == parent]


def assign(parent: str, lat, lon) -> np.ndarray:
    """Sub-region code of each place (nearest county seat of the parent)."""
    anc = anchor_child(parent)
    D = haversine_matrix(np.atleast_1d(np.asarray(lat, float)), np.atleast_1d(np.asarray(lon, float)),
                         np.array([a[0] for a in anc]), np.array([a[1] for a in anc]))
    return np.array([anc[k][2] for k in D.argmin(axis=1)])
