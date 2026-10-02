"""Soviet Belarus (the Byelorussian SSR of December 1926 - September 1939) as
four voivodeships of a Polish state, for scenarios in which Poland holds it
(``include_belarus``).

Premise. The counterfactual has Poland obtain the whole of Soviet Belarus in
1920-21, so the 1931 starting point is the population of the 1926 Soviet
census carried forward under Polish rule.

Data
----
* **Okrugs.** The census of 17 December 1926 by okrug (12 okrugs, 4,983,240
  people): population and the shares of Belarusians, Russians, Jews, Poles
  and Ukrainians (nationality). Read through search summaries of the
  published tables; the okrug populations add up to the census total and
  the national shares (80.6 % Belarusians, 8.2 % Jews, 7.7 % Russians, 2.0 %
  Poles) are reproduced to 0.2 points.
* **Voivodeships.** The okrugs are grouped into four units close to the
  oblasts of 1938: witebskie (Witebsk, Połock, Orsza), mińskie (Mińsk,
  Borysów, Słuck), mohylewskie (Mohylew, Kalinin/Klimowicze, Bobrujsk) and
  homelskie (Homel, Rzeczyca, Mozyrz). The okrugs are their counties
  (grade A in ``data.counties``).
* **Growth to 1931.** x 1.075 (about 1.45 %/yr, the natural increase of the
  Polish north-east in 1927-31; the Soviet republic grew more slowly).

From nationality to home language
---------------------------------
* **Belarusians.** 91 % speak Belarusian at home, 9 % Russian. In 1926,
  93.9 % of rural and 54.1 % of urban Belarusians gave Belarusian as their
  native language.
* **Jews.** 90.7 % Yiddish (1926 native language), the rest Russian.
* **Poles.** 40 % Polish, 55 % Belarusian, 5 % Russian. In 1926 only a
  third (Minsk okrug) to just under half (Vitebsk) of the Poles gave Polish
  as their native language, most of the rest Belarusian.
* **Ukrainians.** 85 % Ukrainian, 15 % Russian.
* **Russians.** Russian, except in Homel and Rzeczyca. These okrugs were
  transferred from the RSFSR a week before the census, and their "Russians"
  (37 % and 26 %) were largely speakers of the local Belarusian dialects
  recorded by identity. Their share falls to under 10 % in the post-war
  censuses of the same lands. Two thirds (Homel) and 70 % (Rzeczyca) of
  them are counted as Belarusian speakers here, a correction of the same
  kind as Tomaszewski's for Poland.
* **Religion.** There was no religion question. Belarusian speakers are
  Orthodox apart from a Catholic minority in the west (10 % in Połock,
  8 % Borysów, 7 % Mińsk, falling to 1 % in the east). Poles are Catholic.
* **Others** (Latvians, Germans, Lithuanians, Tatars, Roma): Latvian
  speakers in the Witebsk and Połock okrugs, "other" elsewhere.

Sources: the 1926 all-Union census (Всесоюзная перепись населения 1926 г.),
via Latysheva, "Perepisi naseleniya 1897 i 1926 gg." (BSU, Istochnik 5) and
Demoscope Weekly; Koryakov (2002) on native language. Okrug centres are
approximate.
"""
from __future__ import annotations

GROWTH_1926_1931 = 1.075

# name, region, centre (lat, lon), population 1926, shares (Belarusians,
# Russians, Jews, Poles, Ukrainians) of the 1926 census
OKRUGS = [
    ("okręg połocki", "Połock", "BY_WIT", 55.45, 28.45, 323_900, (.860, .046, .054, .027, .003)),
    ("okręg witebski", "Witebsk", "BY_WIT", 55.25, 30.05, 583_400, (.779, .092, .092, .017, .001)),
    ("okręg orszański", "Orsza", "BY_WIT", 54.45, 30.30, 416_300, (.885, .033, .059, .015, .001)),
    ("okręg borysowski", "Borysów", "BY_MIN", 54.30, 28.65, 381_300, (.857, .031, .062, .042, .002)),
    ("okręg miński", "Mińsk", "BY_MIN", 53.85, 27.55, 539_700, (.798, .031, .131, .025, .004)),
    ("okręg słucki", "Słuck", "BY_MIN", 52.95, 27.65, 309_400, (.900, .014, .067, .013, .002)),
    ("okręg mohylewski", "Mohylew", "BY_MOH", 53.85, 30.30, 531_000, (.881, .019, .065, .010, .001)),
    ("okręg kaliniński (klimowicki)", "Klimowicze", "BY_MOH", 53.55, 31.55, 375_000, (.924, .017, .051, .002, .001)),
    ("okręg bobrujski", "Bobrujsk", "BY_MOH", 53.05, 29.05, 530_800, (.810, .060, .099, .021, .003)),
    ("okręg homelski", "Homel", "BY_HOM", 52.60, 30.85, 408_100, (.477, .369, .112, .016, .021)),
    ("okręg rzeczycki", "Rzeczyca", "BY_HOM", 52.10, 30.25, 255_000, (.610, .260, .069, .021, .035)),
    ("okręg mozyrski", "Mozyrz", "BY_HOM", 51.85, 28.30, 330_000, (.840, .010, .083, .027, .027)),
]

BE_SPEAK_BE = .91           # Belarusians speaking Belarusian at home (rest Russian)
JW_YIDDISH = .907           # Jews speaking Yiddish (rest Russian)
POLES_LANG = {"pl": .40, "be": .55, "ru": .05}
UK_UKRAINIAN = .85          # Ukrainians speaking Ukrainian (rest Russian)
RU_IS_BE = {"Homel": .65, "Rzeczyca": .70}          # recorded Russians speaking Belarusian
BE_CATHOLIC = {"Połock": .10, "Borysów": .08, "Mińsk": .07, "Witebsk": .05, "Słuck": .04, "Orsza": .03}
BE_CATHOLIC_DEFAULT = .015
LATVIAN_OKRUGS = {"Połock", "Witebsk"}
HAREDI = .36                # as in the formerly Russian voivodeships of Poland


def okrug_groups(seat: str) -> dict[tuple[str, str], float]:
    """Latent (community, language) shares of an okrug."""
    _, _, _, _, _, _, (be, ru, jw, pl, uk) = next(o for o in OKRUGS if o[1] == seat)
    other = max(1.0 - be - ru - jw - pl - uk, 0.0)
    out: dict[tuple[str, str], float] = {}

    def add(k, v):
        if v > 0:
            out[k] = out.get(k, 0.0) + v

    ru_be = ru * RU_IS_BE.get(seat, 0.0)
    be_speakers = be * BE_SPEAK_BE + ru_be
    cat = BE_CATHOLIC.get(seat, BE_CATHOLIC_DEFAULT)
    add(("RC", "be"), be_speakers * cat + pl * POLES_LANG["be"])
    add(("OR", "be"), be_speakers * (1 - cat))
    add(("OR", "ru"), be * (1 - BE_SPEAK_BE) + ru - ru_be + uk * (1 - UK_UKRAINIAN))
    add(("JH", "yi"), jw * JW_YIDDISH * HAREDI)
    add(("JW", "yi"), jw * JW_YIDDISH * (1 - HAREDI))
    add(("JW", "ru"), jw * (1 - JW_YIDDISH))
    add(("RC", "pl"), pl * POLES_LANG["pl"])
    add(("RC", "ru"), pl * POLES_LANG["ru"])
    add(("OR", "uk"), uk * UK_UKRAINIAN)
    if seat in LATVIAN_OKRUGS:
        add(("RC", "lv"), other * .6)
        add(("OT", "oth"), other * .4)
    else:
        add(("PR", "de"), other * .3)
        add(("OT", "oth"), other * .7)
    s = sum(out.values())
    return {k: v / s for k, v in out.items()}


def region_groups(code: str) -> dict[tuple[str, str], float]:
    """Latent (community, language) shares of a voivodeship (population-weighted okrugs)."""
    rows = [o for o in OKRUGS if o[2] == code]
    tot = sum(o[5] for o in rows)
    out: dict[tuple[str, str], float] = {}
    for o in rows:
        for k, v in okrug_groups(o[1]).items():
            out[k] = out.get(k, 0.0) + v * o[5] / tot
    return out


def okrug_languages(seat: str) -> dict[str, float]:
    """Persons by home language at the end of 1931 (county seed, ``data.counties``)."""
    o = next(o for o in OKRUGS if o[1] == seat)
    pop = o[5] * GROWTH_1926_1931
    lang: dict[str, float] = {}
    for (_, l), v in okrug_groups(seat).items():
        key = l if l in ("pl", "uk", "yi", "be", "ru", "lt", "de") else "oth"
        lang[key] = lang.get(key, 0.0) + v * pop
    return {k: round(v) for k, v in lang.items()}


def region_population(code: str) -> float:
    return sum(o[5] for o in OKRUGS if o[2] == code) * GROWTH_1926_1931
