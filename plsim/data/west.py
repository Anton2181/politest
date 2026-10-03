"""The German, Danzig and Czechoslovak lands of the western scenarios.

Two scenarios need land outside Poland and Lithuania of 1932:

* ``plebiscite_poland``: the plebiscite areas of 1920-21 all go to Poland
  (Upper Silesia, the Allenstein and Marienwerder areas, Cieszyn Silesia,
  Spiš and Orava), with the Free City of Danzig;
* ``historical``: the borders of 1945, for calibration. Poland gains the
  German land east of the Oder and Lusatian Neisse and Danzig, and loses
  the east.

The land is the German territory that Poland held after 1945 (``DE``), the
Free City (``DZ``) and the Czechoslovak parts of the Cieszyn, Spiš and Orava
plebiscite areas (``CS``): ``tools/build_west.py``, keys of
``borders_1932.json``. It forms 14 regions on the Prussian
Regierungsbezirke, with East Prussia split by faith and language:

=========  ========================================================  =======  ========
code       land                                                      km²      1933
=========  ========================================================  =======  ========
DE_OPO     RB Oppeln (Upper Silesia)                                 9,700    1,483 k
DE_WRO     RB Breslau                                                13,573   1,955 k
DE_LEG     RB Liegnitz east of the Neisse                            10,800   970 k
DE_NMK     the Neumark and Lusatia east of the Oder and Neisse       11,300   640 k
DE_GRZ     Grenzmark Posen-Westpreußen                               7,695    337 k
DE_KOS     RB Köslin                                                 12,936   690 k
DE_SZC     Stettin and the RB Stettin east of the Oder               7,600    700 k
DE_WAR     Warmia (Allenstein, Rößel, Heilsberg, Braunsberg)         4,290    268 k
DE_MAZ     Masuria (the rest of the Allenstein area, Angerburg,      14,090   613 k
           Goldap) and the Barten land (Rastenburg, the south of
           Bartenstein)
DE_OBL     Elbing and the Oberland (Pr. Holland, Mohrungen)          3,500    206 k
DE_MAR     the Marienwerder plebiscite area (Marienwerder east of    2,927    213 k
           the Vistula, Stuhm, Rosenberg, Marienburg)
DZ_GDA     the Free City of Danzig                                   1,966    410 k
CS_CIE     Cieszyn Silesia west of the Olza (Fryštát, Český Těšín,   1,300    311 k
           Frýdek)
CS_SPO     Upper Orava and Zamagurie (Spiš)                          1,250    60 k
=========  ========================================================  =======  ========

The Upper Silesian plebiscite area is RB Oppeln without the counties of
Neisse, Grottkau and Falkenberg; the Allenstein area is DE_WAR's Allenstein
and Rößel with DE_MAZ without Angerburg, Goldap, Rastenburg and Bartenstein.

Data (grade E: estimates)
-------------------------
* **Population.** Regierungsbezirk totals of the census of 16 June 1933
  (Statistik des Deutschen Reichs; RB Allenstein 552,541 with Oletzko),
  split at the Oder-Neisse line by county; Danzig from its 1929 census
  (407,517) grown to 1931; Cieszyn Silesia from the Czechoslovak census of
  1930 (Fryštát and Český Těšín 216,255; Frýdek about 95,000); Spiš and
  Orava from village counts (about 44 villages, 60,000 people). The county
  units below are groups of Kreise with weights from the same tables
  (rounded), scaled to the region totals. The 1933 count stands for the
  end of 1931.
* **Home language and faith.** Home language is latent speech, not the
  census answer: the 1925 Prussian census gave Polish 26.7 % and bilingual
  7.6 % in the province of Upper Silesia, with Polish majorities in the
  eastern rural counties (in Landkreis Oppeln only 26 % answered German
  alone) and German majorities in the cities and the west; Masurian or
  Polish was spoken in perhaps a quarter of the homes of southern Masuria
  (Neidenburg, Ortelsburg, Johannisburg), less to the north, and by about a
  fifth of rural Warmia; Stuhm was about a third Polish; Kashubian lived on
  in Bütow and Lauenburg. Upper Silesia and Warmia were Catholic, Masuria
  and Pomerania Lutheran (the Masurians Lutheran Polish speakers), Lower
  Silesia about 60 % Protestant with Catholic Glatz. Jews were 3.2 % of
  Breslau, under 1 % elsewhere, 2.5 % of Danzig. Cieszyn Silesia: the 1930
  census counted 76,230 Poles, 120,639 Czechs and 17,182 Germans in Fryštát
  and Český Těšín; latent Polish speech is set higher (the census answers
  followed the state), about 40 % of the Poles Lutheran. Spiš and Orava:
  Goral speech in about two thirds of the homes, Slovak (as Czechoslovak)
  in most of the rest, a few Jews, Rusyns and Zipser Germans.
* **Other inputs.** Income per head about 1.45 times Poland's (the eastern
  provinces at about three quarters of Germany's 3,400 1990 GK$ in
  1932-33), Danzig 1.9; Cieszyn 1.3, Spiš and Orava 0.6. Fertility from
  the provincial birth rates of 1933 (Upper Silesia and East Prussia
  19-21 per thousand, Lower Silesia 15), German life expectancy of 1932-34
  (62.8 female) a little lower in the east, literacy near universal.
"""
from __future__ import annotations

# seat, unit name, parent, lat, lon, weight (1933, thousands), (community, language) shares
UNITS = [
    # RB Oppeln
    ("Bytom", "Beuthen (city and Beuthen-Tarnowitz)", "DE_OPO", 50.35, 18.92, 141,
     {("RC", "de"): .70, ("RC", "pl"): .22, ("PR", "de"): .05, ("JW", "de"): .025, ("PR", "pl"): .005}),
    ("Zabrze", "Hindenburg", "DE_OPO", 50.31, 18.78, 130,
     {("RC", "de"): .68, ("RC", "pl"): .26, ("PR", "de"): .05, ("JW", "de"): .01}),
    ("Gliwice", "Gleiwitz and Tost-Gleiwitz", "DE_OPO", 50.29, 18.67, 191,
     {("RC", "de"): .63, ("RC", "pl"): .30, ("PR", "de"): .055, ("JW", "de"): .015}),
    ("Opole", "Oppeln (city and county)", "DE_OPO", 50.67, 17.93, 175,
     {("RC", "de"): .47, ("RC", "pl"): .47, ("PR", "de"): .05, ("JW", "de"): .005, ("PR", "pl"): .005}),
    ("Racibórz", "Ratibor (city and county)", "DE_OPO", 50.09, 18.22, 110,
     {("RC", "de"): .62, ("RC", "pl"): .22, ("RC", "cs"): .12, ("PR", "de"): .03, ("JW", "de"): .01}),
    ("Koźle", "Cosel", "DE_OPO", 50.33, 18.15, 80, {("RC", "de"): .45, ("RC", "pl"): .52, ("PR", "de"): .03}),
    ("Strzelce Opolskie", "Groß Strehlitz", "DE_OPO", 50.51, 18.30, 75,
     {("RC", "pl"): .60, ("RC", "de"): .37, ("PR", "de"): .03}),
    ("Olesno", "Rosenberg O.S. and Guttentag", "DE_OPO", 50.88, 18.42, 50,
     {("RC", "pl"): .55, ("RC", "de"): .40, ("PR", "de"): .05}),
    ("Kluczbork", "Kreuzburg", "DE_OPO", 50.97, 18.22, 50,
     {("PR", "de"): .45, ("RC", "de"): .25, ("PR", "pl"): .18, ("RC", "pl"): .12}),
    ("Głubczyce", "Leobschütz", "DE_OPO", 50.20, 17.83, 85,
     {("RC", "de"): .88, ("RC", "cs"): .08, ("PR", "de"): .03, ("RC", "pl"): .01}),
    ("Prudnik", "Neustadt O.S.", "DE_OPO", 50.32, 17.58, 90, {("RC", "de"): .80, ("RC", "pl"): .16, ("PR", "de"): .04}),
    ("Nysa", "Neisse (city and county)", "DE_OPO", 50.47, 17.33, 105,
     {("RC", "de"): .95, ("PR", "de"): .04, ("JW", "de"): .005, ("RC", "pl"): .005}),
    ("Grodków", "Grottkau", "DE_OPO", 50.70, 17.38, 42, {("RC", "de"): .92, ("PR", "de"): .07, ("RC", "pl"): .01}),
    ("Niemodlin", "Falkenberg", "DE_OPO", 50.64, 17.62, 40, {("RC", "de"): .80, ("PR", "de"): .10, ("RC", "pl"): .10}),
    # RB Breslau
    ("Wrocław", "Breslau (city)", "DE_WRO", 51.11, 17.03, 625,
     {("PR", "de"): .58, ("RC", "de"): .385, ("JW", "de"): .032, ("RC", "pl"): .003}),
    ("Oleśnica", "Oels, Groß Wartenberg, Namslau, Trebnitz, Militsch", "DE_WRO", 51.21, 17.39, 250,
     {("PR", "de"): .62, ("RC", "de"): .33, ("RC", "pl"): .03, ("PR", "pl"): .015, ("JW", "de"): .005}),
    ("Środa Śląska", "Landkreis Breslau, Neumarkt, Wohlau, Steinau, Guhrau", "DE_WRO", 51.16, 16.59, 275,
     {("PR", "de"): .65, ("RC", "de"): .34, ("JW", "de"): .003, ("RC", "pl"): .007}),
    ("Brzeg", "Brieg, Ohlau, Strehlen, Nimptsch", "DE_WRO", 50.86, 17.47, 195,
     {("PR", "de"): .62, ("RC", "de"): .37, ("JW", "de"): .004, ("RC", "pl"): .006}),
    ("Wałbrzych", "Waldenburg", "DE_WRO", 50.77, 16.28, 180, {("PR", "de"): .60, ("RC", "de"): .395, ("JW", "de"): .005}),
    ("Świdnica", "Schweidnitz, Reichenbach", "DE_WRO", 50.84, 16.49, 190,
     {("PR", "de"): .55, ("RC", "de"): .445, ("JW", "de"): .005}),
    ("Kłodzko", "Glatz, Habelschwerdt, Neurode", "DE_WRO", 50.44, 16.66, 185,
     {("RC", "de"): .92, ("PR", "de"): .065, ("RC", "cs"): .015}),
    ("Ząbkowice Śląskie", "Frankenstein, Münsterberg", "DE_WRO", 50.59, 16.81, 90, {("RC", "de"): .70, ("PR", "de"): .30}),
    # RB Liegnitz east of the Neisse
    ("Legnica", "Liegnitz, Lüben, Goldberg, Jauer", "DE_LEG", 51.21, 16.16, 266,
     {("PR", "de"): .80, ("RC", "de"): .195, ("JW", "de"): .005}),
    ("Jelenia Góra", "Hirschberg, Landeshut, Schönau", "DE_LEG", 50.90, 15.73, 185, {("PR", "de"): .72, ("RC", "de"): .28}),
    ("Lwówek Śląski", "Löwenberg", "DE_LEG", 51.11, 15.59, 60, {("PR", "de"): .78, ("RC", "de"): .22}),
    ("Głogów", "Glogau, Freystadt, Sprottau", "DE_LEG", 51.66, 16.08, 155,
     {("PR", "de"): .70, ("RC", "de"): .296, ("JW", "de"): .004}),
    ("Zielona Góra", "Grünberg, Sagan", "DE_LEG", 51.94, 15.51, 125, {("PR", "de"): .82, ("RC", "de"): .18}),
    ("Bolesławiec", "Bunzlau, Lauban, Görlitz east of the Neisse", "DE_LEG", 51.26, 15.57, 135,
     {("PR", "de"): .85, ("RC", "de"): .15}),
    # Brandenburg east of the Oder and Neisse
    ("Gorzów Wielkopolski", "Landsberg, Friedeberg, Soldin", "DE_NMK", 52.73, 15.24, 203,
     {("PR", "de"): .93, ("RC", "de"): .065, ("JW", "de"): .005}),
    ("Kostrzyn", "Küstrin, Königsberg Nm., Oststernberg", "DE_NMK", 52.59, 14.65, 118, {("PR", "de"): .945, ("RC", "de"): .055}),
    ("Choszczno", "Arnswalde", "DE_NMK", 53.17, 15.42, 50, {("PR", "de"): .95, ("RC", "de"): .05}),
    ("Świebodzin", "Züllichau-Schwiebus, Crossen, Weststernberg", "DE_NMK", 52.25, 15.53, 120,
     {("PR", "de"): .80, ("RC", "de"): .20}),
    ("Żary", "Sorau, Guben east of the Neisse", "DE_NMK", 51.64, 15.14, 105, {("PR", "de"): .90, ("RC", "de"): .10}),
    # Grenzmark Posen-Westpreußen
    ("Piła", "Schneidemühl, Netzekreis, Deutsch Krone", "DE_GRZ", 53.15, 16.74, 175,
     {("PR", "de"): .55, ("RC", "de"): .43, ("JW", "de"): .005, ("RC", "pl"): .015}),
    ("Złotów", "Flatow, Schlochau", "DE_GRZ", 53.36, 17.04, 110,
     {("RC", "de"): .50, ("PR", "de"): .38, ("RC", "pl"): .10, ("RC", "csb"): .02}),
    ("Międzyrzecz", "Meseritz, Schwerin, Bomst, Fraustadt", "DE_GRZ", 52.44, 15.58, 125,
     {("PR", "de"): .55, ("RC", "de"): .42, ("RC", "pl"): .03}),
    # RB Köslin
    ("Słupsk", "Stolp", "DE_KOS", 54.46, 17.03, 126,
     {("PR", "de"): .97, ("RC", "de"): .021, ("JW", "de"): .004, ("RC", "csb"): .005}),
    ("Lębork", "Lauenburg, Bütow", "DE_KOS", 54.54, 17.75, 105,
     {("PR", "de"): .80, ("RC", "de"): .10, ("RC", "csb"): .06, ("RC", "pl"): .04}),
    ("Koszalin", "Köslin, Kolberg-Körlin", "DE_KOS", 54.19, 16.17, 158, {("PR", "de"): .96, ("RC", "de"): .04}),
    ("Szczecinek", "Neustettin, Rummelsburg", "DE_KOS", 53.71, 16.70, 115, {("PR", "de"): .93, ("RC", "de"): .07}),
    ("Białogard", "Belgard, Schivelbein, Dramburg", "DE_KOS", 54.01, 15.99, 125, {("PR", "de"): .96, ("RC", "de"): .04}),
    ("Sławno", "Schlawe", "DE_KOS", 54.36, 16.68, 75, {("PR", "de"): .97, ("RC", "de"): .03}),
    # Stettin and the RB Stettin east of the Oder
    ("Szczecin", "Stettin (and Randow east of the Oder)", "DE_SZC", 53.43, 14.55, 311,
     {("PR", "de"): .90, ("RC", "de"): .092, ("JW", "de"): .008}),
    ("Świnoujście", "Swinemünde, Wollin", "DE_SZC", 53.91, 14.25, 46, {("PR", "de"): .95, ("RC", "de"): .05}),
    ("Stargard", "Saatzig, Pyritz, Greifenhagen", "DE_SZC", 53.34, 15.05, 153, {("PR", "de"): .94, ("RC", "de"): .06}),
    ("Nowogard", "Naugard, Regenwalde", "DE_SZC", 53.67, 15.12, 106, {("PR", "de"): .96, ("RC", "de"): .04}),
    ("Gryfice", "Greifenberg, Cammin", "DE_SZC", 53.92, 15.20, 85, {("PR", "de"): .96, ("RC", "de"): .04}),
    # Warmia
    ("Olsztyn", "Allenstein (city and county)", "DE_WAR", 53.78, 20.49, 110,
     {("RC", "de"): .62, ("RC", "pl"): .22, ("PR", "de"): .144, ("JW", "de"): .006, ("PR", "pl"): .01}),
    ("Reszel", "Rößel", "DE_WAR", 54.05, 21.15, 50, {("RC", "de"): .82, ("RC", "pl"): .10, ("PR", "de"): .08}),
    ("Lidzbark Warmiński", "Heilsberg", "DE_WAR", 54.13, 20.58, 53, {("RC", "de"): .93, ("PR", "de"): .06, ("RC", "pl"): .01}),
    ("Braniewo", "Braunsberg", "DE_WAR", 54.38, 19.82, 55, {("RC", "de"): .90, ("PR", "de"): .10}),
    # Masuria
    ("Ostróda", "Osterode", "DE_MAZ", 53.70, 19.97, 75,
     {("PR", "de"): .72, ("PR", "pl"): .10, ("RC", "de"): .14, ("RC", "pl"): .04}),
    ("Nidzica", "Neidenburg", "DE_MAZ", 53.36, 20.43, 55,
     {("PR", "de"): .60, ("PR", "pl"): .26, ("RC", "de"): .08, ("RC", "pl"): .06}),
    ("Szczytno", "Ortelsburg", "DE_MAZ", 53.56, 21.00, 70,
     {("PR", "de"): .60, ("PR", "pl"): .30, ("RC", "de"): .07, ("RC", "pl"): .03}),
    ("Pisz", "Johannisburg", "DE_MAZ", 53.63, 21.81, 50,
     {("PR", "de"): .63, ("PR", "pl"): .30, ("RC", "de"): .05, ("RC", "pl"): .02}),
    ("Ełk", "Lyck", "DE_MAZ", 53.83, 22.36, 55, {("PR", "de"): .71, ("PR", "pl"): .235, ("RC", "de"): .05, ("JW", "de"): .005}),
    ("Olecko", "Oletzko (Treuburg)", "DE_MAZ", 54.04, 22.50, 38, {("PR", "de"): .80, ("PR", "pl"): .15, ("RC", "de"): .05}),
    ("Mrągowo", "Sensburg", "DE_MAZ", 53.86, 21.30, 50,
     {("PR", "de"): .72, ("PR", "pl"): .19, ("RC", "de"): .065, ("RC", "pl"): .025}),
    ("Giżycko", "Lötzen", "DE_MAZ", 54.04, 21.76, 45, {("PR", "de"): .81, ("PR", "pl"): .14, ("RC", "de"): .05}),
    ("Węgorzewo", "Angerburg", "DE_MAZ", 54.21, 21.75, 30, {("PR", "de"): .92, ("PR", "pl"): .03, ("RC", "de"): .05}),
    ("Gołdap", "Goldap", "DE_MAZ", 54.31, 22.30, 40, {("PR", "de"): .93, ("PR", "pl"): .02, ("RC", "de"): .05}),
    # Elbing and the Oberland
    ("Elbląg", "Elbing (city and county)", "DE_OBL", 54.16, 19.40, 112,
     {("PR", "de"): .86, ("RC", "de"): .125, ("JW", "de"): .005, ("RC", "pl"): .01}),
    ("Pasłęk", "Preußisch Holland", "DE_OBL", 54.06, 19.66, 40, {("PR", "de"): .93, ("RC", "de"): .07}),
    ("Morąg", "Mohrungen", "DE_OBL", 53.92, 19.93, 54, {("PR", "de"): .90, ("RC", "de"): .08, ("PR", "pl"): .02}),
    ("Kętrzyn", "Rastenburg", "DE_MAZ", 54.08, 21.38, 55, {("PR", "de"): .88, ("RC", "de"): .115, ("JW", "de"): .005}),
    ("Bartoszyce", "Bartenstein, Preußisch Eylau and Gerdauen (south)", "DE_MAZ", 54.25, 20.81, 50,
     {("PR", "de"): .87, ("RC", "de"): .13}),
    # the Marienwerder plebiscite area
    ("Kwidzyn", "Marienwerder east of the Vistula", "DE_MAR", 53.73, 18.93, 60,
     {("PR", "de"): .68, ("RC", "de"): .245, ("RC", "pl"): .07, ("JW", "de"): .005}),
    ("Sztum", "Stuhm", "DE_MAR", 53.92, 19.03, 38, {("RC", "pl"): .32, ("RC", "de"): .45, ("PR", "de"): .23}),
    ("Iława", "Rosenberg", "DE_MAR", 53.60, 19.57, 52,
     {("PR", "de"): .87, ("RC", "de"): .10, ("RC", "pl"): .02, ("PR", "pl"): .01}),
    ("Malbork", "Marienburg", "DE_MAR", 54.04, 19.03, 63,
     {("PR", "de"): .55, ("RC", "de"): .42, ("RC", "pl"): .025, ("JW", "de"): .005}),
    # the Free City of Danzig
    ("Gdańsk", "Danzig (city)", "DZ_GDA", 54.35, 18.65, 256,
     {("PR", "de"): .55, ("RC", "de"): .33, ("RC", "pl"): .055, ("JW", "de"): .025, ("JW", "yi"): .015,
      ("RC", "csb"): .005, ("OT", "oth"): .02}),
    ("Sopot", "Zoppot", "DZ_GDA", 54.44, 18.56, 31, {("PR", "de"): .62, ("RC", "de"): .30, ("RC", "pl"): .04, ("JW", "de"): .04}),
    ("Pruszcz Gdański", "Danziger Höhe, Danziger Niederung", "DZ_GDA", 54.26, 18.64, 60,
     {("PR", "de"): .50, ("RC", "de"): .38, ("RC", "pl"): .07, ("RC", "csb"): .05}),
    ("Nowy Dwór Gdański", "Großes Werder", "DZ_GDA", 54.21, 19.12, 40, {("PR", "de"): .80, ("RC", "de"): .20}),
    # Cieszyn Silesia west of the Olza
    ("Karwina", "Fryštát (Frysztat)", "CS_CIE", 49.85, 18.54, 125,
     {("RC", "cs"): .48, ("PR", "cs"): .03, ("RC", "pl"): .21, ("PR", "pl"): .09, ("RC", "de"): .07, ("PR", "de"): .01,
      ("JW", "de"): .01, ("JW", "yi"): .01, ("RC", "oth"): .02}),
    ("Czeski Cieszyn", "Český Těšín and Jablunkov", "CS_CIE", 49.75, 18.63, 91,
     {("RC", "pl"): .25, ("PR", "pl"): .20, ("RC", "cs"): .38, ("PR", "cs"): .04, ("RC", "de"): .07, ("PR", "de"): .02,
      ("JW", "de"): .015, ("JW", "yi"): .01, ("RC", "oth"): .015}),
    ("Frydek", "Frýdek", "CS_CIE", 49.68, 18.35, 95,
     {("RC", "cs"): .80, ("PR", "cs"): .04, ("RC", "pl"): .05, ("PR", "pl"): .02, ("RC", "de"): .08, ("JW", "de"): .01}),
    # Upper Orava and Zamagurie
    ("Namiestów", "Upper Orava (Námestovo, Trstená)", "CS_SPO", 49.41, 19.48, 38,
     {("RC", "pl"): .68, ("RC", "cs"): .27, ("JH", "yi"): .03, ("RC", "de"): .01, ("RC", "oth"): .01}),
    ("Spiska Stara Wieś", "Zamagurie and Ždiar", "CS_SPO", 49.38, 20.37, 22,
     {("RC", "pl"): .55, ("RC", "cs"): .30, ("GC", "rue"): .07, ("JH", "yi"): .03, ("RC", "de"): .04, ("PR", "de"): .01}),
]

# region totals at the end of 1931 (the 1933 census, Danzig 1929 grown, Czechoslovakia 1930)
REGION_POP = {"DE_OPO": 1_483_000, "DE_WRO": 1_955_000, "DE_LEG": 970_000, "DE_NMK": 640_000, "DE_GRZ": 337_000,
              "DE_KOS": 690_000, "DE_SZC": 700_000, "DE_WAR": 268_000, "DE_MAZ": 613_000, "DE_OBL": 206_000,
              "DE_MAR": 213_000, "DZ_GDA": 410_000, "CS_CIE": 311_000, "CS_SPO": 60_000}

# the Upper Silesian plebiscite area left out three western counties of RB Oppeln;
# the Allenstein area left out Heilsberg, Braunsberg, Angerburg and Goldap
OUTSIDE_PLEBISCITE = ["Nysa", "Grodków", "Niemodlin", "Lidzbark Warmiński", "Braniewo", "Węgorzewo", "Gołdap",
                      "Kętrzyn", "Bartoszyce"]


def _unit(seat: str):
    return next(u for u in UNITS if u[0] == seat)


def unit_population(seat: str) -> float:
    u = _unit(seat)
    tot = sum(v[5] for v in UNITS if v[2] == u[2])
    return REGION_POP[u[2]] * u[5] / tot


def unit_groups(seat: str) -> dict[tuple[str, str], float]:
    sh = _unit(seat)[6]
    s = sum(sh.values())
    return {k: v / s for k, v in sh.items()}


def unit_languages(seat: str) -> dict[str, float]:
    """Persons by home language at the end of 1931 (county seed, ``data.counties``)."""
    pop = unit_population(seat)
    out: dict[str, float] = {}
    for (_, l), v in unit_groups(seat).items():
        key = l if l in ("pl", "uk", "yi", "be", "ru", "lt", "de") else "oth"
        out[key] = out.get(key, 0.0) + v * pop
    return {k: round(v) for k, v in out.items()}


def region_groups(code: str) -> dict[tuple[str, str], float]:
    out: dict[tuple[str, str], float] = {}
    for u in UNITS:
        if u[2] != code:
            continue
        w = unit_population(u[0]) / REGION_POP[code]
        for k, v in unit_groups(u[0]).items():
            out[k] = out.get(k, 0.0) + v * w
    return out


def region_population(code: str) -> float:
    return float(REGION_POP[code])
