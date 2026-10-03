"""The north-western governorates outside Poland, Lithuania and the BSSR of 1932.

Scenarios drawn on the governorates of 1897 (``nw_krai``) need the land of
the Vitebsk and Mogilev governorates that lay outside the model's 1932
territory (``include_krai_east``). Its outline is the RISTAT 1897 layer minus
the 1932 states (``tools/build_governorates.py``; key ``XK`` of
``borders_1932.json``). It forms three units:

* ``LV_LAT``, Latgale: the Dvinsk, Rezhitsa and Lyutsin uezds (Latvia from
  1920), with the strip of the Drissa uezd north of the Dvina. Counties
  Dyneburg (Daugavpils), Rzeżyca (Rēzekne), Lucyn (Ludza), on the uezd
  borders.
* ``RU_VIT``: the Nevel, Sebezh and Velizh uezds (and a strip of Gorodok),
  in the RSFSR from 1924. Counties Newel, Siebież, Wieliż.
* ``RU_MOH``: the eastern edge of the Mogilev governorate left in the RSFSR
  (parts of the Mstislavl, Orsha, Klimovichi, Gorki and Gomel uezds).

Data (grade E: estimates built on the 1897 census)
--------------------------------------------------
* **Population.** The 1897 census by uezd (the English Wikipedia uezd
  articles, from the census tables): Dvinsk 237,023; Rezhitsa 136,445;
  Lyutsin 128,155; Nevel 110,394; Sebezh 92,055; Velizh 100,079 (91 % of its
  land is outside the BSSR). The Drissa strip and the Gorodok strip are put
  at 12,000 and 14,000 people, the Mogilev edge at 35 per km² (160,000).
  Growth to the end of 1931: x 1.02 for Latgale, which reaches the 567,000
  of the 1935 Latvian census for all Latgale (27,974 Jews were 4.93 %) with
  the Pytalovo strip of the Pskov governorate; x 1.22 for the Russian lands
  (rural growth of 1897-1926 and to 1931).
* **Home language.** The 1897 native-language shares: Dvinsk 39.0 %
  Latvian, 20.0 Yiddish, 15.3 Russian, 13.8 Belarusian, 9.1 Polish, 1.8
  German; Rezhitsa 57.9 Latvian, 23.9 Russian, 7.4 Yiddish, 5.4 Belarusian,
  4.8 Polish; Lyutsin 64.2 Latvian, 20.5 Belarusian, 7.1 Russian, 4.9
  Yiddish, 2.2 Polish; Nevel 84.0 Belarusian, 7.4 Yiddish, 7.1 Russian;
  Sebezh 47.1 Russian, 47.1 Belarusian, 3.8 Yiddish, 1.5 Polish; Velizh 85.7
  Belarusian, 9.8 Yiddish, 2.5 Latvian, 1.3 Russian. Yiddish is cut to the
  Jewish numbers of the 1930s (Latgale: about 27,000 in the Vitebsk
  part in 1935; the Russian towns lost about 40 % of their Jews by 1926)
  and the other languages are scaled up to fill. The Soviet censuses
  recorded most of the Belarusian speakers of Nevel, Sebezh and Velizh as
  Russians by nationality; the 1897 speech is kept, as in ``data.bssr``.
* **Religion.** Latgalian Latvians are Catholic, Russians Orthodox (with the
  Old Believers), Belarusians Catholic and Orthodox in Latgale and Orthodox
  further east.
* **Other inputs** like those of Soviet Belarus; Latgale a little richer and
  more literate (Latvia's poorest region, but Latvian).
"""
from __future__ import annotations

GROWTH = {"LV_LAT": 1.02, "RU_VIT": 1.22, "RU_MOH": 1.22}

# seat, county name, parent, lat, lon, population 1897, 1897 shares
UNITS = [
    ("Dyneburg", "powiat dyneburski (Daugavpils)", "LV_LAT", 55.87, 26.55, 249_023,
     {"lv": .390, "yi": .200, "ru": .153, "be": .138, "pl": .091, "de": .018, "lt": .004, "oth": .006}),
    ("Rzeżyca", "powiat rzeżycki (Rēzekne)", "LV_LAT", 56.51, 27.33, 136_445,
     {"lv": .579, "ru": .239, "yi": .074, "be": .054, "pl": .048, "de": .004, "lt": .001, "oth": .001}),
    ("Lucyn", "powiat lucyński (Ludza)", "LV_LAT", 56.55, 27.72, 128_155,
     {"lv": .642, "be": .205, "ru": .071, "yi": .049, "pl": .022, "de": .002, "lt": .002, "oth": .007}),
    ("Newel", "powiat newelski", "RU_VIT", 56.02, 29.92, 124_394,
     {"be": .840, "yi": .074, "ru": .071, "pl": .010, "oth": .005}),
    ("Siebież", "powiat siebieski", "RU_VIT", 56.29, 28.48, 92_055,
     {"ru": .471, "be": .471, "yi": .038, "pl": .015, "de": .001, "lt": .001, "oth": .003}),
    ("Wieliż", "powiat wieliski", "RU_VIT", 55.60, 31.20, 91_072,
     {"be": .857, "yi": .098, "lv": .025, "ru": .013, "pl": .003, "de": .001, "oth": .003}),
    ("Chisławicze", "wschodnia Mohylewszczyzna", "RU_MOH", 54.19, 32.16, 160_000,
     {"be": .910, "ru": .040, "yi": .040, "pl": .005, "oth": .005}),
]
# Yiddish speakers in 1931 as a share of the population (the Jewish numbers of the 1930s)
YIDDISH_1931 = {"Dyneburg": .067, "Rzeżyca": .043, "Lucyn": .031, "Newel": .045, "Siebież": .025,
                "Wieliż": .055, "Chisławicze": .025}
CATHOLIC = {  # Catholic share of the speakers of a language, by unit
    "LV_LAT": {"lv": .92, "be": .55, "ru": 0.0}, "RU_VIT": {"lv": .60, "be": .07}, "RU_MOH": {"be": .03}}
HAREDI = .36


def _shares(seat: str) -> dict[str, float]:
    u = next(u for u in UNITS if u[0] == seat)
    sh = dict(u[6])
    yi = YIDDISH_1931[seat]
    rest = 1.0 - sh.get("yi", 0.0)
    out = {k: v * (1.0 - yi) / rest for k, v in sh.items() if k != "yi"}
    out["yi"] = yi
    return out


def unit_groups(seat: str) -> dict[tuple[str, str], float]:
    """Latent (community, language) shares of a unit."""
    u = next(u for u in UNITS if u[0] == seat)
    cat = CATHOLIC[u[2]]
    out: dict[tuple[str, str], float] = {}

    def add(k, v):
        if v > 0:
            out[k] = out.get(k, 0.0) + v
    for lang, v in _shares(seat).items():
        if lang == "yi":
            add(("JH", "yi"), v * HAREDI)
            add(("JW", "yi"), v * (1 - HAREDI))
        elif lang in ("lv", "be"):
            c = cat.get(lang, 0.0)
            add(("RC", lang), v * c)
            add(("PR" if lang == "lv" else "OR", lang), v * (1 - c))
        elif lang == "ru":
            add(("OR", "ru"), v)
        elif lang in ("pl", "lt"):
            add(("RC", lang), v)
        elif lang == "de":
            add(("PR", "de"), v)
        else:
            add(("OT", "oth"), v)
    s = sum(out.values())
    return {k: v / s for k, v in out.items()}


def unit_population(seat: str) -> float:
    u = next(u for u in UNITS if u[0] == seat)
    return u[5] * GROWTH[u[2]]


def unit_languages(seat: str) -> dict[str, float]:
    """Persons by home language at the end of 1931 (county seed, ``data.counties``)."""
    pop = unit_population(seat)
    lang: dict[str, float] = {}
    for (_, l), v in unit_groups(seat).items():
        key = l if l in ("pl", "uk", "yi", "be", "ru", "lt", "de", "lv") else "oth"
        lang[key] = lang.get(key, 0.0) + v * pop
    return {k: round(v) for k, v in lang.items()}


def region_groups(code: str) -> dict[tuple[str, str], float]:
    rows = [u for u in UNITS if u[2] == code]
    tot = sum(unit_population(u[0]) for u in rows)
    out: dict[tuple[str, str], float] = {}
    for u in rows:
        w = unit_population(u[0]) / tot
        for k, v in unit_groups(u[0]).items():
            out[k] = out.get(k, 0.0) + v * w
    return out


def region_population(code: str) -> float:
    return sum(unit_population(u[0]) for u in UNITS if u[2] == code)
