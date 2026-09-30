"""Languages, confessional communities and the (community, language) groups.

The simulation separates two things that the interwar censuses conflated:

* **community** (``c``): an ethno-confessional community which governs
  fertility, mortality, emigration channels and the *direction* in which a
  vernacular is likely to shift (e.g. Catholic Belarusian-speakers are pulled
  towards Polish, Orthodox ones towards Russian/Belarusian);
* **home language** (``l``): the vernacular actually transmitted to children.

A population group is a pair ``(c, l)``.  Each group additionally carries a
binary competence flag ``b`` (1 = also speaks the region's dominant/state
language), which is the intermediate bilingual state of Minett & Wang (2008)
and Kandler, Unger & Steele (2010).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Language:
    code: str
    name: str
    family: str
    notes: str = ""


LANGUAGES: list[Language] = [
    Language("pl", "Polish", "West Slavic"),
    Language("uk", "Ukrainian", "East Slavic", "incl. the 1931 census category 'ruski' (Ruthenian) except Lemkos"),
    Language("be", "Belarusian", "East Slavic"),
    Language("pls", "West Polesian ('tutejszy')", "East Slavic",
             "vernacular of the 1931 'local' declarants, a Ukrainian-Belarusian transitional dialect continuum"),
    Language("yi", "Yiddish", "Germanic", "incl. 1931 'Hebrew' declarants (identity declaration, mostly Yiddish-speaking)"),
    Language("de", "German", "West Germanic"),
    Language("ru", "Russian", "East Slavic", "incl. Old Believers"),
    Language("lt", "Lithuanian", "Baltic", "incl. Samogitian and Prussian-Lithuanian (Memelländisch) vernaculars"),
    Language("csb", "Kashubian", "West Slavic", "counted as Polish by the 1931 census; carved out by estimate"),
    Language("rue", "Lemko-Rusyn", "East Slavic", "Lemkos, carved out of the census 'ruski'/'ukraiński' categories"),
    Language("cs", "Czech", "West Slavic", "Volhynian Czechs"),
    Language("lv", "Latvian", "Baltic"),
    Language("rom", "Romani", "Indo-Aryan", "not enumerated in 1931; estimate"),
    Language("kdr", "Karaim", "Turkic (Kipchak)", "Trakai/Łuck/Halicz Karaites; <1,000 speakers"),
    Language("wym", "Wymysorys", "West Germanic", "Wilamowice enclave; ~1,500 speakers"),
    Language("oth", "Other", "-"),
]
LANG_INDEX: dict[str, int] = {l.code: i for i, l in enumerate(LANGUAGES)}
NL = len(LANGUAGES)


@dataclass(frozen=True)
class Community:
    code: str
    name: str


COMMUNITIES: list[Community] = [
    Community("RC", "Roman (Latin) Catholic"),
    Community("GC", "Greek Catholic"),
    Community("OR", "Orthodox (incl. Old Believers)"),
    Community("JW", "Jewish (acculturating / non-Haredi)"),
    Community("JH", "Jewish (Haredi / Hasidic-traditionalist)"),
    Community("PR", "Protestant"),
    Community("OT", "Other (Karaite, Muslim-Tatar, Armenian, ...)"),
]
COMM_INDEX: dict[str, int] = {c.code: i for i, c in enumerate(COMMUNITIES)}
NC = len(COMMUNITIES)

# ---------------------------------------------------------------------------------
# Shift targets: T(c, l) = languages that children of (c, l) parents can be raised
# in instead of l.  Targets not present locally get zero attraction automatically.
# Region-specific dominant languages (Polish / Lithuanian) are always admissible.
# ---------------------------------------------------------------------------------
SHIFT_TARGETS: dict[tuple[str, str], tuple[str, ...]] = {
    ("RC", "pl"): ("lt", "be"),
    ("RC", "be"): ("pl", "lt", "ru"),
    ("RC", "lt"): ("pl",),
    ("RC", "de"): ("pl", "lt"),
    ("RC", "csb"): ("pl",),
    ("RC", "cs"): ("pl", "uk"),
    ("RC", "uk"): ("pl",),
    ("RC", "wym"): ("pl", "de"),
    ("RC", "rom"): ("pl", "lt"),
    ("RC", "pls"): ("pl", "be"),
    ("RC", "ru"): ("pl", "lt"),
    ("RC", "lv"): ("lt",),
    ("GC", "uk"): ("pl",),
    ("GC", "rue"): ("uk", "pl"),
    ("GC", "pl"): ("uk",),
    ("OR", "uk"): ("pl", "ru"),
    ("OR", "be"): ("pl", "ru"),
    ("OR", "pls"): ("uk", "be", "pl", "ru"),
    ("OR", "ru"): ("pl", "lt"),
    ("OR", "pl"): ("be", "uk"),
    ("OR", "rue"): ("uk", "pl"),
    ("OR", "cs"): ("uk", "pl"),
    ("JW", "yi"): ("pl", "lt", "ru", "de"),
    ("JW", "de"): ("pl",),
    ("JW", "ru"): ("pl", "lt"),
    ("JW", "lt"): ("pl",),
    ("JW", "pl"): (),
    ("JH", "yi"): ("pl",),
    ("JH", "pl"): (),
    ("PR", "de"): ("pl", "lt"),
    ("PR", "pl"): ("de",),
    ("PR", "lt"): ("de",),
    ("PR", "lv"): ("lt",),
    ("PR", "cs"): ("pl",),
    ("OT", "kdr"): ("pl", "ru", "lt"),
    ("OT", "pl"): (),
    ("OT", "ru"): ("pl",),
    ("OT", "be"): ("pl",),
    ("OT", "oth"): ("pl", "lt"),
    ("RC", "oth"): ("pl", "lt"),
}


def build_groups() -> list[tuple[str, str]]:
    """All (community, language) pairs reachable from the shift graph."""
    groups: set[tuple[str, str]] = set(SHIFT_TARGETS)
    for (c, _l), targets in SHIFT_TARGETS.items():
        for t in targets:
            groups.add((c, t))
    # The dominant languages must exist for every community (children of
    # bilingual parents can always be raised in the state language).
    for c in [x.code for x in COMMUNITIES]:
        groups.add((c, "pl"))
        if c not in ("JH",):
            groups.add((c, "lt"))
    order_c = {c.code: i for i, c in enumerate(COMMUNITIES)}
    return sorted(groups, key=lambda g: (order_c[g[0]], LANG_INDEX[g[1]]))


GROUPS: list[tuple[str, str]] = build_groups()
GROUP_INDEX: dict[tuple[str, str], int] = {g: i for i, g in enumerate(GROUPS)}
NG = len(GROUPS)
GROUP_COMM = [COMM_INDEX[c] for c, _ in GROUPS]
GROUP_LANG = [LANG_INDEX[l] for _, l in GROUPS]


def group_label(g: int) -> str:
    c, l = GROUPS[g]
    return f"{c}:{l}"


# Small / endangered languages tracked for extinction diagnostics.
ENDANGERED = ["pls", "csb", "rue", "kdr", "wym", "rom", "cs", "lv", "be", "yi"]
