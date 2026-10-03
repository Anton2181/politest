"""Transport network: towns (nodes), the c. 1931-38 railway and road network,
and dated historical / planned projects.

This is a *stylised reconstruction* of the trunk and secondary network of
interwar Poland and Lithuania at the scale of ~170 towns.  Local branch
lines, industrial sidings and most narrow-gauge feeders are not represented
individually, so modelled route-km are well below the ~20 k km operated by PKP
in 1938; the model is meant to reproduce connectivity, not every line.

Rail classes: ``nar`` narrow gauge, ``sec`` single-track secondary, ``main``
trunk (mostly double track), ``main_el`` electrified trunk, ``hsr`` high speed.
Road classes: ``dirt``, ``gravel`` (macadam "bite"), ``paved``,
``express`` (dual carriageway), ``motorway``.

Historical facts encoded as dated projects
------------------------------------------
* Kutno-Konin-Strzałkowo (Warsaw-Poznań shortcut, started 1924) - in service.
* Coal Trunk Line Herby Nowe - Karsznice - Inowrocław - Bydgoszcz -
  Kościerzyna - Gdynia, completed 1933 (Karsznice-Inowrocław modelled as
  opening 1933).
* Warszawa - Radom new line opened 1934 (new Warsaw-Kraków route).
* Kužiai-Telšiai-Kretinga (Samogitian railway), 1924-1932.
* Warsaw cross-city tunnel and suburban electrification (1933-36).
* Unfinished in 1939: Łapy - Ostrołęka - Przasnysz - Mława (Wilno-Gdynia
  shortcut) and Dębica - Pilzno - Jasło; the COP-era Łódź - Dębica
  trunk (Tomaszów-Końskie-Skarżysko-Ostrowiec-Sandomierz-Tarnobrzeg).
* Nestorowicz's March 1939 plan for ~5,000 km of category I/II trunk roads.
* Vilnius-Kaunas line (cut at the demarcation line 1920-1938) - reopens
  immediately under the federation scenario.

Soviet Belarus
--------------
Towns and lines of the BSSR (1926 borders) are ``optional``: they exist only
in scenarios that include Soviet Belarus, together with the gateways beyond
it (Smolensk, Nevel, Unecha, Bakhmach, Ovruch). Elsewhere they are left out
of the network entirely, and Mińsk stays the foreign gateway it was. Town
populations are the 1926 census grown to 1931 (thousands); the lines are
the main railways of c. 1931: Moscow-Brest (Stołpce-Mińsk-Orsza),
Libau-Romny (Mołodeczno-Mińsk-Bobrujsk-Homel), Riga-Orel (Dryssa-Połock-
Witebsk), the Vitebsk railway (Witebsk-Orsza-Mohylew-Żłobin-Kalinkowicze),
the Polesie railway (Łuniniec-Kalinkowicze-Homel), Bologoye-Siedlce
(Głębokie-Połock) and Orsza-Krzyczew.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Node:
    name: str
    region: str       # region code, or 'EXT' for foreign nodes
    lat: float
    lon: float
    pop_1931: float   # thousands (urban population of the town)
    terrain: str = "flat"
    capital: bool = False
    optional: bool | str = False   # True or "BY": only with Soviet Belarus; "XK": only with the rest of the
                                   # north-western governorates; "DE", "DZ", "CS": only with German, Danzig or
                                   # Czechoslovak land (data.west); "-XK", "BY-XK", "-DE" ...: not with them
                                   # (superseded gateways)


# fmt: off
NODES: list[Node] = [
    # --- Warszawa city and warszawskie
    Node("Warszawa", "WAW", 52.23, 21.01, 1172, capital=True),
    Node("Płock", "WAR", 52.55, 19.70, 33), Node("Włocławek", "WAR", 52.65, 19.07, 56),
    Node("Siedlce", "WAR", 52.17, 22.29, 36), Node("Mława", "WAR", 53.11, 20.38, 20),
    Node("Ciechanów", "WAR", 52.88, 20.62, 15), Node("Łowicz", "WAR", 52.11, 19.94, 20),
    Node("Skierniewice", "WAR", 51.96, 20.15, 20), Node("Mińsk Mazowiecki", "WAR", 52.18, 21.56, 15),
    Node("Sierpc", "WAR", 52.86, 19.67, 9), Node("Kutno", "WAR", 52.23, 19.36, 24),
    Node("Pułtusk", "WAR", 52.70, 21.08, 16), Node("Otwock", "WAR", 52.10, 21.26, 16),
    Node("Nasielsk", "WAR", 52.59, 20.81, 6), Node("Tłuszcz", "WAR", 52.43, 21.44, 4),
    Node("Przasnysz", "WAR", 53.02, 20.88, 10), Node("Grójec", "WAR", 51.87, 20.87, 9),
    # --- łódzkie
    Node("Łódź", "LOD", 51.76, 19.46, 605), Node("Pabianice", "LOD", 51.66, 19.35, 45),
    Node("Zgierz", "LOD", 51.86, 19.41, 26), Node("Tomaszów Mazowiecki", "LOD", 51.53, 20.01, 38),
    Node("Piotrków", "LOD", 51.41, 19.70, 51), Node("Kalisz", "LOD", 51.76, 18.09, 55),
    Node("Sieradz", "LOD", 51.60, 18.73, 12), Node("Zduńska Wola", "LOD", 51.60, 18.94, 24),
    Node("Radomsko", "LOD", 51.07, 19.45, 22), Node("Wieluń", "LOD", 51.22, 18.57, 14),
    Node("Konin", "LOD", 52.22, 18.25, 12), Node("Koło", "LOD", 52.20, 18.64, 12),
    Node("Łęczyca", "LOD", 52.06, 19.20, 12), Node("Koluszki", "LOD", 51.74, 19.82, 5),
    Node("Opoczno", "LOD", 51.38, 20.28, 9),
    # --- kieleckie
    Node("Kielce", "KIE", 50.87, 20.63, 59), Node("Radom", "KIE", 51.40, 21.15, 78),
    Node("Częstochowa", "KIE", 50.81, 19.12, 117), Node("Sosnowiec", "KIE", 50.29, 19.10, 109),
    Node("Dąbrowa Górnicza", "KIE", 50.32, 19.19, 40), Node("Będzin", "KIE", 50.33, 19.13, 48),
    Node("Zawiercie", "KIE", 50.49, 19.42, 32), Node("Ostrowiec", "KIE", 50.93, 21.39, 26),
    Node("Skarżysko-Kamienna", "KIE", 51.12, 20.87, 17), Node("Sandomierz", "KIE", 50.68, 21.75, 11),
    Node("Końskie", "KIE", 51.19, 20.41, 11), Node("Miechów", "KIE", 50.36, 20.03, 9),
    Node("Jędrzejów", "KIE", 50.64, 20.30, 12), Node("Starachowice", "KIE", 51.05, 21.07, 15),
    # --- lubelskie
    Node("Lublin", "LUB", 51.25, 22.57, 112), Node("Chełm", "LUB", 51.14, 23.47, 29),
    Node("Zamość", "LUB", 50.72, 23.25, 25), Node("Biała Podlaska", "LUB", 52.03, 23.13, 17),
    Node("Dęblin", "LUB", 51.56, 21.85, 6), Node("Puławy", "LUB", 51.42, 21.97, 11),
    Node("Krasnystaw", "LUB", 50.98, 23.17, 10), Node("Hrubieszów", "LUB", 50.81, 23.89, 12),
    Node("Łuków", "LUB", 51.93, 22.38, 15), Node("Kraśnik", "LUB", 50.92, 22.22, 8),
    Node("Garwolin", "LUB", 51.90, 21.61, 8), Node("Tomaszów Lubelski", "LUB", 50.45, 23.42, 12),
    Node("Włodawa", "LUB", 51.55, 23.55, 9),
    # --- białostockie
    Node("Białystok", "BIA", 53.13, 23.16, 91), Node("Grodno", "BIA", 53.68, 23.83, 50),
    Node("Łomża", "BIA", 53.18, 22.06, 25), Node("Suwałki", "BIA", 54.10, 22.93, 22),
    Node("Augustów", "BIA", 53.84, 22.98, 12), Node("Wołkowysk", "BIA", 53.15, 24.45, 15),
    Node("Bielsk Podlaski", "BIA", 52.77, 23.19, 7), Node("Ostrołęka", "BIA", 53.09, 21.57, 15),
    Node("Łapy", "BIA", 52.99, 22.88, 8), Node("Grajewo", "BIA", 53.65, 22.45, 9),
    Node("Ostrów Mazowiecka", "BIA", 52.80, 21.89, 18), Node("Czeremcha", "BIA", 52.52, 23.35, 2),
    Node("Sokółka", "BIA", 53.41, 23.50, 8),
    # --- wileńskie
    Node("Wilno", "WIL", 54.69, 25.28, 195, "hill"), Node("Mołodeczno", "WIL", 54.31, 26.84, 8),
    Node("Oszmiana", "WIL", 54.43, 25.94, 7), Node("Święciany", "WIL", 55.14, 26.16, 7),
    Node("Głębokie", "WIL", 55.13, 27.69, 8), Node("Postawy", "WIL", 55.11, 26.84, 5),
    Node("Brasław", "WIL", 55.64, 27.04, 3, "hill"), Node("Dzisna", "WIL", 55.56, 28.21, 6),
    Node("Wilejka", "WIL", 54.49, 26.92, 6), Node("Troki", "WIL", 54.64, 24.93, 3, "hill"),
    Node("Landwarów", "WIL", 54.63, 25.10, 5),
    # --- nowogródzkie
    Node("Nowogródek", "NOW", 53.60, 25.82, 10, "hill"), Node("Baranowicze", "NOW", 53.13, 26.01, 23),
    Node("Lida", "NOW", 53.89, 25.30, 20), Node("Słonim", "NOW", 53.09, 25.32, 16),
    Node("Nieśwież", "NOW", 53.22, 26.67, 8), Node("Stołpce", "NOW", 53.48, 26.73, 5),
    Node("Mosty", "NOW", 53.41, 24.54, 5),
    # --- poleskie
    Node("Brześć", "POL", 52.10, 23.69, 49), Node("Pińsk", "POL", 52.11, 26.10, 32, "marsh"),
    Node("Kobryń", "POL", 52.21, 24.36, 10, "marsh"), Node("Łuniniec", "POL", 52.25, 26.80, 9, "marsh"),
    Node("Kamień Koszyrski", "POL", 51.62, 24.96, 4, "marsh"), Node("Prużana", "POL", 52.56, 24.46, 8),
    Node("Dawidgródek", "POL", 52.06, 27.21, 11, "marsh"), Node("Stolin", "POL", 51.89, 26.85, 5, "marsh"),
    Node("Drohiczyn Poleski", "POL", 52.18, 25.15, 4, "marsh"),
    # --- wołyńskie
    Node("Łuck", "WOL", 50.75, 25.33, 36), Node("Równe", "WOL", 50.62, 26.25, 41),
    Node("Kowel", "WOL", 51.21, 24.71, 28), Node("Włodzimierz Wołyński", "WOL", 50.85, 24.32, 25),
    Node("Dubno", "WOL", 50.42, 25.74, 15), Node("Krzemieniec", "WOL", 50.10, 25.73, 20, "hill"),
    Node("Sarny", "WOL", 51.34, 26.60, 10, "marsh"), Node("Zdołbunów", "WOL", 50.51, 26.25, 10),
    Node("Ostróg", "WOL", 50.33, 26.52, 13), Node("Kostopol", "WOL", 50.88, 26.45, 8),
    Node("Horochów", "WOL", 50.50, 24.76, 6), Node("Luboml", "WOL", 51.23, 24.04, 5),
    # --- poznańskie (1931 borders: incl. Bydgoszcz)
    Node("Poznań", "POZ", 52.41, 16.93, 247), Node("Bydgoszcz", "POZ", 53.12, 18.01, 117),
    Node("Inowrocław", "POZ", 52.80, 18.26, 38), Node("Gniezno", "POZ", 52.54, 17.60, 32),
    Node("Leszno", "POZ", 51.84, 16.57, 18), Node("Ostrów Wielkopolski", "POZ", 51.65, 17.81, 29),
    Node("Krotoszyn", "POZ", 51.70, 17.44, 14), Node("Rawicz", "POZ", 51.61, 16.86, 12),
    Node("Zbąszyń", "POZ", 52.25, 15.92, 5), Node("Nakło", "POZ", 53.14, 17.60, 10),
    Node("Września", "POZ", 52.33, 17.57, 11), Node("Kępno", "POZ", 51.28, 17.99, 7),
    Node("Szamotuły", "POZ", 52.61, 16.58, 9), Node("Wągrowiec", "POZ", 52.81, 17.20, 9),
    Node("Jarocin", "POZ", 51.97, 17.50, 10), Node("Chodzież", "POZ", 52.99, 16.92, 11),
    # --- pomorskie
    Node("Toruń", "POM", 53.01, 18.60, 54), Node("Grudziądz", "POM", 53.48, 18.75, 51),
    Node("Gdynia", "POM", 54.52, 18.53, 33), Node("Tczew", "POM", 54.09, 18.78, 24),
    Node("Chojnice", "POM", 53.70, 17.56, 15), Node("Starogard", "POM", 53.97, 18.53, 16),
    Node("Kościerzyna", "POM", 54.12, 17.98, 8), Node("Kartuzy", "POM", 54.33, 18.20, 6),
    Node("Wejherowo", "POM", 54.60, 18.24, 12), Node("Chełmno", "POM", 53.35, 18.43, 12),
    Node("Brodnica", "POM", 53.26, 19.40, 10), Node("Działdowo", "POM", 53.23, 20.18, 7),
    Node("Puck", "POM", 54.72, 18.41, 4), Node("Laskowice", "POM", 53.49, 18.43, 3),
    # --- śląskie
    Node("Katowice", "SLA", 50.26, 19.02, 127), Node("Chorzów", "SLA", 50.30, 18.95, 81),
    Node("Rybnik", "SLA", 50.10, 18.54, 20), Node("Cieszyn", "SLA", 49.75, 18.63, 16, "hill"),
    Node("Bielsko", "SLA", 49.82, 19.04, 23, "hill"), Node("Tarnowskie Góry", "SLA", 50.44, 18.86, 15),
    Node("Mysłowice", "SLA", 50.24, 19.14, 20), Node("Pszczyna", "SLA", 49.98, 18.95, 8),
    Node("Lubliniec", "SLA", 50.67, 18.69, 7), Node("Żywiec", "SLA", 49.69, 19.19, 11, "mountain"),
    # --- krakowskie
    Node("Kraków", "KRA", 50.06, 19.94, 219), Node("Tarnów", "KRA", 50.01, 20.99, 45),
    Node("Nowy Sącz", "KRA", 49.62, 20.69, 34, "mountain"), Node("Wadowice", "KRA", 49.88, 19.49, 9, "hill"),
    Node("Oświęcim", "KRA", 50.04, 19.23, 12), Node("Chrzanów", "KRA", 50.14, 19.40, 18),
    Node("Nowy Targ", "KRA", 49.48, 20.03, 11, "mountain"), Node("Zakopane", "KRA", 49.30, 19.95, 17, "mountain"),
    Node("Dębica", "KRA", 50.05, 21.41, 12), Node("Gorlice", "KRA", 49.65, 21.16, 6, "hill"),
    Node("Bochnia", "KRA", 49.97, 20.43, 13), Node("Mielec", "KRA", 50.29, 21.42, 10),
    Node("Pilzno", "KRA", 49.98, 21.29, 4, "hill"),
    # --- lwowskie
    Node("Lwów", "LWO", 49.84, 24.03, 312, "hill"), Node("Przemyśl", "LWO", 49.78, 22.77, 51, "hill"),
    Node("Rzeszów", "LWO", 50.04, 22.00, 27), Node("Jarosław", "LWO", 50.02, 22.68, 22),
    Node("Drohobycz", "LWO", 49.35, 23.51, 33, "hill"), Node("Borysław", "LWO", 49.29, 23.43, 41, "mountain"),
    Node("Sambor", "LWO", 49.52, 23.20, 21, "hill"), Node("Sanok", "LWO", 49.56, 22.20, 14, "mountain"),
    Node("Krosno", "LWO", 49.69, 21.77, 13, "hill"), Node("Jasło", "LWO", 49.75, 21.47, 11, "hill"),
    Node("Rawa Ruska", "LWO", 50.23, 23.62, 11), Node("Żółkiew", "LWO", 50.06, 23.97, 10),
    Node("Sokal", "LWO", 50.48, 24.28, 12), Node("Gródek Jagielloński", "LWO", 49.78, 23.65, 13),
    Node("Tarnobrzeg", "LWO", 50.57, 21.68, 5), Node("Rozwadów", "LWO", 50.57, 22.05, 5),
    Node("Łańcut", "LWO", 50.07, 22.23, 8), Node("Nisko", "LWO", 50.52, 22.14, 5),
    # --- stanisławowskie
    Node("Stanisławów", "STA", 48.92, 24.71, 60), Node("Kołomyja", "STA", 48.53, 25.04, 33),
    Node("Stryj", "STA", 49.26, 23.85, 31), Node("Kałusz", "STA", 49.03, 24.36, 13),
    Node("Halicz", "STA", 49.12, 24.72, 5), Node("Nadwórna", "STA", 48.63, 24.58, 9, "mountain"),
    Node("Śniatyn", "STA", 48.44, 25.57, 11), Node("Skole", "STA", 49.04, 23.51, 6, "mountain"),
    Node("Dolina", "STA", 48.97, 23.97, 9, "hill"), Node("Horodenka", "STA", 48.67, 25.50, 11),
    Node("Rohatyn", "STA", 49.41, 24.61, 9), Node("Worochta", "STA", 48.29, 24.56, 4, "mountain"),
    # --- tarnopolskie
    Node("Tarnopol", "TAR", 49.55, 25.59, 36), Node("Brody", "TAR", 50.08, 25.15, 11),
    Node("Złoczów", "TAR", 49.81, 24.90, 13), Node("Czortków", "TAR", 49.02, 25.80, 19),
    Node("Brzeżany", "TAR", 49.45, 24.93, 11), Node("Buczacz", "TAR", 49.07, 25.39, 10),
    Node("Zbaraż", "TAR", 49.66, 25.78, 10), Node("Podwołoczyska", "TAR", 49.53, 26.14, 6),
    Node("Trembowla", "TAR", 49.30, 25.71, 9), Node("Zaleszczyki", "TAR", 48.65, 25.73, 7),
    Node("Husiatyn", "TAR", 49.07, 26.18, 5),
    # --- Lithuania
    Node("Kaunas", "LT_KAU", 54.90, 23.90, 115, capital=True), Node("Kaišiadorys", "LT_KAU", 54.86, 24.45, 4),
    Node("Jonava", "LT_KAU", 55.08, 24.28, 5),
    Node("Kėdainiai", "LT_LAU", 55.29, 23.97, 8), Node("Panevėžys", "LT_LAU", 55.73, 24.36, 23),
    Node("Ukmergė", "LT_LAU", 55.25, 24.76, 12), Node("Raseiniai", "LT_LAU", 55.38, 23.12, 6),
    Node("Radviliškis", "LT_LAU", 55.81, 23.54, 6),
    Node("Šiauliai", "LT_ZEM", 55.93, 23.31, 29), Node("Telšiai", "LT_ZEM", 55.98, 22.25, 6, "hill"),
    Node("Kretinga", "LT_ZEM", 55.89, 21.24, 5), Node("Mažeikiai", "LT_ZEM", 56.31, 22.34, 5),
    Node("Tauragė", "LT_ZEM", 55.25, 22.29, 9), Node("Joniškis", "LT_ZEM", 56.24, 23.62, 5),
    Node("Marijampolė", "LT_SUV", 54.56, 23.35, 12), Node("Vilkaviškis", "LT_SUV", 54.65, 23.03, 8),
    Node("Kybartai", "LT_SUV", 54.64, 22.76, 6), Node("Alytus", "LT_SUV", 54.40, 24.05, 6),
    Node("Šakiai", "LT_SUV", 54.95, 23.05, 4), Node("Lazdijai", "LT_SUV", 54.23, 23.52, 3),
    Node("Utena", "LT_NEA", 55.50, 25.60, 5), Node("Rokiškis", "LT_NEA", 55.96, 25.59, 6),
    Node("Biržai", "LT_NEA", 56.20, 24.76, 6), Node("Zarasai", "LT_NEA", 55.73, 26.25, 6, "hill"),
    Node("Klaipėda", "LT_KLA", 55.71, 21.13, 38), Node("Šilutė", "LT_KLA", 55.35, 21.48, 6),
    Node("Pagėgiai", "LT_KLA", 55.14, 21.91, 3),
    # --- foreign nodes (gateways)
    Node("Gdańsk (Free City)", "EXT", 54.35, 18.65, 256, optional="-DZ"), Node("Berlin via Frankfurt/O.", "EXT", 52.35, 14.55, 1500),
    Node("Breslau", "EXT", 51.11, 17.03, 620, optional="-DE"), Node("Gleiwitz-Beuthen", "EXT", 50.30, 18.67, 300, optional="-DE"),
    Node("Königsberg", "EXT", 54.71, 20.51, 370), Node("Riga via Daugavpils", "EXT", 55.87, 26.54, 400, optional="-XK"),
    Node("Mińsk", "BY_MIN", 53.90, 27.56, 240), Node("Kyiv via Shepetivka", "EXT", 50.18, 27.06, 500),
    Node("Proskurov", "EXT", 49.42, 26.98, 100), Node("Chernivtsi", "EXT", 48.29, 25.94, 110),
    Node("Žilina", "EXT", 49.22, 18.74, 100), Node("Ostrava", "EXT", 49.84, 18.29, 200),
    Node("Mukachevo", "EXT", 48.44, 22.72, 60), Node("Tilsit", "EXT", 55.08, 21.88, 60),
    Node("Insterburg", "EXT", 54.63, 21.81, 50), Node("Liepāja", "EXT", 56.51, 21.01, 60),
    Node("Jelgava-Riga", "EXT", 56.65, 23.72, 400), Node("Stettin", "EXT", 53.43, 14.55, 270, optional="-DE"),
    # --- Soviet Belarus (optional; 1926 census grown to 1931, thousands)
    Node("Witebsk", "BY_WIT", 55.19, 30.20, 106, optional=True), Node("Połock", "BY_WIT", 55.49, 28.79, 28, optional=True),
    Node("Orsza", "BY_WIT", 54.51, 30.42, 24, optional=True), Node("Lepel", "BY_WIT", 54.88, 28.70, 7, optional=True),
    Node("Horki", "BY_WIT", 54.29, 30.99, 7, optional=True), Node("Dryssa", "BY_WIT", 55.78, 27.96, 4, optional=True),
    Node("Borysów", "BY_MIN", 54.23, 28.50, 26, optional=True), Node("Słuck", "BY_MIN", 53.02, 27.55, 18, optional=True),
    Node("Mohylew", "BY_MOH", 53.90, 30.33, 54, optional=True), Node("Bobrujsk", "BY_MOH", 53.14, 29.22, 55, optional=True),
    Node("Klimowicze", "BY_MOH", 53.61, 31.96, 7, optional=True), Node("Krzyczew", "BY_MOH", 53.71, 31.71, 9, optional=True),
    Node("Mścisław", "BY_MOH", 54.02, 31.73, 8, optional=True), Node("Szkłów", "BY_MOH", 54.21, 30.29, 8, optional=True),
    Node("Bychów", "BY_MOH", 53.52, 30.25, 8, optional=True), Node("Rohaczów", "BY_MOH", 53.09, 30.05, 12, optional=True),
    Node("Osipowicze", "BY_MOH", 53.30, 28.64, 6, optional=True),
    Node("Homel", "BY_HOM", 52.44, 30.98, 93, optional=True), Node("Rzeczyca", "BY_HOM", 52.36, 30.39, 17, optional=True),
    Node("Mozyrz", "BY_HOM", 52.05, 29.25, 15, optional=True), Node("Kalinkowicze", "BY_HOM", 52.13, 29.33, 8, optional=True),
    Node("Żłobin", "BY_HOM", 52.89, 30.03, 12, optional=True), Node("Żytkowicze", "BY_HOM", 52.24, 27.86, 3, "marsh", optional=True),
    Node("Smolensk", "EXT", 54.78, 32.05, 150, optional=True), Node("Nevel-Velikiye Luki", "EXT", 56.02, 29.92, 60, optional="BY-XK"),
    Node("Unecha-Bryansk", "EXT", 52.85, 32.69, 100, optional=True), Node("Bakhmach-Chernihiv", "EXT", 51.50, 31.30, 80, optional=True),
    Node("Kyiv via Ovruch", "EXT", 51.32, 28.80, 300, optional=True),
    # --- Latgale and the Russian lands of the Vitebsk and Mogilev governorates (optional, "XK")
    Node("Dyneburg", "LV_LAT", 55.87, 26.54, 43, optional="XK"), Node("Rzeżyca", "LV_LAT", 56.51, 27.33, 13, optional="XK"),
    Node("Lucyn", "LV_LAT", 56.55, 27.72, 5.5, optional="XK"), Node("Krasław", "LV_LAT", 55.90, 27.17, 4.5, optional="XK"),
    Node("Prele", "LV_LAT", 56.29, 26.73, 3.5, optional="XK"), Node("Mariampol (Viļaka)", "LV_LAT", 57.18, 27.68, 1.5, optional="XK"),
    Node("Newel", "RU_VIT", 56.02, 29.92, 15, optional="XK"), Node("Siebież", "RU_VIT", 56.29, 28.48, 5, optional="XK"),
    Node("Wieliż", "RU_VIT", 55.60, 31.20, 12, optional="XK"), Node("Chisławicze", "RU_MOH", 54.19, 32.16, 3, optional="XK"),
    Node("Riga via Krustpils", "EXT", 56.51, 25.86, 400, optional="XK"),
    Node("Pskov via Ostrov", "EXT", 57.34, 28.35, 80, optional="XK"), Node("Velikiye Luki", "EXT", 56.34, 30.52, 40, optional="XK"),
    # --- German land held by Poland after 1945, Danzig, Czechoslovak plebiscite lands (optional; data.west).
    # Towns of the 1933 census (thousands), under their Polish names; a town whose region is not in the
    # run is a foreign town (gateway) of the run.
    Node("Wrocław", "DE_WRO", 51.11, 17.03, 625), Node("Wałbrzych", "DE_WRO", 50.77, 16.28, 64, "hill"),
    Node("Świdnica", "DE_WRO", 50.84, 16.49, 39), Node("Brzeg", "DE_WRO", 50.86, 17.47, 31),
    Node("Kłodzko", "DE_WRO", 50.44, 16.66, 18, "hill"), Node("Dzierżoniów", "DE_WRO", 50.73, 16.65, 17),
    Node("Oleśnica", "DE_WRO", 51.21, 17.39, 17), Node("Oława", "DE_WRO", 50.95, 17.29, 13),
    Node("Ząbkowice Śląskie", "DE_WRO", 50.59, 16.81, 11), Node("Namysłów", "DE_WRO", 51.08, 17.72, 9),
    Node("Wołów", "DE_WRO", 51.34, 16.64, 6), Node("Nowa Ruda", "DE_WRO", 50.58, 16.50, 13, "hill"),
    Node("Gliwice", "DE_OPO", 50.29, 18.67, 111), Node("Zabrze", "DE_OPO", 50.31, 18.78, 130),
    Node("Bytom", "DE_OPO", 50.35, 18.92, 101), Node("Opole", "DE_OPO", 50.67, 17.93, 50),
    Node("Racibórz", "DE_OPO", 50.09, 18.22, 50), Node("Nysa", "DE_OPO", 50.47, 17.33, 37),
    Node("Kędzierzyn-Koźle", "DE_OPO", 50.35, 18.21, 15), Node("Strzelce Opolskie", "DE_OPO", 50.51, 18.30, 11),
    Node("Kluczbork", "DE_OPO", 50.97, 18.22, 12), Node("Głubczyce", "DE_OPO", 50.20, 17.83, 13),
    Node("Prudnik", "DE_OPO", 50.32, 17.58, 17), Node("Olesno", "DE_OPO", 50.88, 18.42, 7),
    Node("Grodków", "DE_OPO", 50.70, 17.38, 5),
    Node("Legnica", "DE_LEG", 51.21, 16.16, 76), Node("Jelenia Góra", "DE_LEG", 50.90, 15.73, 34, "hill"),
    Node("Głogów", "DE_LEG", 51.66, 16.08, 33), Node("Zielona Góra", "DE_LEG", 51.94, 15.51, 26),
    Node("Bolesławiec", "DE_LEG", 51.26, 15.57, 21), Node("Żagań", "DE_LEG", 51.62, 15.32, 18),
    Node("Lubań", "DE_LEG", 51.12, 15.29, 17), Node("Kamienna Góra", "DE_LEG", 50.78, 16.03, 13, "hill"),
    Node("Jawor", "DE_LEG", 51.05, 16.19, 13), Node("Nowa Sól", "DE_LEG", 51.80, 15.71, 17),
    Node("Lubin", "DE_LEG", 51.40, 16.20, 10),
    Node("Gorzów Wielkopolski", "DE_NMK", 52.73, 15.24, 48), Node("Kostrzyn", "DE_NMK", 52.59, 14.65, 18),
    Node("Żary", "DE_NMK", 51.64, 15.14, 25), Node("Świebodzin", "DE_NMK", 52.25, 15.53, 10),
    Node("Sulechów", "DE_NMK", 52.08, 15.63, 10), Node("Krosno Odrzańskie", "DE_NMK", 52.05, 15.10, 11),
    Node("Choszczno", "DE_NMK", 53.17, 15.42, 13), Node("Myślibórz", "DE_NMK", 52.92, 14.87, 7),
    Node("Piła", "DE_GRZ", 53.15, 16.74, 45), Node("Wałcz", "DE_GRZ", 53.27, 16.47, 15),
    Node("Złotów", "DE_GRZ", 53.36, 17.04, 7), Node("Międzyrzecz", "DE_GRZ", 52.44, 15.58, 12),
    Node("Krzyż", "DE_GRZ", 52.88, 16.01, 5), Node("Wschowa", "DE_GRZ", 51.80, 16.32, 8),
    Node("Człuchów", "DE_GRZ", 53.67, 17.36, 6),
    Node("Słupsk", "DE_KOS", 54.46, 17.03, 46), Node("Koszalin", "DE_KOS", 54.19, 16.17, 33),
    Node("Kołobrzeg", "DE_KOS", 54.18, 15.58, 33), Node("Szczecinek", "DE_KOS", 53.71, 16.70, 19),
    Node("Lębork", "DE_KOS", 54.54, 17.75, 19), Node("Białogard", "DE_KOS", 54.01, 15.99, 16),
    Node("Sławno", "DE_KOS", 54.36, 16.68, 10), Node("Bytów", "DE_KOS", 54.17, 17.49, 10),
    Node("Świdwin", "DE_KOS", 53.77, 15.78, 9), Node("Drawsko Pomorskie", "DE_KOS", 53.53, 15.81, 6),
    Node("Szczecin", "DE_SZC", 53.43, 14.55, 271), Node("Stargard", "DE_SZC", 53.34, 15.05, 39),
    Node("Świnoujście", "DE_SZC", 53.91, 14.25, 21), Node("Pyrzyce", "DE_SZC", 53.15, 14.89, 10),
    Node("Goleniów", "DE_SZC", 53.56, 14.83, 10), Node("Nowogard", "DE_SZC", 53.67, 15.12, 8),
    Node("Gryfice", "DE_SZC", 53.92, 15.20, 10), Node("Łobez", "DE_SZC", 53.64, 15.62, 6),
    Node("Olsztyn", "DE_WAR", 53.78, 20.49, 50), Node("Braniewo", "DE_WAR", 54.38, 19.82, 21),
    Node("Lidzbark Warmiński", "DE_WAR", 54.13, 20.58, 11), Node("Reszel", "DE_WAR", 54.05, 21.15, 4),
    Node("Ełk", "DE_MAZ", 53.83, 22.36, 16), Node("Giżycko", "DE_MAZ", 54.04, 21.76, 15),
    Node("Ostróda", "DE_MAZ", 53.70, 19.97, 17), Node("Szczytno", "DE_MAZ", 53.56, 21.00, 14),
    Node("Mrągowo", "DE_MAZ", 53.86, 21.30, 7), Node("Pisz", "DE_MAZ", 53.63, 21.81, 5),
    Node("Nidzica", "DE_MAZ", 53.36, 20.43, 9), Node("Olecko", "DE_MAZ", 54.04, 22.50, 7),
    Node("Węgorzewo", "DE_MAZ", 54.21, 21.75, 10), Node("Gołdap", "DE_MAZ", 54.31, 22.30, 12),
    Node("Elbląg", "DE_OBL", 54.16, 19.40, 72), Node("Kętrzyn", "DE_MAZ", 54.08, 21.38, 19),
    Node("Bartoszyce", "DE_MAZ", 54.25, 20.81, 13), Node("Morąg", "DE_OBL", 53.92, 19.93, 7),
    Node("Pasłęk", "DE_OBL", 54.06, 19.66, 7),
    Node("Malbork", "DE_MAR", 54.04, 19.03, 25), Node("Kwidzyn", "DE_MAR", 53.73, 18.93, 19),
    Node("Iława", "DE_MAR", 53.60, 19.57, 13), Node("Sztum", "DE_MAR", 53.92, 19.03, 5),
    Node("Gdańsk", "DZ_GDA", 54.35, 18.65, 256), Node("Sopot", "DZ_GDA", 54.44, 18.56, 31),
    Node("Nowy Dwór Gdański", "DZ_GDA", 54.21, 19.12, 4),
    Node("Karwina", "CS_CIE", 49.86, 18.54, 40), Node("Bogumin", "CS_CIE", 49.90, 18.36, 15),
    Node("Czeski Cieszyn", "CS_CIE", 49.75, 18.62, 10), Node("Trzyniec", "CS_CIE", 49.68, 18.67, 12, "hill"),
    Node("Jabłonków", "CS_CIE", 49.58, 18.76, 4, "mountain"), Node("Frydek", "CS_CIE", 49.68, 18.35, 13),
    Node("Trzciana", "CS_SPO", 49.36, 19.61, 3, "mountain"), Node("Namiestów", "CS_SPO", 49.41, 19.48, 2, "mountain"),
    Node("Spiska Stara Wieś", "CS_SPO", 49.38, 20.37, 1.5, "mountain"),
    Node("Görlitz-Dresden", "EXT", 51.15, 14.99, 94, optional="DE"), Node("Cottbus-Berlin", "EXT", 51.76, 14.33, 55, optional="DE"),
    Node("Angermünde-Berlin", "EXT", 53.02, 14.00, 150, optional="DE"),
    Node("Pasewalk-Stralsund", "EXT", 53.51, 13.99, 60, optional="DE"), Node("Opava", "EXT", 49.94, 17.90, 40, optional="DE"),
]
# fmt: on

for _n in NODES:                          # towns of the west lands exist only with that land
    if _n.region[:3] in ("DE_", "DZ_", "CS_") and not _n.optional:
        _n.optional = _n.region[:2]
NODE_INDEX = {n.name: i for i, n in enumerate(NODES)}

# ---------------------------------------------------------------------------------
# Railway network c. 1931 (pairs of node names, class)
# ---------------------------------------------------------------------------------
_M, _S, _N = "main", "sec", "nar"
RAIL_1931: list[tuple[str, str, str]] = [
    # Warsaw radials
    ("Warszawa", "Skierniewice", _M), ("Skierniewice", "Łowicz", _M), ("Łowicz", "Kutno", _M),
    ("Kutno", "Koło", _M), ("Koło", "Konin", _M), ("Konin", "Września", _M), ("Września", "Poznań", _M),
    ("Poznań", "Zbąszyń", _M), ("Zbąszyń", "Berlin via Frankfurt/O.", _M),
    ("Skierniewice", "Koluszki", _M), ("Koluszki", "Łódź", _M), ("Koluszki", "Piotrków", _M),
    ("Piotrków", "Radomsko", _M), ("Radomsko", "Częstochowa", _M), ("Częstochowa", "Zawiercie", _M),
    ("Zawiercie", "Dąbrowa Górnicza", _M), ("Dąbrowa Górnicza", "Sosnowiec", _M),
    ("Sosnowiec", "Katowice", _M), ("Będzin", "Sosnowiec", _S), ("Będzin", "Dąbrowa Górnicza", _S),
    ("Warszawa", "Mińsk Mazowiecki", _M), ("Mińsk Mazowiecki", "Siedlce", _M), ("Siedlce", "Łuków", _M),
    ("Łuków", "Biała Podlaska", _M), ("Biała Podlaska", "Brześć", _M), ("Brześć", "Baranowicze", _M),
    ("Baranowicze", "Stołpce", _M), ("Stołpce", "Mińsk", _M),
    ("Warszawa", "Tłuszcz", _M), ("Tłuszcz", "Ostrów Mazowiecka", _M), ("Ostrów Mazowiecka", "Łapy", _M),
    ("Łapy", "Białystok", _M), ("Białystok", "Sokółka", _M), ("Sokółka", "Grodno", _M),
    ("Grodno", "Landwarów", _M), ("Landwarów", "Wilno", _M), ("Wilno", "Święciany", _M),
    ("Święciany", "Riga via Daugavpils", _M),
    ("Warszawa", "Nasielsk", _M), ("Nasielsk", "Ciechanów", _M), ("Ciechanów", "Mława", _M),
    ("Mława", "Działdowo", _M), ("Działdowo", "Königsberg", _S),
    ("Warszawa", "Otwock", _M), ("Otwock", "Garwolin", _M), ("Garwolin", "Dęblin", _M),
    ("Dęblin", "Puławy", _M), ("Puławy", "Lublin", _M), ("Lublin", "Chełm", _M), ("Chełm", "Luboml", _M),
    ("Luboml", "Kowel", _M), ("Kowel", "Łuck", _M), ("Łuck", "Równe", _M), ("Równe", "Zdołbunów", _M),
    ("Zdołbunów", "Kyiv via Shepetivka", _M),
    # Łódź region
    ("Łowicz", "Zgierz", _M), ("Zgierz", "Łódź", _M), ("Łódź", "Pabianice", _M),
    ("Pabianice", "Zduńska Wola", _M), ("Zduńska Wola", "Sieradz", _M), ("Sieradz", "Kalisz", _M),
    ("Zgierz", "Łęczyca", _S), ("Łęczyca", "Kutno", _S), ("Koluszki", "Tomaszów Mazowiecki", _S),
    ("Tomaszów Mazowiecki", "Opoczno", _S), ("Opoczno", "Końskie", _S), ("Końskie", "Skarżysko-Kamienna", _S),
    ("Wieluń", "Kępno", _S),
    # Coal trunk line (1926-1933), Silesia - Gdynia
    ("Katowice", "Chorzów", _M), ("Chorzów", "Tarnowskie Góry", _M), ("Tarnowskie Góry", "Lubliniec", _M),
    ("Lubliniec", "Zduńska Wola", _M), ("Bydgoszcz", "Kościerzyna", _M), ("Kościerzyna", "Gdynia", _M),
    ("Lubliniec", "Częstochowa", _S),
    # Kraków - Lwów (Carl Ludwig railway) and Galicia
    ("Kraków", "Bochnia", _M), ("Bochnia", "Tarnów", _M), ("Tarnów", "Dębica", _M), ("Dębica", "Rzeszów", _M),
    ("Rzeszów", "Łańcut", _M), ("Łańcut", "Jarosław", _M), ("Jarosław", "Przemyśl", _M),
    ("Przemyśl", "Gródek Jagielloński", _M), ("Gródek Jagielloński", "Lwów", _M),
    ("Kraków", "Chrzanów", _M), ("Chrzanów", "Mysłowice", _M), ("Mysłowice", "Katowice", _M),
    ("Chrzanów", "Oświęcim", _S), ("Oświęcim", "Pszczyna", _S), ("Katowice", "Pszczyna", _M),
    ("Pszczyna", "Bielsko", _M), ("Bielsko", "Cieszyn", _S), ("Cieszyn", "Ostrava", _M),
    ("Katowice", "Rybnik", _M), ("Bielsko", "Żywiec", _S), ("Żywiec", "Žilina", _S),
    ("Bielsko", "Wadowice", _S), ("Wadowice", "Kraków", _S), ("Katowice", "Gleiwitz-Beuthen", _M),
    ("Kraków", "Miechów", _M), ("Miechów", "Jędrzejów", _S), ("Jędrzejów", "Kielce", _S),
    ("Tarnów", "Nowy Sącz", _S), ("Kraków", "Nowy Targ", _S), ("Nowy Targ", "Zakopane", _S),
    ("Nowy Targ", "Nowy Sącz", _S), ("Nowy Sącz", "Gorlice", _S), ("Gorlice", "Jasło", _S),
    ("Jasło", "Krosno", _S), ("Krosno", "Sanok", _S), ("Sanok", "Sambor", _S), ("Sanok", "Przemyśl", _S),
    ("Jasło", "Rzeszów", _S), ("Dębica", "Mielec", _S), ("Mielec", "Tarnobrzeg", _S),
    ("Tarnobrzeg", "Rozwadów", _S), ("Rozwadów", "Nisko", _S), ("Nisko", "Łańcut", _S),
    ("Rozwadów", "Kraśnik", _S), ("Kraśnik", "Lublin", _S),
    ("Sambor", "Drohobycz", _S), ("Drohobycz", "Borysław", _S), ("Drohobycz", "Stryj", _S),
    ("Lwów", "Stryj", _M), ("Stryj", "Skole", _S), ("Skole", "Mukachevo", _S),
    ("Stryj", "Dolina", _S), ("Dolina", "Kałusz", _S), ("Kałusz", "Stanisławów", _S),
    ("Lwów", "Rohatyn", _S), ("Rohatyn", "Halicz", _S), ("Lwów", "Halicz", _M), ("Halicz", "Stanisławów", _M),
    ("Stanisławów", "Kołomyja", _M), ("Kołomyja", "Śniatyn", _M), ("Śniatyn", "Chernivtsi", _M),
    ("Stanisławów", "Nadwórna", _S), ("Nadwórna", "Worochta", _S), ("Kołomyja", "Horodenka", _S),
    ("Horodenka", "Zaleszczyki", _S), ("Stanisławów", "Buczacz", _S), ("Buczacz", "Czortków", _S),
    ("Czortków", "Husiatyn", _S), ("Czortków", "Zaleszczyki", _S), ("Brzeżany", "Rohatyn", _S),
    ("Lwów", "Złoczów", _M), ("Złoczów", "Tarnopol", _M), ("Tarnopol", "Podwołoczyska", _M),
    ("Podwołoczyska", "Proskurov", _M), ("Tarnopol", "Trembowla", _S), ("Trembowla", "Czortków", _S),
    ("Tarnopol", "Zbaraż", _S), ("Tarnopol", "Brzeżany", _S),
    ("Lwów", "Brody", _S), ("Brody", "Dubno", _S), ("Dubno", "Zdołbunów", _S), ("Dubno", "Krzemieniec", _S),
    ("Zdołbunów", "Ostróg", _S),
    ("Lwów", "Żółkiew", _S), ("Żółkiew", "Rawa Ruska", _S), ("Rawa Ruska", "Jarosław", _S),
    ("Rawa Ruska", "Tomaszów Lubelski", _S), ("Tomaszów Lubelski", "Zamość", _S), ("Zamość", "Krasnystaw", _S),
    ("Krasnystaw", "Chełm", _S), ("Zamość", "Hrubieszów", _S), ("Hrubieszów", "Włodzimierz Wołyński", _S),
    ("Rawa Ruska", "Sokal", _S), ("Sokal", "Włodzimierz Wołyński", _S), ("Włodzimierz Wołyński", "Kowel", _S),
    ("Łuck", "Horochów", _N), ("Horochów", "Włodzimierz Wołyński", _N), ("Równe", "Kostopol", _S),
    ("Kostopol", "Sarny", _S),
    # Kielce - Radom - Dęblin (Ivangorod-Dombrovo railway)
    ("Dęblin", "Radom", _M), ("Radom", "Skarżysko-Kamienna", _M), ("Skarżysko-Kamienna", "Kielce", _M),
    ("Kielce", "Zawiercie", _S), ("Kielce", "Częstochowa", _S), ("Skarżysko-Kamienna", "Starachowice", _S),
    ("Starachowice", "Ostrowiec", _S),
    # Lublin - Łuków, Dęblin - Łuków
    ("Lublin", "Łuków", _S), ("Dęblin", "Łuków", _S), ("Chełm", "Włodawa", _S), ("Włodawa", "Brześć", _S),
    # Podlasie / Belarus
    ("Siedlce", "Czeremcha", _S), ("Czeremcha", "Wołkowysk", _S), ("Białystok", "Bielsk Podlaski", _S),
    ("Bielsk Podlaski", "Czeremcha", _S), ("Czeremcha", "Brześć", _S), ("Białystok", "Wołkowysk", _S),
    ("Wołkowysk", "Baranowicze", _S), ("Wołkowysk", "Mosty", _S), ("Mosty", "Lida", _S),
    ("Białystok", "Grajewo", _S), ("Grajewo", "Königsberg", _S), ("Sokółka", "Augustów", _S),
    ("Augustów", "Suwałki", _S), ("Siedlce", "Ostrów Mazowiecka", _S), ("Tłuszcz", "Ostrołęka", _S),
    ("Łapy", "Łomża", _S),
    ("Wilno", "Lida", _S), ("Lida", "Baranowicze", _S), ("Baranowicze", "Łuniniec", _S),
    ("Łuniniec", "Sarny", _S), ("Sarny", "Równe", _S), ("Lida", "Mołodeczno", _S), ("Wilno", "Mołodeczno", _S),
    ("Mołodeczno", "Wilejka", _S), ("Wilejka", "Głębokie", _S), ("Wilejka", "Postawy", _S),
    ("Postawy", "Święciany", _S), ("Głębokie", "Dzisna", _N), ("Święciany", "Brasław", _N),
    ("Baranowicze", "Nowogródek", _S), ("Baranowicze", "Słonim", _S), ("Słonim", "Wołkowysk", _S),
    ("Baranowicze", "Nieśwież", _N), ("Landwarów", "Troki", _S), ("Oszmiana", "Mołodeczno", _N),
    # Polesie railway
    ("Brześć", "Kobryń", _S), ("Kobryń", "Drohiczyn Poleski", _S), ("Drohiczyn Poleski", "Pińsk", _S),
    ("Pińsk", "Łuniniec", _S), ("Kowel", "Brześć", _S), ("Kowel", "Sarny", _S), ("Kowel", "Kamień Koszyrski", _N),
    ("Kobryń", "Prużana", _N),
    # Greater Poland / Pomerania
    ("Poznań", "Gniezno", _M), ("Gniezno", "Inowrocław", _M), ("Inowrocław", "Toruń", _M),
    ("Inowrocław", "Bydgoszcz", _M), ("Kutno", "Włocławek", _M), ("Włocławek", "Toruń", _M),
    ("Toruń", "Bydgoszcz", _M), ("Bydgoszcz", "Nakło", _M), ("Bydgoszcz", "Laskowice", _M),
    ("Laskowice", "Tczew", _M), ("Tczew", "Gdańsk (Free City)", _M), ("Gdańsk (Free City)", "Gdynia", _M),
    ("Gdynia", "Wejherowo", _M), ("Wejherowo", "Puck", _S), ("Kartuzy", "Kościerzyna", _S),
    ("Kartuzy", "Gdańsk (Free City)", _S), ("Kościerzyna", "Chojnice", _S), ("Chojnice", "Nakło", _S),
    ("Starogard", "Tczew", _S), ("Starogard", "Kościerzyna", _S), ("Laskowice", "Grudziądz", _S),
    ("Grudziądz", "Toruń", _S), ("Toruń", "Brodnica", _S), ("Brodnica", "Działdowo", _S),
    ("Chełmno", "Grudziądz", _S), ("Toruń", "Sierpc", _S), ("Sierpc", "Nasielsk", _S), ("Kutno", "Płock", _S),
    ("Płock", "Sierpc", _S), ("Nasielsk", "Pułtusk", _N),
    ("Poznań", "Szamotuły", _M), ("Szamotuły", "Stettin", _M), ("Poznań", "Leszno", _M),
    ("Leszno", "Rawicz", _M), ("Rawicz", "Breslau", _M), ("Poznań", "Jarocin", _M), ("Jarocin", "Ostrów Wielkopolski", _M),
    ("Ostrów Wielkopolski", "Kępno", _S), ("Ostrów Wielkopolski", "Kalisz", _S), ("Ostrów Wielkopolski", "Krotoszyn", _S),
    ("Krotoszyn", "Leszno", _S), ("Gniezno", "Września", _S), ("Września", "Jarocin", _S), ("Gniezno", "Wągrowiec", _S),
    ("Wągrowiec", "Nakło", _S), ("Poznań", "Wągrowiec", _S), ("Kępno", "Breslau", _S), ("Nakło", "Chodzież", _S),
    ("Chodzież", "Poznań", _S),
    # Lithuania
    ("Kaunas", "Vilkaviškis", _M), ("Vilkaviškis", "Kybartai", _M), ("Kybartai", "Insterburg", _M),
    ("Kaunas", "Kaišiadorys", _M), ("Kaišiadorys", "Jonava", _M), ("Jonava", "Kėdainiai", _M),
    ("Kėdainiai", "Radviliškis", _M), ("Radviliškis", "Šiauliai", _M), ("Šiauliai", "Mažeikiai", _M),
    ("Mažeikiai", "Liepāja", _M), ("Šiauliai", "Joniškis", _M), ("Joniškis", "Jelgava-Riga", _M),
    ("Radviliškis", "Panevėžys", _S), ("Panevėžys", "Rokiškis", _S), ("Rokiškis", "Riga via Daugavpils", _S),
    ("Šiauliai", "Telšiai", _S), ("Kretinga", "Klaipėda", _S), ("Kretinga", "Liepāja", _S),
    ("Klaipėda", "Šilutė", _S), ("Šilutė", "Pagėgiai", _S), ("Pagėgiai", "Tilsit", _S), ("Pagėgiai", "Tauragė", _S),
    ("Kaunas", "Marijampolė", _S), ("Marijampolė", "Alytus", _S), ("Panevėžys", "Biržai", _N),
    ("Panevėžys", "Utena", _N), ("Ukmergė", "Jonava", _N), ("Šakiai", "Kaunas", _N),
    ("Tauragė", "Raseiniai", _N),
]

# Soviet Belarus: lines of c. 1931, only in scenarios that include it (the
# Mołodeczno-Mińsk line was cut at the Polish-Soviet border otherwise)
RAIL_1931_BY: list[tuple[str, str, str]] = [
    ("Mińsk", "Borysów", _M), ("Borysów", "Orsza", _M), ("Orsza", "Smolensk", _M),
    ("Mołodeczno", "Mińsk", _M), ("Mińsk", "Osipowicze", _M), ("Osipowicze", "Bobrujsk", _M),
    ("Bobrujsk", "Żłobin", _M), ("Żłobin", "Homel", _M), ("Homel", "Bakhmach-Chernihiv", _M),
    ("Riga via Daugavpils", "Dryssa", _M), ("Dryssa", "Połock", _M), ("Połock", "Witebsk", _M),
    ("Witebsk", "Smolensk", _M), ("Witebsk", "Nevel-Velikiye Luki", _S), ("Połock", "Nevel-Velikiye Luki", _S),
    ("Witebsk", "Orsza", _M), ("Orsza", "Szkłów", _S), ("Szkłów", "Mohylew", _S), ("Mohylew", "Bychów", _S),
    ("Bychów", "Rohaczów", _S), ("Rohaczów", "Żłobin", _S), ("Żłobin", "Kalinkowicze", _S),
    ("Kalinkowicze", "Kyiv via Ovruch", _S), ("Kalinkowicze", "Mozyrz", _S),
    ("Łuniniec", "Żytkowicze", _S), ("Żytkowicze", "Kalinkowicze", _S), ("Kalinkowicze", "Rzeczyca", _S),
    ("Rzeczyca", "Homel", _S), ("Homel", "Unecha-Bryansk", _M), ("Głębokie", "Połock", _S),
    ("Orsza", "Krzyczew", _S), ("Krzyczew", "Unecha-Bryansk", _S), ("Osipowicze", "Słuck", _S),
]

# Latgale and the Nevel lands: lines of c. 1931, only with them ("XK"):
# Riga-Orel (Krustpils-Dyneburg-Krasław-Dryssa), Petersburg-Warsaw (Pskov-
# Rzeżyca-Dyneburg-Święciany), Moscow-Windau (Krustpils-Rzeżyca-Lucyn-
# Siebież-Novosokolniki), Radviliškis-Dyneburg, Bologoye-Polotsk (Newel).
RAIL_1931_XK: list[tuple[str, str, str]] = [
    ("Dyneburg", "Riga via Krustpils", _M), ("Dyneburg", "Krasław", _M), ("Krasław", "Dryssa", _M),
    ("Święciany", "Dyneburg", _M), ("Rokiškis", "Dyneburg", _S), ("Dyneburg", "Rzeżyca", _M),
    ("Rzeżyca", "Pskov via Ostrov", _M), ("Riga via Krustpils", "Rzeżyca", _M), ("Rzeżyca", "Lucyn", _M),
    ("Lucyn", "Siebież", _M), ("Siebież", "Velikiye Luki", _M), ("Newel", "Velikiye Luki", _S),
    ("Newel", "Połock", _S), ("Newel", "Witebsk", _S),
]

# The west lands (``data.west``): main and secondary lines of c. 1931, only with them. Where a line
# replaces a gateway of the 1932 network (Breslau, Gleiwitz-Beuthen, Stettin, Gdańsk), the old edge is
# re-pointed to the town (``GATEWAY_TOWNS``) or dropped (``SUPERSEDED_WITH``).
RAIL_1931_WEST: list[tuple[str, str, str]] = [
    # Silesia
    ("Wrocław", "Oława", _M), ("Oława", "Brzeg", _M), ("Brzeg", "Opole", _M), ("Opole", "Kędzierzyn-Koźle", _M),
    ("Kędzierzyn-Koźle", "Gliwice", _M), ("Gliwice", "Zabrze", _M), ("Zabrze", "Bytom", _M), ("Zabrze", "Katowice", _M),
    ("Bytom", "Chorzów", _S), ("Bytom", "Tarnowskie Góry", _S), ("Kędzierzyn-Koźle", "Racibórz", _M),
    ("Racibórz", "Rybnik", _S), ("Racibórz", "Ostrava", _M), ("Racibórz", "Głubczyce", _S), ("Głubczyce", "Opava", _S),
    ("Głubczyce", "Prudnik", _S), ("Prudnik", "Nysa", _S), ("Nysa", "Grodków", _S), ("Grodków", "Brzeg", _S),
    ("Nysa", "Opole", _S), ("Nysa", "Kłodzko", _S), ("Opole", "Strzelce Opolskie", _S), ("Strzelce Opolskie", "Gliwice", _S),
    ("Opole", "Kluczbork", _S), ("Kluczbork", "Olesno", _S), ("Olesno", "Lubliniec", _S), ("Kluczbork", "Namysłów", _S),
    ("Namysłów", "Oleśnica", _S), ("Wrocław", "Oleśnica", _M), ("Oleśnica", "Kępno", _S),
    ("Wrocław", "Legnica", _M), ("Legnica", "Bolesławiec", _M), ("Bolesławiec", "Görlitz-Dresden", _M),
    ("Bolesławiec", "Żagań", _M), ("Żagań", "Żary", _M), ("Żary", "Cottbus-Berlin", _M),
    ("Wrocław", "Świdnica", _M), ("Świdnica", "Wałbrzych", _M), ("Wałbrzych", "Jelenia Góra", _M),
    ("Jelenia Góra", "Lubań", _M), ("Lubań", "Görlitz-Dresden", _M), ("Legnica", "Jawor", _S), ("Jawor", "Świdnica", _S),
    ("Jelenia Góra", "Kamienna Góra", _S), ("Kamienna Góra", "Wałbrzych", _S), ("Wałbrzych", "Nowa Ruda", _S),
    ("Nowa Ruda", "Kłodzko", _S), ("Kłodzko", "Ząbkowice Śląskie", _S), ("Ząbkowice Śląskie", "Wrocław", _S),
    ("Świdnica", "Dzierżoniów", _S), ("Dzierżoniów", "Ząbkowice Śląskie", _S), ("Wrocław", "Wołów", _S),
    ("Wołów", "Głogów", _S), ("Legnica", "Lubin", _S), ("Lubin", "Głogów", _S), ("Głogów", "Leszno", _M),
    ("Głogów", "Nowa Sól", _S), ("Nowa Sól", "Zielona Góra", _S), ("Zielona Góra", "Żagań", _S),
    ("Zielona Góra", "Sulechów", _S), ("Sulechów", "Świebodzin", _S), ("Zielona Góra", "Krosno Odrzańskie", _S),
    ("Krosno Odrzańskie", "Berlin via Frankfurt/O.", _S), ("Głogów", "Wschowa", _S), ("Wschowa", "Leszno", _S),
    # Neumark, Grenzmark, Pomerania
    ("Berlin via Frankfurt/O.", "Świebodzin", _M), ("Świebodzin", "Zbąszyń", _M), ("Międzyrzecz", "Świebodzin", _S),
    ("Międzyrzecz", "Zbąszyń", _S), ("Międzyrzecz", "Gorzów Wielkopolski", _S),
    ("Berlin via Frankfurt/O.", "Kostrzyn", _M), ("Kostrzyn", "Gorzów Wielkopolski", _M), ("Gorzów Wielkopolski", "Krzyż", _M),
    ("Krzyż", "Piła", _M), ("Piła", "Złotów", _M), ("Złotów", "Chojnice", _M), ("Krzyż", "Szamotuły", _M),
    ("Krzyż", "Choszczno", _M), ("Choszczno", "Stargard", _M), ("Stargard", "Szczecin", _M),
    ("Szczecin", "Angermünde-Berlin", _M), ("Szczecin", "Pasewalk-Stralsund", _M), ("Kostrzyn", "Myślibórz", _S),
    ("Myślibórz", "Pyrzyce", _S), ("Pyrzyce", "Stargard", _S), ("Kostrzyn", "Szczecin", _S),
    ("Piła", "Nakło", _M), ("Piła", "Chodzież", _S), ("Piła", "Wałcz", _S), ("Wałcz", "Szczecinek", _S),
    ("Człuchów", "Chojnice", _S), ("Człuchów", "Szczecinek", _S),
    ("Stargard", "Łobez", _M), ("Łobez", "Świdwin", _M), ("Świdwin", "Białogard", _M), ("Białogard", "Koszalin", _M),
    ("Koszalin", "Sławno", _M), ("Sławno", "Słupsk", _M), ("Słupsk", "Lębork", _M), ("Lębork", "Wejherowo", _M),
    ("Szczecinek", "Białogard", _M), ("Białogard", "Kołobrzeg", _S), ("Szczecinek", "Drawsko Pomorskie", _S),
    ("Drawsko Pomorskie", "Świdwin", _S), ("Słupsk", "Bytów", _S), ("Bytów", "Kościerzyna", _S),
    ("Szczecin", "Goleniów", _S), ("Goleniów", "Świnoujście", _S), ("Goleniów", "Nowogard", _S),
    ("Nowogard", "Gryfice", _S), ("Gryfice", "Kołobrzeg", _S),
    # Danzig, the Vistula, East Prussia
    ("Gdańsk", "Sopot", _M), ("Sopot", "Gdynia", _M), ("Gdańsk", "Nowy Dwór Gdański", _N),
    ("Tczew", "Malbork", _M), ("Malbork", "Elbląg", _M), ("Elbląg", "Braniewo", _M), ("Braniewo", "Königsberg", _M),
    ("Malbork", "Iława", _M), ("Iława", "Działdowo", _M), ("Iława", "Ostróda", _M), ("Ostróda", "Olsztyn", _M),
    ("Olsztyn", "Nidzica", _S), ("Nidzica", "Działdowo", _S), ("Olsztyn", "Szczytno", _S), ("Szczytno", "Pisz", _S),
    ("Pisz", "Ełk", _S), ("Olsztyn", "Reszel", _S), ("Reszel", "Kętrzyn", _S), ("Olsztyn", "Lidzbark Warmiński", _S),
    ("Lidzbark Warmiński", "Bartoszyce", _S), ("Olsztyn", "Morąg", _S), ("Morąg", "Pasłęk", _S), ("Pasłęk", "Elbląg", _S),
    ("Olsztyn", "Braniewo", _S), ("Königsberg", "Bartoszyce", _M), ("Bartoszyce", "Kętrzyn", _M),
    ("Kętrzyn", "Giżycko", _M), ("Giżycko", "Ełk", _M), ("Ełk", "Grajewo", _M), ("Ełk", "Olecko", _S),
    ("Olecko", "Gołdap", _S), ("Gołdap", "Insterburg", _S), ("Kętrzyn", "Węgorzewo", _S), ("Węgorzewo", "Gołdap", _S),
    ("Mrągowo", "Kętrzyn", _S), ("Mrągowo", "Pisz", _S), ("Kwidzyn", "Sztum", _S), ("Sztum", "Malbork", _S),
    ("Kwidzyn", "Grudziądz", _S), ("Kwidzyn", "Iława", _S),
    # Cieszyn Silesia, Orava
    ("Bogumin", "Ostrava", _M), ("Bogumin", "Racibórz", _M), ("Bogumin", "Karwina", _M), ("Karwina", "Czeski Cieszyn", _M),
    ("Czeski Cieszyn", "Cieszyn", _M), ("Czeski Cieszyn", "Trzyniec", _M), ("Trzyniec", "Jabłonków", _M),
    ("Jabłonków", "Žilina", _M), ("Frydek", "Ostrava", _S), ("Frydek", "Czeski Cieszyn", _S),
    ("Trzciana", "Nowy Targ", _S), ("Trzciana", "Žilina", _S),
]
# edges of the 1932 network that cross land of the west and are replaced by its lines
SUPERSEDED_WITH: dict[tuple[str, str], str] = {
    ("Szamotuły", "Stettin"): "DE", ("Zbąszyń", "Berlin via Frankfurt/O."): "DE", ("Działdowo", "Königsberg"): "DE",
    ("Grajewo", "Königsberg"): "DE", ("Gdańsk (Free City)", "Gdynia"): "DZ", ("Cieszyn", "Ostrava"): "CS",
}
# 1932 gateways that are towns of the west lands: with that land, their edges go to the town
GATEWAY_TOWNS = {"Breslau": "Wrocław", "Gleiwitz-Beuthen": "Gliwice", "Stettin": "Szczecin",
                 "Gdańsk (Free City)": "Gdańsk"}

# ---------------------------------------------------------------------------------
# Dated projects: (a, b, mode, class, year_opened, label, status)
# status: 'historical' (really opened) | 'planned' (on 1938-39 plans; opened in
# the counterfactual at the stated year if the scenario enables it) |
# 'federation' (only if the Lithuanian-Polish union exists)
# ---------------------------------------------------------------------------------
PROJECTS: list[tuple[str, str, str, str, int, str, str]] = [
    ("Zduńska Wola", "Inowrocław", "rail", "main", 1933, "Coal Trunk Line Karsznice-Inowrocław", "historical"),
    ("Warszawa", "Radom", "rail", "main", 1934, "Warszawa-Radom new line", "historical"),
    ("Telšiai", "Kretinga", "rail", "sec", 1932, "Samogitian railway Telšiai-Kretinga", "historical"),
    ("Warszawa", "Otwock", "rail", "main_el", 1936, "Warsaw node electrification", "historical"),
    ("Warszawa", "Skierniewice", "rail", "main_el", 1937, "Warsaw suburban electrification (Żyrardów)", "historical"),
    ("Łapy", "Ostrołęka", "rail", "sec", 1941, "Wilno-Gdynia shortcut (Łapy-Ostrołęka)", "planned"),
    ("Ostrołęka", "Przasnysz", "rail", "sec", 1942, "Wilno-Gdynia shortcut (Ostrołęka-Przasnysz)", "planned"),
    ("Przasnysz", "Mława", "rail", "sec", 1942, "Wilno-Gdynia shortcut (Przasnysz-Mława)", "planned"),
    ("Dębica", "Pilzno", "rail", "sec", 1940, "Dębica-Pilzno-Jasło (under construction 1939)", "planned"),
    ("Pilzno", "Jasło", "rail", "sec", 1940, "Dębica-Pilzno-Jasło (under construction 1939)", "planned"),
    ("Ostrowiec", "Sandomierz", "rail", "sec", 1941, "Łódź-Dębica COP trunk (Ostrowiec-Sandomierz)", "planned"),
    ("Sandomierz", "Tarnobrzeg", "rail", "sec", 1942, "Łódź-Dębica COP trunk (Vistula bridge)", "planned"),
    ("Tomaszów Mazowiecki", "Opoczno", "rail", "main", 1943, "Łódź-Dębica COP trunk upgrade", "planned"),
    ("Warszawa", "Łódź", "road", "express", 1946, "Nestorowicz 1939 trunk-road plan: Warszawa-Łódź", "planned"),
    ("Warszawa", "Poznań", "road", "express", 1950, "Nestorowicz 1939 trunk-road plan: Warszawa-Poznań", "planned"),
    ("Katowice", "Kraków", "road", "express", 1947, "Nestorowicz 1939 trunk-road plan: Katowice-Kraków", "planned"),
    ("Warszawa", "Lublin", "road", "paved", 1941, "Fifteen-Year Plan stage II roads", "planned"),
    ("Wilno", "Kaišiadorys", "rail", "main", 1932, "Vilnius-Kaunas line reopened across demarcation line", "federation"),
    ("Suwałki", "Marijampolė", "rail", "sec", 1935, "Suwałki-Šeštokai-Marijampolė reconnection", "federation"),
    ("Kaunas", "Wilno", "road", "paved", 1934, "Kaunas-Vilnius road reopened", "federation"),
]
# fmt: on

# Main roads paved by c. 1931 (state roads, mostly ex-Prussian & Austrian and
# the Warsaw-Brest/Warsaw-Kraków imperial chaussées).
PAVED_ROADS_1931: list[tuple[str, str]] = [
    ("Warszawa", "Łowicz"), ("Łowicz", "Kutno"), ("Poznań", "Gniezno"), ("Poznań", "Leszno"),
    ("Poznań", "Września"), ("Bydgoszcz", "Toruń"), ("Bydgoszcz", "Inowrocław"), ("Toruń", "Grudziądz"),
    ("Katowice", "Chorzów"), ("Katowice", "Mysłowice"), ("Katowice", "Pszczyna"), ("Pszczyna", "Bielsko"),
    ("Kraków", "Bochnia"), ("Bochnia", "Tarnów"), ("Tarnów", "Dębica"), ("Dębica", "Rzeszów"),
    ("Rzeszów", "Łańcut"), ("Łańcut", "Jarosław"), ("Jarosław", "Przemyśl"), ("Przemyśl", "Gródek Jagielloński"),
    ("Gródek Jagielloński", "Lwów"), ("Warszawa", "Mińsk Mazowiecki"), ("Mińsk Mazowiecki", "Siedlce"),
    ("Siedlce", "Łuków"), ("Łuków", "Biała Podlaska"), ("Biała Podlaska", "Brześć"), ("Warszawa", "Grójec"),
    ("Grójec", "Radom"), ("Radom", "Skarżysko-Kamienna"), ("Skarżysko-Kamienna", "Kielce"), ("Kielce", "Jędrzejów"),
    ("Jędrzejów", "Miechów"), ("Miechów", "Kraków"), ("Warszawa", "Garwolin"), ("Łódź", "Pabianice"),
    ("Łódź", "Zgierz"), ("Lwów", "Złoczów"), ("Złoczów", "Tarnopol"), ("Lwów", "Stryj"), ("Gdynia", "Wejherowo"),
    ("Kraków", "Chrzanów"), ("Chrzanów", "Mysłowice"), ("Kaunas", "Kaišiadorys"), ("Kaunas", "Marijampolė"),
    ("Klaipėda", "Kretinga"),
]
