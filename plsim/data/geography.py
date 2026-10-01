"""Spatial grid for maps: territory mask, regions, terrain, and the county-level
anchors used to place each language inside its voivodeship.

Territory
---------
A regular grid of 0.0625° x 0.1° cells (about 7 x 7 km) is laid over the
area. A cell belongs to the state when its centre lies on land (GSHHS
coastline from basemap-data, lakes removed) and inside the borders of
Poland or Lithuania on 1 January 1932, as given by CShapes 2.0
(``borders_1932.json``; Schvitz et al. 2022). Land cells within 2.5 km of
the Polish or Lithuanian coastline are also kept: the two coastlines differ
by a few km on the Hel peninsula and the Curonian Spit.

Cells are assigned to a voivodeship or Lithuanian unit by a multiplicatively
weighted Voronoi diagram of the domestic towns of their state, with one
weight per region calibrated so that the cell areas match the official
region areas. State borders are therefore exact to the cell; internal
borders are approximations.

County anchors
--------------
The voivodeship totals come from the 1931 census (see ``census1931``). Inside a
voivodeship, each language is spread with a smooth field interpolated from
county-seat anchors carrying 1931 county language shares. Grades:

* "A": county values from the 1931 census tables, as quoted in published
  secondary sources, e.g. Sokal 55.0 % Ukrainian/Ruthenian, Turka 70.3 %,
  Lesko 63.0 %, Jarosław 14.2 %, Lubaczów 43.8 %, Przemyśl 36.9 %,
  Brzozów 12.8 %, Chełm 8.1 %, Hrubieszów 14.7 %, Tomaszów 17.1 %, Biłgoraj
  2.3 %, Brasław, Dzisna, Oszmiana, Mołodeczno, Wilejka, Lida, Szczuczyn,
  Nieśwież, Baranowicze, Bielsk, Grodno, Kamień Koszyrski, Kostopol, Łuck
  (59.2 % Ukrainian), Krzemieniec (80.7 %).
* "C": estimates from the known linguistic geography (Kashubian counties,
  German colonies, Lemko districts, Old Believer and Latvian border areas,
  Lauda gentry). They are flagged in the table and only shape the
  distribution; regional totals always equal the census.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

import numpy as np
from matplotlib.path import Path

from .network import NODES
from .regions import REGIONS

HERE = os.path.dirname(os.path.abspath(__file__))



# fmt: off
@dataclass(frozen=True)
class Anchor:
    region: str
    name: str
    lat: float
    lon: float
    shares: dict
    grade: str = "C"


ANCHORS: list[Anchor] = [
    # Lwów voivodeship (Ukrainian incl. 'Ruthenian'; Lemko-Rusyn separately)
    Anchor("LWO", "Lwów (rural)", 49.84, 24.03, {"uk": .50}), Anchor("LWO", "Żółkiew", 50.06, 23.97, {"uk": .60}),
    Anchor("LWO", "Rawa Ruska", 50.23, 23.62, {"uk": .58}), Anchor("LWO", "Sokal", 50.48, 24.28, {"uk": .550}, "A"),
    Anchor("LWO", "Kamionka Strumiłowa", 50.10, 24.35, {"uk": .62}), Anchor("LWO", "Radziechów", 50.28, 24.65, {"uk": .65}),
    Anchor("LWO", "Bóbrka", 49.63, 24.28, {"uk": .60}), Anchor("LWO", "Gródek", 49.78, 23.65, {"uk": .50}),
    Anchor("LWO", "Rudki", 49.65, 23.48, {"uk": .55}), Anchor("LWO", "Mościska", 49.79, 23.15, {"uk": .45}),
    Anchor("LWO", "Jaworów", 49.94, 23.38, {"uk": .60}), Anchor("LWO", "Lubaczów", 50.16, 23.12, {"uk": .438}, "A"),
    Anchor("LWO", "Jarosław", 50.02, 22.68, {"uk": .142}, "A"), Anchor("LWO", "Przemyśl", 49.78, 22.77, {"uk": .369}, "A"),
    Anchor("LWO", "Dobromil", 49.57, 22.79, {"uk": .55}), Anchor("LWO", "Sambor", 49.52, 23.20, {"uk": .55}),
    Anchor("LWO", "Drohobycz", 49.35, 23.51, {"uk": .55}), Anchor("LWO", "Turka", 49.15, 23.03, {"uk": .703}, "A"),
    Anchor("LWO", "Lesko", 49.47, 22.33, {"uk": .630}, "A"), Anchor("LWO", "Sanok", 49.56, 22.20, {"uk": .25, "rue": .10}),
    Anchor("LWO", "Komańcza (Lemko)", 49.34, 22.06, {"rue": .70, "uk": .10}),
    Anchor("LWO", "Dukla (Lemko)", 49.45, 21.68, {"rue": .45}), Anchor("LWO", "Brzozów", 49.70, 22.02, {"uk": .128}, "A"),
    Anchor("LWO", "Krosno", 49.69, 21.77, {"rue": .05}), Anchor("LWO", "Jasło", 49.75, 21.47, {"rue": .04}),
    Anchor("LWO", "Rzeszów", 50.04, 22.00, {"uk": .01}), Anchor("LWO", "Łańcut", 50.07, 22.23, {"uk": .02}),
    Anchor("LWO", "Przeworsk", 50.06, 22.49, {"uk": .05}), Anchor("LWO", "Tarnobrzeg", 50.57, 21.68, {"uk": 0.0}),
    Anchor("LWO", "Nisko", 50.52, 22.14, {"uk": .02}), Anchor("LWO", "Kolbuszowa", 50.24, 21.77, {"uk": 0.0}),
    # Tarnopol
    Anchor("TAR", "Tarnopol", 49.55, 25.59, {"uk": .40}), Anchor("TAR", "Zbaraż", 49.66, 25.78, {"uk": .45}),
    Anchor("TAR", "Skałat", 49.43, 25.97, {"uk": .38}), Anchor("TAR", "Trembowla", 49.30, 25.71, {"uk": .45}),
    Anchor("TAR", "Czortków", 49.02, 25.80, {"uk": .52}), Anchor("TAR", "Kopyczyńce", 49.10, 25.91, {"uk": .58}),
    Anchor("TAR", "Borszczów", 48.80, 26.05, {"uk": .72}), Anchor("TAR", "Zaleszczyki", 48.65, 25.73, {"uk": .70}),
    Anchor("TAR", "Buczacz", 49.07, 25.39, {"uk": .55}), Anchor("TAR", "Podhajce", 49.27, 25.13, {"uk": .60}),
    Anchor("TAR", "Brzeżany", 49.45, 24.93, {"uk": .58}), Anchor("TAR", "Przemyślany", 49.67, 24.56, {"uk": .55}),
    Anchor("TAR", "Złoczów", 49.81, 24.90, {"uk": .52}), Anchor("TAR", "Zborów", 49.66, 25.14, {"uk": .62}),
    Anchor("TAR", "Brody", 50.08, 25.15, {"uk": .55}),
    # Stanisławów
    Anchor("STA", "Stanisławów", 48.92, 24.71, {"uk": .61}, "B"), Anchor("STA", "Tłumacz", 48.86, 25.00, {"uk": .65}),
    Anchor("STA", "Horodenka", 48.67, 25.50, {"uk": .70}), Anchor("STA", "Śniatyn", 48.44, 25.57, {"uk": .78}),
    Anchor("STA", "Kołomyja", 48.53, 25.04, {"uk": .70}), Anchor("STA", "Kosów (Hutsul)", 48.31, 25.09, {"uk": .88}),
    Anchor("STA", "Nadwórna", 48.63, 24.58, {"uk": .75}), Anchor("STA", "Bohorodczany", 48.80, 24.53, {"uk": .75}),
    Anchor("STA", "Kałusz", 49.03, 24.36, {"uk": .75}), Anchor("STA", "Dolina", 48.97, 23.97, {"uk": .75}),
    Anchor("STA", "Stryj", 49.26, 23.85, {"uk": .60, "de": .04}), Anchor("STA", "Żydaczów", 49.38, 24.14, {"uk": .62}),
    Anchor("STA", "Rohatyn", 49.41, 24.61, {"uk": .60}),
    # Wołyń
    Anchor("WOL", "Łuck", 50.75, 25.33, {"uk": .592, "de": .06, "cs": .03}, "A"),
    Anchor("WOL", "Włodzimierz", 50.85, 24.32, {"uk": .60, "de": .02}),
    Anchor("WOL", "Horochów", 50.50, 24.76, {"uk": .70, "de": .03, "cs": .02}),
    Anchor("WOL", "Kowel", 51.21, 24.71, {"uk": .72, "de": .02}), Anchor("WOL", "Luboml", 51.23, 24.04, {"uk": .72}),
    Anchor("WOL", "Sarny", 51.34, 26.60, {"uk": .72, "pls": .03}),
    Anchor("WOL", "Kostopol", 50.88, 26.45, {"uk": .643, "de": .03, "cs": .02}, "A"),
    Anchor("WOL", "Równe", 50.62, 26.25, {"uk": .68, "cs": .04, "de": .02}),
    Anchor("WOL", "Dubno", 50.42, 25.74, {"uk": .72, "cs": .05}), Anchor("WOL", "Zdołbunów", 50.51, 26.25, {"uk": .72, "cs": .03}),
    Anchor("WOL", "Krzemieniec", 50.10, 25.73, {"uk": .807}, "A"),
    # Polesie
    Anchor("POL", "Brześć", 52.10, 23.69, {"pls": .40, "uk": .10}), Anchor("POL", "Kobryń", 52.21, 24.36, {"pls": .72}),
    Anchor("POL", "Prużana", 52.56, 24.46, {"pls": .40, "be": .30}), Anchor("POL", "Kosów Poleski", 52.75, 25.15, {"pls": .65, "be": .12}),
    Anchor("POL", "Drohiczyn", 52.18, 25.15, {"pls": .80}), Anchor("POL", "Pińsk", 52.11, 26.10, {"pls": .72}),
    Anchor("POL", "Łuniniec", 52.25, 26.80, {"pls": .68, "be": .12}), Anchor("POL", "Stolin", 51.89, 26.85, {"pls": .70, "uk": .15}),
    Anchor("POL", "Kamień Koszyrski", 51.62, 24.96, {"pls": .78, "uk": .087}, "A"),
    # Nowogródek
    Anchor("NOW", "Nowogródek", 53.60, 25.82, {"be": .37}), Anchor("NOW", "Lida", 53.89, 25.30, {"be": .112}, "A"),
    Anchor("NOW", "Szczuczyn", 53.60, 24.75, {"be": .099}, "B"), Anchor("NOW", "Wołożyn", 54.09, 26.53, {"be": .45}),
    Anchor("NOW", "Stołpce", 53.48, 26.73, {"be": .55}), Anchor("NOW", "Nieśwież", 53.22, 26.67, {"be": .674}, "A"),
    Anchor("NOW", "Baranowicze", 53.13, 26.01, {"be": .439}, "A"), Anchor("NOW", "Słonim", 53.09, 25.32, {"be": .35}),
    # Wilno
    Anchor("WIL", "Wilno-Troki", 54.64, 25.10, {"lt": .15, "be": .05}),
    Anchor("WIL", "Oszmiana", 54.43, 25.94, {"be": .097, "lt": .015, "ru": .009}, "A"),
    Anchor("WIL", "Mołodeczno", 54.31, 26.84, {"be": .537}, "A"), Anchor("WIL", "Wilejka", 54.49, 26.92, {"be": .498}, "A"),
    Anchor("WIL", "Dzisna", 55.56, 28.21, {"be": .50, "ru": .032}, "A"),
    Anchor("WIL", "Głębokie", 55.13, 27.69, {"be": .45, "ru": .03}),
    Anchor("WIL", "Brasław", 55.64, 27.04, {"be": .162, "ru": .102, "lt": .024}, "A"),
    Anchor("WIL", "Postawy", 55.11, 26.84, {"be": .37}),
    Anchor("WIL", "Święciany", 55.14, 26.16, {"lt": .28, "be": .08, "ru": .03}),
    Anchor("WIL", "Ejszyszki", 54.17, 25.00, {"lt": .25, "be": .05}),
    # Białystok
    Anchor("BIA", "Białystok (rural)", 53.13, 23.16, {"be": .08}), Anchor("BIA", "Bielsk", 52.77, 23.19, {"be": .348}, "A"),
    Anchor("BIA", "Grodno", 53.68, 23.83, {"be": .328}, "A"), Anchor("BIA", "Sokółka", 53.41, 23.50, {"be": .20}),
    Anchor("BIA", "Wołkowysk", 53.15, 24.45, {"be": .40}), Anchor("BIA", "Augustów", 53.84, 22.98, {"ru": .015}),
    Anchor("BIA", "Suwałki", 54.10, 22.93, {"lt": .05, "ru": .03}), Anchor("BIA", "Sejny", 54.11, 23.35, {"lt": .35}),
    Anchor("BIA", "Łomża", 53.18, 22.06, {"be": 0.0}), Anchor("BIA", "Wysokie Mazowieckie", 52.92, 22.52, {"be": 0.0}),
    Anchor("BIA", "Ostrów Mazowiecka", 52.80, 21.89, {"be": 0.0}), Anchor("BIA", "Kolno", 53.41, 21.93, {"be": 0.0}),
    # Lublin
    Anchor("LUB", "Biłgoraj", 50.54, 22.72, {"uk": .023}, "A"), Anchor("LUB", "Chełm", 51.14, 23.47, {"uk": .081, "de": .02}, "A"),
    Anchor("LUB", "Hrubieszów", 50.81, 23.89, {"uk": .147}, "A"), Anchor("LUB", "Tomaszów Lubelski", 50.45, 23.42, {"uk": .171}, "A"),
    Anchor("LUB", "Włodawa", 51.55, 23.55, {"uk": .20}), Anchor("LUB", "Biała Podlaska", 52.03, 23.13, {"uk": .06}),
    Anchor("LUB", "Zamość", 50.72, 23.25, {"uk": .02}), Anchor("LUB", "Krasnystaw", 50.98, 23.17, {"uk": .02}),
    Anchor("LUB", "Lublin (rural)", 51.25, 22.57, {"uk": 0.0}), Anchor("LUB", "Puławy", 51.42, 21.97, {"uk": 0.0}),
    Anchor("LUB", "Łuków", 51.93, 22.38, {"uk": 0.0}), Anchor("LUB", "Garwolin", 51.90, 21.61, {"uk": 0.0}),
    Anchor("LUB", "Kraśnik", 50.92, 22.22, {"uk": 0.0}), Anchor("LUB", "Radzyń", 51.78, 22.62, {"uk": 0.0}),
    # Pomorze (Kashubian was not enumerated: estimates)
    Anchor("POM", "Kartuzy", 54.33, 18.20, {"csb": .75}), Anchor("POM", "Kościerzyna", 54.12, 17.98, {"csb": .55, "de": .05}),
    Anchor("POM", "Wejherowo (Morski)", 54.60, 18.24, {"csb": .55, "de": .04}), Anchor("POM", "Puck", 54.72, 18.41, {"csb": .60}),
    Anchor("POM", "Chojnice", 53.70, 17.56, {"csb": .12, "de": .10}), Anchor("POM", "Starogard", 53.97, 18.53, {"csb": .05, "de": .05}),
    Anchor("POM", "Sępólno", 53.45, 17.53, {"de": .25}), Anchor("POM", "Świecie", 53.41, 18.45, {"de": .12}),
    Anchor("POM", "Chełmno", 53.35, 18.43, {"de": .12}), Anchor("POM", "Grudziądz", 53.48, 18.75, {"de": .10}),
    Anchor("POM", "Wąbrzeźno", 53.28, 18.95, {"de": .10}), Anchor("POM", "Toruń", 53.01, 18.60, {"de": .10}),
    Anchor("POM", "Brodnica", 53.26, 19.40, {"de": .07}), Anchor("POM", "Działdowo", 53.23, 20.18, {"de": .15}),
    Anchor("POM", "Tczew", 54.09, 18.78, {"de": .06}), Anchor("POM", "Lubawa", 53.50, 19.75, {"de": .05}),
    # Poznań (German share by county, estimates)
    Anchor("POZ", "Nowy Tomyśl", 52.32, 16.13, {"de": .35}), Anchor("POZ", "Wolsztyn", 52.12, 16.12, {"de": .25}),
    Anchor("POZ", "Międzychód", 52.60, 15.89, {"de": .30}), Anchor("POZ", "Leszno", 51.84, 16.57, {"de": .15}),
    Anchor("POZ", "Rawicz", 51.61, 16.86, {"de": .10}), Anchor("POZ", "Chodzież", 52.99, 16.92, {"de": .25}),
    Anchor("POZ", "Czarnków", 52.90, 16.56, {"de": .18}), Anchor("POZ", "Wyrzysk", 53.15, 17.27, {"de": .25}),
    Anchor("POZ", "Bydgoszcz (rural)", 53.15, 17.90, {"de": .20}), Anchor("POZ", "Szubin", 52.99, 17.73, {"de": .10}),
    Anchor("POZ", "Szamotuły", 52.61, 16.58, {"de": .12}), Anchor("POZ", "Oborniki", 52.65, 16.81, {"de": .12}),
    Anchor("POZ", "Kępno", 51.28, 17.99, {"de": .07}), Anchor("POZ", "Gniezno", 52.54, 17.60, {"de": .03}),
    Anchor("POZ", "Września", 52.33, 17.57, {"de": .03}), Anchor("POZ", "Jarocin", 51.97, 17.50, {"de": .03}),
    Anchor("POZ", "Ostrów", 51.65, 17.81, {"de": .03}), Anchor("POZ", "Inowrocław", 52.80, 18.26, {"de": .04}),
    # Łódź, Warsaw, Silesia, Kraków (Germans, Lemkos, Wymysorys)
    Anchor("LOD", "Łódź (rural)", 51.75, 19.40, {"de": .12}), Anchor("LOD", "Łask", 51.59, 19.13, {"de": .08}),
    Anchor("LOD", "Brzeziny", 51.80, 19.75, {"de": .05}), Anchor("LOD", "Łęczyca", 52.06, 19.20, {"de": .04}),
    Anchor("LOD", "Turek", 52.02, 18.50, {"de": .04}), Anchor("LOD", "Koło", 52.20, 18.64, {"de": .04}),
    Anchor("LOD", "Kalisz", 51.76, 18.09, {"de": .03}), Anchor("LOD", "Radomsko", 51.07, 19.45, {"de": .01}),
    Anchor("LOD", "Wieluń", 51.22, 18.57, {"de": .01}), Anchor("LOD", "Piotrków", 51.41, 19.70, {"de": .01}),
    Anchor("WAR", "Gostynin", 52.43, 19.46, {"de": .08}), Anchor("WAR", "Płock", 52.55, 19.70, {"de": .05}),
    Anchor("WAR", "Włocławek", 52.65, 19.07, {"de": .05}), Anchor("WAR", "Lipno", 52.84, 19.18, {"de": .06}),
    Anchor("WAR", "Siedlce", 52.17, 22.29, {"de": .005}), Anchor("WAR", "Mińsk", 52.18, 21.56, {"de": .005}),
    Anchor("WAR", "Ciechanów", 52.88, 20.62, {"de": .01}), Anchor("WAR", "Grójec", 51.87, 20.87, {"de": .01}),
    Anchor("SLA", "Bielsko", 49.82, 19.04, {"de": .25}), Anchor("SLA", "Katowice (rural)", 50.28, 18.95, {"de": .10}),
    Anchor("SLA", "Pszczyna", 49.98, 18.95, {"de": .05}), Anchor("SLA", "Tarnowskie Góry", 50.44, 18.86, {"de": .06}),
    Anchor("SLA", "Lubliniec", 50.67, 18.69, {"de": .05}), Anchor("SLA", "Rybnik", 50.10, 18.54, {"de": .04}),
    Anchor("SLA", "Cieszyn", 49.75, 18.63, {"de": .03}),
    Anchor("KRA", "Gorlice (Lemko)", 49.52, 21.15, {"rue": .30}), Anchor("KRA", "Nowy Sącz (Lemko)", 49.42, 20.95, {"rue": .15}),
    Anchor("KRA", "Nowy Targ", 49.48, 20.03, {"rue": .02}), Anchor("KRA", "Wilamowice", 49.92, 19.15, {"wym": .90, "de": .05}),
    Anchor("KRA", "Biała", 49.82, 19.06, {"de": .10}), Anchor("KRA", "Kraków (rural)", 50.06, 19.94, {"rue": 0.0}),
    Anchor("KRA", "Tarnów", 50.01, 20.99, {"rue": 0.0}), Anchor("KRA", "Bochnia", 49.97, 20.43, {"rue": 0.0}),
    Anchor("KRA", "Miechów", 50.36, 20.03, {"rue": 0.0}), Anchor("KRA", "Dębica", 50.05, 21.41, {"rue": 0.0}),
    # Lithuania (dominant Lithuanian fills the remainder)
    Anchor("LT_LAU", "Kėdainiai", 55.29, 23.97, {"pl": .10}), Anchor("LT_LAU", "Panevėžys", 55.73, 24.36, {"pl": .05}),
    Anchor("LT_LAU", "Ukmergė", 55.25, 24.76, {"pl": .07}), Anchor("LT_LAU", "Raseiniai", 55.38, 23.12, {"pl": .02}),
    Anchor("LT_LAU", "Krakės (Lauda)", 55.40, 23.72, {"pl": .14}),
    Anchor("LT_KAU", "Kaunas (rural)", 54.85, 24.10, {"pl": .07, "ru": .02}),
    Anchor("LT_NEA", "Zarasai", 55.73, 26.25, {"pl": .11, "ru": .15}), Anchor("LT_NEA", "Rokiškis", 55.96, 25.59, {"pl": .04, "ru": .04, "lv": .02}),
    Anchor("LT_NEA", "Utena", 55.50, 25.60, {"pl": .04, "ru": .03}), Anchor("LT_NEA", "Biržai", 56.20, 24.76, {"lv": .05}),
    Anchor("LT_NEA", "Trakai (Lithuanian part)", 54.65, 24.50, {"pl": .10}),
    Anchor("LT_SUV", "Vilkaviškis", 54.65, 23.03, {"de": .06}), Anchor("LT_SUV", "Šakiai", 54.95, 23.05, {"de": .04}),
    Anchor("LT_SUV", "Marijampolė", 54.56, 23.35, {"de": .03}), Anchor("LT_SUV", "Alytus", 54.40, 24.05, {"pl": .03}),
    Anchor("LT_SUV", "Lazdijai", 54.23, 23.52, {"pl": .03, "be": .02}),
    Anchor("LT_ZEM", "Mažeikiai", 56.31, 22.34, {"lv": .05}), Anchor("LT_ZEM", "Šiauliai", 55.93, 23.31, {"lv": .01}),
    Anchor("LT_ZEM", "Tauragė", 55.25, 22.29, {"de": .02}), Anchor("LT_ZEM", "Telšiai", 55.98, 22.25, {"lv": .005}),
    Anchor("LT_KLA", "Klaipėda (rural)", 55.71, 21.13, {"de": .60}), Anchor("LT_KLA", "Šilutė", 55.35, 21.48, {"de": .45}),
    Anchor("LT_KLA", "Pagėgiai", 55.14, 21.91, {"de": .30}),
]
# fmt: on

CELL_DLAT = 0.0625
CELL_DLON = 0.10
BBOX = (13.5, 47.3, 30.5, 57.2)


def load_base_geography() -> dict:
    with open(os.path.join(HERE, "geo_base.json"), encoding="utf-8") as fh:
        return json.load(fh)


_BORDERS = None


def load_borders() -> dict:
    """State borders on 1 January 1932 (CShapes 2.0): rings of Poland and
    Lithuania, their coastlines, and the Polish-Lithuanian border."""
    global _BORDERS
    if _BORDERS is None:
        with open(os.path.join(HERE, "borders_1932.json"), encoding="utf-8") as fh:
            _BORDERS = json.load(fh)
    return _BORDERS


def _inside(polygons, lon, lat) -> np.ndarray:
    pts = np.column_stack([lon, lat])
    m = np.zeros(len(lon), dtype=bool)
    for rings in polygons:
        a = Path(np.array(rings[0])).contains_points(pts)
        for hole in rings[1:]:
            a &= ~Path(np.array(hole)).contains_points(pts)
        m |= a
    return m


def _dist_to_lines(lon, lat, lines) -> np.ndarray:
    """Distance (km, local flat approximation) from points to polylines."""
    kx = 111.2 * np.cos(np.radians(np.mean(lat) if len(lat) else 52.0))
    best = np.full(len(lon), np.inf)
    qx, qy = np.asarray(lon) * kx, np.asarray(lat) * 111.2
    for line in lines:
        p = np.array(line)
        ax, ay = p[:-1, 0] * kx, p[:-1, 1] * 111.2
        dx, dy = p[1:, 0] * kx - ax, p[1:, 1] * 111.2 - ay
        L = np.maximum(dx * dx + dy * dy, 1e-12)
        t = np.clip(((qx[:, None] - ax) * dx + (qy[:, None] - ay) * dy) / L, 0, 1)
        d = np.hypot(qx[:, None] - ax - t * dx, qy[:, None] - ay - t * dy)
        best = np.minimum(best, d.min(axis=1))
    return best


def state_of(lat, lon, coast_km: float = 2.5) -> np.ndarray:
    """'PL', 'LT' or '' for each point (1932 borders; see module docstring)."""
    lat, lon = np.atleast_1d(np.asarray(lat, float)), np.atleast_1d(np.asarray(lon, float))
    b = load_borders()
    out = np.full(len(lat), "", dtype="<U2")
    for st in ("PL", "LT"):
        out[(out == "") & _inside(b[st], lon, lat)] = st
    for st in ("PL", "LT"):
        free = np.where(out == "")[0]
        if len(free):
            out[free[_dist_to_lines(lon[free], lat[free], b["coast"][st]) < coast_km]] = st
    return out


def haversine_matrix(lat1, lon1, lat2, lon2) -> np.ndarray:
    p1, p2 = np.radians(lat1)[:, None], np.radians(lat2)[None, :]
    dphi = p2 - p1
    dl = np.radians(lon2)[None, :] - np.radians(lon1)[:, None]
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


@dataclass
class Grid:
    lat: np.ndarray
    lon: np.ndarray
    region: np.ndarray        # index into region_codes
    terrain: np.ndarray       # density factor
    region_codes: list
    cell_km2: np.ndarray
    dlat: float = CELL_DLAT
    dlon: float = CELL_DLON


def _soft_box(lat, lon, lat0, lat1, lon0, lon1, edge: float = 0.15) -> np.ndarray:
    """Smooth indicator of a lat/lon box (logistic edges, ``edge`` in degrees)."""
    s = lambda x: 1.0 / (1.0 + np.exp(-x / edge))  # noqa: E731
    return s(lat - lat0) * s(lat1 - lat) * s(lon - lon0) * s(lon1 - lon)


def _terrain_factor(lat, lon) -> np.ndarray:
    """Rural density modifiers: Polesie marshes and the Carpathians are thin."""
    f = np.ones_like(lat)
    f *= 1 - 0.40 * _soft_box(lat, lon, 51.4, 52.6, 24.4, 28.3, 0.25)      # Polesie marshes
    f *= 1 - 0.35 * _soft_box(lat, lon, 46.0, 49.45, 19.3, 25.3, 0.12)     # Carpathians
    f *= 1 - 0.30 * _soft_box(lat, lon, 46.0, 48.7, 24.0, 25.2, 0.12)      # Hutsul highlands
    return f


def build_grid(region_codes: list[str], dlat: float = CELL_DLAT, dlon: float = CELL_DLON) -> Grid:
    parents = list(dict.fromkeys(c.split(".")[0] for c in region_codes))
    if parents != list(region_codes):
        # sub-regions (``PARENT.CHILD``): build the parent grid, then split by county seats
        from dataclasses import replace

        from .subregions import assign
        base = build_grid(parents, dlat, dlon)
        idx = {c: i for i, c in enumerate(region_codes)}
        region = np.empty(len(base.lat), dtype=int)
        for pi, pc in enumerate(parents):
            m = base.region == pi
            if pc in idx:
                region[m] = idx[pc]
            else:
                kids = [c for c in region_codes if c.split(".")[0] == pc]
                region[m] = [idx[k] for k in assign(pc, base.lat[m], base.lon[m], kids)]
        return replace(base, region=region, region_codes=list(region_codes))
    lats = np.arange(BBOX[1] + dlat / 2, BBOX[3], dlat)
    lons = np.arange(BBOX[0] + dlon / 2, BBOX[2], dlon)
    LA, LO = np.meshgrid(lats, lons, indexing="ij")
    la, lo = LA.ravel(), LO.ravel()
    geo = load_base_geography()
    pts = np.column_stack([lo, la])
    land = np.zeros(len(la), dtype=bool)
    for poly in geo["land"]:
        land |= Path(np.array(poly)).contains_points(pts)
    for poly in geo["lakes"]:
        land &= ~Path(np.array(poly)).contains_points(pts)
    reg_idx = {c: i for i, c in enumerate(region_codes)}
    reg_state = np.array(["LT" if c.startswith("LT") else "PL" for c in region_codes])
    state = np.full(len(la), "", dtype="<U2")
    state[land] = state_of(la[land], lo[land])
    idx = np.where(np.isin(state, np.unique(reg_state)))[0]
    la, lo, cell_state = la[idx], lo[idx], state[idx]
    dom = [(n.lat, n.lon, reg_idx[n.region]) for n in NODES if n.region in reg_idx]
    nlat = np.array([d[0] for d in dom])
    nlon = np.array([d[1] for d in dom])
    dreg = np.array([d[2] for d in dom])
    # a cell can only go to a town (and region) of its own state
    Dk = haversine_matrix(la, lo, nlat, nlon)
    Dk[cell_state[:, None] != reg_state[dreg][None, :]] = np.inf
    km2 = (dlat * 111.2) * (dlon * 111.2 * np.cos(np.radians(la)))
    # multiplicatively weighted Voronoi: region weights calibrated so that
    # cell areas match the official region areas
    area_of = {r.code: r.area_km2 for r in REGIONS}
    target = np.array([area_of[c] for c in region_codes])
    w = np.ones(len(region_codes))
    for _ in range(60):
        region = dreg[(Dk / w[dreg][None, :]).argmin(axis=1)]
        area = np.bincount(region, weights=km2, minlength=len(region_codes))
        w *= np.clip(target / np.maximum(area, 1.0), 0.5, 2.0) ** 0.25
    return Grid(lat=la, lon=lo, region=region, terrain=_terrain_factor(la, lo), region_codes=list(region_codes),
                cell_km2=km2, dlat=dlat, dlon=dlon)
