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

from . import bssr, krai_east, west
from .languages import COMMUNITIES, GROUP_INDEX, GROUPS, NG
from .regions import REGIONS, Region

# ---------------------------------------------------------------------------------
# Declared mother tongue, 1931 (Poland) -- census categories
# uk = 'ukraiński', ruth = 'ruski', tut = 'tutejszy', he = 'hebrajski'
# ---------------------------------------------------------------------------------
DECLARED_1931: dict[str, dict[str, float]] = {
    "WAW": {"pl": .707, "yi": .245, "he": .038, "ru": .005, "de": .003, "uk": .001, "other": .001},
    "WAR": {"pl": .880, "yi": .078, "he": .008, "de": .029, "ru": .002, "uk": .001, "other": .002},   # powiat pages
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

# Religion, 1931, voivodeship shares. From the powiat pages of the short results (census1931_strata.csv)
# wherever the pages printing the religion hold 90 % of the voivodeship ("other Christian" counted with the Orthodox in the
# north-east, the Protestants in Volhynia and Polesie, the Catholics elsewhere); the rest, and Warsaw (city and
# voivodeship: a city page is missing), are the earlier approximate shares; each row is scaled to 1.
RELIGION_1931: dict[str, dict[str, float]] = {
    "WAW": {"RC": .655, "GC": .002, "OR": .010, "J": .301, "PR": .025, "OT": .007},
    "WAR": {"RC": .880, "J": .091, "PR": .024, "OR": .004, "OT": .001},
    "LOD": {"RC": .781, "J": .144, "PR": .071, "OR": .003, "OT": .001},
    "KIE": {"RC": .887, "J": .108, "PR": .003, "OR": .001, "OT": .001},
    "LUB": {"RC": .762, "J": .127, "OR": .086, "PR": .015, "GC": .009, "OT": .001},
    "BIA": {"RC": .663, "OR": .210, "J": .117, "PR": .007, "OT": .003},
    "WIL": {"RC": .627, "OR": .278, "J": .087, "OT": .005, "PR": .003},
    "NOW": {"OR": .514, "RC": .402, "J": .078, "PR": .003, "OT": .003},
    "POL": {"OR": .775, "RC": .111, "J": .101, "PR": .008, "OT": .006},
    "WOL": {"OR": .699, "RC": .158, "J": .100, "PR": .040, "OT": .003},      # "other Christian" (sects): PR
    "POZ": {"RC": .896, "PR": .097, "J": .004, "OT": .003},
    "POM": {"RC": .903, "PR": .094, "J": .003},
    "SLA": {"RC": .919, "PR": .059, "J": .016, "OT": .006},
    "KRA": {"RC": .887, "J": .075, "GC": .036, "PR": .002},
    "LWO": {"RC": .462, "GC": .416, "J": .109, "PR": .006, "OR": .004, "OT": .002},
    "STA": {"GC": .730, "RC": .166, "J": .095, "PR": .006, "OT": .003},
    "TAR": {"GC": .544, "RC": .366, "J": .084, "OT": .004, "PR": .003},
}

# ---------------------------------------------------------------------------------
# Lithuania: latent (community, language) shares under the 1923-census reading.
# ---------------------------------------------------------------------------------
def _lt_groups_1923() -> dict[str, dict[tuple[str, str], float]]:
    """Shares of every Lithuanian region from the 1923 census by apskritis
    (``census1923_apskritys.csv``): nationality (by language) with religion.
    Germans and Latvians are taken as Protestant and the other Protestants as
    Lithuanian (the Lutherans of the Prussian border and the Reformed of
    Biržai); Russians as Orthodox or Old Believers; Poles and Belarusians as
    Catholic; Jews as Yiddish speakers. The Klaipėda Territory, not
    enumerated in 1923, keeps its earlier estimate."""
    import csv
    import os
    path = os.path.join(os.path.dirname(__file__), "census1923_apskritys.csv")
    agg: dict[str, dict[str, float]] = {}
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(l for l in fh if not l.startswith("#")):
            a = agg.setdefault(r["county"].split(".")[0], {})
            f = int(r["pop"]) / int(r["citizens"])                   # foreigners take the citizens' mix
            for k in ("lt", "jw", "pl", "ru", "de", "lv", "be", "oth"):
                a[k] = a.get(k, 0.0) + int(r[k]) * f
            a["ev"] = a.get("ev", 0.0) + int(r["r_luth"]) + int(r["r_ref"]) + int(r["r_bapt"])
    out = {}
    for code, a in agg.items():
        pr_lt = min(max(a["ev"] - a["de"] - a["lv"], 0.0), a["lt"])
        g = {("RC", "lt"): a["lt"] - pr_lt, ("PR", "lt"): pr_lt, ("JW", "yi"): a["jw"], ("RC", "pl"): a["pl"],
             ("OR", "ru"): a["ru"], ("PR", "de"): a["de"], ("PR", "lv"): a["lv"], ("RC", "be"): a["be"],
             ("OT", "oth"): a["oth"]}
        tot = sum(g.values())
        out[code] = {k: v / tot for k, v in g.items() if v > 0}
    out["LT_KLA"] = {("PR", "de"): .430, ("PR", "lt"): .250, ("RC", "lt"): .270, ("JW", "yi"): .020,
                     ("OR", "ru"): .010, ("RC", "de"): .010, ("OT", "oth"): .010}
    return out


LT_GROUPS_1923: dict[str, dict[tuple[str, str], float]] = _lt_groups_1923()

# Extra Polish-speakers (share of region population, moved from RC:lt) implied by
# the Polish electoral committee's 1923 claim (~202 k, ~10 % nationally; held
# "very probable" by Buchowski 1999), by the 1897 Kovno-governorate language
# tables (~9 %), and by the historians' middle estimate of ~150 k ("research").
_CLAIM = {"LT_KAU": .060, "LT_LAU": .080, "LT_NEA": .060, "LT_SUV": .015, "LT_ZEM": .015}
LT_EXTRA_POLISH = {
    "polish_claim_1923": _CLAIM,
    "research": {k: v * 0.75 for k, v in _CLAIM.items()},
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
# religion_corrected (Tomaszewski 1985): Greek Catholics and Orthodox are taken
# as Ukrainian / Belarusian by nationality. For home language, 5 % of those
# declared Polish keep Polish (Kubijovyč 1983 counts only 16.4 k Polish-speaking
# Greek Catholics in Galicia in 1939, against ~330 k declared in 1931).
RC_REASSIGN_GC = .95
RC_REASSIGN_OR = .95
# ... and part of the Polish-declared Protestants outside Cieszyn Silesia and
# Warsaw are German speakers: Tomaszewski counts ~780 k Germans against 741 k
# declared German speakers.
PR_REASSIGN_DE = {"POZ": .30, "POM": .30, "LOD": .30, "WOL": .30, "LUB": .30, "WAR": .30, "BIA": .30}
OR_PL_TARGET = {"BIA": "be", "WIL": "be", "NOW": "be", "POL": "uk", "WOL": "uk", "LUB": "uk",
                "WAW": "be", "WAR": "be", "LWO": "uk", "STA": "uk", "TAR": "uk"}
# vernacular (upper bound): share of *rural* RC:pl moved to a minority
# vernacular. North-east: Catholic Belarusian and Lithuanian speech anchored on
# the 1897 imperial census proportions. Galicia and Lublin: Latin-rite
# Ukrainian speakers (latynnyky), calibrated to Kubijovyč (1983): 515 k in
# Galicia on 1 Jan 1939 (~470 k in 1931), and his 5.85 M Ukrainians in Poland.
VERNACULAR_RC_SHIFT = {
    "WIL": {"be": .42, "lt": .08},
    "NOW": {"be": .40},
    "BIA": {"be": .15},
    "LWO": {"uk": .18}, "STA": {"uk": .26}, "TAR": {"uk": .44},
    "LUB": {"uk": .03},
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
    if region.country == "BY":
        return bssr.region_groups(code)          # 1926 Soviet census (see data.bssr)
    if region.country == "XK":
        return krai_east.region_groups(code)     # 1897 census carried to 1931 (see data.krai_east)
    if region.country in ("DE", "DZ", "CS"):
        return west.region_groups(code)          # 1933 German, 1929 Danzig, 1930 Czechoslovak censuses (data.west)
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
            pr_pl = shares.get(("PR", "pl"), 0.0)
            _move(shares, ("PR", "pl"), ("PR", "de"), pr_pl * PR_REASSIGN_DE.get(code, 0.0))
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
REGION_SPECIFIC_ODDS = {("LOD", "de"): 2.2, ("SLA", "de"): 1.8, ("LT_KLA", "de"): 1.5,
                        # the west lands (data.west): Polish, Masurian and Kashubian speech was rural,
                        # the towns German; in Cieszyn Silesia the Germans were townspeople
                        ("DE_OPO", "pl"): 0.45, ("DE_WAR", "pl"): 0.4, ("DE_MAZ", "pl"): 0.35, ("DE_MAR", "pl"): 0.4,
                        ("DE_GRZ", "pl"): 0.5, ("DE_KOS", "pl"): 0.4, ("DE_KOS", "csb"): 0.5, ("DE_WRO", "pl"): 0.6,
                        ("DE_OPO", "cs"): 0.3, ("CS_CIE", "de"): 2.5, ("CS_CIE", "pl"): 0.8, ("CS_SPO", "de"): 3.0}


# census category of each latent language (the census strata are by census category)
CENSUS_CATEGORY = {"pl": "pl", "uk": "uk", "be": "be", "pls": "pls", "yi": "yi", "de": "de", "ru": "ru", "lt": "lt",
                   "csb": "pl", "rue": "uk", "cs": "cs", "lv": "oth", "rom": "pl", "kdr": "oth", "wym": "pl",
                   "oth": "oth"}


# a census religion -> community bin; "other Christian" holds the Old Believers in the north-east, Baptists and
# other sects in Volhynia and Polesie, and the Mariavites elsewhere
RELIGION_BIN = {"rc": "RC", "gc": "GC", "or": "OR", "jw": "J", "ev": "PR"}
OTHER_CHRISTIAN_BIN = {"WIL": "OR", "NOW": "OR", "BIA": "OR", "WOL": "PR", "POL": "PR"}
BIN_COMMUNITIES = {"RC": ("RC",), "GC": ("GC",), "OR": ("OR",), "J": ("JW", "JH"), "PR": ("PR",)}


def census_urban_targets() -> dict:
    """{voivodeship: (urban share, {census language: urban share}, {religion bin: urban share})} from the
    1931 census by powiat and stratum (``data.counties.STRATA``: the towns and cities of every powiat page).
    A religion counts where it is printed for both strata of a powiat. A city whose page is missing (Płock)
    is counted as urban in the total but not in the languages and religions."""
    import csv
    import os
    from .counties import CENSUS_1931, STRATA
    from .regions import REGIONS as _ALL
    pop = {r.code: r.pop_1931 for r in _ALL}
    acc: dict = {}
    for code, st in STRATA.items():
        par = code[:3]
        a = acc.setdefault(par, {"u": 0.0, "t": 0.0, "lu": {}, "lt": {}, "ru": {}, "rt": {}})
        xc = OTHER_CHRISTIAN_BIN.get(par, "RC")
        both = set.intersection(*(v[3] for v in st.values())) if len(st) == 2 else set()
        for name, (p, lang, rel, _) in st.items():
            a["t"] += p
            a["u"] += p if name == "urban" else 0.0
            for k, v in lang.items():
                a["lt"][k] = a["lt"].get(k, 0.0) + v
                if name == "urban":
                    a["lu"][k] = a["lu"].get(k, 0.0) + v
            for k, v in rel.items():
                b = xc if k == "xc" else RELIGION_BIN.get(k)
                if b is None or k not in both:
                    continue
                a["rt"][b] = a["rt"].get(b, 0.0) + v
                if name == "urban":
                    a["ru"][b] = a["ru"].get(b, 0.0) + v
    # a powiat without its city page: its rows count in the total only
    path = os.path.join(os.path.dirname(__file__), "census1931_strata.csv")
    partial = {c for c, v in CENSUS_1931.items() if v[3]}
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(l for l in fh if not l.startswith("#")):
            if r["county"] in partial:
                a = acc[r["county"][:3]]
                a["t"] += int(r["pop"])
                a["u"] += int(r["pop"]) if r["stratum"] != "R" else 0
    out = {}
    for par, a in acc.items():
        missing = max(pop.get(par, a["t"]) - a["t"], 0.0)
        out[par] = ((a["u"] + missing) / (a["t"] + missing),
                    {k: a["lu"].get(k, 0.0) / v for k, v in a["lt"].items() if v >= 200},
                    {k: a["ru"].get(k, 0.0) / v for k, v in a["rt"].items() if v >= 200})
    return out


URBAN_TARGETS_1931 = census_urban_targets()


def _urban_split(code: str, shares: dict, urban_target: float, lang_targets: dict | None = None,
                 rel_targets: dict | None = None) -> dict:
    """Split each group's population into urban/rural so that the regional urban
    share equals ``urban_target``; groups differ by fixed odds ratios. With the
    census strata (``lang_targets`` {census language: urban share},
    ``rel_targets`` {religion bin: urban share}), the odds are first raked, a
    factor per census language and per religion, to give each its census share.
    Languages carved out of a census category (Kashubian, Lemko ...) keep their
    odds relative to the rest of it."""
    if urban_target >= 0.999:
        return {k: (0.0, v) for k, v in shares.items()}
    odds = {}
    for (c, l), v in shares.items():
        o = URBAN_ODDS.get(c, 1.0) * (URBAN_ODDS_LANG.get(l, 1.0) if c not in URBAN_ODDS else 1.0)
        if l == "pl" and c in ("RC", "PR", "OT"):
            o *= EAST_POLISH_URBAN_BOOST.get(code, 1.0)
        o *= REGION_SPECIFIC_ODDS.get((code, l), 1.0)
        odds[(c, l)] = o

    def urban_share(base, keys=None):
        tot = 0.0
        for k in keys if keys is not None else shares:
            q = base * odds[k]
            tot += shares[k] * q / (1 + q)
        return tot

    def solve(target, keys=None):
        lo, hi = 1e-6, 1e6
        for _ in range(100):
            mid = np.sqrt(lo * hi)
            if urban_share(mid, keys) < target:
                lo = mid
            else:
                hi = mid
        return np.sqrt(lo * hi)

    # religions first, languages last: where the two disagree, the languages hold
    margins = [([k for k in shares if k[0] in BIN_COMMUNITIES[b] and shares[k] > 0], u)
               for b, u in (rel_targets or {}).items()]
    margins += [([k for k in shares if CENSUS_CATEGORY.get(k[1], "oth") == cat and shares[k] > 0], u)
                for cat, u in (lang_targets or {}).items()]
    for _ in range(30 if rel_targets else 1):
        for keys, u in margins:
            tot = sum(shares[k] for k in keys)
            if tot > 0 and 0.0 < u < 1.0:
                m = solve(u * tot, keys)
                for k in keys:
                    odds[k] *= m
    base = solve(urban_target)
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
    non_waw = sum(r.pop_1931 * r.urban_1931 for r in pl if r.code != "WAW")
    waw = sum(r.pop_1931 for r in pl if r.code == "WAW")
    k = (NATIONAL_URBAN_PL_1931 * tot_pl - waw) / non_waw if non_waw > 0 else 1.0
    for i, reg in enumerate(regions):
        shares = build_region_shares(reg.code, variant, lt_variant)
        u_target = reg.urban_1931 if (reg.code == "WAW" or reg.country != "PL") else min(reg.urban_1931 * k, 0.95)
        lang_targets = rel_targets = None
        if reg.code in URBAN_TARGETS_1931:      # the census towns and countryside of the voivodeship's powiaty
            u_target, lang_targets, rel_targets = URBAN_TARGETS_1931[reg.code]
        split = _urban_split(reg.code, shares, u_target, lang_targets, rel_targets)
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


# In regions where an East Slavic language is dominant (D = uk or be: autonomies,
# cantons), competence in it.  Close vernaculars understand it well; rural
# Poles of the Kresy commonly spoke the local East Slavic speech, townspeople less.
BILINGUAL_0_EAST: dict[tuple[str, str], tuple[float, float]] = {
    ("OR", "pls"): (.85, .85), ("RC", "pls"): (.80, .80), ("OR", "be"): (.55, .65), ("RC", "be"): (.55, .60),
    ("OR", "uk"): (.55, .65), ("GC", "uk"): (.55, .65), ("RC", "uk"): (.6, .7), ("GC", "rue"): (.75, .80),
    ("OR", "rue"): (.75, .80), ("OR", "ru"): (.60, .75), ("RC", "ru"): (.5, .6), ("OT", "ru"): (.5, .6),
    ("RC", "pl"): (.55, .30), ("GC", "pl"): (.85, .60), ("OR", "pl"): (.85, .60), ("PR", "pl"): (.3, .2),
    ("JW", "pl"): (.30, .25), ("JW", "yi"): (.50, .40), ("JH", "yi"): (.40, .30), ("JW", "ru"): (.5, .5),
    ("PR", "de"): (.30, .30), ("RC", "de"): (.3, .3), ("RC", "cs"): (.55, .55), ("OR", "cs"): (.65, .65),
    ("PR", "cs"): (.5, .5), ("RC", "lt"): (.25, .25), ("RC", "rom"): (.5, .5), ("OT", "kdr"): (.6, .6),
}


# In regions where German or Czech is dominant (the west lands before 1945,
# ``data.west``): competence in it. Upper Silesians, Masurians and Kashubians
# went through German schools and the army; the Goral villages of Orava much
# less through Slovak/Czech ones.
BILINGUAL_0_WEST: dict[tuple[str, str], tuple[float, float]] = {
    ("RC", "pl"): (.80, .92), ("PR", "pl"): (.85, .95), ("RC", "csb"): (.85, .92), ("RC", "cs"): (.75, .90),
    ("PR", "cs"): (.75, .90), ("JW", "de"): (1., 1.), ("JW", "yi"): (.6, .8), ("JH", "yi"): (.4, .5),
    ("RC", "de"): (.7, .9), ("PR", "de"): (.7, .9), ("GC", "rue"): (.6, .7), ("RC", "oth"): (.8, .9),
    ("OT", "oth"): (.6, .8),
}


def bilingual_share(group: tuple[str, str], dominant: str, urban: int) -> float:
    if group[1] == dominant:
        return 1.0
    if dominant in ("de", "cs"):
        rur, urb = BILINGUAL_0_WEST.get(group, (.5, .7))
        return urb if urban else rur
    if dominant in ("uk", "be"):
        rur, urb = BILINGUAL_0_EAST.get(group, (.3, .3))
        return urb if urban else rur
    table = BILINGUAL_0_LT if dominant == "lt" else BILINGUAL_0
    rur, urb = table.get(group, (.4, .7))
    return urb if urban else rur


def group_names() -> list[str]:
    return [f"{c}:{l}" for c, l in GROUPS]


__all__ = [
    "DECLARED_1931", "RELIGION_1931", "InitialComposition", "build_initial_composition",
    "bilingual_share", "build_region_shares", "COMMUNITIES",
]
