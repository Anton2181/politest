# plsim: Poland-Lithuania without the Second World War, 1932-2032

`plsim` is a coupled simulation of a surviving interwar Polish state (by
default in a federal union with Lithuania) in a world with no Second World
War. It models four things together:

* **Demography**: cohort-component projection by region, urban/rural,
  ethno-confessional community, language, sex and single year of age.
* **Migration**: rural-urban, inter-regional and international flows,
  including planned eastern settlement and Jewish and German emigration
  channels.
* **Language and identity**: intergenerational and adult language shift
  (history-matched to documented cases), bilingualism, extinction of small
  languages, national identity tracked apart from home language, and what
  different censuses *would have recorded*.
* **Infrastructure**: endogenous growth of the railway and road networks
  under budgets, cost-benefit appraisal and the dated 1930s projects and 1939
  plans.

The simulation starts from the census of 9 December 1931, is back-validated
against the registered statistics of 1932-1939, and then runs forward without
the war. It is a counterfactual *simulation*, not a forecast. Each component
uses a published model structure; see `docs/METHODOLOGY.md` for equations,
calibration, sources and limitations.

## Quick start

```bash
pip install -r requirements.txt
python -m plsim list                    # scenarios
python -m plsim run baseline            # one seeded run -> outputs/runs/baseline/*.csv (+ validation)
python -m plsim validate baseline       # 1932-39 back-validation and plausibility checks
python -m plsim census                  # 1931 census-reconstruction consistency test
python -m plsim ensemble baseline -n 32 # Monte-Carlo ensemble -> outputs/ensemble_baseline/*.csv
python -m plsim report -n 32            # all scenarios + ensembles + figures + outputs/report.html
python -m plsim maps                    # 3.5 km maps, GIF animations and the interactive atlas (outputs/atlas/)
python -m plsim calibrate               # history matching of the language-shift rates (outputs/calibration/)
pytest -q                               # 108 tests
```

A 100-year county-level run takes about 4 minutes (20 s for the
23-voivodeship model, `partition: []`). `maps` runs the scenarios four at a
time and caches the runs; `report` reuses them and adds the 32-member
ensemble (each member also downscaled for the probability maps), about
two hours in all on 4 cores. Run `report` before `maps`, so that the atlas
gets the ensemble certainty layer.

## What is modelled

| Area | Model | Main references |
|---|---|---|
| Starting population | 1931 census cross-read with religion; Lithuania 1923/1925 censuses; three reconstructions of the latent vernacular; 1897 imperial census anchors | GUS 1931; Tomaszewski 1985; Kubijovyč 1983; 1897 census |
| Mortality | Siler age pattern with a health-progress index; best-practice-gap level with a post-1945 catch-up jump | Oeppen & Vaupel 2002; Preston 1975; Raftery et al. 2013 |
| Fertility | three-phase TFR model (double-logistic Phase II, AR(1) Phase III), pace driven by modernisation and community | Alkema et al. 2011; Coale & Watkins 1986 |
| Migration | Rogers-Castro age schedules; income-driven urbanisation; spatial interaction over *network* travel times; migration hump | Rogers & Castro 1981; Wilson 1971; Harris & Todaro 1970; Hatton & Williamson 1998 |
| Language | multi-language Abrams-Strogatz attraction with a bilingual state, vertical and horizontal transmission, enclave concentration, institutional completeness and a diaspora floor; rates history-matched to Masuria, Carinthia, Wales, Posen and second-generation immigrants | Abrams & Strogatz 2003; Minett & Wang 2008; Kandler et al. 2010; Breton 1964; Alba et al. 2002; Vernon et al. 2010 |
| Identity | national identity by county and group, apart from home language: births, switches, nation-building, the pull of the state nation; nationality censuses read identity, mother-tongue censuses read language | Hroch 1985; Weber 1976 |
| Networks | ~190-node multimodal graph; gravity demand; rule-of-half appraisal with the exact single-edge update; running costs and partial local benefit for expressways and motorways (calibrated to European densities); budgets; dated historical and planned projects; Beeching-type closures | Yerra & Levinson 2005; Louf et al. 2013; Donaldson & Hornbeck 2016 |
| Economy (driver) | conditional convergence to a western frontier; regional A/B gradient; COP and Fifteen-Year Plan; Gompertz motorisation | Barro & Sala-i-Martin 1992; Dargay & Gately 1999 |

## Census unreliability, the imperial census and the Lauda question

The 1931 census is itself contested evidence, so the model keeps *what people
spoke at home* separate from *what a census printed*.

* **Starting points** (`census_variant`). Every scenario starts from the
  research estimate unless it says otherwise:
  * `religion_corrected`: the **baseline**, Tomaszewski's (1985) correction.
    It counts Greek Catholics and Orthodox recorded as Polish-speaking as
    Ukrainian or Belarusian, and reproduces his figures: 64.7 % ethnic Poles,
    5.1 M Ukrainians and 1.95 M Belarusians (with the "tutejszy"), 0.78 M
    Germans, 3.11 M Jews.
  * `official`: the 1931 census as printed (scenario `census_official`).
  * `vernacular`: the upper bound for minority speech (scenario
    `census_vernacular`). It adds Kubijovyč's (1983) Latin-rite Ukrainians
    (5.85 M Ukrainians in all) and Catholic Belarusian speech at 1897
    proportions.
* **Lithuania's Polish-speakers** (`lt_variant`): ~150 k in the baseline,
  the middle of the published range. The 1923 census gave 65.6 k, and the
  Polish electoral committee claimed ~202 k in 1923 (held "very probable" by
  Buchowski 1999). The 1897 Kovno governorate had a ~9 % Polish share.
* **Sources and comparison** with the literature: `docs/DATA_SOURCES.md`, "The
  1931 starting point".
* **Census observation model.** It re-expresses any latent state as a
  1931-type Polish census, the 1897 imperial census, the 1923 Lithuanian
  census or a modern self-identification census would have recorded it.
  Passing the baseline through the 1931 regime reproduces the printed
  national shares within 1 point in total (Polish 68.7 % against 68.9 %).
  In other words, the published census is consistent with a considerably less
  Polish-speaking population.
* **Lauda** (Kėdainiai-Panevėžys-Ukmergė-Raseiniai) is its own unit. The
  Polish-speaking petty gentry there are followed through every scenario:
  in the federal baseline Polish is co-official in Lithuania, and under a
  `polonizing_union` it is the only official language.

## Headline results (baseline, 32-member ensemble)

Medians, with 5-95 % ranges in brackets. The whole union is the 17 Polish
first-order units plus 6 Lithuanian units (270 counties). The language rates
are history-matched (METHODOLOGY §6.4), and the ensemble draws them jointly
from the set the matching did not rule out.

| Year | Population (M) | TFR | e0 m / f | Urban % | GDP/head (1990 GK$) |
|---|---|---|---|---|---|
| 1939 | 37.1 (Poland 34.5) | 3.22 | 50.7 / 54.3 | 29 | 2,070 |
| 1960 | 43.9 [42.6-45.9] | 2.80 | 61.3 / 66.2 | 40 | 3,930 |
| 1990 | 50.9 [47.2-56.0] | 1.91 | 69.7 / 76.1 | 57 | 9,700 |
| 2032 | 50.9 [44.4-59.0] | 1.60 | 80.8 / 85.7 | 67 | 18,470 |

**Demography**

* The population peaks at ~52.4 M around 2010 and is 50.9 M in 2032.
* The Polish voivodeships alone reach ~49 M (48.1 M in 2032; the Second
  Republic alone: 47.6 M in its seeded run).
* Net emigration of ~115-135 k/yr in the guest-worker era falls to ~35-65
  k/yr after 2000; net immigration appears only in the high-convergence
  runs.
* Fertility falls late in the poorer east. In the seeded run Polesie and
  Volhynia have about 3.0 children per woman in 1970 and 2.3 in 1990,
  against 2.4 and 1.95 for the whole union. Rural eastern Poland, the
  closest real analogue, had about 2.9 and 2.4-2.6. The fertility model
  is calibrated on it and on the whole of People's Poland (the
  `historical` scenario, METHODOLOGY §4.2); before, these lands kept 4.0
  and 2.8.

**Languages** (home vernacular, shares of the whole union, from the research
start of 1931)

| Language | 1933 | 2032 |
|---|---|---|
| Polish | 61.3 % | 71.7 % |
| Ukrainian | 14.1 % | 13.6 % (6.8 M speakers [5.4-7.9]) |
| Yiddish | 8.3 % | 4.2 % |
| Belarusian | 3.9 % | 2.4 % (1.2 M [0.6-1.6]) |
| Lithuanian | 5.7 % | 5.2 % |
| West Polesian | 2.1 % | 1.1 % |

* **Ukrainian** grows almost as fast as the population (4.9 → 6.8 M):
  high Galician and Volhynian fertility and robust Greek Catholic
  institutions, against the shift to Polish in lwowskie west of Lwów.
  Migrants' children assimilate (the diaspora term): Warsaw city ends 6 %
  Ukrainian-speaking in the seeded run.
* **Yiddish** declines among acculturating Jews and survives through a
  growing Haredi population (very uncertain). Jewish *identity* (7.1 % of
  the union in 2032) outlasts Yiddish (4.2 %).
* **Kashubian**: 202 k -> 108 k [69-158 k]. **Lemko**: 132 k -> 84 k
  [60-121 k].
* **West Polesian**: persists in villages (0.56 M [0.25-1.0]) as a
  declining share.
* **Wymysorys**: 1,500 -> ~80 speakers [17-128], moribund even without the
  post-war ban.
* **Karaim**: ~680 -> ~270 speakers.

**Identity** (separate from home language; the starting mix is fitted to
the 1921 nationality census, METHODOLOGY §6.7): Polish 63.5 -> 66 %,
Ukrainian 13 -> 14.5 %, Belarusian 3.2 -> 3.3 %, "local" 2.8 -> 1.2 %,
Jewish 7.6 -> 7.1 %. Polish identity trails Polish speech (66 % against
72 % in 2032), because many who switch to Polish keep a Ukrainian,
Belarusian or Jewish identity.

**Infrastructure**

* Almost all inter-town roads are paved by ~1960.
* By 2032: ~2,000 km of motorway [1,300-2,800] and ~6,700 km of
  expressway [4,200-10,000], about 20 km per 1000 km², like Czechia and
  Hungary (23,800 km before the road appraisal counted running costs and
  only part of the local traffic). Also ~10,900 km of electrified main
  line and ~1,700 km of high-speed line.
* The 1939 plans are completed in the early 1940s: the Wilno-Gdynia shortcut
  Łapy-Ostrołęka-Przasnysz-Mława, Dębica-Jasło, and the COP Łódź-Dębica
  trunk.

**Uncertainty on the map.** Every ensemble member is downscaled. In 2032,
about one cell in 25 has a leading language that fewer than 80 % of runs
agree on (one in 19 in 1982, then mostly Polesie, Polish against West
Polesian). These cells lie on the Polish-Ukrainian frontier of Tarnopol
and lwowskie and on the Belarusian-Polish frontier of Nowogródek and Wilno
(`outputs/maps/map_uncertainty.png`, and the atlas's Certainty layer).

## Maps: language shift and population on a 3.5 km grid

`python -m plsim maps` downscales every scenario to about 37,500 cells of
3.5 x 3.4 km and draws the result:

* **Interactive atlas**: `outputs/atlas/index.html`.
  * **Scenarios and layers.** A time slider, all 16 scenarios, and six
    layers:
    * plurality language;
    * one language (optionally as change since 1932);
    * national identity (by county);
    * density;
    * growth;
    * ensemble certainty (baseline): the most likely leading language in
      1982 or 2032, paler where the 32 runs disagree.
  * **Zoom and pan.** Scroll, pinch, the buttons or the keyboard (+, −,
    0, arrows) zoom up to 24×; drag to pan. County borders are drawn
    throughout, and county names and smaller towns appear as you zoom in.
  * **Overlays and readout.** It overlays the railway and road network as
    it grows, with km by class and the latest openings. It dashes the
    borders between federal members (cantons, autonomies). It reads out
    any cell: county, voivodeship, member, official languages and home
    languages.
  * **Whole areas.** Click or tap to select the county, voivodeship or
    federal member (canton, autonomy) under the pointer: the panel shows its
    residents, growth since 1932, area, density and home languages, and the
    chart follows it.
  * **Curzon line.** An overlay draws, for every 5-year frame, a continuous
    line across the state along county borders that leaves as many
    non-Poles on its Polish side as Poles on its other side (to within a
    county), with the most Poles on the Polish side (details below and in
    `docs/METHODOLOGY.md` §12.8). A second overlay draws the historical Curzon line of 1919-20
    (line A), with the same people counted on either side.
* **Static maps and animations**: `outputs/maps/`, including
  `anim_languages.gif` and `anim_density.gif`.

How it works (details in `docs/METHODOLOGY.md` §12):

* **Territory.** The state borders are those of 1 January 1932, from
  CShapes 2.0 (Schvitz et al. 2022). Maps clip the cells to them, so the
  border is drawn as a line rather than in steps. Voivodeship and county
  borders inside are approximations (weighted Voronoi of the towns and
  county seats, calibrated to the official areas). Land left out of the
  state in a scenario (`exclude`) is drawn as foreign. Soviet Belarus (the
  BSSR of 1926; modern Belarus minus 1932 Poland, from Natural Earth) is a
  third state, used by Wakar's Poland-Belarus and the krai scenarios. The
  krai's land in Latvia and the RSFSR (the 1897 governorates of the RISTAT
  GIS, outside the 1932 states) is a fourth, used by `nw_krai`.
* **1932.** County anchors from the 1931 census, 25 of them county figures,
  the rest graded estimates, shape each voivodeship's languages inside its
  borders. Iterative proportional fitting keeps the regional totals exact.
* **Each year.** The region's net shift from the main model is placed with
  the neighbourhood rule of Prochazka & Vogl (2017, *PNAS*): speakers shift
  where the gaining language is spoken nearby (Gaussian kernel, 10 km),
  plus a constant institutional part. Towns spread their influence over a
  wider radius as they grow (Trudgill's hierarchical diffusion). Language
  islands therefore dissolve first, and contact zones retreat as fronts.
* **Population.** Rural cells near growing towns gain population and remote
  ones lose it, which gives suburban rings and rural exodus.

![Plurality home language, baseline](outputs/maps/map_plurality.png)

Baseline, area where each language leads (thousand km²):

| | Polish | Ukrainian | Lithuanian | Belarusian | West Polesian | Kashubian/Lemko |
|---|---|---|---|---|---|---|
| 1932 | 226 | 81 | 55 | 40 | 36 | 4 |
| 2032 | 308 | 76 | 56 | 3 | 0 | 0 |

* **Ukrainian** holds its Volhynian and Pokuttya core. It retreats from the
  San and the Lwów hinterland.
* **Belarusian and West Polesian** survive as minorities in the villages,
  but by 2032 Belarusian leads only a few patches on the eastern border and
  West Polesian nowhere. They hold on where the state schools them or keeps
  out of language policy: `ukraine_autonomy_tricantonal`,
  `autonomy_grand_duchy_coofficial`, `wakar_poland` and
  `no_official_language` (where Belarusian leads 49 and West Polesian 24
  thousand km² in 2032).
* **Population.** About 65 % of the land area has fewer people in 2032
  than in 1932, and a tenth has less than half. Growth concentrates
  in the cities, their suburban rings, and high-fertility Polesie and
  Volhynia.

![Population change](outputs/maps/map_population_change.png)

## County level (powiaty)

Every scenario runs on 270 regions (199 and 211 in the Wakar scenarios,
289 and 276 in `nw_krai` and `lit_bel`): the 1931 powiaty and the Lithuanian
apskritys, with Warsaw and Kaunas cities whole, plus the okrugs of Soviet
Belarus and the krai's eastern uezds where a scenario holds them, and the
groups of German Kreise in `plebiscite_poland` and `historical`. One
county, Węgrów, wins no cell on the approximate voivodeship map and is
merged into its neighbours.
`partition: []` runs the original 23-voivodeship model instead (20 s rather
than 4 minutes). Details are in `docs/METHODOLOGY.md` §12.6.

* **Data.** Every Polish powiat has its 1931 census population and mother
  tongue (grade A), read from the census volumes: the voivodeship volumes
  (tabl. 12) for Łódź, Kielce, Kraków, Poznań, Silesia and Pomorze, and the
  powiat pages of the short results for the Warsaw voivodeship, Lublin,
  Nowogródek, Polesie and the large cities, with religion where printed
  (`plsim/data/census1931_powiaty.csv`, with the page of every row; each
  voivodeship read whole reproduces its census population). The east comes
  from published secondary tables of the same census. Lithuania's
  apskritys are still downscaled (grade C). County figures are fitted to the
  voivodeship totals of the starting point, so the county tables decide
  *where* speakers live and the research estimate decides *how many*.
* **Consistency.** Migration, income, enclave concentration and random
  numbers are nested in the voivodeships, so the county run reproduces
  the voivodeship model:

  | 2032 | Voivodeship run | County run |
  |---|---|---|
  | Population | 50.77 M | 50.62 M |
  | Ukrainian speakers | 7.00 M | 7.00 M |
  | Belarusian speakers | 1.31 M | 1.26 M |

* **What it adds is where.** In the baseline, 34 counties change their
  plurality language by 2032, all of them towards Polish except Klaipėda
  (German to Lithuanian):
  * Belarusian blocks: Grodno, Wołkowysk, Bielsk, Głębokie–Wilejka and
    Nieśwież–Słonim (12 counties);
  * all nine Polesie counties;
  * three Kashubian counties;
  * nine Ukrainian counties: eight of lwowskie (Sambor, Drohobycz, Sokal,
    Rudki, Lesko ...) and Kamionka Strumiłowa.

  Lwów county grows from 460 k to 973 k people, Wilno from 415 k to 871 k.

![Plurality home language, 2032](outputs/maps/scenarios_plurality_2032.png)

## Scenarios (single seeded run each, 2032)

| Scenario | Population outside Lithuania (M) | Polish % | Ukrainian % | Yiddish % | Belarusian % | Lithuanian % | W. Polesian (k) |
|---|---|---|---|---|---|---|---|
| baseline | 47.9 | 71.9 | 13.8 | 3.8 | 2.5 | 5.1 | 590 |
| ii_rp_only | 47.6 | 75.7 | 14.7 | 4.1 | 2.7 | 0.1 | 596 |
| federal_autonomy | 47.9 | 66.0 | 16.1 | 4.6 | 3.9 | 5.2 | 996 |
| integral_nationalism | 47.1 | 75.7 | 12.5 | 3.2 | 1.7 | 5.1 | 333 |
| polonizing_union | 47.9 | 72.6 | 13.8 | 3.8 | 2.5 | 4.5 | 590 |
| census_official | 47.9 | 74.0 | 12.4 | 3.9 | 1.7 | 5.3 | 590 |
| census_vernacular | 48.0 | 70.9 | 14.4 | 3.8 | 3.0 | 5.1 | 590 |
| ukraine_autonomy_tricantonal | 47.8 | 63.7 | 16.1 | 4.4 | 6.8 | 5.2 | 877 |
| autonomy_grand_duchy_coofficial | 47.5 | 63.6 | 16.1 | 4.4 | 6.9 | 5.2 | 881 |
| wakar_poland | 35.9 | 78.6 | 4.7 | 4.4 | 8.3 | 0.0 | 716 |
| wakar_poland_belarus | 48.2 | 60.5 | 3.6 | 4.1 | 26.8 | 0.0 | 718 |
| no_official_language | 47.8 | 61.6 | 16.6 | 5.3 | 6.6 | 5.3 | 999 |
| plebiscite_poland | 50.3 | 71.6 | 13.0 | 3.7 | 2.4 | 4.9 | 592 |
| nw_krai (Poland and the krai together) | 62.5 | 51.8 | 10.8 | 3.9 | 23.7 | 3.9 | 814 |
| lit_bel (Poland and Lit-Bel together) | 53.1 | 59.5 | 12.5 | 4.1 | 15.1 | 4.8 | 820 |

Polish-speakers in the Lithuanian units (Polish is co-official in Lithuania
in every scenario with the union, except the unitary `polonizing_union`),
and those of them with a Polish identity:

| Scenario | 1933 | 2032 | of whom Lauda, 1933 → 2032 | Polish identity, 1933 → 2032 |
|---|---|---|---|---|
| baseline (federal) | 150 k | 154 k | 53 k → 53 k | 78 k → 85 k |
| polonizing_union (Polish the only official language) | 150 k | 496 k | 53 k → 112 k | 78 k → 476 k |
| census_official (the 1923 census as printed) | 77 k | 73 k | 23 k → 19 k | 48 k → 52 k |
| ukraine_autonomy_tricantonal (Lithuanian canton) | 150 k | 216 k | 53 k → 65 k | 78 k → 128 k |
| autonomy_grand_duchy_coofficial (one Grand Duchy) | 150 k | 414 k | 53 k → 102 k | 78 k → 289 k |
| nw_krai (the krai's Lithuanian lands, without Suvalkija) | 141 k | 425 k | 53 k → 124 k | 69 k → 296 k |
| lit_bel (the Lithuanian lands of Lit-Bel) | 150 k | 567 k | 53 k → 142 k | 76 k → 414 k |

**Ukrainian autonomy + tri-cantonal Lithuania** (`ukraine_autonomy_tricantonal`).
Lwów, Tarnopol and Stanisławów voivodeships plus Volhynia form a Ukrainian
autonomy, on the never-implemented 1922 statute. Everything east of the
later Curzon line and north of Volhynia joins Lithuania as a Grand Duchy of
Lithuanian, Polish (Wilno–Lida–Grodno) and Belarusian (eastern Wilno lands,
Nowogródek, Polesie) cantons, made of whole counties. Polish is co-official
in the autonomy and in every canton. By 2032:

* Belarusian speakers number 3.45 M (1.26 M in the baseline). Belarusian
  rises from 36 to 55 % of its canton and leads 19 of its 20 counties.
* Ukrainian rises from 55 to 64 % of the autonomy. Seven counties turn
  Ukrainian-plurality: Lwów, Przemyśl and Mościska, and Tarnopol,
  Trembowla, Skałat and Przemyślany. The ten counties west of the San stay
  Polish.
* Polish falls to 64 % of the union (72 % in the baseline).

**Ten more political settlements** (details in `docs/SCENARIOS.md`):

* `autonomy_grand_duchy_coofficial`: the same autonomy, and an undivided
  Grand Duchy with **Lithuanian, Polish and Belarusian co-official**.
  * Belarusian becomes the Duchy's largest language (19 → 33 %), and Polish
    holds its share (24 → 26 %).
  * Polish and Belarusian spread into the Lithuanian lands: Kaunas and the
    north-east fall from 71 to 64 % Lithuanian, Samogitia from 88 to 81 %,
    and Lithuania's Polish-speakers almost treble (150 k → 414 k).
* `wakar_poland` (**Wakar's Poland**): Poland without Volhynia, Stanisławów,
  Tarnopol and the Vilnius region, with Polish and Belarusian co-official.
  * 25.7 M people in 1933, 35.9 M in 2032.
  * Belarusian grows from 1.1 M to 3.0 M speakers (8 %) and leads 18
    counties, Polesie included.
* `wakar_poland_belarus` (**Wakar's Poland-Belarus**): Wakar's Poland
  together with **all of Soviet Belarus** (the BSSR of 1926, from the 1926
  Soviet census), Polish and Belarusian co-official.
  * 31.1 M people in 1933 (5.4 M in Soviet Belarus), 48.2 M in 2032.
  * Polish holds at 61 %, Belarusian rises from 17 to 27 % (12.9 M
    speakers). Soviet Belarus grows to 9.5 M, 84 % Belarusian.
* `no_official_language`: no language is privileged, every written
  standard is official, and each county works in its largest language.
  * Polish ends at 62 % of the union (72 % in the baseline): about 5 M
    more people keep a minority language.
  * Only 19 counties change their plurality language (34 in the baseline),
    and West Polesian still leads two.
* `nw_krai` (**Poland and the Northwestern Krai**) and `lit_bel` (**Poland
  and Lit-Bel**): Poland without the lands of the old north-western
  governorates, which form a separate state with **its own economy**,
  simulated in the same run, with Lithuanian, Belarusian, Polish, Yiddish
  and Russian official. The borders are the **governorates of 1897**
  (RISTAT GIS), not the 1931 counties: units that straddle them are cut.
  The krai (Vilna, Kovno, Grodno, Minsk, Mogilev, Vitebsk) holds Lithuania
  without Klaipėda, the Wilno, Nowogródek and Grodno lands, most of
  Polesie, all of Soviet Belarus, and **Latgale, Nevel, Sebezh and Velizh**
  (from the 1897 census); Suvalkija, in the Kingdom of Poland before 1915,
  goes to Poland. Lit-Bel (Vilna, Kovno, Grodno, Minsk, Suwałki, the
  republic of 1919) keeps Suvalkija, Suwałki and Augustów and only the
  Minsk-governorate part of Soviet Belarus.
  * Poland: 28.3 M in 1933, 40.4 M in 2032, 76 % Polish.
  * The krai: 12.9 M to 25.7 M, Belarusian 48 → 61 %, Polish 15 → 14 %
    (1.9 → 3.6 M speakers), Lithuanian 12 → 9 %. Lit-Bel: 9.3 M to 17.4 M,
    Belarusian 35 → 49 %, Polish 22 → 21 %.
  * Polesie turns Belarusian, and so does Daugavpils in Latgale. Wilno
    county stays Polish-plurality (50-53 %), with about 30 % of it
    Belarusian (82 % Polish in the baseline).
* `plebiscite_poland` (**Poland with the plebiscite lands and Danzig**):
  the baseline union, plus the Free City of Danzig and every area that voted
  or was to vote in 1920-21: all of Upper Silesia (with Oppeln, Gleiwitz and
  Beuthen), the Allenstein and Marienwerder plebiscite districts (southern
  East Prussia), and Cieszyn Silesia, Spisz and Orawa from Czechoslovakia.
  The counties that did not vote (Neisse, Braunsberg, Rastenburg ...) are
  left out. Polish is official everywhere, with German co-official in
  Danzig.
  * 50.3 M people outside Lithuania in 2032 (47.9 M in the baseline).
  * German speakers in the new lands fall from 1.92 M to 0.71 M: Danzig
    grows from 410 k to 730 k and goes from 5 to 71 % Polish-speaking;
    Opole Silesia from 66 to 12 % German. 26 German-plurality counties turn
    Polish.
* `historical`: the counterfactual's control. Poland with the real
  1939-50 history (below), used to calibrate the model on what actually
  happened.

**Historical Poland, for calibration** (`historical`). The same model, run
through the real events: the September campaign, occupation deaths, the
Holocaust, Volhynia, the Warsaw Uprising, the Soviet deportations; the
border moved west in 1945 (the Recovered Territories and Danzig become
Polish, the land east of the Bug becomes Soviet); the flight and expulsion
of the Germans, the repatriation of Poles from the east, the resettlement
of the west, Ukrainians and Belarusians sent to the USSR, Operation
Vistula; and the post-war emigrations (Jews 1946-69, Aussiedler 1951-92),
with post-war fertility, the Soviet-type income path and the 1990s
transition. It reproduces (model / observed):

| | 1946 | 1950 | 1970 | 2002 | 2021 |
|---|---|---|---|---|---|
| Population (M) | 24.1 / 23.9 | 23.8 / 25.0 | 30.4 / 32.6 | 35.6 / 38.2 | 34.4 / 38.0 |
| Urban % | | 38.5 / 36.9 | 50.9 / 52.3 | 58.9 / 61.8 | 62.4 / 60.2 |
| TFR | | 3.70 / 3.71 | 2.19 / 2.20 | 1.41 / 1.37 (2000) | 1.41 / 1.39 (2020) |

* The Recovered Territories hold 5.3 M in 1946 (5.0 M) and 5.6 M in 1950
  (5.9 M); e0 stays within 1.5 years of the life tables.
* The population is 5-10 % short after 1946: the model's post-war
  population is older than the real one (1-1.5 deaths per thousand too
  many in the 1950s), and the return of displaced people in 1946-48 is not
  modelled. Minority identities are too stable: in 2002 the run keeps
  350 k Ukrainians and 230 k Belarusians, against 31 k and 49 k declared;
  Silesians and Germans come out close (240 k and 190 k, against 173 k and
  153 k).
* `outputs/history/` holds the comparison table and chart; METHODOLOGY
  §12.10 the events and their sources.

**Ranges.** Every scenario except `historical` also runs a small ensemble
(8-16 members, same draws for every scenario, so differences between
scenarios are paired). `outputs/scenario_ranges.csv` and the report give
5-95 % ranges for population, the Polish, Ukrainian and Belarusian shares
and Lithuania's Poles; the atlas shows them under the chart.

**The equal-exchange Curzon line.** For every 5-year frame the atlas can
draw (in magenta) a continuous line across the state, from border to border
along county borders, that leaves as many non-Poles on its Polish side as
Poles on its other side (to within one county), with the most Poles on the
Polish side. Kashubians, Wymysorys speakers, Germans and Jews are not
counted.

* In the baseline it moves 1.83 M people each way in 1932 and 4.0 M in
  2032.
* In 1932 the Polish side keeps the western Wilno lands with Wilno (joined
  through Grodno and Lida), Lwów with most of lwowskie, and Tarnopol;
  Lithuania, Polesie, Volhynia, Stanisławów and the eastern Wilno and
  Nowogródek lands are on the other side.
* By 2032 the Polish side has spread east over a Polonised Polesie.
* **Against the historical line** of 1919-20 (line A in Galicia; dashed in
  the atlas): in 1932 it leaves 0.96 M non-Poles west and 3.26 M Poles east,
  against 1.83 M each way for the computed line. The diplomats' line was
  drawn on the ethnographic maps of 1919 and leaves the Poles of the Wilno
  lands, Lwów and the eastern towns on the other side. As the east Polonises
  in the baseline, the gap widens: 2.2 M non-Poles west and 8.1 M Poles east
  by 2032.
* The real transfers of 1944-47 are replayed in `historical` (below).

![Curzon line, baseline](outputs/maps/map_curzon.png)

The full table is in `outputs/scenario_summary.csv`; the assumptions are in
`docs/SCENARIOS.md`. Proposed further developments are in `docs/ROADMAP.md`.

## Repository layout

```
plsim/
  data/regions.py        44 first-order units (17 voivodeships, 6 Lithuanian units, 4 Soviet-Belarusian
                         groups of okrugs, Latgale and two RSFSR units, 11 German, Danzig, 2 Czechoslovak)
  data/languages.py      languages, communities, (community, language) groups, shift targets
  data/census1931.py     1931 / 1923 / 1897-anchored reconstructions, bilingual shares
  data/network.py        towns, c.1931 rail network, paved roads, dated & planned projects
  demography.py          life tables, e0 frontier model, Alkema TFR, schedules, initial ages
  migration.py           Rogers-Castro, urbanisation, spatial interaction, migration hump
  language.py            transmission, enclaves, institutions, diaspora floor, census observation model
  identity.py            national identity apart from home language; nationality censuses
  calibration.py         history matching of the shift rates on documented cases
  data/nroy_language.csv parameter sets not ruled out by the history match (drawn by the ensemble)
  infrastructure.py      network, travel times, gravity demand, appraisal, investment
  economy.py             convergence, regional incomes, motorisation, budgets
  model.py               the annual simulation loop
  ensemble.py            Monte-Carlo parameter sampling and summaries
  validate.py            1932-39 back-validation and plausibility checks
  report.py, export.py   figures, CSVs, HTML report
  data/geography.py      3.5 km map grid (7 km model grid), 1932 state borders, county language anchors
  data/bssr.py           Soviet Belarus (BSSR, 1926 census by okrug), for wakar_poland_belarus
  data/governorates.py   the governorates of 1897 (RISTAT GIS, governorates_1897.json), for nw_krai and lit_bel
  data/krai_east.py      Latgale, Nevel-Sebezh-Velizh and eastern Mogilev from the 1897 census, for nw_krai
  data/west.py           German land of 1945, Danzig, Czechoslovak plebiscite lands (1933, 1929, 1930 censuses)
  data/census1921.py     the 1921 nationality census (identity calibration; county table when supplied)
  history.py             border changes, war deaths, expulsions, transfers, repatriation (historical scenario)
  history_check.py       the historical scenario against the censuses of 1946-2021
  data/borders_1932.json Poland and Lithuania on 1 Jan 1932 (CShapes 2.0); the optional lands; Poland 1946
  data/subregions.py     county-line splits of voivodeships (Curzon line, cantons, the San); real powiat
                         polygons from data/powiaty_1931.geojson when supplied
  data/counties.py       366 counties (1931 powiaty, 1923 apskritys, 1926 BSSR okrugs, krai uezds, groups of
                         Kreise) with graded census rows
  partition.py           1931 population of sub-regions and counties, via the grid
  data/geo_base.json     coastline, lakes and rivers (GSHHS via basemap-data)
  spatial.py             downscaling + neighbourhood (Prochazka-Vogl) language-shift allocation
  maps.py, webmap.py     static maps, GIF animations, interactive atlas data
  curzon.py              the equal-exchange Curzon line (whole counties), the 1919-20 line
  atlas_template.html    the interactive atlas page
  cli.py                 command-line interface
scenarios/*.yaml         16 scenarios (extends/override)
tools/build_geodata.py   rebuilds the base map and the Soviet Belarus border (shapely; not needed to run)
tools/match_powiaty.py   adds county codes to a GeoJSON of 1931 powiat polygons
tools/build_governorates.py  rebuilds the 1897 governorates and the krai's land outside the 1932 states (shapely)
tools/build_west.py      the German, Danzig and Czechoslovak lands and Poland 1946 from CShapes (shapely)
docs/                    METHODOLOGY, DATA_SOURCES (with reliability grades), SCENARIOS, ROADMAP
outputs/                 report.html, figures/, maps/, atlas/, calibration/, history/, scenario_summary.csv,
                         identity summaries, scenario ranges, ensemble CSVs, baseline run CSVs
tests/                   census reconstruction, demography, language, network, model accounting
```

## Caveats

This is not a prediction of what "would have happened". The 1930s are
anchored to data. Everything after depends on explicit and adjustable
assumptions:

* **Political assumptions** (federalism vs. nationalism, the union with
  Lithuania, the growth path) are scenarios.
* **Parameter uncertainty** is sampled in the ensembles.
* **Weakest parts**: the fate of Jewish emigration and Haredi fertility in a
  world without the Holocaust; regional starting data graded "C" in
  `docs/DATA_SOURCES.md`; the stylised transport network.
