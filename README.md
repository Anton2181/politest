# plsim: Poland-Lithuania without the Second World War, 1932-2032

`plsim` is a coupled simulation of a surviving interwar Polish state (by
default in a federal union with Lithuania) in a world with no Second World
War. It models four things together:

* **Demography**: cohort-component projection by region, urban/rural,
  ethno-confessional community, language, sex and single year of age.
* **Migration**: rural-urban, inter-regional and international flows,
  including planned eastern settlement and Jewish and German emigration
  channels.
* **Language**: intergenerational and adult language shift, bilingualism,
  extinction of small languages, and what different censuses *would have
  recorded*.
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
pytest -q                               # 78 tests
```

A 100-year county-level run takes about 4 minutes (20 s for the
23-voivodeship model, `partition: []`). `maps` runs the scenarios four at a
time and caches the runs; `report` reuses them and adds the 32-member
ensemble, about an hour in all on 4 cores.

## What is modelled

| Area | Model | Main references |
|---|---|---|
| Starting population | 1931 census cross-read with religion; Lithuania 1923/1925 censuses; three reconstructions of the latent vernacular; 1897 imperial census anchors | GUS 1931; Tomaszewski 1985; Kubijovyč 1983; 1897 census |
| Mortality | Siler age pattern with a health-progress index; best-practice-gap level with a post-1945 catch-up jump | Oeppen & Vaupel 2002; Preston 1975; Raftery et al. 2013 |
| Fertility | three-phase TFR model (double-logistic Phase II, AR(1) Phase III), pace driven by modernisation and community | Alkema et al. 2011; Coale & Watkins 1986 |
| Migration | Rogers-Castro age schedules; income-driven urbanisation; spatial interaction over *network* travel times; migration hump | Rogers & Castro 1981; Wilson 1971; Harris & Todaro 1970; Hatton & Williamson 1998 |
| Language | multi-language Abrams-Strogatz attraction with a bilingual state, vertical and horizontal transmission, enclave concentration, institutional completeness, a census observation model | Abrams & Strogatz 2003; Minett & Wang 2008; Kandler et al. 2010; Breton 1964 |
| Networks | ~190-node multimodal graph; gravity demand; rule-of-half appraisal with the exact single-edge update; budgets; dated historical and planned projects; Beeching-type closures | Yerra & Levinson 2005; Louf et al. 2013; Donaldson & Hornbeck 2016 |
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
first-order units plus 6 Lithuanian units (270 counties).

| Year | Population (M) | TFR | e0 m / f | Urban % | GDP/head (1990 GK$) |
|---|---|---|---|---|---|
| 1939 | 37.2 (Poland 34.6) | 3.28 | 50.7 / 54.3 | 29 | 2,070 |
| 1960 | 44.4 [43.1-46.2] | 2.91 | 59.4 / 64.3 | 39 | 3,830 |
| 1990 | 50.9 [46.7-55.9] | 1.91 | 68.1 / 74.6 | 57 | 9,500 |
| 2032 | 51.8 [43.0-62.9] | 1.58 | 79.5 / 84.3 | 67 | 18,200 |

**Demography**

* The population peaks at ~53 M around 2014.
* The Polish voivodeships alone reach ~49-50 M (the Second Republic alone:
  48.3 M [39-61] in 2032).
* Net emigration of ~100-120 k/yr in the guest-worker era falls to ~30-60
  k/yr after 2000; net immigration appears only in the high-convergence
  runs.

**Languages** (home vernacular, shares of the whole union, from the research
start of 1931)

| Language | 1933 | 2032 |
|---|---|---|
| Polish | 61.3 % | 64.8 % |
| Ukrainian | 14.2 % | 18.2 % (~9.4 M speakers, nearly doubling) |
| Yiddish | 8.2 % | 4.5 % |
| Belarusian | 3.9 % | 3.6 % |
| Lithuanian | 5.7 % | 4.2 % |
| West Polesian | 2.1 % | 1.7 % |

* **Ukrainian** grows faster than the population as a whole: high Galician
  and Volhynian fertility plus robust Greek-Catholic institutions. Part of
  the growth is migrants who keep Ukrainian in Warsaw, Lublin and Silesia,
  probably too many (see `docs/ROADMAP.md`).
* **Yiddish** declines among acculturating Jews and survives through a
  growing Haredi population (very uncertain).
* **Kashubian**: 200 k -> 115 k [77-164 k].
* **Lemko**: 133 k -> 120 k.
* **West Polesian**: persists in villages (0.9 M) as a declining share.
* **Wymysorys**: 1,500 -> ~100 speakers, moribund even without the post-war
  ban.
* **Karaim**: ~700 -> ~200 speakers.

**Infrastructure** (see the caveat in `docs/ROADMAP.md`: the road programme
is overbuilt)

* Almost all inter-town roads are paved by ~1960.
* By 2032: ~6,900 km of motorway and ~16,900 km of expressway, ~9,000 km of
  electrified main line and ~1,850 km of high-speed line.
* The 1939 plans are completed in the early 1940s: the Wilno-Gdynia shortcut
  Łapy-Ostrołęka-Przasnysz-Mława, Dębica-Jasło, and the COP Łódź-Dębica
  trunk.

## Maps: language shift and population on a 3.5 km grid

`python -m plsim maps` downscales every scenario to about 37,500 cells of
3.5 x 3.4 km and draws the result:

* **Interactive atlas**: `outputs/atlas/index.html`.
  * **Scenarios and layers.** A time slider, all 12 scenarios, and four
    layers: plurality language, one language (optionally as change since
    1932), density and growth.
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
    line across the state, free to wind cell by cell, that leaves as many
    non-Poles on its Polish side as Poles on its other side, with the most
    Poles on the Polish side (details below and in `docs/METHODOLOGY.md`
    §12.8).
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
  third state, used by Wakar's Poland-Belarus.
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
| 1932 | 229 | 79 | 55 | 39 | 35 | 4 |
| 2032 | 302 | 76 | 56 | 10 | 0 | 0 |

* **Ukrainian** holds its Volhynian and Pokuttya core. It retreats from the
  San and the Lwów hinterland.
* **Belarusian and West Polesian** survive as minorities in the villages,
  but by 2032 Belarusian leads only a strip along the eastern border and
  West Polesian nowhere. They hold on where the state schools them or keeps
  out of language policy: `ukraine_autonomy_tricantonal`,
  `autonomy_grand_duchy_coofficial`, `wakar_poland` and
  `no_official_language` (where Belarusian leads 54 and West Polesian 21
  thousand km² in 2032).
* **Population.** Almost two-thirds of the land area has fewer people in
  2032 than in 1932, and a sixth has less than half. Growth concentrates
  in the cities, their suburban rings, and high-fertility Polesie and
  Volhynia.

![Population change](outputs/maps/map_population_change.png)

## County level (powiaty)

Every scenario runs on 270 regions: the 1931 powiaty and the Lithuanian
apskritys, with Warsaw and Kaunas cities whole. One county, Węgrów, wins no
cell on the approximate voivodeship map and is merged into its neighbours.
`partition: []` runs the original 23-voivodeship model instead (20 s rather
than 4 minutes). Details are in `docs/METHODOLOGY.md` §12.6.

* **Data.** The 1931 county census by mother tongue covers the eight
  eastern voivodeships (97 counties, grade A). Lublin has county
  populations (grade B). The other counties have seats only and are
  downscaled from their voivodeship (grade C). County figures are fitted
  to the voivodeship totals of the starting point, so the county tables
  decide *where* speakers live and the research estimate decides *how many*.
* **Consistency.** Migration, income, enclave concentration and random
  numbers are nested in the voivodeships, so the county run reproduces
  the voivodeship model:

  | 2032 | Voivodeship run | County run |
  |---|---|---|
  | Population | 48.31 M | 48.21 M |
  | Ukrainian speakers | 9.06 M | 9.10 M |
  | Belarusian speakers | 1.92 M | 1.93 M |

* **What it adds is where.** In the baseline, 34 counties change their
  plurality language by 2032, all of them towards Polish except Klaipėda
  (German to Lithuanian):
  * Belarusian blocks: Grodno, Wołkowysk, Bielsk, Głębokie–Wilejka and
    Nieśwież–Słonim (12 counties);
  * all nine Polesie counties;
  * three Kashubian counties;
  * nine Ukrainian counties: eight of lwowskie (Sambor, Drohobycz, Sokal,
    Lesko ...) and Kamionka Strumiłowa.

  Lwów county grows from 460 k to 840 k people, Wilno from 415 k to 803 k.

![Plurality home language, 2032](outputs/maps/scenarios_plurality_2032.png)

## Scenarios (single seeded run each, 2032)

| Scenario | Population outside Lithuania (M) | Polish % | Ukrainian % | Yiddish % | Belarusian % | Lithuanian % | W. Polesian (k) |
|---|---|---|---|---|---|---|---|
| baseline | 46.2 | 64.6 | 18.9 | 3.9 | 4.0 | 4.2 | 924 |
| ii_rp_only | 46.3 | 67.2 | 19.9 | 4.1 | 4.2 | 0.2 | 945 |
| federal_autonomy | 46.1 | 59.1 | 20.2 | 4.6 | 5.7 | 4.2 | 1,536 |
| integral_nationalism | 45.7 | 69.0 | 17.6 | 3.2 | 3.0 | 4.1 | 534 |
| polonizing_union | 46.1 | 65.0 | 18.9 | 3.9 | 4.0 | 3.8 | 923 |
| census_official | 46.1 | 67.4 | 17.0 | 3.9 | 2.9 | 4.3 | 923 |
| census_vernacular | 46.2 | 63.3 | 19.8 | 3.9 | 4.4 | 4.2 | 924 |
| ukraine_autonomy_tricantonal | 45.7 | 55.8 | 20.2 | 4.4 | 9.6 | 4.2 | 1,331 |
| autonomy_grand_duchy_coofficial | 45.3 | 55.8 | 20.2 | 4.5 | 9.6 | 4.3 | 1,334 |
| wakar_poland | 32.7 | 70.1 | 6.6 | 4.7 | 12.5 | 0.0 | 1,091 |
| wakar_poland_belarus | 49.4 | 48.1 | 4.6 | 3.8 | 36.3 | 0.0 | 1,098 |
| no_official_language | 45.8 | 54.0 | 20.8 | 5.4 | 9.2 | 4.3 | 1,517 |

Polish-speakers in the Lithuanian units (Polish is co-official in Lithuania
in every scenario with the union, except the unitary `polonizing_union`):

| Scenario | 1933 | 2032 | of whom Lauda, 1933 → 2032 |
|---|---|---|---|
| baseline (federal) | 152 k | 127 k | 54 k → 38 k |
| polonizing_union (Polish the only official language) | 154 k | 355 k | 54 k → 78 k |
| census_official (the 1923 census as printed) | 78 k | 76 k | 23 k → 19 k |
| ukraine_autonomy_tricantonal (Lithuanian canton) | 153 k | 178 k | 54 k → 49 k |
| autonomy_grand_duchy_coofficial (one Grand Duchy) | 154 k | 347 k | 54 k → 80 k |

**Ukrainian autonomy + tri-cantonal Lithuania** (`ukraine_autonomy_tricantonal`).
Lwów, Tarnopol and Stanisławów voivodeships plus Volhynia form a Ukrainian
autonomy, on the never-implemented 1922 statute. Everything east of the
later Curzon line and north of Volhynia joins Lithuania as a Grand Duchy of
Lithuanian, Polish (Wilno–Lida–Grodno) and Belarusian (eastern Wilno lands,
Nowogródek, Polesie) cantons, made of whole counties. Polish is co-official
in the autonomy and in every canton. By 2032:

* Belarusian speakers number 4.6 M (1.9 M in the baseline). Belarusian
  rises from 36 to 55 % of its canton and leads 19 of its 20 counties.
* Ukrainian rises from 55 to 68 % of the autonomy. Lwów, Przemyśl,
  Tarnopol and four more counties turn Ukrainian-plurality; the ten
  counties west of the San stay Polish (79 → 58 %).
* Polish falls to 56 % of the union (64.6 % in the baseline).

**Four more political settlements** (details in `docs/SCENARIOS.md`):

* `autonomy_grand_duchy_coofficial`: the same autonomy, and an undivided
  Grand Duchy with **Lithuanian, Polish and Belarusian co-official**.
  * Belarusian becomes the Duchy's largest language (19 → 39 %), and Polish
    holds its share (24 → 22 %).
  * Polish and Belarusian spread into the Lithuanian lands: Kaunas falls
    from 64 to 51 % Lithuanian, and Lithuania's Poles more than double.
* `wakar_poland` (**Wakar's Poland**): Poland without Volhynia, Stanisławów,
  Tarnopol and the Vilnius region, with Polish and Belarusian co-official.
  * 25.7 M people in 1933, 32.7 M in 2032.
  * Belarusian grows from 1.1 M to 4.1 M speakers (12.5 %) and leads 19
    counties, Polesie included.
* `wakar_poland_belarus` (**Wakar's Poland-Belarus**): Wakar's Poland
  together with **all of Soviet Belarus** (the BSSR of 1926, from the 1926
  Soviet census), Polish and Belarusian co-official.
  * 31.1 M people in 1933 (5.4 M in Soviet Belarus), 49.4 M in 2032.
  * Polish falls from 61 to 48 %, Belarusian rises from 17 to 36 %
    (18 M speakers). Soviet Belarus grows to 13.5 M, 84 % Belarusian.
* `no_official_language`: no language is privileged, every written
  standard is official, and each county works in its largest language.
  * Polish ends at 54 % of the union, and about 5 M more people keep a
    minority language than in the baseline.
  * Only 18 counties change their plurality language.

**The equal-exchange Curzon line.** For every 5-year frame the atlas can
draw (in magenta) a continuous line across the state, from border to border
and free to wind cell by cell, that leaves as many non-Poles on its Polish
side as Poles on its other side, with the most Poles on the Polish side.
Kashubians, Wymysorys speakers, Germans and Jews are not counted.

* In the baseline it moves 1.9 M people each way in 1932 and 5.2 M in 2032.
* In 1932 the Polish side keeps the Wilno lands (through a strip along the
  Lithuanian frontier) and Lwów; Lithuania, the Belarusian lands, Volhynia
  and the rest of eastern Galicia are on the other side.
* By 2032 the Polish side has spread east over a Polonised Polesie.

![Curzon line, baseline](outputs/maps/map_curzon.png)

The full table is in `outputs/scenario_summary.csv`; the assumptions are in
`docs/SCENARIOS.md`. Proposed further developments are in `docs/ROADMAP.md`.

## Repository layout

```
plsim/
  data/regions.py        23 spatial units (1931 voivodeships + Lithuanian units)
  data/languages.py      languages, communities, (community, language) groups, shift targets
  data/census1931.py     1931 / 1923 / 1897-anchored reconstructions, bilingual shares
  data/network.py        towns, c.1931 rail network, paved roads, dated & planned projects
  demography.py          life tables, e0 frontier model, Alkema TFR, schedules, initial ages
  migration.py           Rogers-Castro, urbanisation, spatial interaction, migration hump
  language.py            transmission, enclaves, institutions, census observation model
  infrastructure.py      network, travel times, gravity demand, appraisal, investment
  economy.py             convergence, regional incomes, motorisation, budgets
  model.py               the annual simulation loop
  ensemble.py            Monte-Carlo parameter sampling and summaries
  validate.py            1932-39 back-validation and plausibility checks
  report.py, export.py   figures, CSVs, HTML report
  data/geography.py      3.5 km map grid (7 km model grid), 1932 state borders, county language anchors
  data/bssr.py           Soviet Belarus (BSSR, 1926 census by okrug), for wakar_poland_belarus
  data/borders_1932.json Poland and Lithuania on 1 Jan 1932 (CShapes 2.0)
  data/subregions.py     county-line splits of voivodeships (Curzon line, cantons, the San)
  data/counties.py       269 counties (1931 powiaty, 1923 apskritys) with graded census rows
  partition.py           1931 population of sub-regions and counties, via the grid
  data/geo_base.json     coastline, lakes and rivers (GSHHS via basemap-data)
  spatial.py             downscaling + neighbourhood (Prochazka-Vogl) language-shift allocation
  maps.py, webmap.py     static maps, GIF animations, interactive atlas data
  curzon.py              the equal-exchange Curzon line (dynamic programming over the grid rows)
  atlas_template.html    the interactive atlas page
  cli.py                 command-line interface
scenarios/*.yaml         12 scenarios (extends/override)
tools/build_geodata.py   rebuilds the base map and the Soviet Belarus border (shapely; not needed to run)
docs/                    METHODOLOGY, DATA_SOURCES (with reliability grades), SCENARIOS, ROADMAP
outputs/                 report.html, figures/, maps/, atlas/, scenario_summary.csv, ensemble CSVs, baseline run CSVs
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
