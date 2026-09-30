"""Initial population by region x (community, language), with alternative
reconstructions of the "true" 1931 vernacular map.

Why alternatives?
-----------------
The 1931 Polish census asked for *mother tongue* (the 1921 census had asked
for *nationality*).  It is widely regarded as politically shaped:

* the category "tutejszy" (local, 707 k) absorbed most of Polesie;
* "ruski" (Ruthenian, 1.22 M) was offered alongside "ukraiński" (3.22 M),
  splitting the Ukrainian count;
* Orthodox and Greek-Catholic respondents recorded as Polish-speaking
  (clearly visible when language and religion tables are cross-read);
* the head of the census office (E. Szturm de Sztrem) later admitted forms may
  have been altered by the administration, to an unknown extent;
* J. Tomaszewski's religion-based correction lowers the Polish share from
  ~69 % (language) to ~64.7 % (ethnic Poles), with Jews 9.8 % and other
  minorities 25.5 %; V. Kubijovyč's Galician estimates go further, e.g.
  ~360 k Latin-rite Ukrainian speakers (latynnyky) in Podlachia/Chełm/Lublin.

Earlier imperial Russian data point the same way: in the 1897 Russian census
(native language) Vilna governorate was 56 % Belarusian, 17.6 % Lithuanian,
12.7 % Jewish and only 8.2 % Polish, while the overlapping Wilno voivodeship
reported 59.7 % Polish in 1931.  Part of that gap is genuine shift and the
Polish-speaking city of Wilno; part is a change in *what was recorded*
(Catholic Belarusian speakers recorded as Polish by identity).

For Lithuania, the 1923 census found 65,599 Poles (3.2 %) whereas the Polish
electoral committee claimed ~202 k (~10 %) from 1923 election returns; the
1897 census (Kovno governorate) recorded ~9 % Polish speakers.

The simulation therefore carries a latent *home vernacular* and lets the user
choose how to reconstruct it:

``official``            census declarations taken at face value.
``religion_corrected``  Tomaszewski-style: Polish-declared Greek Catholics ->
                        Ukrainian, Polish-declared Orthodox -> Belarusian or
                        Ukrainian (by region).
``vernacular``          ``religion_corrected`` + Catholic Belarusian and
                        Lithuanian vernaculars in the north-east and latynnyky
                        in Galicia/Lublin, anchored on the 1897 imperial
                        census proportions (upper bound for minority speech).

and independently for Lithuania (``lt_variant``):
``census_1923`` | ``polish_claim_1923`` | ``imperial_1897``.

A census *observation model* (``plsim.language.CensusRegime``) maps the latent
state back to what a given census regime would have recorded, so that any
reconstruction can be checked for consistency against the published 1931
figures (see tests/test_census.py).

All shares below are fractions of the region total.  Values are rounded
reconstructions of the published voivodeship tables; they reproduce the
national totals (Polish 68.9 %, Ukr+Ruth 13.9 %, Yiddish 7.8 %, Hebrew 0.8 %,
Belarusian 3.1 %, German 2.3 %, tutejszy 2.2 %, Russian 0.4 %, Lithuanian
0.3 %) to within a few per cent of each category.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .languages import COMMUNITIES, GROUP_INDEX, GROUPS, NG
from .regions import REGIONS, Region

# ---------------------------------------------------------------------------------
# Declared mother tongue, 1931 (Poland) -- census categories
# uk = 'ukraiński', ruth = 'ruski', tut = 'tutejszy', he = 'hebrajski'
# ---------------------------------------------------------------------------------
DECLARED_1931: dict[str, dict[str, float]] = {
    "WAW": {"pl": .707, "yi": .245, "he": .038, "ru": .005, "de": .003, "uk": .001, "other": .001},
    "WAR": {"pl": .889, "yi": .077, "he": .007, "de": .019, "ru": .003, "uk": .001, "other": .004},
    "LOD": {"pl": .797, "yi": .130, "he": .008, "de": .058, "ru": .001, "other": .006},
    "KIE": {"pl": .887, "yi": .097, "he": .008, "de": .004, "ru": .001, "other": .003},
    "LUB": {"pl": .851, "uk": .030, "ruth": .012, "yi": .089, "he": .008, "de": .007, "ru": .002, "be": .001},
    "BIA": {"pl": .719, "be": .125, "ru": .021, "lt": .008, "yi": .114, "he": .005, "de": .005, "uk": .002, "other": .001},
    "WIL": {"pl": .597, "be": .227, "yi": .080, "he": .005, "ru": .032, "lt": .052, "de": .001, "other": .002, "tut": .004},
    "NOW": {"pl": .524, "be": .392, "yi": .069, "he": .002, "ru": .012, "lt": .001},
    "POL": {"pl": .145, "tut": .625, "yi": .096, "he": .004, "uk": .048, "be": .066, "ru": .015, "other": .001},
    "WOL": {"uk": .680, "ruth": .004, "pl": .166, "yi": .084, "he": .015, "de": .022, "cs": .015, "ru": .011,
            "be": .001, "other": .002},
    "POZ": {"pl": .905, "de": .092, "yi": .003},
    "POM": {"pl": .897, "de": .098, "yi": .003, "other": .002},
    "SLA": {"pl": .918, "de": .075, "yi": .005, "other": .002},
    "KRA": {"pl": .913, "uk": .006, "ruth": .020, "yi": .053, "he": .003, "de": .004, "other": .001},
    "LWO": {"pl": .577, "uk": .190, "ruth": .151, "yi": .071, "he": .004, "de": .004, "other": .003},
    "STA": {"uk": .469, "ruth": .219, "pl": .224, "yi": .068, "he": .004, "de": .012, "other": .004},
    "TAR": {"pl": .493, "uk": .251, "ruth": .204, "yi": .045, "he": .004, "de": .002, "other": .001},
}

# Religion, 1931 (approximate voivodeship shares).
RELIGION_1931: dict[str, dict[str, float]] = {
    "WAW": {"RC": .655, "GC": .002, "OR": .010, "J": .301, "PR": .025, "OT": .007},
    "WAR": {"RC": .880, "J": .091, "PR": .024, "OR": .004, "OT": .001},
    "LOD": {"RC": .768, "J": .147, "PR": .081, "OR": .003, "OT": .001},
    "KIE": {"RC": .887, "J": .108, "PR": .003, "OR": .001, "OT": .001},
    "LUB": {"RC": .782, "OR": .087, "J": .106, "PR": .015, "GC": .009, "OT": .001},
    "BIA": {"RC": .652, "OR": .215, "J": .123, "PR": .007, "OT": .003},
    "WIL": {"RC": .615, "OR": .290, "J": .087, "PR": .003, "OT": .005},
    "NOW": {"RC": .399, "OR": .522, "J": .073, "PR": .003, "OT": .003},
    "POL": {"OR": .774, "RC": .112, "J": .100, "PR": .008, "OT": .006},
    "WOL": {"OR": .701, "RC": .159, "J": .099, "PR": .025, "OT": .016},
    "POZ": {"RC": .893, "PR": .100, "J": .004, "OT": .003},
    "POM": {"RC": .893, "PR": .104, "J": .003},
    "SLA": {"RC": .914, "PR": .064, "J": .016, "OT": .006},
    "KRA": {"RC": .889, "GC": .036, "J": .073, "PR": .002},
    "LWO": {"RC": .474, "GC": .386, "J": .128, "PR": .006, "OR": .004, "OT": .002},
    "STA": {"GC": .733, "RC": .163, "J": .095, "PR": .006, "OT": .003},
    "TAR": {"GC": .530, "RC": .379, "J": .084, "PR": .003, "OT": .004},
}

# ---------------------------------------------------------------------------------
# Lithuania: latent (community, language) shares under the 1923-census reading.
# ---------------------------------------------------------------------------------
LT_GROUPS_1923: dict[str, dict[tuple[str, str], float]] = {
    "LT_KAU": {("RC", "lt"): .675, ("JW", "yi"): .150, ("RC", "pl"): .070, ("OR", "ru"): .050,
               ("PR", "de"): .030, ("OT", "pl"): .005, ("RC", "rom"): .002, ("PR", "lt"): .005,
               ("OT", "oth"): .013},
    "LT_LAU": {("RC", "lt"): .855, ("JW", "yi"): .070, ("RC", "pl"): .045, ("OR", "ru"): .020,
               ("PR", "de"): .005, ("PR", "lv"): .002, ("OT", "kdr"): .0001, ("OT", "oth"): .0029},
    "LT_ZEM": {("RC", "lt"): .880, ("JW", "yi"): .065, ("RC", "pl"): .010, ("OR", "ru"): .010,
               ("PR", "de"): .010, ("PR", "lv"): .012, ("PR", "lt"): .010, ("OT", "oth"): .003},
    "LT_SUV": {("RC", "lt"): .860, ("JW", "yi"): .060, ("RC", "pl"): .020, ("OR", "ru"): .010,
               ("PR", "de"): .040, ("RC", "be"): .005, ("RC", "rom"): .002, ("OT", "oth"): .003},
    "LT_NEA": {("RC", "lt"): .780, ("JW", "yi"): .060, ("RC", "pl"): .045, ("OR", "ru"): .060,
               ("PR", "lv"): .020, ("PR", "lt"): .020, ("RC", "be"): .010, ("PR", "de"): .002,
               ("OT", "oth"): .003},
    "LT_KLA": {("PR", "de"): .430, ("PR", "lt"): .250, ("RC", "lt"): .270, ("JW", "yi"): .020,
               ("OR", "ru"): .010, ("RC", "de"): .010, ("OT", "oth"): .010},
}

# Extra Polish-speakers (share of region population, moved from RC:lt) implied by
# the Polish electoral committee's 1923 claim (~202 k, ~10 % nationally) and by
# the 1897 Kovno-governorate language tables (~9 %).
LT_EXTRA_POLISH = {
    "polish_claim_1923": {"LT_KAU": .060, "LT_LAU": .080, "LT_NEA": .060, "LT_SUV": .015, "LT_ZEM": .015},
    "imperial_1897": {"LT_KAU": .050, "LT_LAU": .070, "LT_NEA": .055, "LT_SUV": .012, "LT_ZEM": .012},
}

# ---------------------------------------------------------------------------------
# Estimates for languages not separately enumerated in 1931 (absolute speakers)
# ---------------------------------------------------------------------------------
KASHUBIAN_1931 = {"POM": 200_000}           # estimates range ~150k-500k
LEMKO_1931 = {"KRA": 60_000, "LWO": 55_000}  # 130,121 Lemkos per studies of the 1931 census
LEMKO_ORTHODOX_1931 = {"KRA": 12_000, "LWO": 4_000}  # ~18k Orthodox Lemkos (1935)
WYMYSORYS_1931 = {"KRA": 1_500}             # Wilamowice; 92 % of 1,662 in 1880, 72 % by 1890
KARAIM_1931 = {"WIL": 420, "WOL": 50, "STA": 110, "LT_LAU": 50}  # community 800-900 souls
ROMANI_1931 = {"KRA": 6000, "LWO": 5000, "STA": 2000, "TAR": 1000, "WAR": 3000, "LOD": 2000,
               "KIE": 3000, "LUB": 2000, "BIA": 1000, "WIL": 1000, "NOW": 1000, "POL": 500,
               "WOL": 1500, "POZ": 500, "POM": 300, "SLA": 500, "WAW": 500,
               "LT_SUV": 600, "LT_KAU": 400, "LT_ZEM": 300}

# Share of Belarusian speakers who are Catholic (rest Orthodox).
BE_CATHOLIC_SHARE = {"WIL": .15, "NOW": .05, "BIA": .10, "POL": .05, "LUB": .50}
# Share of Ukrainian (+Ruthenian) speakers who are Greek Catholic (rest Orthodox).
UK_GC_SHARE = {"KRA": 1.0, "LWO": .995, "STA": .998, "TAR": .995, "LUB": .25, "WAW": .5, "WAR": .5}
# Community of German speakers.
DE_RC_SHARE = {"SLA": .75, "POZ": .12, "POM": .12, "KRA": .5, "LWO": .3, "STA": .3, "TAR": .3}
# Share of Yiddish speakers belonging to Haredi/Hasidic-traditionalist milieus.
HAREDI_SHARE = {"WAW": .25, "RU": .36, "AT": .40, "DE": .10, "LT": .22}

# Variant parameters -------------------------------------------------------------
# religion_corrected: share of Polish-declared GC / Orthodox reassigned.
RC_REASSIGN_GC = .80
RC_REASSIGN_OR = .85
OR_PL_TARGET = {"BIA": "be", "WIL": "be", "NOW": "be", "POL": "uk", "WOL": "uk", "LUB": "uk",
                "WAW": "be", "WAR": "be", "LWO": "uk", "STA": "uk", "TAR": "uk"}
# vernacular: share of *rural* RC:pl moved to a minority vernacular.
VERNACULAR_RC_SHIFT = {
    "WIL": {"be": .42, "lt": .08},
    "NOW": {"be": .40},
    "BIA": {"be": .15},
    "LWO": {"uk": .08}, "STA": {"uk": .12}, "TAR": {"uk": .12},
    "LUB": {"uk": .05},
}


@dataclass
class InitialComposition:
    """Population by region x group x urban/rural (absolute persons)."""

    regions: list[Region]
    pop: np.ndarray          # (R, 2, G)   u=0 rural, u=1 urban
    variant: str
    lt_variant: str


def _declared_to_groups(code: str) -> dict[tuple[str, str], float]:
    """Cross-read declared language with religion to get (community, language)
    shares under the official reading."""
    d = dict(DECLARED_1931[code])
    rel = dict(RELIGION_1931[code])
    region = next(r for r in REGIONS if r.code == code)
    out: dict[tuple[str, str], float] = {}

    def add(key, v):
        if v > 0:
            out[key] = out.get(key, 0.0) + v

    # Jews: Yiddish & Hebrew declarants.  Remainder of religion 'J' -> Polish speakers.
    yid = d.get("yi", 0) + d.get("he", 0)
    jw_rest = max(rel.get("J", 0) - yid, 0.0)
    part = region.partition if code != "WAW" else "WAW"
    h = HAREDI_SHARE.get(part, HAREDI_SHARE.get(region.partition, .3))
    add(("JH", "yi"), yid * h)
    add(("JW", "yi"), yid * (1 - h))
    add(("JW", "pl"), jw_rest)

    # Germans.
    de = d.get("de", 0)
    rc_share = DE_RC_SHARE.get(code, .10)
    add(("RC", "de"), de * rc_share)
    add(("PR", "de"), de * (1 - rc_share))
    pr_rest = max(rel.get("PR", 0) - de * (1 - rc_share), 0.0)
    add(("PR", "pl"), pr_rest)

    # Ukrainian + Ruthenian.
    ukr = d.get("uk", 0) + d.get("ruth", 0)
    gc_share = UK_GC_SHARE.get(code, 0.0)
    add(("GC", "uk"), ukr * gc_share)
    add(("OR", "uk"), ukr * (1 - gc_share))
    gc_rest = max(rel.get("GC", 0) - ukr * gc_share, 0.0)
    add(("GC", "pl"), gc_rest)

    # Russian, Belarusian, tutejszy -> Orthodox capacity.
    add(("OR", "ru"), d.get("ru", 0))
    be = d.get("be", 0)
    be_rc = BE_CATHOLIC_SHARE.get(code, .10)
    add(("RC", "be"), be * be_rc)
    add(("OR", "be"), be * (1 - be_rc))
    tut = d.get("tut", 0)
    add(("RC", "pls"), tut * .02)
    add(("OR", "pls"), tut * .98)
    or_used = d.get("ru", 0) + be * (1 - be_rc) + tut * .98 + ukr * (1 - gc_share)
    # Czechs in Volhynia: part Orthodox.
    cs = d.get("cs", 0)
    add(("RC", "cs"), cs * .55)
    add(("OR", "cs"), cs * .35)
    add(("PR", "cs"), cs * .10)
    or_used += cs * .35
    or_rest = max(rel.get("OR", 0) - or_used, 0.0)
    add(("OR", "pl"), or_rest)

    add(("RC", "lt"), d.get("lt", 0))
    oth = d.get("other", 0)
    ot_rel = rel.get("OT", 0)
    add(("OT", "oth"), min(oth, ot_rel) * .5)
    add(("OT", "pl"), max(ot_rel - min(oth, ot_rel) * .5, 0.0))
    add(("RC", "oth"), max(oth - min(oth, ot_rel) * .5, 0.0))

    # Polish remainder -> Catholic.
    pl_other = sum(v for (c, l), v in out.items() if l == "pl")
    add(("RC", "pl"), max(d.get("pl", 0) - pl_other, 0.0))
    tot = sum(out.values())
    return {k: v / tot for k, v in out.items()}


def _move(shares: dict, src: tuple[str, str], dst: tuple[str, str], amount: float) -> None:
    amount = min(amount, shares.get(src, 0.0))
    if amount <= 0:
        return
    shares[src] -= amount
    shares[dst] = shares.get(dst, 0.0) + amount


def _carve(shares: dict, src: tuple[str, str], dst: tuple[str, str], persons: float, total: float) -> None:
    _move(shares, src, dst, persons / total)


def build_region_shares(code: str, variant: str, lt_variant: str) -> dict[tuple[str, str], float]:
    region = next(r for r in REGIONS if r.code == code)
    if region.country == "LT":
        shares = dict(LT_GROUPS_1923[code])
        if lt_variant in LT_EXTRA_POLISH:
            _move(shares, ("RC", "lt"), ("RC", "pl"), LT_EXTRA_POLISH[lt_variant].get(code, 0.0))
        if lt_variant == "imperial_1897" and code == "LT_NEA":
            _move(shares, ("RC", "lt"), ("RC", "be"), .02)
    else:
        shares = _declared_to_groups(code)
        total = region.pop_1931
        if variant in ("religion_corrected", "vernacular"):
            gc_pl = shares.get(("GC", "pl"), 0.0)
            _move(shares, ("GC", "pl"), ("GC", "uk"), gc_pl * RC_REASSIGN_GC)
            or_pl = shares.get(("OR", "pl"), 0.0)
            tgt = OR_PL_TARGET.get(code, "be")
            _move(shares, ("OR", "pl"), ("OR", tgt), or_pl * RC_REASSIGN_OR)
        if variant == "vernacular":
            for lang, frac in VERNACULAR_RC_SHIFT.get(code, {}).items():
                # applied to the rural Catholic Polish-declared population:
                # approximated as (1 - urban share) of RC:pl
                rc_pl = shares.get(("RC", "pl"), 0.0)
                _move(shares, ("RC", "pl"), ("RC", lang), rc_pl * (1 - region.urban_1931) * frac)
        elif variant not in ("official", "religion_corrected"):
            raise ValueError(f"unknown census variant {variant!r}")
        # Carve-outs of unenumerated languages.
        _carve(shares, ("RC", "pl"), ("RC", "csb"), KASHUBIAN_1931.get(code, 0), total)
        _carve(shares, ("GC", "uk"), ("GC", "rue"), LEMKO_1931.get(code, 0), total)
        _carve(shares, ("GC", "uk"), ("OR", "rue"), LEMKO_ORTHODOX_1931.get(code, 0), total)
        _carve(shares, ("RC", "pl"), ("RC", "wym"), WYMYSORYS_1931.get(code, 0), total)
    total = region.pop_1931
    kd = KARAIM_1931.get(code, 0)
    if kd:
        src = ("OT", "oth") if shares.get(("OT", "oth"), 0) * total >= kd else ("OT", "pl")
        if shares.get(src, 0) * total < kd:
            src = ("RC", "pl") if region.country == "PL" else ("RC", "lt")
        _carve(shares, src, ("OT", "kdr"), kd, total)
    rom = ROMANI_1931.get(code, 0)
    if rom:
        src = ("RC", "pl") if region.country == "PL" else ("RC", "lt")
        _carve(shares, src, ("RC", "rom"), rom, total)
    shares = {k: v for k, v in shares.items() if v > 1e-9}
    s = sum(shares.values())
    return {k: v / s for k, v in shares.items()}


# Relative odds of urban residence by (community, language).
URBAN_ODDS = {
    "JW": 22.0, "JH": 12.0,
}
URBAN_ODDS_LANG = {
    "pl": 1.0, "de": 0.9, "ru": 1.5, "lt": 0.6, "uk": 0.25, "be": 0.2, "pls": 0.12, "rue": 0.1,
    "csb": 0.35, "cs": 0.25, "lv": 0.4, "rom": 1.0, "kdr": 4.0, "wym": 0.6, "oth": 2.0, "yi": 1.0,
}
# In the eastern voivodeships Polish-speakers (officials, gentry, townspeople) were
# markedly more urban than the Orthodox/Greek-Catholic peasantry.
EAST_POLISH_URBAN_BOOST = {"WIL": 1.8, "NOW": 2.2, "POL": 3.0, "WOL": 2.5, "LWO": 1.5, "STA": 2.0,
                           "TAR": 1.4, "BIA": 1.3, "LUB": 1.2}
REGION_SPECIFIC_ODDS = {("LOD", "de"): 2.2, ("SLA", "de"): 1.8, ("LT_KLA", "de"): 1.5}


def _urban_split(code: str, shares: dict, urban_target: float) -> dict:
    """Split each group's population into urban/rural so that the regional urban
    share equals ``urban_target``; groups differ by fixed odds ratios."""
    if urban_target >= 0.999:
        return {k: (0.0, v) for k, v in shares.items()}
    odds = {}
    for (c, l), v in shares.items():
        o = URBAN_ODDS.get(c, 1.0) * (URBAN_ODDS_LANG.get(l, 1.0) if c not in URBAN_ODDS else 1.0)
        if l == "pl" and c in ("RC", "PR", "OT"):
            o *= EAST_POLISH_URBAN_BOOST.get(code, 1.0)
        o *= REGION_SPECIFIC_ODDS.get((code, l), 1.0)
        odds[(c, l)] = o

    def urban_share(base):
        tot = 0.0
        for k, v in shares.items():
            q = base * odds[k]
            tot += v * q / (1 + q)
        return tot

    lo, hi = 1e-6, 1e3
    for _ in range(100):
        mid = np.sqrt(lo * hi)
        if urban_share(mid) < urban_target:
            lo = mid
        else:
            hi = mid
    base = np.sqrt(lo * hi)
    out = {}
    for k, v in shares.items():
        q = base * odds[k]
        u = q / (1 + q)
        out[k] = (v * (1 - u), v * u)
    return out


NATIONAL_URBAN_PL_1931 = 0.274


def build_initial_composition(regions: list[Region], variant: str = "official",
                              lt_variant: str = "census_1923",
                              scale_overrides: dict | None = None) -> InitialComposition:
    """Return absolute population by region x urban x group."""
    R = len(regions)
    pop = np.zeros((R, 2, NG))
    # Rescale regional urban shares so the Polish total matches the census 27.4 %.
    pl = [r for r in regions if r.country == "PL"]
    tot_pl = sum(r.pop_1931 for r in pl)
    raw_urban = sum(r.pop_1931 * r.urban_1931 for r in pl)
    non_waw = sum(r.pop_1931 * r.urban_1931 for r in pl if r.code != "WAW")
    waw = sum(r.pop_1931 for r in pl if r.code == "WAW")
    k = (NATIONAL_URBAN_PL_1931 * tot_pl - waw) / non_waw if non_waw > 0 else 1.0
    for i, reg in enumerate(regions):
        shares = build_region_shares(reg.code, variant, lt_variant)
        u_target = reg.urban_1931 if (reg.code == "WAW" or reg.country == "LT") else min(reg.urban_1931 * k, 0.95)
        split = _urban_split(reg.code, shares, u_target)
        total = reg.pop_1931 * (scale_overrides or {}).get(reg.code, 1.0)
        for grp, (rur, urb) in split.items():
            g = GROUP_INDEX[grp]
            pop[i, 0, g] += rur * total
            pop[i, 1, g] += urb * total
    return InitialComposition(regions=regions, pop=pop, variant=variant, lt_variant=lt_variant)


# ---------------------------------------------------------------------------------
# Initial competence in the regional dominant language (bilingual share) by
# (community, language): (rural, urban).  Age profile applied in the model.
# ---------------------------------------------------------------------------------
BILINGUAL_0: dict[tuple[str, str], tuple[float, float]] = {
    ("RC", "be"): (.55, .80), ("OR", "be"): (.28, .70), ("OR", "uk"): (.22, .65),
    ("GC", "uk"): (.38, .80), ("GC", "rue"): (.35, .70), ("OR", "rue"): (.30, .60),
    ("OR", "pls"): (.18, .60), ("RC", "pls"): (.50, .80), ("JW", "yi"): (.65, .85),
    ("JH", "yi"): (.35, .55), ("JW", "de"): (.80, .90), ("JW", "ru"): (.60, .80),
    ("PR", "de"): (.45, .75), ("RC", "de"): (.75, .90), ("OR", "ru"): (.45, .70),
    ("RC", "ru"): (.60, .80), ("RC", "lt"): (.45, .80), ("RC", "csb"): (.85, .95),
    ("RC", "cs"): (.60, .80), ("OR", "cs"): (.50, .70), ("PR", "cs"): (.5, .7),
    ("RC", "rom"): (.60, .80), ("RC", "wym"): (.90, .95), ("OT", "kdr"): (.90, .95),
    ("OT", "oth"): (.50, .80), ("RC", "oth"): (.5, .8), ("PR", "lv"): (.60, .80),
    ("PR", "lt"): (.9, .95), ("RC", "uk"): (.7, .9), ("GC", "pl"): (1., 1.), ("OR", "pl"): (1., 1.),
    ("OT", "be"): (.7, .9), ("OT", "ru"): (.6, .8),
}
# In Lithuanian-dominant regions (D = lt), competence in Lithuanian.
BILINGUAL_0_LT: dict[tuple[str, str], tuple[float, float]] = {
    ("RC", "pl"): (.55, .60), ("JW", "yi"): (.40, .55), ("JH", "yi"): (.25, .35),
    ("OR", "ru"): (.45, .55), ("PR", "de"): (.50, .55), ("RC", "de"): (.5, .6),
    ("PR", "lv"): (.6, .7), ("RC", "be"): (.6, .7), ("RC", "rom"): (.6, .7),
    ("OT", "oth"): (.5, .6), ("OT", "kdr"): (.8, .9), ("OT", "pl"): (.5, .6), ("JW", "pl"): (.5, .6),
}


def bilingual_share(group: tuple[str, str], dominant: str, urban: int) -> float:
    if group[1] == dominant:
        return 1.0
    table = BILINGUAL_0_LT if dominant == "lt" else BILINGUAL_0
    rur, urb = table.get(group, (.4, .7))
    return urb if urban else rur


def group_names() -> list[str]:
    return [f"{c}:{l}" for c, l in GROUPS]


__all__ = [
    "DECLARED_1931", "RELIGION_1931", "InitialComposition", "build_initial_composition",
    "bilingual_share", "build_region_shares", "COMMUNITIES",
]
