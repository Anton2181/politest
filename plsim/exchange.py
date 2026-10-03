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

By declared nationality (``population_exchange: {by: identity}``), as in the
agreements of 1944-46, which went by nationality rather than speech: Poles
are the people of Polish national identity (``plsim.identity``), whatever
their home language; non-Poles are the Ukrainians, Belarusians, Lithuanians,
Russians, "locals", Lemkos and others by identity; Jews, Germans and
Kashubians (by identity) do not move, nor does any Jewish community. A
Polish-identity speaker of Lithuanian (a Lauda gentleman) moves west with
his language; a Lithuanian-identity speaker of Polish moves east with his.
Home language and identity move together (``apply_exchange_identity``).
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


def apply_exchange_identity(P: np.ndarray, I: np.ndarray, codes: list[str], plan: dict) -> dict:
    """The exchange by national identity: move people in ``P`` (R,2,G,B,S,A)
    and their identity in ``I`` (R,2,G,NI) in place; return a summary."""
    from .identity import ID_INDEX, IDENTITIES
    R = len(codes)
    idx = {c: i for i, c in enumerate(codes)}
    NI = len(IDENTITIES)
    pl = ID_INDEX["pl"]
    f_west = np.zeros((R, NI))            # share of each identity to move west (Poles) / east (others)
    for c, f in plan["east_poles"].items():
        if c in idx:
            f_west[idx[c], pl] = f
    f_east = np.zeros((R, NI))
    for c, d in plan["west_others"].items():
        if c in idx:
            for k, f in d.items():
                f_east[idx[c], ID_INDEX[k]] = f
    stay = np.array([c in EXCLUDED_COMMUNITIES for c, _ in GROUPS])          # Jews of any language
    glang = np.array([LANG_INDEX[l] for _, l in GROUPS])
    tot = P.sum(axis=(3, 4, 5))                                               # (R,2,G)

    def take(f):
        mov_i = I * f[:, None, None, :]                                       # (R,2,G,NI)
        mov_i[:, :, stay] = 0.0
        frac = np.where(tot > 0, mov_i.sum(axis=3) / np.maximum(tot, 1e-12), 0.0)
        frac = np.clip(frac, 0.0, 1.0)
        mov_p = P * frac[..., None, None, None]                               # same age-sex mix as the group
        P[...] -= mov_p
        I[...] -= mov_i
        return mov_p, mov_i
    west_p, west_i = take(f_west)
    east_p, east_i = take(f_east)
    vac_west = east_p.sum(axis=(2, 3, 4, 5))            # (R,2) places left on the Polish side
    vac_east = west_p.sum(axis=(2, 3, 4, 5))            # (R,2) places left on the other side
    n_west, n_east = float(west_p.sum()), float(east_p.sum())
    if n_west > 0 and vac_west.sum() > 0:
        w = vac_west / vac_west.sum()
        P += w[:, :, None, None, None, None] * west_p.sum(axis=(0, 1))[None, None]
        I += w[:, :, None, None] * west_i.sum(axis=(0, 1))[None, None]
    by_id: dict[str, float] = {}
    if n_east > 0 and vac_east.sum() > 0:
        home = np.zeros(P.shape[:2] + (NL,))
        np.add.at(home, (slice(None), slice(None), glang), P.sum(axis=(3, 4, 5)))
        counted = home.sum(axis=2)
        mp, mi = east_p.sum(axis=(0, 1)), east_i.sum(axis=(0, 1))               # (G,B,S,A), (G,NI)
        for g in np.where(mp.reshape(len(GROUPS), -1).sum(axis=1) > 0)[0]:
            share = np.where(counted > 0, home[:, :, glang[g]] / np.maximum(counted, 1e-12), 0.0)
            w = vac_east * (share + OWN_WEIGHT)
            w /= w.sum()
            P[:, :, g] += w[:, :, None, None, None] * mp[g][None, None]
            I[:, :, g] += w[:, :, None] * mi[g][None, None]
        for k, ident in enumerate(IDENTITIES):
            if mi[:, k].sum() > 0:
                by_id[ident] = float(mi[:, k].sum())
    np.maximum(I, 0.0, out=I)
    return {"year": int(plan["year"]), "by": "identity", "to_polish_side": n_west, "to_other_side": n_east,
            "by_identity": by_id, "by_language": _by_language(east_p), "west_languages": _by_language(west_p),
            "lines": plan.get("lines", [])}


def _by_language(mov: np.ndarray) -> dict:
    out: dict[str, float] = {}
    for g, (_, l) in enumerate(GROUPS):
        v = float(mov[:, :, g].sum())
        if v > 0:
            out[l] = out.get(l, 0.0) + v
    return out
