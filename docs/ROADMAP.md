# Roadmap: proposed developments

The current model is a county-level (powiat) cohort-component projection,
started from a research reconstruction of the 1931 population. It has
language shift, migration and network growth, and a 3.5 km spatial layer
for maps. The proposals below are ordered by value for effort.
Each names the part of the code it touches.

## Priority list

| # | Development | Why it matters | Effort |
|---|---|---|---|
| 1 | "As a census would print it" maps | The observation model exists (`language.census_view`). Applying it per cell would show, for the same latent population, what a 1931-style Polish census, a 1923-style Lithuanian census or a modern self-identification census would record. This turns census unreliability into something visible. | small |
| 2 | Identity as a state separate from home language | Many key cases are identity, not language: Catholic Belarusian speakers declaring Polish, Polish-speaking Lauda gentry who became Lithuanian by identity, Polish-speaking Jews. The census regimes would then map identity, and "Lithuanisation" could be modelled as identity shift with or without language shift. | medium |
| 3 | County data — **projection done, data partial** | Every scenario now runs on the powiats (270 regions; `data/counties.py`, METHODOLOGY §12.6). The 1931 county tables are in for the eight eastern voivodeships (grade A); Lublin has county populations only, and the centre, the west and Lithuania have seats only. Still to do: the central and western county tables (Kashubian, German and Jewish districts), the 1923 Lithuanian apskritis tables (Lauda), county religion for all voivodeships, and digitised powiat boundaries. | small (data entry) |
| 4 | Calibration by history matching | Fit shift propensities, status and institutional parameters to observed changes rather than by hand. Targets: 1897→1931 county language change, 1921 vs 1931 censuses, interwar Lithuanian censuses, and analogues (Carinthia, Bukovina, Finland Swedes). | medium |
| 5 | Probability maps from ensembles | Downscale every ensemble member and map, for example, the probability that Belarusian still leads a cell in 2032. Shows which fronts are robust and which are noise. | small |

## Spatial resolution and geography

* **Real boundaries.** The state borders now come from CShapes 2.0. The
  voivodeships and counties inside them are still weighted Voronoi
  approximations. Digitised 1931 voivodeship and powiat boundaries
  (historical GIS sources, e.g. the MPIDR Population History GIS
  Collection) would replace them; `data/geography.py` keeps the same
  interface. County shapes
  would then come from the boundaries rather than from the cells nearest
  each seat; on the maps, a county now ends halfway to the next seat.
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

* **History matching or ABC** with emulators (Vernon et al. 2010;
  Andrianakis et al. 2015). This rules out parameter regions inconsistent
  with the targets listed above.
* **Global sensitivity analysis** (Sobol indices) of the language outcomes,
  to show which assumptions drive them, e.g. status versus schooling versus
  differential fertility.
* **Out-of-sample checks** against settings the model was not tuned on:
  Lithuanian Poles 1959-2011, Carinthian Slovenes 1880-2001, Bukovina
  1880-1930.

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
