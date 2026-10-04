"""Counties (powiaty, 1931; Lithuanian apskritys, 1923) for county-level runs.

Sources and grades
------------------
* **A**: 1931 census, population and declared mother tongue by powiat.
  * Read from the census volumes themselves (``census1931_powiaty.csv``,
    loaded at the end of this module): Tabl. 12 of the voivodeship volumes
    of Statystyka Polski seria C for Łódź, Kielce, Kraków, Poznań, Silesia
    and Pomorze, and the powiat pages of the short results (GUS, MBC
    edition 14481) for the Warsaw voivodeship, Lublin, Nowogródek and
    Polesie and the three large cities. Every row adds up to its printed
    total, and each voivodeship read whole reproduces its census population.
    The short results also give religion, and for Nowogródek and Polesie
    they separate Belarusian, "tutejszy", Russian and Ukrainian.
  * Every powiat, by stratum (``census1931_strata.csv``, ``STRATA``): the
    towns and the countryside of each powiat page of the short results, by
    religion and mother tongue, and the cities with their own page. They
    give the urban/rural split and the religions of every county, and the
    mother tongue of Tarnopol, Stanisławów, Lwów, Volhynia, Wilno and
    Białystok, which replace the county tables of the Polish Wikipedia
    articles used before (those disagreed with the pages by up to 6,000
    persons a county, and in Galicia gave the religions as the languages:
    Turka's "6,301 Polish speakers" are its Roman Catholics; 26,123 spoke
    Polish). Every voivodeship of the pages adds up to its census
    population; Warsaw's is short the city of Płock.
* **B**: population from the 1931 administrative tables (rounded), language
  shares from the county anchors of ``data.geography``. No Polish county is
  left at this grade.
* **C**: county seat only. Population and languages are downscaled from the
  voivodeship (``partition``), so they are estimates. Only Lithuania's
  apskritys are left at this grade.

Coverage: every Polish voivodeship but Warsaw city (one unit) at grade A;
Płock's town page is missing from the scan, so powiat Płock has shares only
and takes the remainder of the voivodeship (128,144 persons, town included).
Soviet Belarus, when included, has its 12 okrugs of 1926 as grade-A
counties (``data.bssr``). Latgale and the Nevel lands, when included, have
their uezds as grade-E counties: estimates from the 1897 census
(``data.krai_east``). The German, Danzig and Czechoslovak lands, when
included, have groups of Kreise and districts as grade-E counties
(``data.west``).

Conventions
-----------
* Cities with county rights are merged into the surrounding powiat (Lwów
  into powiat lwowski, Wilno into wileńsko-trocki, Białystok into
  białostocki, ...), so every county has land.
* Counties abolished in 1932 are merged into their successors (Bohorodczany,
  Kolno, Konstantynów, Grybów, Pilzno, Ropczyce).
* ``lat``/``lon`` are county centres (the seat where it is central), used
  for the Voronoi assignment of grid cells.
* ``lang`` keys: pl, uk (Ukrainian + Ruthenian), yi (Yiddish + Hebrew), be,
  pls (tutejszy), ru, lt, de, cs, oth, and ``bepr`` for the merged
  Belarusian + tutejszy + Russian category (no longer used by any row).
  ``rel``: rc, gc, or, ev, xc (other Christian), jw, orel (other or not
  stated); a religion a page does not print is inside orel.
* Powiaty abolished in 1932 (Słupca, Oświęcim, Pleszew, Ostrzeszów,
  Grodzisk, Odolanów) were printed with the powiat that absorbed them:
  ``GROUPS`` holds the pair and its population, and the partition splits it
  by the downscaled pattern. Rawa (Warsaw voivodeship in 1931) is a WAR
  county.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

from . import bssr as _bssr
from . import krai_east as _xk
from . import west as _west

_TR = str.maketrans("ąćęłńóśźżĄĆĘŁŃÓŚŹŻėęįšųūžčĖĮŠŲŪŽČ", "acelnoszzACELNOSZZeeisuuzcEISUUZC")


def _slug(name: str) -> str:
    base = name.split("(")[0].strip().translate(_TR).lower()
    return "".join(ch for ch in base if ch.isalnum())[:14]


@dataclass(frozen=True)
class County:
    parent: str
    name: str
    seat: str
    lat: float
    lon: float
    pop: float | None = None
    lang: dict = field(default_factory=dict)
    rel: dict = field(default_factory=dict)
    grade: str = "C"

    @property
    def code(self) -> str:
        return f"{self.parent}.{_slug(self.seat)}"


def _a(parent, name, seat, lat, lon, pop, lang, rel=None, grade="A"):
    return County(parent, name, seat, lat, lon, pop, dict(lang), dict(rel or {}), grade)


def _c(parent, name, seat, lat, lon, pop=None, grade="C"):
    return County(parent, name, seat, lat, lon, pop, {}, {}, grade)


# fmt: off
COUNTIES: list[County] = [
    # ---------------------------------------------------------------- Tarnopol (A)
    _a("TAR", "borszczowski", "Borszczów", 48.80, 26.05, 103277, {"pl": 46153, "uk": 52612, "yi": 4302, "oth": 23}),
    _a("TAR", "brodzki", "Brody", 50.08, 25.15, 91248, {"pl": 32843, "uk": 50490, "yi": 7640, "oth": 165}),
    _a("TAR", "brzeżański", "Brzeżany", 49.45, 24.93, 103824, {"pl": 48168, "uk": 51757, "yi": 3716, "oth": 6}),
    _a("TAR", "buczacki", "Buczacz", 49.07, 25.39, 139062, {"pl": 60523, "uk": 70336, "yi": 8059}),
    _a("TAR", "czortkowski", "Czortków", 49.02, 25.80, 84008, {"pl": 36486, "uk": 40866, "yi": 6474, "oth": 102}),
    _a("TAR", "kamionecki", "Kamionka Strumiłowa", 50.10, 24.35, 82111, {"pl": 41693, "uk": 35178, "yi": 4737, "oth": 429}),
    _a("TAR", "kopyczyniecki", "Kopyczyńce", 49.10, 25.91, 88614, {"pl": 38158, "uk": 45196, "yi": 5164, "oth": 37}),
    _a("TAR", "podhajecki", "Podhajce", 49.27, 25.13, 95663, {"pl": 46710, "uk": 45031, "yi": 3464, "de": 381}),
    _a("TAR", "przemyślański", "Przemyślany", 49.67, 24.56, 89908, {"pl": 52269, "uk": 32777, "yi": 4445, "de": 367}),
    _a("TAR", "radziechowski", "Radziechów", 50.28, 24.65, 69313, {"pl": 25427, "uk": 39970, "yi": 3277, "de": 583}),
    _a("TAR", "skałacki", "Skałat", 49.43, 25.97, 89215, {"pl": 60091, "uk": 25369, "yi": 3654, "de": 84}),
    _a("TAR", "tarnopolski", "Tarnopol", 49.55, 25.59, 142220, {"pl": 93874, "uk": 42374, "yi": 5836, "de": 34}),
    _a("TAR", "trembowelski", "Trembowla", 49.30, 25.71, 84321, {"pl": 50178, "uk": 30868, "yi": 3173, "de": 5}),
    _a("TAR", "zaleszczycki", "Zaleszczyki", 48.65, 25.73, 72021, {"pl": 27549, "uk": 41147, "yi": 3261, "de": 26}),
    _a("TAR", "zbaraski", "Zbaraż", 49.66, 25.78, 65579, {"pl": 32740, "uk": 29609, "yi": 3142, "de": 7}),
    _a("TAR", "zborowski", "Zborów", 49.66, 25.14, 81413, {"pl": 39624, "uk": 39174, "yi": 2522, "de": 12}),
    _a("TAR", "złoczowski", "Złoczów", 49.81, 24.90, 118609, {"pl": 56628, "uk": 55381, "yi": 6066, "de": 405}),
    # ---------------------------------------------------------------- Stanisławów (A; post-1932 counties)
    _a("STA", "doliński", "Dolina", 48.90, 23.85, 118373, {"pl": 21158, "uk": 83880, "yi": 9031, "de": 4013}),
    _a("STA", "horodeński", "Horodenka", 48.67, 25.50, 92894, {"pl": 27751, "uk": 59957, "yi": 5031, "de": 16}),
    _a("STA", "kałuski", "Kałusz", 49.03, 24.36, 102252, {"pl": 18637, "uk": 77506, "yi": 5109, "de": 944}),
    _a("STA", "kołomyjski", "Kołomyja", 48.53, 25.04, 176000, {"pl": 52006, "uk": 110533, "yi": 11191, "de": 1875}),
    _a("STA", "kosowski", "Kosów", 48.22, 24.95, 93952, {"pl": 6718, "uk": 79838, "yi": 6730, "de": 25}),
    _a("STA", "nadwórniański", "Nadwórna", 48.55, 24.45, 140702, {"pl": 16907, "uk": 112128, "yi": 11020, "de": 343}),
    _a("STA", "rohatyński", "Rohatyn", 49.41, 24.61, 127252, {"pl": 36152, "uk": 85245, "yi": 6111, "de": 32}),
    _a("STA", "stanisławowski", "Stanisławów", 48.92, 24.71, 198359, {"pl": 49032, "uk": 120214, "yi": 26996, "de": 1706}),
    _a("STA", "stryjski", "Stryj", 49.20, 23.75, 152631, {"pl": 25186, "uk": 106183, "yi": 15413, "de": 5497}),
    _a("STA", "śniatyński", "Śniatyn", 48.44, 25.57, 78025, {"pl": 17206, "uk": 56007, "yi": 4341, "de": 346}),
    _a("STA", "tłumacki", "Tłumacz", 48.86, 25.00, 116028, {"pl": 44958, "uk": 66659, "yi": 3677, "de": 502}),
    _a("STA", "żydaczowski", "Żydaczów", 49.38, 24.14, 83817, {"pl": 16464, "uk": 61098, "yi": 4728, "de": 1438}),
    # ---------------------------------------------------------------- Lwów (A; city merged into powiat lwowski)
    _a("LWO", "bóbrecki", "Bóbrka", 49.63, 24.28, 97124, {"pl": 30672, "uk": 60444, "yi": 5533, "de": 211}),
    _a("LWO", "brzozowski", "Brzozów", 49.70, 22.02, 83205, {"pl": 68149, "uk": 10677, "yi": 3836, "de": 3}),
    _a("LWO", "dobromilski", "Dobromil", 49.57, 22.79, 93970, {"pl": 35945, "uk": 52463, "yi": 4997, "de": 358}),
    _a("LWO", "drohobycki", "Drohobycz", 49.35, 23.51, 194456, {"pl": 91935, "uk": 79214, "yi": 20484, "de": 2428}),
    _a("LWO", "gródecki", "Gródek Jagielloński", 49.78, 23.65, 85007, {"pl": 33228, "uk": 47812, "yi": 2975, "de": 846}),
    _a("LWO", "jarosławski", "Jarosław", 50.02, 22.68, 148028, {"pl": 120429, "uk": 20993, "yi": 6064, "de": 33}),
    _a("LWO", "jaworowski", "Jaworów", 49.94, 23.38, 86762, {"pl": 26938, "uk": 55868, "yi": 3044, "de": 590}),
    _a("LWO", "kolbuszowski", "Kolbuszowa", 50.24, 21.77, 69565, {"pl": 65361, "uk": 62, "yi": 3693, "de": 80}),
    _a("LWO", "krośnieński", "Krosno", 49.69, 21.77, 113387, {"pl": 93691, "uk": 14666, "yi": 4416, "de": 35}),
    _a("LWO", "leski", "Lesko", 49.35, 22.45, 111575, {"pl": 31840, "uk": 70346, "yi": 8475, "de": 547}),
    _a("LWO", "lubaczowski", "Lubaczów", 50.16, 23.12, 87266, {"pl": 43294, "uk": 38237, "yi": 5485, "de": 124}),
    _a("LWO", "lwowski", "Lwów", 49.84, 24.03, 455031, {"pl": 278924, "uk": 93532, "yi": 76885, "de": 4257}),
    _a("LWO", "łańcucki", "Łańcut", 50.07, 22.23, 97679, {"pl": 92084, "uk": 2590, "yi": 2318, "de": 70}),
    _a("LWO", "mościski", "Mościska", 49.79, 23.15, 89460, {"pl": 49989, "uk": 37196, "yi": 2164, "de": 19}),
    _a("LWO", "niżański", "Nisko", 50.52, 22.14, 64233, {"pl": 60602, "uk": 115, "yi": 3084, "de": 60}),
    _a("LWO", "przemyski", "Przemyśl", 49.78, 22.77, 162544, {"pl": 86393, "uk": 60005, "yi": 15891, "de": 76}),
    _a("LWO", "przeworski", "Przeworsk", 50.06, 22.49, 61388, {"pl": 58632, "uk": 406, "yi": 2154, "de": 3}),
    _a("LWO", "rawski", "Rawa Ruska", 50.23, 23.62, 121800, {"pl": 27376, "uk": 82130, "yi": 10991, "de": 115}, grade="B"),
    _a("LWO", "rudecki", "Rudki", 49.65, 23.48, 79170, {"pl": 38417, "uk": 36254, "yi": 4247, "de": 22}),
    _a("LWO", "rzeszowski", "Rzeszów", 50.04, 22.00, 185106, {"pl": 173897, "uk": 963, "yi": 9065, "de": 18}),
    _a("LWO", "samborski", "Sambor", 49.52, 23.20, 133814, {"pl": 56818, "uk": 68222, "yi": 7794, "de": 700}),
    _a("LWO", "sanocki", "Sanok", 49.56, 22.20, 114195, {"pl": 67955, "uk": 38192, "yi": 7354, "de": 20}),
    _a("LWO", "sokalski", "Sokal", 50.48, 24.28, 109111, {"pl": 42851, "uk": 59984, "yi": 5917, "de": 136}),
    _a("LWO", "tarnobrzeski", "Tarnobrzeg", 50.57, 21.68, 73297, {"pl": 67624, "uk": 93, "yi": 5186, "de": 10}),
    _a("LWO", "turczański", "Turka", 49.15, 23.03, 114457, {"pl": 6301, "uk": 96564, "yi": 10627}),
    _a("LWO", "żółkiewski", "Żółkiew", 50.06, 23.97, 95507, {"pl": 20279, "uk": 66784, "yi": 7848, "de": 282}),
    # ---------------------------------------------------------------- Volhynia (A; oth = Czech, Russian and other)
    _a("WOL", "dubieński", "Dubno", 50.42, 25.74, 226809, {"pl": 33987, "uk": 158173, "yi": 17430, "de": 2789, "oth": 14430}),
    _a("WOL", "horochowski", "Horochów", 50.50, 24.76, 122045, {"pl": 21100, "uk": 84224, "yi": 9993, "de": 4977, "oth": 1751}),
    _a("WOL", "kostopolski", "Kostopol", 50.95, 26.45, 159602, {"pl": 34951, "uk": 105346, "yi": 10481, "de": 7545, "oth": 1279}),
    _a("WOL", "kowelski", "Kowel", 51.30, 24.80, 255492, {"pl": 36720, "uk": 185240, "yi": 26475, "de": 1813, "oth": 5244}),
    _a("WOL", "krzemieniecki", "Krzemieniec", 50.05, 25.73, 243032, {"pl": 25758, "uk": 196000, "yi": 18679, "de": 118, "oth": 2477}),
    _a("WOL", "lubomelski", "Luboml", 51.23, 24.04, 85507, {"pl": 12150, "uk": 65906, "yi": 6818, "de": 8, "oth": 625}),
    _a("WOL", "łucki", "Łuck", 50.75, 25.33, 289805, {"pl": 55446, "uk": 172038, "yi": 34142, "de": 17619, "oth": 10560}),
    _a("WOL", "rówieński", "Równe", 50.68, 26.15, 258589, {"pl": 36990, "uk": 166286, "yi": 37484, "de": 7458, "oth": 10371}),
    _a("WOL", "sarneński", "Sarny", 51.38, 26.75, 181284, {"pl": 30426, "uk": 129637, "yi": 16019, "de": 922, "oth": 4280}),
    _a("WOL", "włodzimierski", "Włodzimierz", 50.85, 24.32, 150384, {"pl": 40286, "uk": 88174, "yi": 17236, "de": 2788, "oth": 1900}),
    _a("WOL", "zdołbunowski", "Zdołbunów", 50.51, 26.25, 118334, {"pl": 17826, "uk": 81650, "yi": 10787, "de": 856, "oth": 7215}),
    # ---------------------------------------------------------------- Wilno (A; city merged into wileńsko-trocki)
    _a("WIL", "brasławski", "Brasław", 55.64, 27.04, 143161, {"pl": 93958, "be": 23138, "lt": 3490, "yi": 7181, "ru": 15394}),
    _a("WIL", "dziśnieński", "Głębokie", 55.35, 27.85, 159886, {"pl": 62282, "be": 79984, "ru": 5067, "yi": 11762, "oth": 609}),
    _a("WIL", "mołodeczański", "Mołodeczno", 54.25, 26.80, 91285, {"pl": 35523, "be": 49012, "ru": 735, "yi": 5789, "oth": 226}),
    _a("WIL", "oszmiański", "Oszmiana", 54.43, 25.94, 104612, {"pl": 84951, "be": 10149, "ru": 915, "lt": 1562, "yi": 6721, "oth": 314}),
    _a("WIL", "postawski", "Postawy", 55.11, 26.84, 99907, {"pl": 47917, "be": 47707, "lt": 84, "yi": 2683, "ru": 1516}),
    _a("WIL", "święciański", "Święciany", 55.14, 26.16, 136475, {"pl": 68441, "be": 8062, "lt": 42993, "yi": 7654, "ru": 9325}),
    _a("WIL", "wilejski", "Wilejka", 54.62, 27.00, 131070, {"pl": 59477, "be": 64337, "lt": 30, "yi": 5934, "ru": 1292}),
    _a("WIL", "wileńsko-trocki", "Wilno", 54.62, 25.15, 409543,
       {"pl": 309147, "be": 11022, "lt": 18434, "yi": 60720, "ru": 9115}, grade="B"),
    # ---------------------------------------------------------------- Nowogródek (A; bepr = Belarusian + tutejszy + Russian)
    _a("NOW", "baranowicki", "Baranowicze", 53.13, 26.01, 161038, {"bepr": 70627, "pl": 74916}),
    _a("NOW", "lidzki", "Lida", 53.89, 25.30, 183485, {"bepr": 20538, "pl": 145609}),
    _a("NOW", "nieświeski", "Nieśwież", 53.22, 26.67, 114464, {"bepr": 77094, "pl": 27933}),
    _a("NOW", "nowogródzki", "Nowogródek", 53.60, 25.82, 149536, {"bepr": 103783, "pl": 35084}, {"OR": 109162, "RC": 28796}),
    _a("NOW", "słonimski", "Słonim", 53.09, 25.32, 126510, {"bepr": 63445, "pl": 52313}, {"OR": 89724, "RC": 23817}),
    _a("NOW", "stołpecki", "Stołpce", 53.48, 26.73, 99389, {"bepr": 40875, "pl": 51820}, {"OR": 54076, "RC": 37856}),
    _a("NOW", "szczuczyński", "Szczuczyn", 53.60, 24.75, 107203, {"bepr": 10658, "pl": 89462}, {"OR": 38900, "RC": 60097}),
    _a("NOW", "wołożyński", "Wołożyn", 54.09, 26.53, 115522, {"bepr": 33240, "pl": 76722}, {"OR": 47923, "RC": 61852}),
    # ---------------------------------------------------------------- Białystok (A; city merged into białostocki)
    _a("BIA", "augustowski", "Augustów", 53.84, 22.98, 70943, {"pl": 68674, "be": 104, "yi": 423, "oth": 1742}),
    _a("BIA", "białostocki", "Białystok", 53.13, 23.25, 231179, {"pl": 163095, "be": 10150, "yi": 49704, "oth": 8230}),
    _a("BIA", "bielski", "Bielsk Podlaski", 52.77, 23.19, 202410, {"pl": 111377, "be": 57817, "yi": 18261, "oth": 14955}),
    _a("BIA", "grodzieński", "Grodno", 53.68, 23.83, 213105, {"pl": 101089, "be": 63731, "yi": 35354, "oth": 12931}),
    _a("BIA", "łomżyński", "Łomża", 53.18, 22.06, 168167, {"pl": 146308, "be": 47, "yi": 21203, "oth": 609}),
    _a("BIA", "ostrołęcki", "Ostrołęka", 53.08, 21.57, 112587, {"pl": 104341, "be": 14, "yi": 8013, "oth": 219}),
    _a("BIA", "ostrowski", "Ostrów Mazowiecka", 52.80, 21.89, 99741, {"pl": 85925, "be": 21, "yi": 12227, "oth": 1568}),
    _a("BIA", "sokólski", "Sokółka", 53.41, 23.50, 103135, {"pl": 92816, "be": 1606, "yi": 8133, "oth": 580}),
    _a("BIA", "suwalski", "Suwałki", 54.10, 22.93, 110124, {"pl": 85707, "be": 36, "yi": 8026, "lt": 16355}),
    _a("BIA", "szczuczyński", "Grajewo", 53.56, 22.30, 68215, {"pl": 60935, "be": 28, "yi": 6910, "oth": 342}),
    _a("BIA", "wołkowyski", "Wołkowysk", 53.15, 24.45, 171327, {"pl": 83111, "be": 71984, "yi": 13082, "oth": 3150}),
    _a("BIA", "wysokomazowiecki", "Wysokie Mazowieckie", 52.92, 22.52, 89103, {"pl": 78881, "be": 52, "yi": 9791, "oth": 379}),
    # ---------------------------------------------------------------- Polesie (A where found, else B)
    _a("POL", "brzeski", "Brześć", 52.15, 23.85, 216200, {}, grade="B"),
    _a("POL", "drohiczyński", "Drohiczyn", 52.18, 25.15, 97000, {}, grade="B"),
    _a("POL", "koszyrski", "Kamień Koszyrski", 51.62, 24.96, 95000, {"pls": 74313, "uk": 8271, "be": 1136, "ru": 250}),
    _a("POL", "kobryński", "Kobryń", 52.21, 24.36, 114000, {}, grade="B"),
    _a("POL", "kosowski", "Kosów Poleski", 52.75, 25.15, 48586, {"pls": 36143, "uk": 7}),
    _a("POL", "łuniniecki", "Łuniniec", 52.25, 26.80, 109300, {}, grade="B"),
    _a("POL", "piński", "Pińsk", 52.11, 26.10, 184305, {"bepr": 128787, "pl": 29077}, {"OR": 140022, "RC": 16465}),
    _a("POL", "prużański", "Prużana", 52.56, 24.46, 108583, {"bepr": 81032, "pl": 17762}, {"OR": 82015, "RC": 16311}),
    _a("POL", "stoliński", "Stolin", 51.89, 26.85, 124765, {"bepr": 92253, "pl": 18452}, {"OR": 105280, "RC": 6893}),
    # ---------------------------------------------------------------- Lublin (B: populations; uk shares from anchors)
    _c("LUB", "bialski", "Biała Podlaska", 52.08, 23.20, 174460, "B"),
    _c("LUB", "biłgorajski", "Biłgoraj", 50.54, 22.72, 116900, "B"),
    _c("LUB", "chełmski", "Chełm", 51.14, 23.47, 162300, "B"),
    _c("LUB", "garwoliński", "Garwolin", 51.90, 21.61, 159900, "B"),
    _c("LUB", "hrubieszowski", "Hrubieszów", 50.81, 23.89, 130000, "B"),
    _c("LUB", "janowski", "Janów Lubelski", 50.71, 22.41, 152700, "B"),
    _c("LUB", "krasnostawski", "Krasnystaw", 50.98, 23.17, 134200, "B"),
    _c("LUB", "lubartowski", "Lubartów", 51.46, 22.61, 108000, "B"),
    _c("LUB", "lubelski", "Lublin", 51.20, 22.60),
    _c("LUB", "łukowski", "Łuków", 51.93, 22.38, 129100, "B"),
    _c("LUB", "puławski", "Puławy", 51.42, 21.97, 156500, "B"),
    _c("LUB", "radzyński", "Radzyń Podlaski", 51.78, 22.62, 99100, "B"),
    _c("LUB", "siedlecki", "Siedlce", 52.17, 22.29, 151400, "B"),
    _c("LUB", "sokołowski", "Sokołów Podlaski", 52.41, 22.25, 83900, "B"),
    _c("LUB", "tomaszowski", "Tomaszów Lubelski", 50.45, 23.42),
    _c("LUB", "węgrowski", "Węgrów", 52.40, 22.02),
    _c("LUB", "włodawski", "Włodawa", 51.55, 23.55),
    _c("LUB", "zamojski", "Zamość", 50.72, 23.25),
    # ---------------------------------------------------------------- Kraków (C)
    _c("KRA", "bialski", "Biała", 49.82, 19.10), _c("KRA", "bocheński", "Bochnia", 49.97, 20.43),
    _c("KRA", "brzeski", "Brzesko", 49.97, 20.61), _c("KRA", "chrzanowski", "Chrzanów", 50.14, 19.40),
    _c("KRA", "dąbrowski", "Dąbrowa Tarnowska", 50.17, 20.99), _c("KRA", "dębicki", "Dębica", 50.05, 21.41),
    _c("KRA", "gorlicki", "Gorlice", 49.62, 21.16), _c("KRA", "jasielski", "Jasło", 49.75, 21.47),
    _c("KRA", "krakowski", "Kraków", 50.06, 19.94), _c("KRA", "limanowski", "Limanowa", 49.71, 20.42),
    _c("KRA", "mielecki", "Mielec", 50.29, 21.42), _c("KRA", "myślenicki", "Myślenice", 49.83, 19.94),
    _c("KRA", "nowosądecki", "Nowy Sącz", 49.55, 20.75), _c("KRA", "nowotarski", "Nowy Targ", 49.45, 20.03),
    _c("KRA", "oświęcimski", "Oświęcim", 50.03, 19.21), _c("KRA", "tarnowski", "Tarnów", 50.01, 20.99),
    _c("KRA", "wadowicki", "Wadowice", 49.88, 19.49), _c("KRA", "żywiecki", "Żywiec", 49.62, 19.19),
    # ---------------------------------------------------------------- Kielce (C)
    _c("KIE", "będziński", "Będzin", 50.33, 19.13), _c("KIE", "częstochowski", "Częstochowa", 50.81, 19.12),
    _c("KIE", "iłżecki", "Iłża", 51.10, 21.20), _c("KIE", "jędrzejowski", "Jędrzejów", 50.64, 20.30),
    _c("KIE", "kielecki", "Kielce", 50.87, 20.63), _c("KIE", "konecki", "Końskie", 51.19, 20.41),
    _c("KIE", "kozienicki", "Kozienice", 51.58, 21.55), _c("KIE", "miechowski", "Miechów", 50.36, 20.03),
    _c("KIE", "olkuski", "Olkusz", 50.28, 19.56), _c("KIE", "opatowski", "Opatów", 50.80, 21.42),
    _c("KIE", "opoczyński", "Opoczno", 51.38, 20.28), _c("KIE", "pińczowski", "Pińczów", 50.52, 20.53),
    _c("KIE", "radomski", "Radom", 51.40, 21.15), _c("KIE", "sandomierski", "Sandomierz", 50.68, 21.75),
    _c("KIE", "stopnicki", "Busko", 50.47, 20.72), _c("KIE", "włoszczowski", "Włoszczowa", 50.85, 19.97),
    _c("KIE", "zawierciański", "Zawiercie", 50.49, 19.42),
    # ---------------------------------------------------------------- Łódź (C)
    _c("LOD", "brzeziński", "Brzeziny", 51.70, 19.95), _c("LOD", "kaliski", "Kalisz", 51.76, 18.09),
    _c("LOD", "kolski", "Koło", 52.20, 18.64), _c("LOD", "koniński", "Konin", 52.22, 18.25),
    _c("LOD", "łaski", "Łask", 51.59, 19.13), _c("LOD", "łęczycki", "Łęczyca", 52.06, 19.20),
    _c("LOD", "łódzki", "Łódź", 51.77, 19.46), _c("LOD", "piotrkowski", "Piotrków", 51.41, 19.70),
    _c("LOD", "radomszczański", "Radomsko", 51.07, 19.45), _c("WAR", "rawski", "Rawa Mazowiecka", 51.76, 20.25),
    _c("LOD", "sieradzki", "Sieradz", 51.60, 18.73), _c("LOD", "słupecki", "Słupca", 52.29, 17.87),
    _c("LOD", "turecki", "Turek", 52.02, 18.50), _c("LOD", "wieluński", "Wieluń", 51.22, 18.57),
    # ---------------------------------------------------------------- Warsaw voivodeship (C)
    _c("WAR", "błoński", "Grodzisk Mazowiecki", 52.11, 20.63), _c("WAR", "ciechanowski", "Ciechanów", 52.88, 20.62),
    _c("WAR", "gostyniński", "Gostynin", 52.43, 19.46), _c("WAR", "grójecki", "Grójec", 51.87, 20.87),
    _c("WAR", "kutnowski", "Kutno", 52.23, 19.36), _c("WAR", "lipnowski", "Lipno", 52.84, 19.18),
    _c("WAR", "łowicki", "Łowicz", 52.11, 19.94), _c("WAR", "makowski", "Maków Mazowiecki", 52.86, 21.10),
    _c("WAR", "mławski", "Mława", 53.11, 20.38), _c("WAR", "miński", "Mińsk Mazowiecki", 52.18, 21.56),
    _c("WAR", "nieszawski", "Nieszawa", 52.85, 18.75), _c("WAR", "płocki", "Płock", 52.55, 19.70),
    _c("WAR", "płoński", "Płońsk", 52.62, 20.37), _c("WAR", "przasnyski", "Przasnysz", 53.02, 20.88),
    _c("WAR", "pułtuski", "Pułtusk", 52.70, 21.08), _c("WAR", "radzymiński", "Radzymin", 52.42, 21.18),
    _c("WAR", "rypiński", "Rypin", 53.07, 19.43), _c("WAR", "sierpecki", "Sierpc", 52.86, 19.67),
    _c("WAR", "skierniewicki", "Skierniewice", 51.95, 20.15), _c("WAR", "sochaczewski", "Sochaczew", 52.23, 20.24),
    _c("WAR", "warszawski", "Warszawa", 52.25, 20.85), _c("WAR", "włocławski", "Włocławek", 52.65, 19.07),
    # ---------------------------------------------------------------- Poznań (C)
    _c("POZ", "babimojski", "Wolsztyn", 52.12, 16.05), _c("POZ", "bydgoski", "Bydgoszcz", 53.12, 18.00),
    _c("POZ", "chodzieski", "Chodzież", 52.99, 16.92), _c("POZ", "czarnkowski", "Czarnków", 52.90, 16.56),
    _c("POZ", "gnieźnieński", "Gniezno", 52.54, 17.60), _c("POZ", "gostyński", "Gostyń", 51.88, 17.01),
    _c("POZ", "grodziski", "Grodzisk Wielkopolski", 52.23, 16.37), _c("POZ", "inowrocławski", "Inowrocław", 52.80, 18.26),
    _c("POZ", "jarociński", "Jarocin", 51.97, 17.50), _c("POZ", "kępiński", "Kępno", 51.28, 17.99),
    _c("POZ", "kościański", "Kościan", 52.09, 16.65), _c("POZ", "krotoszyński", "Krotoszyn", 51.70, 17.43),
    _c("POZ", "leszczyński", "Leszno", 51.84, 16.57), _c("POZ", "międzychodzki", "Międzychód", 52.60, 15.89),
    _c("POZ", "mogileński", "Mogilno", 52.66, 17.96), _c("POZ", "nowotomyski", "Nowy Tomyśl", 52.32, 16.13),
    _c("POZ", "obornicki", "Oborniki", 52.65, 16.81), _c("POZ", "odolanowski", "Odolanów", 51.57, 17.67),
    _c("POZ", "ostrowski", "Ostrów Wielkopolski", 51.65, 17.81), _c("POZ", "ostrzeszowski", "Ostrzeszów", 51.43, 17.93),
    _c("POZ", "pleszewski", "Pleszew", 51.90, 17.79), _c("POZ", "poznański", "Poznań", 52.41, 16.93),
    _c("POZ", "rawicki", "Rawicz", 51.61, 16.86), _c("POZ", "szamotulski", "Szamotuły", 52.61, 16.58),
    _c("POZ", "szubiński", "Szubin", 52.99, 17.73), _c("POZ", "średzki", "Środa Wielkopolska", 52.23, 17.28),
    _c("POZ", "śremski", "Śrem", 52.09, 17.02), _c("POZ", "wągrowiecki", "Wągrowiec", 52.81, 17.20),
    _c("POZ", "wrzesiński", "Września", 52.33, 17.57), _c("POZ", "wyrzyski", "Wyrzysk", 53.15, 17.27),
    _c("POZ", "żniński", "Żnin", 52.85, 17.72),
    # ---------------------------------------------------------------- Pomorze (A; Statystyka Polski C 75, tabl. 12;
    # Gdynia into morski, Grudziądz and Toruń into their powiaty; Kashubians are inside "pl")
    _a("POM", "brodnicki", "Brodnica", 53.26, 19.40, 56287, {"pl": 50990, "uk": 8, "yi": 96, "be": 3, "ru": 9, "lt": 2, "de": 5100, "oth": 79}),
    _a("POM", "chełmiński", "Chełmno", 53.35, 18.43, 52765, {"pl": 44700, "uk": 5, "yi": 23, "be": 1, "ru": 10, "lt": 3, "de": 7930, "oth": 93}),
    _a("POM", "chojnicki", "Chojnice", 53.70, 17.56, 76935, {"pl": 68999, "uk": 23, "yi": 8, "be": 3, "ru": 3, "lt": 8, "de": 7631, "oth": 260}),
    _a("POM", "działdowski", "Działdowo", 53.23, 20.18, 42716, {"pl": 39645, "uk": 11, "yi": 117, "be": 4, "ru": 10, "lt": 1, "de": 2862, "oth": 66}),
    _a("POM", "grudziądzki", "Grudziądz", 53.48, 18.75, 96815, {"pl": 84538, "uk": 75, "yi": 454, "be": 144, "ru": 63, "lt": 8, "de": 11368, "oth": 165}),
    _a("POM", "kartuski", "Kartuzy", 54.33, 18.20, 68674, {"pl": 64103, "uk": 8, "yi": 19, "be": 2, "ru": 1, "lt": 3, "de": 4445, "oth": 93}),
    _a("POM", "kościerski", "Kościerzyna", 54.12, 17.98, 51716, {"pl": 45658, "uk": 8, "be": 2, "ru": 4, "lt": 4, "de": 5978, "oth": 62}),
    _a("POM", "lubawski", "Lubawa", 53.50, 19.75, 53621, {"pl": 51812, "uk": 7, "yi": 65, "ru": 8, "lt": 1, "de": 1612, "oth": 116}),
    _a("POM", "morski", "Wejherowo", 54.65, 18.30, 118512, {"pl": 112212, "uk": 51, "yi": 128, "be": 11, "ru": 87, "lt": 3, "de": 5542, "oth": 478}),
    _a("POM", "sępoleński", "Sępólno Krajeńskie", 53.45, 17.53, 29563, {"pl": 17538, "uk": 10, "yi": 31, "be": 1, "ru": 11, "lt": 1, "de": 11942, "oth": 29}),
    _a("POM", "starogardzki", "Starogard", 53.97, 18.53, 71829, {"pl": 67937, "uk": 22, "yi": 258, "be": 6, "ru": 13, "lt": 1, "de": 3433, "oth": 159}),
    _a("POM", "świecki", "Świecie", 53.41, 18.45, 87998, {"pl": 74171, "uk": 25, "yi": 129, "be": 10, "ru": 30, "lt": 8, "de": 13422, "oth": 203}),
    _a("POM", "tczewski", "Tczew", 54.09, 18.78, 67399, {"pl": 62832, "uk": 21, "yi": 64, "be": 3, "ru": 11, "lt": 2, "de": 4359, "oth": 107}),
    _a("POM", "toruński", "Toruń", 53.01, 18.60, 114207, {"pl": 103915, "uk": 83, "yi": 311, "be": 14, "ru": 152, "lt": 10, "de": 9574, "oth": 148}),
    _a("POM", "tucholski", "Tuchola", 53.59, 17.86, 41249, {"pl": 37990, "uk": 14, "yi": 3, "be": 2, "ru": 7, "lt": 1, "de": 3151, "oth": 81}),
    _a("POM", "wąbrzeski", "Wąbrzeźno", 53.28, 18.95, 49852, {"pl": 42346, "uk": 31, "yi": 259, "be": 3, "ru": 18, "lt": 5, "de": 7051, "oth": 139}),
    # ---------------------------------------------------------------- Silesia (C)
    _c("SLA", "bielski", "Bielsko", 49.82, 19.04), _c("SLA", "cieszyński", "Cieszyn", 49.75, 18.63),
    _c("SLA", "katowicki", "Katowice", 50.26, 19.02), _c("SLA", "lubliniecki", "Lubliniec", 50.67, 18.69),
    _c("SLA", "pszczyński", "Pszczyna", 49.98, 18.95), _c("SLA", "rybnicki", "Rybnik", 50.10, 18.54),
    _c("SLA", "świętochłowicki", "Świętochłowice", 50.29, 18.92), _c("SLA", "tarnogórski", "Tarnowskie Góry", 50.44, 18.86),
    # ---------------------------------------------------------------- Lithuania, apskritys (C)
    _c("LT_LAU", "Kėdainių apskritis", "Kėdainiai", 55.29, 23.97), _c("LT_LAU", "Panevėžio apskritis", "Panevėžys", 55.73, 24.36),
    _c("LT_LAU", "Raseinių apskritis", "Raseiniai", 55.38, 23.12), _c("LT_LAU", "Ukmergės apskritis", "Ukmergė", 55.25, 24.76),
    _c("LT_ZEM", "Šiaulių apskritis", "Šiauliai", 55.93, 23.31), _c("LT_ZEM", "Telšių apskritis", "Telšiai", 55.98, 22.25),
    _c("LT_ZEM", "Mažeikių apskritis", "Mažeikiai", 56.31, 22.34), _c("LT_ZEM", "Kretingos apskritis", "Kretinga", 55.89, 21.24),
    _c("LT_ZEM", "Tauragės apskritis", "Tauragė", 55.25, 22.29),
    _c("LT_SUV", "Marijampolės apskritis", "Marijampolė", 54.56, 23.35), _c("LT_SUV", "Vilkaviškio apskritis", "Vilkaviškis", 54.65, 23.03),
    _c("LT_SUV", "Šakių apskritis", "Šakiai", 54.95, 23.05), _c("LT_SUV", "Alytaus apskritis", "Alytus", 54.40, 24.05),
    _c("LT_SUV", "Seinų apskritis", "Lazdijai", 54.23, 23.52),
    _c("LT_NEA", "Utenos apskritis", "Utena", 55.50, 25.60), _c("LT_NEA", "Zarasų apskritis", "Zarasai", 55.73, 26.25),
    _c("LT_NEA", "Rokiškio apskritis", "Rokiškis", 55.96, 25.59), _c("LT_NEA", "Biržų apskritis", "Biržai", 56.20, 24.76),
    _c("LT_NEA", "Trakų apskritis", "Kaišiadorys", 54.87, 24.45),
    _c("LT_KLA", "Klaipėdos apskritis", "Klaipėda", 55.71, 21.13), _c("LT_KLA", "Šilutės apskritis", "Šilutė", 55.35, 21.48),
    _c("LT_KLA", "Pagėgių apskritis", "Pagėgiai", 55.14, 21.91),
]
# fmt: on

# Soviet Belarus (only with include_belarus): the 12 okrugs of the 1926 census
# as counties, at their okrug centres, grown to 1931 (grade A; see data.bssr).
COUNTIES += [_a(par, name, seat, lat, lon, round(pop * _bssr.GROWTH_1926_1931), _bssr.okrug_languages(seat))
             for name, seat, par, lat, lon, pop, _ in _bssr.OKRUGS]
# The rest of the north-western governorates (only with include_krai_east):
# Latgale and the Nevel-Sebezh-Velizh lands by uezd (grade E: the 1897 census
# carried to 1931; see data.krai_east). The Mogilev edge is a single unit.
COUNTIES += [_a(par, name, seat, lat, lon, round(_xk.unit_population(seat)), _xk.unit_languages(seat), grade="E")
             for seat, name, par, lat, lon, _, _ in _xk.UNITS if par != "RU_MOH"]

# The west lands (only with include_west): groups of Kreise and districts as
# grade-E counties (data.west).
COUNTIES += [_a(par, name, seat, lat, lon, round(_west.unit_population(seat)), _west.unit_languages(seat), grade="E")
             for seat, name, par, lat, lon, _, _ in _west.UNITS]

# ---------------------------------------------------------------- the 1931 census by powiat (grade A)
# plsim/data/census1931_powiaty.csv: mother tongue and religion read from the census volumes (Tabl. 12 of the
# voivodeship volumes of Statystyka Polski seria C; the powiat pages of the short results, MBC 14481). They
# replace the Wikipedia rows and the seat-only rows. "Ruthenian" is counted as Ukrainian and Hebrew as Yiddish,
# as in the rows above; persons the census could not place ("unk") are shared pro rata. A county code with
# "+" is a powiat of 1932 that absorbed another (GROUPS: one population for both, shares for each); a code
# with "*" gives shares only (Płock without its city, whose page is missing from the scan).
CENSUS_KEYS = {"pl": "pl", "uk": "uk", "rue": "uk", "be": "be", "ru": "ru", "cs": "cs", "lt": "lt", "de": "de",
               "yi": "yi", "he": "yi", "oth": "oth", "pls": "pls"}
RELIGION_KEYS = ("rc", "gc", "or", "ev", "jw", "orel")


def census_1931_rows(path=None) -> dict:
    """{county code or "a+b": (pop, {lang: persons}, {religion: persons}, shares_only, source)}."""
    import csv
    import os
    path = path or os.path.join(os.path.dirname(__file__), "census1931_powiaty.csv")
    out: dict = {}
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(l for l in fh if not l.startswith("#")):
            code = r["county"].rstrip("*")
            pop = int(r["pop"])
            lang: dict = {}
            for col, key in CENSUS_KEYS.items():
                lang[key] = lang.get(key, 0) + int(r[col] or 0)
            known = sum(lang.values())
            lang = {k: v * pop / known for k, v in lang.items() if v > 0}       # unknown, pro rata
            rel = {k: int(r[k] or 0) for k in RELIGION_KEYS if r.get(k)}
            p0, l0, r0, so, src = out.get(code, (0, {}, {}, False, []))
            for k, v in lang.items():
                l0[k] = l0.get(k, 0) + v
            for k, v in rel.items():
                r0[k] = r0.get(k, 0) + v
            out[code] = (p0 + pop, l0, r0, so or r["county"].endswith("*"), src + [r["source"]])
    return out


CENSUS_1931 = census_1931_rows()
GROUPS: dict[str, tuple[tuple[str, ...], float]] = {}       # member -> (members, 1931 population of the group)
_by = {c.code: i for i, c in enumerate(COUNTIES)}
for _code, (_pop, _lang, _rel, _shares, _src) in CENSUS_1931.items():
    _members = tuple(_code.split("+"))
    for _m in _members:
        _c = COUNTIES[_by[_m]]
        _whole = len(_members) == 1 and not _shares
        COUNTIES[_by[_m]] = County(_c.parent, _c.name, _c.seat, _c.lat, _c.lon, round(_pop) if _whole else None,
                                   {k: round(v) for k, v in _lang.items()}, _rel, "A")
        if len(_members) > 1:
            GROUPS[_m] = (_members, float(_pop))


# ------------------------------------------------- the 1931 census by powiat and stratum (short results)
# plsim/data/census1931_strata.csv: religion and mother tongue of the towns and the countryside of every powiat,
# from the powiat and city pages of the short results (MBC 14481). They give the county's urban/rural split by
# language and its religions by stratum, and they replace the Wikipedia rows of the six eastern voivodeships
# (which disagree with the census pages by up to 6,000 persons a county, and in Galicia give the religions as
# the languages). "Other" and "not stated" religions are kept together as "orel"; "other Christian" (xc) as its
# own key, since what it holds differs by region.
FROM_WIKIPEDIA = ("TAR", "STA", "LWO", "WOL", "WIL", "BIA")
STRATA_REL = {"rc": "rc", "gc": "gc", "or": "or", "ev": "ev", "xc": "xc", "jw": "jw", "xn": "orel", "ro": "orel"}


def census_1931_strata(path=None) -> dict:
    """{county code or "a+b": {"urban" | "rural": (pop, {lang: persons}, {religion: persons}, printed)}}.
    Towns (T) and cities with their own page (C) are urban, the countryside (R) rural. Unstated languages
    are shared pro rata. ``printed``: the religions printed on every page of the stratum (a religion not
    printed is inside "other")."""
    import csv
    import os
    path = path or os.path.join(os.path.dirname(__file__), "census1931_strata.csv")
    out: dict = {}
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(l for l in fh if not l.startswith("#")):
            st = "rural" if r["stratum"] == "R" else "urban"
            pop = int(r["pop"])
            lang: dict = {}
            for col, key in CENSUS_KEYS.items():
                if r.get(col):
                    lang[key] = lang.get(key, 0) + int(r[col])
            known = sum(lang.values())
            lang = {k: v * pop / known for k, v in lang.items() if v > 0}
            rel: dict = {}
            for col, key in STRATA_REL.items():
                if r[col]:
                    rel[key] = rel.get(key, 0) + int(r[col])
            printed = {STRATA_REL[c] for c in STRATA_REL if r[c] and STRATA_REL[c] != "orel"}
            p0, l0, r0, pr0 = out.setdefault(r["county"], {}).get(st, (0, {}, {}, None))
            for k, v in lang.items():
                l0[k] = l0.get(k, 0) + v
            for k, v in rel.items():
                r0[k] = r0.get(k, 0) + v
            out[r["county"]][st] = (p0 + pop, l0, r0, printed if pr0 is None else pr0 & printed)
    return out


STRATA = census_1931_strata()
for _code, _st in list(STRATA.items()):
    _pop = sum(v[0] for v in _st.values())
    _lang: dict = {}
    _rel: dict = {}
    for _p, _l, _r, _pr in _st.values():
        for _k, _v in _l.items():
            _lang[_k] = _lang.get(_k, 0) + _v
        for _k, _v in _r.items():
            _rel[_k] = _rel.get(_k, 0) + _v
    if CENSUS_1931.get(_code, (0, {}, {}, False))[3]:
        del STRATA[_code]           # a page missing (Płock's city): the split and religions are not the county's
        continue
    for _m in _code.split("+"):
        _c = COUNTIES[_by[_m]]
        if _c.parent not in FROM_WIKIPEDIA:     # mother tongue from the county tables already; add the religions
            COUNTIES[_by[_m]] = dataclasses.replace(_c, rel=_c.rel or {k: round(v) for k, v in _rel.items()})
        else:                                   # the Wikipedia rows: the census pages instead
            COUNTIES[_by[_m]] = County(_c.parent, _c.name, _c.seat, _c.lat, _c.lon, _pop,
                                       {k: round(v) for k, v in _lang.items()},
                                       {k: round(v) for k, v in _rel.items()}, "A")

BY_PARENT: dict[str, list[County]] = {}
for _cty in COUNTIES:
    BY_PARENT.setdefault(_cty.parent, []).append(_cty)
BY_CODE: dict[str, County] = {c.code: c for c in COUNTIES}
assert len(BY_CODE) == len(COUNTIES), "duplicate county codes"
