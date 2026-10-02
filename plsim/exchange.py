"""A population exchange along an equal-exchange Curzon line (``plsim.curzon``).

At 1 January of the exchange year every Pole on the other side of the line
moves to the Polish side and every counted non-Pole on the Polish side moves
to the other side, as in the transfers of 1944-46 (Poles and Jews west;
Ukrainians, Belarusians and Lithuanians east), but along the line computed
for that year. The line is drawn so that the two flows are equal.

Who moves follows the count of the line: Poles are the speakers of Polish
at home; non-Poles are the speakers of every other language except
Kashubian, Wymysorys, German and Yiddish; Jews (of any language) do not
move. The plan gives, for every county, the share of its Poles living on
the other side of the line and, language by language, the share of its
counted non-Poles living on the Polish side (from the 3.5 km grid, so a
county the line cuts gives up only the people on the wrong side).

Where they go. Each mover takes the place of someone who left: Poles settle
in the counties (town or country) that the non-Poles vacated, in proportion
to the places vacated; the speakers of each other language settle where the
Poles left, weighted towards the counties where their language is spoken
(Ukrainians to Ukrainian counties, Belarusians to Belarusian ones). Age,
sex, community and bilingualism move with them.
"""
from __future__ import annotations

import numpy as np

from .data.languages import GROUPS, LANG_INDEX, NL

EXCLUDED_LANGS = ("csb", "wym", "de", "yi")
EXCLUDED_COMMUNITIES = ("JW", "JH")
OWN_WEIGHT = 0.05      # floor of the own-language weight of a destination


def mover_groups():
    poles = [g for g, (c, l) in enumerate(GROUPS) if l == "pl" and c not in EXCLUDED_COMMUNITIES]
    others = [g for g, (c, l) in enumerate(GROUPS)
              if l != "pl" and l not in EXCLUDED_LANGS and c not in EXCLUDED_COMMUNITIES]
    return poles, others


def apply_exchange(P: np.ndarray, codes: list[str], plan: dict) -> dict:
    """Move people in ``P`` (R,2,G,B,S,A) in place; return a summary."""
    R = len(codes)
    idx = {c: i for i, c in enumerate(codes)}
    east_pl = np.zeros(R)
    west_oth = np.zeros((R, NL))
    for c, f in plan["east_poles"].items():
        if c in idx:
            east_pl[idx[c]] = f
    for c, d in plan["west_others"].items():
        if c in idx:
            for l, f in d.items():
                west_oth[idx[c], LANG_INDEX[l]] = f
    glang = np.array([LANG_INDEX[l] for _, l in GROUPS])
    pole_g, oth_g = mover_groups()
    west = P[:, :, pole_g] * east_pl[:, None, None, None, None, None]
    east = P[:, :, oth_g] * west_oth[:, glang[oth_g]][:, None, :, None, None, None]
    P[:, :, pole_g] -= west
    P[:, :, oth_g] -= east
    vac_west = east.sum(axis=(2, 3, 4, 5))              # (R,2) places left on the Polish side
    vac_east = west.sum(axis=(2, 3, 4, 5))              # (R,2) places left on the other side
    n_west, n_east = float(west.sum()), float(east.sum())
    if n_west > 0 and vac_west.sum() > 0:
        w = vac_west / vac_west.sum()
        P[:, :, pole_g] += w[:, :, None, None, None, None] * west.sum(axis=(0, 1))[None, None]
    by_lang: dict[str, float] = {}
    if n_east > 0 and vac_east.sum() > 0:
        home = np.zeros(P.shape[:2] + (NL,))
        np.add.at(home, (slice(None), slice(None), glang), P.sum(axis=(3, 4, 5)))
        counted = home[:, :, sorted(set(glang[oth_g]))].sum(axis=2)
        for j, g in enumerate(oth_g):
            m = east[:, :, j].sum(axis=(0, 1))          # (B,S,A)
            if m.sum() <= 0:
                continue
            L = glang[g]
            share = np.where(counted > 0, home[:, :, L] / np.maximum(counted, 1e-12), 0.0)
            w = vac_east * (share + OWN_WEIGHT)
            w /= w.sum()
            P[:, :, g] += w[:, :, None, None, None] * m[None, None]
            code = GROUPS[g][1]
            by_lang[code] = by_lang.get(code, 0.0) + float(m.sum())
    return {"year": int(plan["year"]), "to_polish_side": n_west, "to_other_side": n_east,
            "by_language": by_lang, "lines": plan.get("lines", [])}
