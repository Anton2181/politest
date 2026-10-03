# Roadmap: proposed developments

The current model is a county-level (powiat) cohort-component projection,
started from a research reconstruction of the 1931 population. It has
language shift, migration and network growth, and a 3.5 km spatial layer
for maps. The proposals below are ordered by value for effort.
Each names the part of the code it touches.

## Priority list

Done in earlier rounds (see METHODOLOGY): identity separate from home
language (§6.7), history-matching calibration of the shift rates (§6.4),
probability maps from the ensemble (§11), a calibrated road programme
(§7.3), second-generation assimilation (the diaspora term, §6.4), the
historical Curzon line and a population-exchange scenario (§12.8).

Done in this round: the Pomorze county tables, from the census volume
(§12.6); the governorates of 1897 as borders for the krai scenarios and as
constraints on the north-eastern voivodeship and county shapes (§12.1,
§12.5), with the krai's lands outside the 1932 states (§12.7); separate
economies for separate states (§8); settlement destinations from the
military-settler statistics (§5.2); an exchange by declared nationality
(§12.8); the eastern fertility transition checked against rural eastern
Poland (§4.2).

| # | Development | Why it matters | Effort |
|---|---|---|---|
| 1 | **County language tables for the centre and the west, Lithuania and Soviet Belarus** | Pomerania is done (grade A, from the census volume). Grade C counties (Warsaw, Łódź, Kielce, Kraków, Poznań, Silesia; the Lithuanian apskritys) are still downscaled from their voivodeship, so the German districts of Poznań, and the Jewish shtetl counties of Kielce and Lublin are smoothed. The tables exist: the 1931 census volumes by voivodeship (*Statystyka Polski*, seria C), digitised in the Kujawsko-Pomorska, Mazowiecka and Wielkopolska digital libraries; the 1923 Lithuanian census by apskritis; the 1926 Soviet census by raion. All of those hosts were blocked from the build environment. Entering them is data entry into `data/counties.py` (grade A rows). | small (data entry) |
| 2 | **Real 1931 powiat boundaries** | The county borders are Voronoi approximations. The MPIDR Population History GIS Collection holds Poland's 1931 administrative division (registration required; not reachable here). The model is ready for it: put the polygons in `plsim/data/powiaty_1931.geojson`, with `tools/match_powiaty.py` adding the county codes by name, and `data/subregions.assign` uses them. | small once the file is in hand |
| 3 | A stronger frequency effect | History matching shows the model's loss is less concentrated where a minority is small than in Masuria (1890-1910). Attraction now counts bilingual minority speakers as competent in the state language, which flattens the Abrams-Strogatz frequency term. Testing an attraction based on home-language shares, or a separate local-majority term, against the Masurian and Carinthian district series would sharpen language frontiers. | medium |
| 4 | Calibrate identity | The identity layer's starting mixes match the 1921 nationality census and the 1923 Lithuanian census, but its rates (nation-building, the state pull, `follow`) are judgements. County-level 1921 nationality against 1931 mother tongue, and the 1923 -> 1942 Lithuanian series, would let them be history-matched like the shift rates. Identity by age would also let the "follow" rule act on cohorts. | medium |
| 5 | Downscaling uncertainty | The probability maps vary the model's parameters and shocks but not the spatial downscaling (kernel widths, town seeding, the share of shift placed by neighbourhood). Drawing those per member would widen the bands on the frontiers. | small |
| 6 | "As a census would print it" maps | The observation model (`language.census_view`, `identity.identity_census`) applied per cell would show what a 1931-style census, a 1921-style nationality census or a modern self-identification census would record, for the same population. | small |

## Spatial resolution and geography

* **Real boundaries.** The state borders now come from CShapes 2.0. The
  voivodeships and counties inside them are still weighted Voronoi
  approximations. Digitised 1931 powiat boundaries plug in through
  `plsim/data/powiaty_1931.geojson` (priority 2); voivodeship boundaries
  would need the same in `data/geography.py`.
* **County-level calibration.** County runs inherit the voivodeship
  calibration. Migration is nested so a split voivodeship sends and draws
  as one, but language shift runs on each county's own mix. Comparing
  1897 (uezd) or 1921 county figures with 1931 would test shift rates
  county by county.
* **Town composition.** Use 1931 town-level religion and language (the
  Jewish share of each town) instead of the regional urban mix tilted by
  the hinterland. This fixes Pińsk, Brody and the Galician shtetls
  (`spatial.Downscaler.initial_state`).
* **Village resolution.** A 1 km grid would match Prochazka & Vogl's scale,
  with gminas as the administrative unit for schools. That needs real
  population density (e.g. 1931 gmina totals) rather than terrain factors.

## Language dynamics

* **Local dynamics.** At present, regional rates are set by the cohort model
  and placed by the neighbourhood rule. The next step is a genuine
  reaction-diffusion or agent model on the grid (Patriarca & Heinsalu 2009;
  Prochazka & Vogl 2017), constrained by or replacing the regional rates,
  and fitted to observed front movements such as the Polish-Belarusian line
  in the Wilno lands between 1897 and 1931.
* **Boundary sharpening and dialects.** Burridge's surface-tension model
  (2017) would let linguistic borders sharpen or blur, and could represent
  dialect levelling inside Polish (Silesian, Podhale) and the Polesian
  continuum, which is now a single category.
* **Mixed marriages.** Polish-Ukrainian and Polish-Belarusian mixed
  marriages were common in Galicia and the north-east, with rite rules
  (sons follow the father, daughters the mother). Transmission is now
  mother-based. A marriage market with an intermarriage rate would add a
  realistic shift channel.
* **Municipal language rules.** Finnish-style thresholds (a municipality is
  bilingual if the minority exceeds 8 % or 3,000 people) give minority
  schooling and status locally rather than per voivodeship. They need the
  county or cell level.
* **Endogenous religion.** Rite change between Greek and Roman Catholicism
  (the latynnyky), Orthodox autocephaly, secularisation, and Jewish
  community transitions tied to scenarios for Palestine and Israel.

## Demography and migration

* **Bayesian vital rates.** Probabilistic TFR and e0 by region in the
  manner of the UN World Population Prospects (Alkema et al. 2011; Raftery
  et al. 2013), with hierarchical regional effects fitted to European
  comparators instead of single draws per run.
* **Agrarian sub-model.** The 1925 land reform and estate parcellation,
  farm sizes and rural overpopulation as the push behind migration. This
  replaces the reduced-form push.
* **Cell-level migration.** Radiation or intervening-opportunities models
  (Stouffer 1940; Simini et al. 2012), and return migration from France,
  Belgium and the Americas.

## Infrastructure and economy

* **Real alignments and freight.** Historical railway geometry, Vistula
  navigation, the ports of Gdynia and Gdańsk, and coal flows from Silesia
  to Gdynia along the Coal Trunk Line. A freight model would drive the
  1930s investments the way passenger demand does now.
* **Better network design.** The current algorithm is greedy yearly
  appraisal by benefit-cost ratio. Multi-period portfolio optimisation (a
  bi-level network-design problem) would value complementary projects
  together and add wider economic impacts from agglomeration.
* **Sectoral economy.** A two- or three-sector Lewis model (agriculture,
  industry, services) with the Central Industrial District as an industrial
  shock. This would link urbanisation, income convergence and the
  modernisation that drives language shift.
* **Access to schools and towns.** Travel time from each cell to a town or
  secondary school over the network, as a local driver of shift (Weber's
  "peasants into Frenchmen"), instead of a regional market-access index.

## Calibration, uncertainty and validation

* **History matching: next waves.** The language rates are now history
  matched on five cases (METHODOLOGY §6.4) by brute force. Next steps:
  * an emulator (Gaussian process; Vernon et al. 2010; Andrianakis et
    al. 2015), which would allow more parameters and more waves;
  * more cases: Bukovina 1880-1910, Finland Swedes with their demography,
    Upper Silesian Polish 1890-1910, Latgale;
  * per-case settings drawn as nuisance parameters, instead of fixed
    judgements.
* **Global sensitivity analysis** (Sobol indices) of the language outcomes,
  to show which assumptions drive them, e.g. status versus schooling versus
  differential fertility.
* **Out-of-sample checks** against settings the model was not tuned on:
  Lithuanian Poles 1959-2011, Carinthian Slovenes 1910-2001 (the matching
  stops at 1910), Bukovina 1880-1930.

## Belarus and the Curzon line

* **Soviet Belarus at raion level.** The 1926 census also has raion
  tables. With them the 12 okrugs could become ~100 counties, and the
  religion split (Catholic Belarusians in the west) could rest on data
  rather than assumption.
* **Counterfactual 1921-31.** Soviet Belarus now starts from the Soviet 1926
  census, grown under Polish-like vital rates. A Polish 1921-31 (no
  Belarusisation, no early collectivisation, Polish schools in the towns)
  would change the start, mostly in the towns.
* **Curzon line.** The line follows county borders; the search is a
  heuristic. An exact or better bound (integer programming on the county
  graph, or simulated annealing) would show how far from the optimum it is.
  Counting by identity is done (`curzon_count: identity`). Variants: a
  length penalty for a smoother line, a line fixed in 1932 with the
  minorities on each side followed over time, or Poland alone in the union
  scenarios. The historical line (A in Galicia) is now digitised to about
  10 km from its description. Line B and a survey-grade digitisation are
  still to do.
* **Population exchange.** The two exchange scenarios along the computed
  line were removed; the real transfers of 1944-47 are replayed in
  `historical` (METHODOLOGY §12.10). A counterfactual exchange could now be
  written with the same `history` events (``transfer`` by identity).

## Political structure

* **Endogenous politics.** A small political-economy module: minority
  shares, income gaps and policy produce mobilisation (autonomy demands,
  radicalisation), which feeds back into policy, emigration and conflict
  risk. Scenarios would become stochastic trees, e.g. a yearly probability
  of federalisation after 1938.
* **Hypothetical censuses.** Simulated 1950, 1960 or Grand-Duchy censuses
  with a nationality question, using the observation model, for direct
  comparison with real post-war censuses of the same lands.

## Software and the atlas

* **Speed.** A county-level run takes about 4 minutes, against 20 s for
  the voivodeship model. Runs are cached and run four at a time, but a
  32-member county ensemble still takes about 40 minutes. Vectorising the remaining per-region loops
  (network step, settlement) and compiling the language step (e.g. numba)
  would make county ensembles practical.
* **Atlas.** A split view to compare two scenarios, a census-regime toggle
  (see 1), a time series of the clicked cell, and deep links to a scenario
  and year.
