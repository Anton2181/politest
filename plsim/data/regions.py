"""Spatial units of the simulation.

Poland is represented at the level of the 17 first-order units of the 1931
census (16 voivodeships + the city of Warsaw), using the *1931* boundaries
(before the April 1938 border adjustments that moved e.g. Bydgoszcz to
Pomorze and Kalisz to Poznań).

Lithuania (the Kaunas state + Klaipėda Territory) is split into six units built
from groups of interwar apskritys.  "Lauda" (LT_LAU) is kept as its own unit
because the Polish-speaking petty gentry of the Liaudė/Lauda country
(Kėdainiai-Panevėžys-Ukmergė-Raseiniai) is one of the populations whose fate
depends most on the counterfactual language regime.

Figures
-------
* ``pop_1931``: Polish units - census of 9 Dec 1931 (GUS, Drugi Powszechny
  Spis Ludności).  Lithuanian units - 1923 Lithuanian census (and 1925
  Klaipėda census) carried forward to end-1931 at ~1.1 %/yr so that the
  national total (~2.38 M) is consistent with the 2.56 M reported for 1938.
* ``area_km2``: 1931 areas (Poland total 388.6 k km²; Lithuania 55.7 k km²).
* ``urban_1931``: legal-urban share.  The national Polish figure (27.4 %) is
  from the census; regional values are approximate reconstructions and are
  rescaled at start-up so that the national total matches.
* ``income_index``: relative income per head vs. the Polish average around
  1929-1931 ("Polska A / Polska B" gradient), reconstructed from interwar
  regional income estimates (approximate; see docs/DATA_SOURCES.md).
* ``tfr_rural`` / ``tfr_urban`` / ``e0_female``: starting fertility and
  mortality levels, set from 1931-32 regional crude rates and the
  religion-specific TFRs reported for 1931 (RC 3.3-3.7, Jewish 2.5-2.9) and
  then calibrated so that national crude rates match 1931-1938 (see
  ``plsim.validate``).
* ``partition``: pre-1914 sovereign (RU = Russian Empire, AT = Austria,
  DE = Prussia/Germany), used for historical-institutional effects
  (schooling, literacy, network density).

Soviet Belarus (``country`` BY) enters only scenarios that set
``include_belarus``: the 1926 BSSR as four voivodeships of a Polish state,
from the 1926 Soviet census grown to 1931 (``data.bssr``). Their areas are
estimates (okrug centres on the 1932 territory); urban shares, incomes,
vital rates and literacy are set like those of the neighbouring Polish
north-east (Wilno, Nowogródek, Polesie).
"""
from __future__ import annotations

from dataclasses import dataclass

from .bssr import region_population as _by_pop


@dataclass(frozen=True)
class Region:
    code: str
    name: str
    country: str          # 'PL', 'LT' or 'BY' (Soviet Belarus, optional)
    partition: str        # 'RU', 'AT', 'DE'
    area_km2: float
    pop_1931: float
    urban_1931: float
    income_index: float
    tfr_rural: float
    tfr_urban: float
    e0_female: float
    literacy_1931: float  # share literate, age 10+
    lat: float
    lon: float
    terrain: str = "flat"  # flat | marsh | hill | mountain (dominant)
    notes: str = ""


REGIONS: list[Region] = [
    # --- Poland (1931 boundaries) -------------------------------------------------
    Region("WAW", "Warszawa (city)", "PL", "RU", 141, 1_171_898, 1.00, 2.20, 1.95, 1.95, 57.5, 0.90, 52.23, 21.01),
    Region("WAR", "warszawskie", "PL", "RU", 31_656, 2_529_228, 0.21, 0.85, 4.10, 2.80, 52.5, 0.78, 52.45, 20.70),
    Region("LOD", "łódzkie", "PL", "RU", 19_034, 2_632_010, 0.43, 1.25, 3.85, 2.25, 53.0, 0.80, 51.70, 19.20),
    Region("KIE", "kieleckie", "PL", "RU", 25_720, 2_935_697, 0.22, 0.90, 4.35, 2.90, 51.5, 0.75, 50.90, 20.30),
    Region("LUB", "lubelskie", "PL", "RU", 31_155, 2_464_923, 0.17, 0.72, 4.70, 3.00, 49.5, 0.70, 51.25, 22.70),
    Region("BIA", "białostockie", "PL", "RU", 32_386, 1_643_844, 0.21, 0.75, 4.35, 3.00, 51.0, 0.72, 53.30, 22.90),
    Region("WIL", "wileńskie", "PL", "RU", 29_011, 1_276_017, 0.21, 0.70, 4.25, 2.50, 50.0, 0.65, 54.80, 26.30, "hill"),
    Region("NOW", "nowogródzkie", "PL", "RU", 22_966, 1_057_147, 0.10, 0.55, 4.60, 3.00, 49.0, 0.58, 53.40, 25.80),
    Region("POL", "poleskie", "PL", "RU", 36_668, 1_131_939, 0.13, 0.48, 5.25, 3.40, 46.5, 0.52, 52.10, 25.80, "marsh"),
    Region("WOL", "wołyńskie", "PL", "RU", 35_754, 2_085_574, 0.13, 0.55, 5.05, 3.20, 47.5, 0.53, 50.80, 25.60),
    Region("POZ", "poznańskie", "PL", "DE", 28_089, 2_106_500, 0.34, 1.40, 3.55, 2.40, 57.0, 0.97, 52.40, 17.20),
    Region("POM", "pomorskie", "PL", "DE", 16_386, 1_080_138, 0.30, 1.35, 3.95, 2.70, 56.0, 0.96, 53.60, 18.40),
    Region("SLA", "śląskie", "PL", "DE", 5_122, 1_295_027, 0.33, 1.90, 3.00, 2.35, 57.5, 0.97, 50.20, 18.90, "hill"),
    Region("KRA", "krakowskie", "PL", "AT", 17_560, 2_297_773, 0.25, 0.90, 3.85, 2.45, 52.5, 0.84, 49.90, 20.30, "hill"),
    Region("LWO", "lwowskie", "PL", "AT", 28_402, 3_126_329, 0.23, 0.88, 3.65, 2.30, 51.0, 0.75, 49.90, 23.20, "hill"),
    Region("STA", "stanisławowskie", "PL", "AT", 16_894, 1_480_285, 0.16, 0.65, 3.95, 2.60, 48.5, 0.65, 48.80, 24.50, "mountain"),
    Region("TAR", "tarnopolskie", "PL", "AT", 16_533, 1_600_406, 0.16, 0.62, 3.65, 2.50, 49.0, 0.68, 49.40, 25.40),
    # --- Lithuania (Kaunas state + Klaipėda Territory) -----------------------------
    Region("LT_KAU", "Kaunas (city & county)", "LT", "RU", 2_900, 265_000, 0.45, 1.15, 3.40, 2.20, 58.0, 0.85, 54.90, 23.95,
           notes="Kaunas city ~115k (1923: 92k; 1939: 152k)"),
    Region("LT_LAU", "Lauda / central Lithuania", "LT", "RU", 12_500, 505_000, 0.10, 0.80, 3.60, 2.40, 56.5, 0.80, 55.45, 24.00,
           notes="Kėdainiai, Panevėžys, Ukmergė, Raseiniai apskritys; Lauda gentry"),
    Region("LT_ZEM", "Samogitia", "LT", "RU", 14_000, 570_000, 0.10, 0.80, 3.65, 2.45, 56.5, 0.78, 55.85, 22.60),
    Region("LT_SUV", "Suvalkija / Dzūkija", "LT", "RU", 11_500, 470_000, 0.08, 0.80, 3.50, 2.35, 57.0, 0.82, 54.60, 23.40),
    Region("LT_NEA", "Northeast Lithuania", "LT", "RU", 12_000, 430_000, 0.07, 0.72, 3.65, 2.40, 56.0, 0.74, 55.75, 25.30,
           notes="Biržai, Rokiškis, Zarasai, Utena, Lithuanian part of Trakai"),
    Region("LT_KLA", "Klaipėda Territory", "LT", "DE", 2_848, 150_000, 0.30, 1.30, 3.00, 2.10, 59.5, 0.95, 55.55, 21.35,
           notes="1925 census 141,645"),
    # --- Soviet Belarus (BSSR of 1926), only with include_belarus ------------------
    Region("BY_WIT", "witebskie", "BY", "RU", 29_140, _by_pop("BY_WIT"), 0.15, 0.62, 4.60, 2.70, 50.5, 0.60, 55.05, 29.60,
           notes="okrugs of Witebsk, Połock, Orsza (1926 census)"),
    Region("BY_MIN", "mińskie", "BY", "RU", 30_160, _by_pop("BY_MIN"), 0.17, 0.66, 4.55, 2.70, 50.5, 0.60, 53.70, 27.90,
           notes="okrugs of Mińsk, Borysów, Słuck (1926 census)"),
    Region("BY_MOH", "mohylewskie", "BY", "RU", 33_030, _by_pop("BY_MOH"), 0.14, 0.56, 4.70, 2.80, 50.0, 0.56, 53.40, 30.30,
           notes="okrugs of Mohylew, Kalinin (Klimowicze), Bobrujsk (1926 census)"),
    Region("BY_HOM", "homelskie", "BY", "RU", 33_480, _by_pop("BY_HOM"), 0.17, 0.58, 4.90, 2.90, 49.0, 0.55, 52.25, 29.70,
           notes="okrugs of Homel, Rzeczyca, Mozyrz (1926 census)"),
]

REGION_INDEX: dict[str, int] = {r.code: i for i, r in enumerate(REGIONS)}

# Historical territorial groupings used by reports and policies.
POLAND_A = ["WAW", "LOD", "POZ", "POM", "SLA", "KRA"]
POLAND_B_EAST = ["WIL", "NOW", "POL", "WOL", "LWO", "STA", "TAR", "BIA", "LUB"]
KRESY = ["WIL", "NOW", "POL", "WOL", "LWO", "STA", "TAR"]
LITHUANIA = [r.code for r in REGIONS if r.country == "LT"]
BELARUS = [r.code for r in REGIONS if r.country == "BY"]
CARPATHIAN = ["KRA", "LWO", "STA"]


def state_of_code(code: str) -> str:
    """1932 state of a region, county or sub-region code: 'PL', 'LT' or 'BY'."""
    return "LT" if code.startswith("LT") else ("BY" if code.startswith("BY_") else "PL")


def select_regions(include_lithuania: bool = True, include_belarus: bool = False) -> list[Region]:
    return [r for r in REGIONS if (include_lithuania or r.country != "LT") and (include_belarus or r.country != "BY")]
