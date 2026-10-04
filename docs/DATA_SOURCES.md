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

## Soviet Belarus, 1926 (only `wakar_poland_belarus`)

The Byelorussian SSR in its borders of December 1926, as four voivodeships of
a Polish state (`plsim/data/bssr.py`; method in METHODOLOGY §12.7).

| Input | Value | Grade | Source / note |
|---|---|---|---|
| Population and nationality by okrug, 17 Dec 1926 | 12 okrugs, 4,983,240 people; Belarusians 80.6 %, Jews 8.2 %, Russians 7.7 %, Poles 2.0 %, Ukrainians 0.7 % (e.g. Minsk okrug 539.7 k: 79.8 % Belarusian, 13.1 % Jewish; Homel 408.1 k: 47.7 % Belarusian, 36.9 % Russian) | A | 1926 all-Union census, as tabulated by Latysheva, "Perepisi naseleniya 1897 i 1926 gg." (BSU, *Istochnik* 5), read through search summaries; okrug totals add up to the census total |
| Native language | Yiddish for 90.7 % of Jews; Belarusian for 93.9 % of rural and 54.1 % of urban Belarusians; Polish for a third (Minsk okrug) to just under half (Vitebsk) of Poles | B | 1926 census, via Demoscope Weekly, Koryakov (2002, *Voprosy yazykoznaniya*) and regional studies of the Polish minority |
| Russians in Homel and Rzeczyca | two thirds counted as Belarusian speakers | C | assumption: these okrugs joined the BSSR a week before the census, and their "Russian" share falls below 10 % in later censuses of the same lands |
| Growth 1926-31 | x 1.075 | C | natural increase of the Polish north-east; the counterfactual has these lands Polish from 1921 |
| Areas of the voivodeships | 29-33 k km² each (125.8 k km² in all) | C | Voronoi of okrug centres on the 1932 territory; Mozyr okrug: 15.6 k km² in 1926 |
| Incomes, vital rates, literacy, urban shares | as Wilno, Nowogródek and Polesie | C | assumption |
| Towns and railways | 24 towns (1926 populations grown to 1931; Mińsk 240 k, Witebsk 106 k, Homel 93 k), the c. 1931 main lines | B | 1926 census town populations; standard railway histories |

## Governorates of 1897 and the krai's eastern lands (only `nw_krai`, `lit_bel`)

The scenarios drawn on the old imperial borders (METHODOLOGY §12.1, §12.5,
§12.7; `plsim/data/governorates.py`, `plsim/data/krai_east.py`).

| Input | Value | Grade | Source / note |
|---|---|---|---|
| Governorate borders, 1897 | Vilna, Kovno, Grodno, Minsk, Mogilev, Vitebsk and Suwałki governorates (and the uezds of Vitebsk and Mogilev for the land outside the 1932 states), simplified to about 300 m | A | Electronic Repository of Russian Historical Statistics (RISTAT), "Russian Empire Historical GIS Maps (1897)", IISG Dataverse hdl:10622/DN9QDM, CC0; read from the GeoJSON republished in github.com/Baushkiner/history_stats (the Dataverse host was blocked). `tools/build_governorates.py`. Checked at 25 places (Włodawa west of the Bug, Brest east of it, Tykocin in the Łomża governorate, Garliava south of the Niemen in Suwałki ...) |
| The krai outside the 1932 states | 31,600 km²: Latgale 14,200, Nevel-Sebezh-Velizh 12,400, east Mogilev 4,600 | B | the governorates minus Poland, Lithuania and the BSSR of 1932 (CShapes / Natural Earth); pieces under 150 km² (border slivers) dropped |
| Uezd populations and native languages, 1897 | Dvinsk 237,023 (39.0 % Latvian, 20.0 Yiddish, 15.3 Russian, 13.8 Belarusian, 9.1 Polish); Rezhitsa 136,445 (57.9 Latvian, 23.9 Russian); Lyutsin 128,155 (64.2 Latvian, 20.5 Belarusian); Nevel 110,394 (84.0 Belarusian); Sebezh 92,055 (47.1 Russian, 47.1 Belarusian); Velizh 100,079 (85.7 Belarusian, 9.8 Yiddish) | A | 1897 census, as quoted in the English Wikipedia uezd articles (read through search summaries; Demoscope was blocked) |
| Latgale in 1935 | 567,000 people (27,974 Jews = 4.93 %); Daugavpils city 45,100, Rēzekne 13,139, Ludza 5,546 | A | Latvian census of 1935, via secondary sources |
| Growth to 1931, strips, east Mogilev | Latgale x 1.02; Russian lands x 1.22; Drissa strip 12,000, Gorodok strip 14,000; east Mogilev 35 per km² in 1897 | C | estimates (see `data/krai_east.py`) |
| Military settlers by voivodeship (settlement destinations) | Wołyń 41.5 %, Nowogródek 21.7 %, Wilno 13.3 %, Polesie 12.6 %, Białystok 10.9 % of households | B | osadnicy.org, kresy24.pl, polesie.org (from the interwar settlement statistics) |

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
| Polish-declared Orthodox and Greek Catholics | visible in the language x religion cross-read (e.g. Nowogródek 52 % Polish-speaking vs ~40 % Catholic) | `religion_corrected`, the baseline |
| Possible tampering | admission by E. Szturm de Sztrem (census office head) after WW2 | variants bracket the range |
| Tomaszewski correction | ethnic Poles 64.7 %, Jews 9.8 %, others 25.5 %; Ukrainians 5.11 M, Belarusians 1.95 M, Germans 0.78 M | reproduced by `religion_corrected`, the baseline (tests) |
| Kubijovyč (Galicia, 1939) | 5.85 M Ukrainians in Poland (1931); 515 k latynnyky in Galicia; rounded village figures | `vernacular` variant (upper bound), calibrated to these |
| Lithuania: Poles under-counted? | 65.6 k (census) vs ~150 k (middle estimate) vs 202 k (Polish claim) vs ~9 % Polish in 1897 Kovno governorate | `lt_variant` (baseline: ~150 k) |
| Under-registration of deaths in the east | modelled CDR ~1 pt above registered | stated in the validation table |

## The 1931 starting point: census or research estimates?

The baseline no longer starts from the census as printed. It starts from the
mainstream scholarly correction of the 1931 census (Tomaszewski 1985), which
reads religion together with language. The printed census and the maximal
estimates are kept as alternative scenarios (`census_official`,
`census_vernacular`).

**Why not the census?**

* **Language, not nationality.** The 1931 census asked for mother tongue
  rather than nationality. It offered "ruski" beside "ukraiński", and
  "tutejszy" ("local") absorbed most of Polesie.
* **Polish-declared Greek Catholics and Orthodox.** In the language x
  religion cross-read, about 330 k Greek Catholics in eastern Galicia and
  about 500 k Orthodox in the north-east, Lublin and Polesie were recorded as
  Polish-speaking.
* **Admitted tampering.** The head of the statistical office, E. Szturm de
  Sztrem, later admitted that the administration may have altered forms.

**Estimates in the literature, and what the model uses**

| | 1931 census (language) | Tomaszewski 1985 | Kubijovyč 1983 | Other | Baseline (`religion_corrected`) | Upper bound (`vernacular`) |
|---|---|---|---|---|---|---|
| Ukrainians (with "Ruthenians", Lemkos) | 4.44 M | 5.11 M | 5.85 M (inflated per Polish historians) | | 4.98 M + share of West Polesian | 5.50 M (5.86 M with half the West Polesian) |
| Belarusians | 0.99 M | 1.95 M | | most historians 1.7–2.0 M | 1.34 M + share of West Polesian | 1.83 M |
| "Tutejszy" / West Polesian | 0.71 M | split between the two | | | 0.71 M, kept as a vernacular | 0.71 M |
| Ukrainians + Belarusians + West Polesian | 6.17 M | 7.07 M | | | 7.03 M | 8.15 M |
| Ethnic Poles | 68.9 % by language | 64.7 % | | | 64.7 % | 61.4 % |
| Jews | 2.73 M Yiddish/Hebrew; 3.11 M by religion | 3.11 M (9.8 %) | | | 3.13 M | 3.13 M |
| Germans | 0.74 M | 0.78 M | | | 0.785 M | 0.785 M |
| Latin-rite Ukrainian speakers (latynnyky) | counted as Polish | counted as Poles | 515 k in Galicia (1939) | | not separated | 524 k |
| Poles in Lithuania | 65.6 k (1923 census) | | | 202 k (Polish electoral committee, held "very probable" by Buchowski 1999); ~150 k (middle estimate) | ~150 k (`lt_variant: research`) | 160 k (1897 shares) |

**How the baseline is built**

* **Greek Catholics and Orthodox.** Of those declared Polish, 95 % are
  reassigned to Ukrainian or Belarusian home language by region (Tomaszewski
  counts them all; Kubijovyč finds only 16 k Polish-speaking Greek Catholics
  in 1939).
* **Protestants.** 30 % of Polish-declared Protestants outside Cieszyn
  Silesia and Warsaw are reassigned to German.
* **The Lemko and Kashubian carve-outs** are unchanged.
* **Lithuania.** The Polish-speaking population is set at about 150 k, the
  middle of the 65.6 k–202 k range.

These settings reproduce Tomaszewski's totals (tested).

**Check against the printed census.** Passed through the model of how the 1931
census recorded people (`plsim.language.census_mapping`: Catholic Belarusian
speakers mostly recorded as Polish, Greek Catholics split between
"ukraiński", "ruski" and Polish, Polesians as "tutejszy"), the baseline gives
back the printed national shares within 1.0 point in total across eight
categories:

| | Polish | Ukr.+Ruth. | Yiddish+Hebrew | Belarusian | German | Tutejszy |
|---|---|---|---|---|---|---|
| Printed census | 68.9 | 13.9 | 8.6 | 3.1 | 2.3 | 2.2 |
| Baseline, as recorded | 68.7 | 14.1 | 8.5 | 3.2 | 2.2 | 2.2 |

The census is therefore consistent with a population that was considerably
less Polish-speaking at home than it printed.

**What the baseline does not include.** Tomaszewski counts Roman Catholics as
Poles. Ukrainian-speaking Latin-rite Catholics (latynnyky) and
Belarusian-speaking Catholics in the Wilno and Nowogródek lands are
therefore not in the baseline. They are in the upper bound
(`census_vernacular`), at Kubijovyč's level for Galicia and at 1897
proportions in the north-east. Their real number lies between the two.
Regional studies such as Hryciuk (2005) on eastern Galicia and Volhynia
could narrow it.

**Sources**

* Tomaszewski, J. (1985). *Ojczyzna nie tylko Polaków. Mniejszości narodowe w
  Polsce w latach 1918–1939*. Warsaw: MAW.
* Kubijovyč, V. (1983). *Etnichni hrupy pivdennozakhidnoi Ukrainy
  (Halychyny) na 1.1.1939*. Wiesbaden.
* Buchowski, K. (1999). *Polacy w niepodległym państwie litewskim
  1918–1940*. Białystok.
* Eberhardt, P. (2003). *Ethnic Groups and Population Changes in
  Twentieth-Century Central-Eastern Europe*. Armonk: M. E. Sharpe.
* Hryciuk, G. (2005). *Przemiany narodowościowe i ludnościowe w Galicji
  Wschodniej i na Wołyniu w latach 1931–1948*. Toruń.
* The figures were read through secondary summaries (Polish and English
  Wikipedia articles on Ukrainians in the Second Republic, Belarusians in
  Poland, Poles in Lithuania and Kubijovyč; Encyclopedia of Ukraine,
  "Galicia"). The books themselves were not reachable from this
  environment.

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

### History-matching cases (`plsim/calibration.py`)

| Case | Value used | Grade | Source / note |
|---|---|---|---|
| Masurian districts 1890 -> 1910 | Polish/Masurian speakers: Johannisburg 78.8 -> 68.0 %, Lyck 66.6 -> 51 %, Neidenburg 75.6 -> 66.6 %, Oletzko 47.7 -> 29.6 % | B | Prussian censuses by Kreis, as quoted in the literature on the Masurians (e.g. the English Wikipedia article "Masurians"); bilingual answers and German settlement add noise (sd 0.042 with model error) |
| Carinthian Slovenes 1880 -> 1910 | 91,927 (26.4 % of 348,730) -> 74,210-82,212 of 396,200 (sources differ); share ratio 0.75 ± 0.064 | B | Austrian censuses (Umgangssprache, a language-of-use question open to pressure) |
| Wales 1921 -> 1951 | able to speak Welsh 37.1 -> 28.9 % (aged 3+); Welsh only 6.3 -> 1.7 % of the population | A | Censuses of England and Wales (Vision of Britain); 1901: 49.9 %, Welsh only 15.1 % |
| Province of Posen 1871 -> 1910 | Polish share stable or rising; shift net of migration ~0 (ratio 0.99 ± 0.021) | B | Prussian censuses; the rise reflects German out-migration, so the target is the absence of shift |
| Second generation of immigrants | 40 % (Indian) to 76 % (Filipino) of children of immigrants spoke only English at home (1990); 60-70 % of third-generation Hispanics | A | Alba, Logan, Lutz & Stults 2002, *Demography* 39: 467-484; Portes & Rumbaut 2001 |
| Finland Swedes 1880 -> 1950 | 14.3 % -> 8.6 % | A | not used as a target: most of the fall is lower fertility and emigration to Sweden, which the stylised harness does not represent |

### The historical Curzon line (`curzon.HISTORICAL_LINE`)

The Allied declaration of 8 December 1919 and Curzon's note of 11 July 1920:
"Grodno, Vapovka [Jałówka], Nemirov, Brest-Litovsk, Dorogusk, Ustilug, east of
Grubeshov, Krilov, and thence west of Rawa Ruska, east of Przemysl to the
Carpathians" (Britannica; the English Wikipedia article "Curzon Line"; Oxford
Public International Law). The northern section follows the declaration: the
Bug downstream to the Bielsk-Brest district boundary, north-east past
Hajnówka to the source of the Łosośna, the Łosośna and the Niemen past
Grodno, then the Suwałki district boundary to East Prussia. Digitised by hand
from these descriptions (about 10 km); grade C as a line, A as a description.

### Data that could not be obtained here

* **1931 county language tables**: now complete for every Polish
  voivodeship, from the volumes the user supplied (see "Counties, 1931").
* **1931 powiat boundaries.** The MPIDR Population History GIS Collection
  (mosaic.ipums.org) has Poland's 1931 administrative division, but an
  account needs an academic affiliation, so the user could not get it. The
  only GeoJSON powiat sets on GitHub are modern. County borders stay the
  weighted Voronoi approximation; the model accepts a boundary file when one
  is supplied (`plsim/data/powiaty_1931.geojson`, `tools/match_powiaty.py`).
* **1926 Soviet census by raion** (for Soviet Belarus below the okrug): the
  rusneb copy could not be opened by the user either. The supplied *Kratkie
  svodki* vyp. IV (nationality and native language, archive.org) is by
  okrug: its Table III confirms the okrug data of `data.bssr` (Minsk
  539,529 against 539,700 in the model; Vitebsk 583,391; Polotsk 323,861,
  86.1 % Belarusian; Slutsk 309,384; Rechitsa 254,816).
* **1923 Lithuanian apskritis nationality**: the supplied *Lietuvos
  apgyventos vietos* lists settlements and their populations only; the
  nationality tables are in the main results volume.
* **German Kreise, 1933**: the supplied file is the user handbook of the
  GESIS study ZA8013, without its data files; the west lands keep the
  figures of `data.west`.

### Where to download them (for the user; not reachable from the build environment)

| What | Where |
|---|---|
| 1931 census, short results for **every voivodeship, powiat and town** ("wyniki ostateczne ... w postaci skróconej") | MBC: https://mbc.cyfrowemazowsze.pl/dlibra/publication/17019/edition/14481 |
| 1931 census, voivodeship volumes (seria C) | Kraków (Wikimedia Commons): https://commons.wikimedia.org/wiki/File:Woj.krakowskie-Polska_spis_powszechny_1931.pdf · Śląsk (Śląska BC): https://sbc.org.pl/dlibra/publication/556434/edition/522609 · Stanisławów (MBC): https://mbc.cyfrowemazowsze.pl/dlibra/publication/16930/edition/14199 · Kielce (MBC): https://bc.cyfrowemazowsze.pl/publication/16942 · Łódź without the city (MBC): http://mbc.cyfrowemazowsze.pl/dlibra/doccontent?id=14233 · Poznań without the city (KPBC): https://kpbc.umk.pl/dlibra/publication/4893/edition/10837 · Białystok (Podlaska BC): https://pbc.biaman.pl/dlibra/publication/1867/edition/2107/content · Wilno city (Podlaska BC): https://www.pbc.biaman.pl/dlibra/publication/1870/edition/2108 |
| 1931 census forms and instructions | MBC: https://mbc.cyfrowemazowsze.pl/dlibra/publication/edition/14167 |
| **1921 census**: nationality and religion by powiat (voivodeship volumes "mieszkania, ludność, stosunki zawodowe") | Lwów (Podlaska BC): https://pbc.biaman.pl/dlibra/doccontent?id=2280 · the series in GUS's library: https://statlibr.stat.gov.pl/ |
| 1921 *Skorowidz miejscowości* (nationality and religion by locality, a volume per voivodeship) | archive.org: https://archive.org/details/skorowidzmiejsco02pola · Polesie (PBC): https://pbc.biaman.pl/dlibra/publication/2225/edition/3106 · Białystok (PBC): https://pbc.biaman.pl/dlibra/publication/26774/edition/27140 · Lublin (MBC): https://mbc.cyfrowemazowsze.pl/dlibra/publication/17131/edition/14618 · Lwów (Podkarpacka BC): https://www.pbc.rzeszow.pl/dlibra/publication/2501/edition/2330 · Poznań (WBC): https://www.wbc.poznan.pl/dlibra/publication/648193/edition/559067 · Polona: https://polona.pl/preview/ef39d8e9-bd8d-43ab-aeec-f94dd3b04762 |
| **1923 Lithuanian census** (*Lietuvos apgyventos vietos*, by settlement, with the apskritis tables) | archive.org: https://archive.org/details/lietuvos-apgyventos-vietos-1925 · overview: https://lt.wikipedia.org/wiki/1923_m._Lietuvos_gyventoj%C5%B3_sura%C5%A1ymas |
| **1926 Soviet census**, vol. 10 (BSSR), by okrug and raion | rusneb: https://rusneb.ru/catalog/000199_000009_009004429/ · vyp. 4 (nationality and native language): https://archive.org/details/vyp4nariridmova |
| **1931 powiat boundaries** (MPIDR Population History GIS Collection; free registration) | https://mosaic.ipums.org/historical-gis-datafiles |
| German census of 1933 by Kreis (for `data.west`) | GESIS, Falter's Weimar election and census data (Kreise 1920-33): https://access.gesis.org/dbk/67914 · HISTAT: https://histat.safe-frankfurt.de/ · Statistisches Jahrbuch für das Deutsche Reich 1937 (Mannheim): https://digi.bib.uni-mannheim.de/fileadmin/statjahrb/514401303_1937/pdf/514401303_0069.pdf |

A 1921 nationality table by powiat, saved as
`plsim/data/census1921_powiaty.csv` (columns in `plsim/data/census1921.py`),
is read and checked county by county (`plsim.validate.identity_1921`).

## The 1921 nationality census (identity layer)

`plsim/data/census1921.py`. Poland's totals (Polish 69.23 %, Ukrainian and
Ruthenian 15.17, Jewish 7.97, Belarusian 4.03, German 2.99, Russian 0.19,
"tutejszy" 0.15) are from the census summary (Polish and English Wikipedia
articles on the census; GUS). Voivodeship shares of grade A were confirmed
in two places: Volhynia (Ukrainian and Ruthenian 68.4 %, Polish 16.6),
Stanisławów (70.2, 21.8, Jewish 6.8, German 1.1), Tarnopol (Polish 49.3,
Ukrainian and Ruthenian 45.5), Polesie (Belarusian 42.6 %, 375 thousand;
Ruthenian 17.7 %, 156 thousand; Jewish 10.5; "tutejszy" 4.4; Polish 24.3).
Lwów, Nowogródek and Białystok are recalled (grade C) and only reported.
The identity layer's starting mixes for the Orthodox and the Jews were
fitted to the grade-A figures (METHODOLOGY §6.7).

## The German, Danzig and Czechoslovak lands (`plebiscite_poland`, `historical`)

`plsim/data/west.py` (grade E). Region totals: the German census of
16 June 1933 by Regierungsbezirk (RB Oppeln 1.48 M; RB Breslau about
1.96 M; RB Liegnitz east of the Neisse 0.97 M; Brandenburg east of the Oder
0.64 M; Grenzmark 0.34 M; RB Köslin 0.69 M; Stettin and the RB Stettin east
of the Oder 0.70 M; RB Allenstein 552,541 with Oletzko), split at the
Oder-Neisse line by county and among the units by Kreis estimates; Danzig's
1929 census (407,517); the Czechoslovak census of 1930 for Cieszyn Silesia
(Fryštát and Český Těšín 216,255: 76,230 Poles, 120,639 Czechs and 17,182
Germans; Frýdek about 95,000). The 1939 total of the land Poland received
(8.86 M with Danzig) is reproduced to within 0.1 M by the model. Home
language and faith by unit: the 1925 Prussian census (Upper Silesia:
Polish 26.7 %, bilingual 7.6 %; Landkreis Oppeln only 26.1 % German-only),
estimates for Masuria, Warmia, Stuhm and Kashubian Bütow and Lauenburg, and
confessional shares (details in the module docstring). Borders: CShapes 2.0
(Germany and Danzig on 1 Jan 1932, Poland 1946-2019) and hand-drawn
outlines of the Cieszyn, Spiš and Orava plebiscite areas clipped to
Czechoslovakia (`tools/build_west.py`). Towns and lines: 1933 town
populations and the main and secondary railways of c. 1931 (Breslau-Oppeln-
Gleiwitz, the Silesian mountain railway, the Ostbahn, Stettin-Danzig, the
East Prussian lines, the Košice-Bohumín railway).

## The historical scenario (calibration targets and event sizes)

`scenarios/historical.yaml`, `plsim/history_check.py`. Targets: GUS census
populations 1946-2021 and urban shares; GUS total fertility (1950 3.71,
1960 2.98, 1970 2.20 with rural 2.99 and urban 1.67, 1980 2.28 with rural
2.92 and urban 1.93, 1990 2.04 with rural 2.44 and urban 1.77, 2000 1.37);
GUS life tables (1952-53 58.6/64.2, 1960-61 64.8/70.5, 1970-72 66.8/73.8,
1990 66.2/75.2, 2019 74.1/81.8); the 2002 census of nationality and home
language. Event sizes are rounded from the standard accounts: the
Holocaust (about 3 M Polish Jews), Polish war losses (about 2 M non-Jewish
citizens), the Soviet deportations of 1940-41 (about 320,000), the
repatriation of 1944-47 (1.52 M) and of 1955-59 (0.25 M), the transfer of
Ukrainians in 1944-46 (482,000), Operation Vistula (141,000), the flight
and expulsion of the Germans and the "verification" of the autochthons
(1946 census: 2.29 M Germans and 0.42 M awaiting verification), the
settlement of the Recovered Territories (5.94 M people in 1950), Jewish
emigration in 1946-47, 1949-51, 1956-58 and 1968-69, and the Aussiedler
(about 1.2 M in 1950-1992), with Maddison's income series for Poland.

## Geography (maps only)

| Item | Value | Grade | Source / note |
|---|---|---|---|
| Coastline, lakes, rivers | GSHHS / World Data Bank II, intermediate resolution, clipped to 13.5-33.0 E, 47.3-57.2 N (islands under 200 km², lakes under 100 km² and river pieces under 6 points dropped) | A | basemap-data 2.0; `plsim/data/geo_base.json`, rebuilt by `tools/build_geodata.py` |
| State territory (1 Jan 1932) | Poland and Lithuania from CShapes 2.0 (Gleditsch-Ward coding; Lithuania with Klaipėda, without the Wilno region; Danzig separate); median vertex spacing 3.5 km; extracted to `plsim/data/borders_1932.json` | B | Schvitz et al. 2022, *J. Conflict Resolution* 66: 144-161; R package cshapes 2.0. Areas: Poland 387,000 km² on the grid (official 388,600), Lithuania 55,600 (55,750) |
| Soviet Belarus (BSSR, 1926-39) | modern Belarus minus Poland and Lithuania of 1932; 125,900 km² (1926: 126,800) | B | Natural Earth 1:10m admin-0 countries v5 (Belarus's eastern and southern borders are those of 1926); `tools/build_geodata.py` |
| Voivodeship borders | weighted Voronoi of county towns, with weights calibrated to the official areas | C | approximate shapes, exact areas (±5 %) |
| County language anchors, 1931 (25) | e.g. Sokal 55.0 % Ukrainian, Turka 70.3 %, Lesko 63.0 %, Lubaczów 43.8 %, Przemyśl 36.9 %, Jarosław 14.2 %, Łuck 59.2 %, Kostopol 64.3 %, Krzemieniec 80.7 %, Kamień Koszyrski 8.7 % Ukrainian, Nieśwież 67.4 % Belarusian, Baranowicze 43.9 %, Mołodeczno 53.7 %, Wilejka 49.8 %, Bielsk 34.8 %, Grodno 32.8 %, Lida 11.2 %, Oszmiana 9.7 % | A | 1931 county tables as quoted in secondary sources |
| Other county anchors (190, incl. Szczuczyn at grade B) | Kashubian counties (not enumerated in 1931), German colonies in Poznań, Pomorze, Łódź and Volhynia, Lemko districts, Old Believers, Latvians, Lauda; zero anchors for counties without a minority | C | shape the pattern inside a voivodeship only; regional totals come from the census reconstruction |
| Terrain thinning | Polesie marshes -40 %, Carpathians -35 %, Hutsul highlands -30 % rural density | C | |

## Counties, 1931 (county-level runs)

`plsim/data/counties.py` holds the 269 county seats used by
`partition: counties`. That is every 1931 powiat outside Warsaw city, plus
the Lithuanian apskritys outside Kaunas city. The grade says what is known
about each county besides its seat.

**The 1931 county table** (`plsim/data/census1931_powiaty.csv`, checked by
`tools/check_census1931.py` and the tests). Read from the volumes the user
supplied, one row per powiat (or town with county rights), with the source
volume and page:

* the voivodeship volumes of the 1931 census (*Mieszkania i gospodarstwa
  domowe. Ludność. Stosunki zawodowe*, Statystyka Polski seria C: Łódź
  without the city, z. 77; Kielce, z. 86; Kraków, z. 88; Poznań without the
  city; Silesia, z. 54), tabl. 12, "Ludność według płci i języka
  ojczystego", all twelve language categories;
* the short results by powiat (*Drugi Powszechny Spis Ludności ... w postaci
  skróconej*, GUS; MBC edition 14481): one page per powiat with population
  by religion and mother tongue for towns and villages. Its language columns
  are those of the powiat's main languages; the remainder ("unk") is shared
  pro rata. Every powiat page and city page of the volume is in
  `census1931_strata.csv` (536 rows, 241 powiaty: towns, countryside and
  cities with their own page, by religion and mother tongue; checked by
  `tools/check_census1931_strata.py`). About a quarter of the pages were
  read by machine (`tools/parse_census1931.py`) and kept only where they
  reproduced the county totals; the rest were read from the page images,
  each row against its printed total and each powiat against its county
  population. Every voivodeship adds up to its census population (Warsaw's
  is short the city of Płock, whose page is missing).

Every row adds up to its printed total. Each voivodeship read whole
reproduces the census population of the voivodeship: Łódź, Kielce, Lublin,
Nowogródek, Polesie, Poznań, Silesia and Kraków exactly (to 29 persons).
The library's text layer of the short results is too noisy for the digits
(`tools/parse_census1931.py` tries, with the census identities total =
religions = languages, and reads about half the pages); the table was read
from the page images.

| Voivodeship | Counties | Grade | What is known | Source / check |
|---|---|---|---|---|
| Tarnopol, Stanisławów, Lwów, Volhynia, Wilno, Białystok | 17, 12, 26, 11, 8, 12 | A | population, mother tongue, religion, towns and countryside | the short results by powiat (below). Until now these rows came from the county tables of the Polish Wikipedia voivodeship articles; the pages showed those to be off by up to 6,000 persons a county (Augustów, Równe, Łuck, Kowel, Rawa Ruska) and, for Galicia, to give the religions as the languages: Turka's "6,301 Polish speakers" are its Roman Catholics (26,123 spoke Polish), Żółkiew's 20,279 likewise. Cities merged into their powiat (Lwów into lwowski, Wilno into wileńsko-trocki, Białystok into białostocki). Bóbrka's page is missing from the scan (only its continuation is there): its towns and countryside are the voivodeship without the city of Lwów (PDF p. 663 prints towns over 20,000, smaller towns and villages) less every other county |
| Nowogródek | 8 | A | population, mother tongue (Belarusian, Russian and Lithuanian separately), religion | the short results by powiat (below) |
| Polesie | 9 | A | population, mother tongue (Belarusian, "tutejszy", Ukrainian, Russian separately), religion | ditto |
| Lublin | 17 | A | population, mother tongue, religion | ditto |
| Warsaw voivodeship | 23 | A | population, mother tongue (Polish, German, Yiddish with Hebrew, other) | ditto. Rawa, in this voivodeship in 1931, is a WAR county (the model's areas already had it there). The page of the town of Płock is missing from the scan: powiat Płock has shares only and takes the voivodeship remainder (128,144 with the town) |
| Pomorze | 16 | A | population, mother tongue | the census volume itself: *Drugi Powszechny Spis Ludności z dn. 9 XII 1931 r.*, województwo pomorskie, Statystyka Polski seria C, zeszyt 75 (GUS 1938), tabl. 12, supplied as a DjVu scan and read from the page images. Every county row sums to its printed total, and the counties add up to the printed voivodeship (1,080,138; Polish 969,386, German 105,400). Gdynia city is merged into the powiat morski, Grudziądz and Toruń cities into their powiaty. Ruthenian is counted with Ukrainian, Hebrew with Yiddish, and Czech, "other" and "not given" as other. Kashubians, not enumerated, are inside "Polish" and split off by the county anchors |
| Łódź, Kielce, Kraków, Poznań, Silesia | 12, 17, 18, 31, 8 | A | population, mother tongue (all twelve categories of the census) | the voivodeship volumes, tabl. 12 (Statystyka Polski seria C; Łódź without the city, Kielce, Kraków without the city, Poznań without the city, Silesia), read from the page images; Łódź, Kraków and Poznań cities from the short results. Each voivodeship reproduces its census population exactly. Powiaty abolished in 1932 (Słupca, Oświęcim, Pleszew, Ostrzeszów, Grodzisk, Odolanów) were printed with the powiat that absorbed them and are split by the downscaled pattern |
| Lithuania (apskritys, 1923) | 22 | C | seat only | the 1923 apskritis nationality tables are in *Lietuvos gyventojai* (1923 census results), not in the supplied *Lietuvos apgyventos vietos* (settlements and their populations) |

How the table enters the model is described in `docs/METHODOLOGY.md` §12.6.
In short:

* **Fitting.** County figures are fitted to the voivodeship totals of the
  selected census variant by iterative proportional fitting. A county table
  therefore decides *where* speakers live, not how many there are.
* **Towns and religions.** The pages give the urban share of every
  language and the religions of the towns and of the countryside of every
  county; the county split follows both (`docs/METHODOLOGY.md` §12.6).
  They also give the voivodeships' religions and urban split, which the
  1931 reconstruction now uses (§3.6): they corrected the older
  approximate religion table, most in Lwów (Jewish 10.9 %, not 12.8 %;
  Greek Catholic 41.6 %, not 38.6 %), Lublin (Jewish 12.7 %, not 10.6 %)
  and Białystok (Orthodox 19 %, not 21.5 %), and the German speakers of
  the Warsaw voivodeship (2.9 %, not 1.9 %).
* **Data repairs.** A few published rows do not add up. Rohatyń's
  languages exceed its population by 0.7 %. Przeworsk's Polish count was
  recomputed from its percentage (58,632). The "other" languages of Dolina
  (4,013) and Horodenka (16) are German. On the pages: two cells of the
  Kopyczyńce towns are smudged (the Roman Catholics are the rest of the
  row), and the machine reading mislabelled a few columns (Brzeziny,
  Końskie, Płock, Nieśwież, Słonim), corrected by eye.

The county table also corrected one of the older anchors in
`data.geography`. The "Szczuczyn" anchor had Belarusian at 0.2 %, which
is the figure for Szczuczyn near Grajewo (Białystok voivodeship). The
Nowogródek county of that name had 9.9 % Belarusian + tutejszy + Russian
and 83.5 % Polish, and the anchor now uses that.
