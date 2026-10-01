# Data sources, provenance and reliability

Every numeric input is graded:

* **A**: a published figure used as printed.
* **B**: reconstructed from published tables. Rounded, or cross-read between
  tables, so it may differ from the original by a few tenths of a point.
* **C**: an estimate or assumption, with the range it was taken from.

Where the sources disagree, the model carries the disagreement as an explicit
option instead of picking one number (see *Census reliability* below).

## Population and composition, Poland 1931

| Input | Value | Grade | Source / note |
|---|---|---|---|
| Population by voivodeship | 17 units, total 31,915,779 | A | GUS, 2nd general census (9 Dec 1931), 1931 borders |
| Area by voivodeship | total 388.6 k km² | A/B | GUS |
| Mother tongue by voivodeship | e.g. Wołyń: Ukrainian 68.0 %, Polish 16.6 %, Yiddish 8.3 %, Hebrew 1.5 %, German 2.2 %, Czech 1.5 %, Russian 1.1 %; Tarnopol: Polish 789,114, Ukrainian 401,963, Ruthenian 326,172, Yiddish 71,890, Hebrew 7,042; Polesie: tutejszy 62.5 %, Polish 14.5 %, Yiddish/Hebrew 10.0 % | A (these units) / B (others, rounded) | GUS voivodeship volumes; reproduced within ~0.5 pt of national totals (tests) |
| Religion by voivodeship | e.g. Warsaw 30.1 % Jewish | B | GUS; approximate for several units. National totals reproduced: RC 64.8 %, GC 10.4 %, Orthodox 11.8 %, Jewish 9.8 %, Protestant 2.6 % |
| Urban share | national 27.4 % | A (national) / B (regional) | GUS; regional values rescaled to the national figure |
| Kashubian speakers | 200 k | C | range in the literature ~150 k - 500 k; not enumerated in 1931 |
| Lemkos | ~130 k (incl. ~16-18 k Orthodox) | B | 130,121 from studies based on the 1931 census; 145 k in the Lemko Apostolic Administration (1935), 18 k of them Orthodox |
| Wymysorys | 1,500 | C | Wilamowice: 92 % of 1,662 inhabitants (1880), 72 % (1890) |
| Karaim | ~630 speakers (community 800-900) | B/C | Trakai (Troki) community 203 (1922) -> 300-350 (late 1920s); Łuck ~65; Halicz/Lwów ~150 |
| Romani | ~30 k | C | not enumerated; estimates for interwar Poland |
| Haredi share of Yiddish speakers | 25-40 % by partition | C | proxied from Agudat Israel's electoral weight and Hasidic geography |

## Lithuania

| Input | Value | Grade | Source / note |
|---|---|---|---|
| 1923 census | 2,028,971 (without Klaipėda); Lithuanians 84.2 %, Jews 7.6 %, Poles 3.2 % (65,599), Russians 2.5 %, Germans 1.4 %, Latvians 0.7 % | A | 1923 Lithuanian census |
| Klaipėda 1925 | 141,645; German 43.5 %, Lithuanian 27.6 %, "Klaipėdan" 25.2 % | A | 1925 census (declared language) |
| Polish claim, 1923 | 202,026 (~10 %) | A (as a claim) | Polish Election Committee, from 1923 election returns |
| Population 1938 | 2.563 M | A | Lithuanian vital statistics |
| CBR / CDR | 25.5 / 13.4 (1933); 22.6 / 12.6 (1938) | A | ditto |
| Regional breakdown into 6 units | shares by group | C | built from county-level patterns (Poles in Kaunas/Lauda/NE, Old Believers in Zarasai/Rokiškis, Latvians and Reformed in Biržai, Germans in Suvalkija and Klaipėda) |
| Kaunas city | 92 k (1923) -> 154 k (1939) | A | |

## Imperial Russian census, 1897 (native language)

| Governorate | Figures used | Grade |
|---|---|---|
| Vilna | 1,591,207; Belarusian 56.05 %, Lithuanian 17.58 %, Jewish 12.72 %, Polish 8.17 % | A |
| Volhynia | Ukrainian 70.26 %, Jewish 13.24 %, Polish 6.17 %, Russian 3.52 % | A |
| Kovno | 1,544,564; Jewish 13.7 %; Polish ~9 % | A/B |
| Grodno (Bielsk uezd) | Ukrainian 39.1 %, Polish 34.9 %, Yiddish 14.9 % | A |

These numbers anchor the `vernacular` reconstruction and the `imperial_1897`
observation regime.

## Census reliability

| Issue | Evidence | How the model handles it |
|---|---|---|
| Mother tongue replaced nationality (1921 -> 1931) | 1921 recorded 3.90 M Ruthenians/Ukrainians and 1.04 M Belarusians by nationality; 1931 recorded 3.22 M Ukrainian + 1.22 M Ruthenian and 0.99 M Belarusian by mother tongue | latent home vernacular + `CensusRegime` observation model |
| "Tutejszy" and "ruski" categories | 707 k "local" (62.5 % of Polesie); 1.22 M "Ruthenian" | Polesians carried as a vernacular (`pls`); census view reproduces the categories |
| Polish-declared Orthodox and Greek Catholics | visible in the language x religion cross-read (e.g. Nowogródek 52 % Polish-speaking vs ~40 % Catholic) | `religion_corrected` variant |
| Possible tampering | admission by E. Szturm de Sztrem (census office head) after WW2 | variants bracket the range |
| Tomaszewski correction | ethnic Poles 64.7 %, Jews 9.8 %, others 25.5 % | reproduced by `religion_corrected` (tests) |
| Kubijovyč (Galicia, 1939) | larger Ukrainian counts, ~360 k latynnyky in Podlachia/Chełm/Lublin; rounded village figures | `vernacular` variant (upper bound) |
| Lithuania: Poles under-counted? | 65.6 k (census) vs 202 k (Polish claim) vs ~9 % Polish in 1897 Kovno governorate | `lt_variant` |
| Under-registration of deaths in the east | modelled CDR ~1 pt above registered | stated in the validation table |

## Vital rates and life tables

| Input | Value | Grade | Source |
|---|---|---|---|
| Life expectancy 1931-32 | m 48.2, f 51.4 | A | GUS life table 1931-32 (also in the Human Life-Table Database) |
| TFR by religion, 1931 | RC 3.28 (west), 3.57 (central), 3.68 (Kraków), 3.33 (Lwów); Jewish 2.48 / 2.67 / 2.89 | A | study of fertility levels in selected territories of Poland in 1931 |
| CBR / CDR, Poland | 1932 ~28.8 / 15.0; 1938 ~24.3 / 13.8 | B | *Mały Rocznik Statystyczny* series (rounded) |
| Population 1939 | 35.1 M (GUS estimate) | A | probably slightly high |
| Regional TFR / e0 1931 | see `plsim/data/regions.py` | C | set from regional crude rates and religion-specific TFRs, calibrated to national aggregates |

## Economy and transport

| Input | Value | Grade | Source |
|---|---|---|---|
| GDP per head 1931 | 1,800 (1990 GK$) | B/C | Maddison-consistent (Poland 1929 ~2,100; Depression trough) |
| Western frontier 1931 | 4,300 | B | Maddison western-European average |
| Motor vehicles, 1 Jan 1938 | 44,200 (incl. 9,876 motorcycles); 0.7 cars per 1000 in 1935 | A | GUS |
| Railway network | stylised ~15 k route-km of the ~20 k km operated in 1938 | C | reconstruction; see `plsim/data/network.py` |
| Coal Trunk Line | Herby Nowe-Karsznice 1930, complete 1933 | A | |
| Warszawa-Radom | opened 1934 | A | |
| Kutno-Konin-Strzałkowo | begun 1924 | A | |
| Unfinished in 1939 | Łapy-Ostrołęka-Przasnysz-Mława; Dębica-Pilzno-Jasło | A | |
| Kužiai-Telšiai-Kretinga | built 1924-1932 | A | |
| Lithuanian narrow gauge | 750 mm network, ~111 km (Aukštaitija) | A | |
| COP | established 1 Jul 1936; 2.4 bn zł; ~60 % of 1937-39 investment | A | |
| Fifteen-Year Plan (1939-54) | five stages; stage II (1942-45) transport; the final stage aimed at erasing Poland A/B | A | Kwiatkowski, Sejm, 2 Dec 1938 |
| Nestorowicz road plan | ~5,000 km category I/II roads (5 Mar 1939) | A | |
| Regional income gradient | e.g. Silesia 1.9x, Polesie 0.48x the Polish average | C | reconstructed "Polska A/B" gradient |

## Language-shift calibration anchors

| Anchor | Value | Grade |
|---|---|---|
| Soviet Jews declaring Yiddish | 70.4 % (1926) -> ~40-41 % (1939); Belorussian SSR 55 % (1939) | A |
| Wymysorys | 92 % (1880) -> 72 % (1890) of Wilamowice | A |
| Scottish Gaelic shift rate | ~0.035 per year (Sutherland 1891-1971, Kandler et al. 2010) | A |
| Abrams-Strogatz exponent | a ~ 1.31 | A |
| Spatial shift kernel (maps) | Gaussian neighbourhood; front velocity 0.11 km/y, D = 0.136 km²/y, k = 0.022/y (southern Carinthia, 1 km grid) | A | Prochazka & Vogl 2017, PNAS 114: 4365 |

## Geography (maps only)

| Item | Value | Grade | Source / note |
|---|---|---|---|
| Coastline, lakes, rivers | GSHHS / World Data Bank II, intermediate resolution, clipped to 13.5-30.5 E, 47.3-57.2 N | A | basemap-data 2.0; `plsim/data/geo_base.json` |
| State territory (1938) | land cells nearest to a domestic town; about 110 foreign "mask" towns trace the borders with Germany, Danzig, East Prussia, Latvia, the USSR, Romania and Czechoslovakia | C | no digital interwar boundary layer was reachable; total cell area about 5 % below the official area |
| Voivodeship borders | weighted Voronoi of county towns, with weights calibrated to the official areas | C | approximate shapes, exact areas (±5 %) |
| County language anchors, 1931 (25) | e.g. Sokal 55.0 % Ukrainian, Turka 70.3 %, Lesko 63.0 %, Lubaczów 43.8 %, Przemyśl 36.9 %, Jarosław 14.2 %, Łuck 59.2 %, Kostopol 64.3 %, Krzemieniec 80.7 %, Kamień Koszyrski 8.7 % Ukrainian, Nieśwież 67.4 % Belarusian, Baranowicze 43.9 %, Mołodeczno 53.7 %, Wilejka 49.8 %, Bielsk 34.8 %, Grodno 32.8 %, Lida 11.2 %, Oszmiana 9.7 % | A | 1931 county tables as quoted in secondary sources |
| Other county anchors (190, incl. Szczuczyn at grade B) | Kashubian counties (not enumerated in 1931), German colonies in Poznań, Pomorze, Łódź and Volhynia, Lemko districts, Old Believers, Latvians, Lauda; zero anchors for counties without a minority | C | shape the pattern inside a voivodeship only; regional totals come from the census reconstruction |
| Terrain thinning | Polesie marshes -40 %, Carpathians -35 %, Hutsul highlands -30 % rural density | C | |

## Counties, 1931 (county-level runs)

`plsim/data/counties.py` holds the 269 county seats used by
`partition: counties`. That is every 1931 powiat outside Warsaw city, plus
the Lithuanian apskritys outside Kaunas city. The grade says what is known
about each county besides its seat.

| Voivodeship | Counties | Grade | What is known | Source / check |
|---|---|---|---|---|
| Tarnopol | 17 | A | population, mother tongue | Polish Wikipedia voivodeship article, from the 1931 census (Statystyka Polski, seria C); reproduces the voivodeship totals exactly |
| Stanisławów | 12 | A | population, mother tongue | ditto (1932 county division); exact |
| Lwów | 25 A + 1 B | A | population, mother tongue | ditto; Lwów city merged into powiat lwowski (455,031: Polish 278,924, Ukrainian 93,532, Yiddish 76,885); population within 0.3 %, but Polish and Ukrainian are about 35 k and 27 k off the voivodeship totals (rounding in the source tables) |
| Volhynia | 11 | A | population, mother tongue | ditto |
| Wilno | 7 A + 1 B | A | population, mother tongue | ditto; Wilno city merged into wileńsko-trocki (409,543, grade B) |
| Białystok | 12 | A | population, mother tongue | ditto; Białystok city merged into białostocki (231,179). The Augustów Yiddish figure is derived from the voivodeship residual |
| Nowogródek | 8 | A | population, mother tongue; Orthodox and Roman Catholic for 5 | English Wikipedia, "Belarusians in Poland" (county table). Belarusian, tutejszy and Russian are given as one category, which the model splits by the downscaled pattern |
| Polesie | 5 A + 4 B | A/B | as Nowogródek where found (Kamień Koszyrski, Kosów, Pińsk, Prużana, Stolin); population only for the rest | ditto |
| Lublin | 13 B + 5 C | B | population (Biała includes Konstantynów, 174,460) | 1931 administrative tables, rounded |
| Kraków, Kielce, Łódź, Warsaw, Poznań, Pomorze, Silesia | 136 | C | seat only | the county language tables were not reachable from this environment |
| Lithuania (apskritys, 1923) | 22 | C | seat only | ditto; the 1923 census apskritis tables |

How the table enters the model is described in `docs/METHODOLOGY.md` §12.6.
In short:

* **Fitting.** County figures are fitted to the voivodeship totals of the
  selected census variant by iterative proportional fitting. A county table
  therefore decides *where* speakers live, not how many there are.
* **Data repairs.** A few published rows do not add up. Rohatyń's
  languages exceed its population by 0.7 %. Przeworsk's Polish count was
  recomputed from its percentage (58,632). Rawa Ruska's total was estimated
  (121,800). The "other" languages of Dolina (4,013) and Horodenka (16) are
  German.

The county table also corrected one of the older anchors in
`data.geography`. The "Szczuczyn" anchor had Belarusian at 0.2 %, which
is the figure for Szczuczyn near Grajewo (Białystok voivodeship). The
Nowogródek county of that name had 9.9 % Belarusian + tutejszy + Russian
and 83.5 % Polish, and the anchor now uses that.
