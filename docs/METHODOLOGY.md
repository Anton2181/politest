# Methodology

This document describes every component of `plsim`, the modelling literature
each one follows, how parameters were chosen, and what the model cannot do.
It is written so that each assumption can be checked and changed.

## Contents

1. [Purpose and design principles](#1-purpose-and-design-principles)
2. [State space and time step](#2-state-space-and-time-step)
3. [Initial conditions and the reliability of the censuses](#3-initial-conditions-and-the-reliability-of-the-censuses)
4. [Demography](#4-demography)
5. [Migration](#5-migration)
6. [Language shift, bilingualism and extinction](#6-language-shift-bilingualism-and-extinction)
7. [Transport networks](#7-transport-networks)
8. [Economic drivers](#8-economic-drivers)
9. [How the parts are coupled](#9-how-the-parts-are-coupled)
10. [Calibration and validation](#10-calibration-and-validation)
11. [Uncertainty](#11-uncertainty)
12. [Maps: spatial downscaling and local language shift](#12-maps-spatial-downscaling-and-local-language-shift)
13. [Limitations](#13-limitations)
14. [References](#14-references)

---

## 1. Purpose and design principles

The question is counterfactual: *what would have happened to the population,
languages and infrastructure of the interwar Polish state, optionally in
union with Lithuania, if there had been no Second World War?* A question like
this cannot be answered by extrapolating a trend. The model therefore:

* **starts from data.** The 9 December 1931 Polish census and the 1923/1925
  Lithuanian censuses fix the starting state. The 1932-1939 years are
  simulated and compared with the registered 1930s aggregates (back-validation,
  §10).
* **uses published model structures** for each process: cohort-component
  projection, the UN/Alkema TFR transition model, best-practice-gap mortality,
  Rogers-Castro age schedules, spatial-interaction migration, the migration
  hump, Abrams-Strogatz / Minett-Wang / Kandler-Steele language dynamics,
  cost-benefit network growth and market access. The parameters come from the
  historical record where one exists, and from comparator societies without a
  Soviet-type regime (Spain, Portugal, Italy, Greece, Ireland, Finland) where
  it does not.
* **separates two kinds of uncertainty.** Uncertainty that can be measured
  (parameters, shocks) goes into Monte-Carlo ensembles. Political
  counterfactuals that cannot be measured (federalism or integral
  nationalism, the fate of the Lithuanian union, the growth path) become
  *scenarios* (see `SCENARIOS.md`).
* **keeps what people speak apart from what censuses record.** The interwar
  censuses are themselves contested evidence (§3), so the model tracks a latent
  home vernacular and adds an explicit observation model on top.

## 2. State space and time step

The population is held in one array

```
P[r, u, g, b, s, a]
  r  23 regions: 16 voivodeships + the city of Warsaw (1931 borders) and
     6 Lithuanian units (Kaunas, Lauda, Samogitia, Suvalkija, North-East,
     Klaipėda)
  u  rural / urban
  g  (community, home language) group, 43 combinations
  b  monolingual / also competent in the region's dominant language
  s  sex
  a  single years of age 0..100+
```

*Communities* are ethno-confessional (Latin Catholic, Greek Catholic,
Orthodox incl. Old Believers, Jewish-acculturating, Jewish-Haredi, Protestant,
Other). They govern fertility, mortality, emigration channels and the
*direction* in which a vernacular is likely to shift. *Languages*: Polish,
Ukrainian (incl. the census "Ruthenian"), Belarusian, West Polesian (the
"tutejszy" vernacular), Yiddish (incl. "Hebrew" declarants), German, Russian,
Lithuanian, Kashubian, Lemko-Rusyn, Czech, Latvian, Romani, Karaim, Wymysorys,
Other.

The model steps once per calendar year. The state is taken on 1 January;
1 January 1932 is identified with the census night of 9 December 1931. The
order of events within a year is:

1. economy (national and regional incomes, literacy, motorisation);
2. network (travel times, gravity demand, market access, appraisal and
   investment, dated projects, closures, town sizes);
3. vital rates (life expectancy and TFR updates);
4. births and **intergenerational language transmission**;
5. survival and ageing;
6. horizontal language processes (schooling, contact, conscription, adult
   re-identification);
7. rural-urban, inter-regional and international migration;
8. bookkeeping (a region's own dominant-language speakers are always
   competent in it) and recording.

A 100-year run takes about 20 s on one core.

## 3. Initial conditions and the reliability of the censuses

### 3.1 Poland, 1931

For each voivodeship, the published *mother-tongue* shares (Polish,
Ukrainian, "Ruthenian", Belarusian, "local"/tutejszy, Yiddish, Hebrew,
German, Russian, Lithuanian, Czech, other) are cross-read with the *religion*
shares (Roman Catholic, Greek Catholic, Orthodox, Jewish, Protestant, other).
Rules turn the two tables into (community, language) groups:

* Yiddish and Hebrew declarants are Jewish. The remaining Jews by religion are
  Polish-speaking Jews. The Haredi share of Yiddish speakers is 25-40 % by
  partition.
* Ukrainian/Ruthenian speakers are Greek Catholic in Galicia and Orthodox in
  Volhynia, Polesie and Chełm. Greek Catholics left over after that are
  *Polish-declared Greek Catholics*.
* Russian, Orthodox Belarusian and tutejszy speakers fill the Orthodox total.
  The Orthodox left over are *Polish-declared Orthodox*.
* A regional share of Belarusian speakers is Catholic (15 % in Wilno,
  5-10 % elsewhere, 50 % in Lublin).
* Germans are mostly Protestant; in Silesia most are Catholic.
* Groups the census did not enumerate are carved out by estimate:
  Kashubian (200 k; published estimates range from ~150 k to 500 k),
  Lemkos (~130 k, the figure derived from the 1931 census in Lemko studies,
  incl. ~16-18 k Orthodox), Wymysorys (~1,500), Karaim (~630 speakers in a
  community of 800-900), Romani (~30 k).

This **official** reading reproduces the published national totals: Polish
68.9 %, Ukrainian+Ruthenian 13.9 %, Yiddish+Hebrew 8.6 %, Belarusian 3.1 %,
German 2.3 %, tutejszy 2.2 %; religion Roman Catholic 64.8 %, Jewish 9.8 %,
Orthodox 11.8 % (tested in `tests/test_census.py`).

### 3.2 Why the census cannot be taken at face value

* In 1931 the question asked for *mother tongue* instead of 1921's
  *nationality*. Offering "tutejszy" and "ruski" as categories fragmented the
  Belarusian and Ukrainian counts.
* Cross-reading language and religion shows several hundred thousand
  Orthodox and Greek-Catholic people recorded as Polish-speaking. In
  Nowogródek, 52 % were recorded as Polish-speaking while only ~40 % were
  Catholic.
* The head of the census office, E. Szturm de Sztrem, later said the returns
  may have been altered by the administration, to an unknown extent. T.
  Piotrowski calls the use of mother tongue as an indicator of nationality
  "questionable methodology".
* J. Tomaszewski's religion-corrected estimate puts ethnic Poles at 64.7 %
  (against 69 % Polish mother tongue). V. Kubijovyč argued that Ukrainians
  were undercounted by much more, including ~360 k Latin-rite
  Ukrainian-speakers (*latynnyky*) in Podlachia, Chełm and Lublin. His own
  figures are rounded and hard to reconcile with administrative units.
* The imperial Russian census of 1897 recorded *native language*. In Vilna
  governorate it found 56.1 % Belarusian, 17.6 % Lithuanian, 12.7 % Jewish and
  8.2 % Polish, yet the overlapping Wilno voivodeship reported 59.7 % Polish in
  1931. Part of the gap is real (Wilno city, three decades of schooling and
  migration). Part is a change in what was recorded: Catholic
  Belarusian-speakers were entered as Polish by identity.

### 3.3 Three reconstructions of the latent vernacular

| `census_variant` | What it assumes | Polish % | Ukr.+Ruth. % | Belarusian % |
|---|---|---|---|---|
| `official` | the census as printed (scenario `census_official`) | 68.7 | 14.0 | 3.1 |
| `religion_corrected` (**baseline**) | Tomaszewski (1985): 95 % of Polish-declared Greek Catholics -> Ukrainian, 95 % of Polish-declared Orthodox -> Belarusian/Ukrainian by region, 30 % of Polish-declared Protestants outside Cieszyn Silesia and Warsaw -> German. Reproduces his 64.7 % ethnic Poles, 7.07 M Ukrainians and Belarusians, 0.78 M Germans | 65.9 | 15.6 | 4.2 |
| `vernacular` | upper bound: the above, plus Catholic Belarusian and Lithuanian vernaculars in rural Wilno, Nowogródek and Białystok at 1897 proportions, and latynnyky calibrated to Kubijovyč (1983): 5.85 M Ukrainians, 515 k latynnyky in Galicia (scenario `census_vernacular`) | 62.6 | 17.2 | 5.7 |

The Polish percentages here are home language, so they include about 0.4 M
Polish-speaking Jews. Ethnic Poles are 67.5 %, 64.7 % and 61.4 %. Sources and
the full comparison with the literature are in `docs/DATA_SOURCES.md`.

### 3.4 The census as an observation model

`plsim.language.census_mapping` gives, for each latent state (community,
home language, bilingual, region), the probability of each census category
under a given regime:

* `polish_1931`: Catholic Belarusian-speakers are mostly returned as Polish,
  Polesians as "tutejszy", Greek Catholics split between "ukraiński" and
  "ruski", some Zionist Yiddish-speakers declare Hebrew, Kashubian is folded
  into Polish, and so on;
* `imperial_1897`: vernacular recording; no Kashubian or Rusyn categories;
  Polesians as "Little/White Russian";

Those two are *language* censuses and read the latent home language. The
*nationality* censuses read national identity, which the model tracks
separately (§6.7):

* `polish_1921`: the nationality question of 1921. There were no Kashubian or
  Lemko categories, and enumerators entered most "local" people under a
  nationality;
* `lithuanian_1923`: the Lithuanian nationality census. Its Polish count
  follows the Polish *identity* of Lithuania's Polish speakers, which starts
  at 42 % and can drift further (Lithuanisation);
* `modern_selfid`: today's self-identification, read directly from identity.

**Consistency test** (`python -m plsim census`). If you pass the baseline
(religion-corrected) or the vernacular reconstruction through the 1931
regime, you get back the published national shares, with a total absolute
error of 1.0 and 1.9 points across the eight categories. The recording
probabilities were calibrated so that Tomaszewski's population gives back
the printed census. So a population that really spoke
the corrected languages at home would have produced the census that was
actually printed. That is the quantitative form of the argument in §3.2. The
model reports its results both as latent home languages and as a given census
regime would have recorded them.

### 3.5 Lithuania

The 1923 Lithuanian census (2.03 M without Klaipėda) and the 1925 Klaipėda
census (141.6 k: 43.5 % German, 27.6 % Lithuanian, 25.2 % "Memellanders")
are carried forward to end-1931 (~2.39 M; Kaunas city to ~115 k, the rest
at ~1.1 % a year) and split into six units. The five units of the Kaunas
state add up their apskritys of 1923 (`census1923_apskritys.csv`): their
areas, and their (community, language) shares from nationality and
religion. Germans and Latvians are taken as Protestant, the other
Protestants as Lithuanian (the Lutherans of the Prussian border, the
Reformed of Biržai), Russians as Orthodox or Old Believers. Klaipėda's
Memellanders become Lutheran Lithuanian-vernacular speakers who are highly
bilingual in German. The Polish-speaking population has three variants
(`lt_variant`):

| variant | Polish-speakers | source |
|---|---|---|
| `census_1923` | 65.6 k declared (3.2 %); ~77 k Polish-speakers with Jews and others | Lithuanian census |
| `research` (**baseline**) | ~150 k (6.3 %) | middle of the range; historians' estimates run from the census to the Polish claim, which Buchowski (1999) holds "very probable" |
| `polish_claim_1923` | ~175 k (7.3 %) | Polish electoral committee's 1923 claim (202 k, ~10 %), from the Polish vote |
| `imperial_1897` | ~160 k (6.8 %) | 1897 Kovno governorate native-language tables (~9 %) |

The **Lauda** country (Kėdainiai-Panevėžys-Ukmergė-Raseiniai), home of the
Polish-speaking petty gentry, is a separate unit (`LT_LAU`). Lithuanisation
there was not inevitable: the scenarios switch between a federal bilingual
regime (baseline), the historical forced Lithuanisation, and a unitary
union in which Lithuania is part of Poland (§6.6).

### 3.6 Urban/rural split, ages, bilingualism

* **Urban split.** Groups differ by urban-residence odds ratios (Jews
  ~12-22x the local baseline; Polish-speakers in the Kresy 1.5-3x;
  Polesians, Lemkos and Ukrainian peasants 0.1-0.25x). In the sixteen
  voivodeships the census prints every powiat's towns and countryside by
  mother tongue and religion (`census1931_strata.csv`); there the odds are
  raked, a factor per census language and per religion, until each has its
  census urban share (religions first, so where the two disagree the
  languages hold), and the base odds then give the census urban share of the
  voivodeship. Kashubian, Lemko and the other languages the census counted
  inside Polish or Ukrainian take that category's factor and keep their
  odds relative to it. Elsewhere a per-region base odds is solved so that
  the regional urban share matches the census and the Polish total matches
  27.4 %. The voivodeship religions are the pages' too wherever the pages
  printing a religion hold 90 % of the voivodeship (`RELIGION_1931`).
* **Age-sex structure.** Each cell is a stable population whose fertility
  blends current and pre-1914 levels (35 %/65 %). This reflects the fact that
  1931 age structures were shaped by earlier fertility and by young-adult
  in-migration to towns. The youngest cohorts (ages 0-11) are blended towards
  a stable population at *current* fertility, scaled to the same number of
  women aged 15-49, so that the 1931 cohort joins the simulated births of 1932
  without a notch. On top of that, the birth deficit of 1915-1920 (cohorts
  aged 11-16 in 1931 at 50-85 % of normal size, deepest in the Russian
  partition) and male war losses at ages 32-55 are imposed. The result is
  ~34 % aged 0-14 and ~8 % aged 60+. It has the characteristic 1931 shape: a
  large base from the post-1920 birth recovery, the hollow WW1 cohorts, then
  the older population. The hollow cohorts entering childbearing ages are part
  of why births fell in the late 1930s.
* **Bilingual competence.** Initial shares by group and rural/urban (e.g.
  urban acculturating Jews 85 %, rural Orthodox Belarusians 28 %, Kashubians
  85 %), with an age profile peaking at 15-29.

## 4. Demography

### 4.1 Mortality

**Age pattern.** A three-component Siler (1979) hazard
`mu(x) = A e^{-Bx} + C + D e^{Gx}`. A single "health progress" index `k`
lowers the child component fastest, the background component next and the
senescent component slowest (log-slopes 1.05, 0.95, 0.25). This reproduces
the rectangularisation of twentieth-century European life tables:

| e0 (female) | infant mortality | e65 |
|---|---|---|
| 51.5 (Poland 1931-32: 51.4) | ~120/1000 (m ~140) | 12.8 |
| 74 | ~16 | 16.9 |
| 85 | ~1 | 23 |

A target e0 is inverted to `k` on a precomputed grid (0.05-year steps), and
the life table supplies survival ratios `L(x+1)/L(x)`. Newborns survive to
the end of their birth year with `L(0)`.

**Level.** A best-practice-gap model:

* The frontier (record female e0) rises 0.243 years per calendar year
  (Oeppen & Vaupel 2002; 67.1 in 1931, 83.9 in 2000), slightly slower after
  2000.
* Each (region, urban/rural, community) cell closes its gap to
  `frontier - gap(y/y*)`, a Preston-curve (Preston 1975) income-dependent gap
  of 1.5 years at the frontier's income up to `gap_max` at zero income:
  12 years until 1945, halving to 6 by 1955 (the post-war shift of the
  Preston curve: in 1960 Poland's women were 3.6 years behind best practice
  at a third of its income; Portugal, Spain, Greece, Bulgaria 2.5-8). The
  1945-55 shift is calibrated on the historical scenario (§12.10), where
  People's Poland adds its own schedule (2.5 in 1955-65, rising to 8 by
  1990: the socialist stagnation, with a sex gap of 9 years in 1991).
* The catch-up rate jumps from 3 %/yr before 1945 to 12 %/yr after 1951.
  This is the sulphonamide / penicillin / streptomycin / DDT / vaccination
  "mortality revolution" that took southern and eastern Europe from e0 ~50
  to ~65-70 within 15 years.
* Community differentials (Jews +4 years in 1931, Protestants +2, Orthodox
  -0.5, Roma -8) decay with a 35-year half-life.
* The male-female gap follows a schedule: 3.2 years in 1931, widening to
  6.6 in 1985 (the European male cardiovascular and smoking peak), then
  narrowing.
* The gain-vs-level profile this produces is close to the double-logistic
  gain function of Raftery et al. (2013) used by the UN; compare Torri &
  Vaupel (2012) for forecasting relative to best practice.

### 4.2 Fertility

The TFR follows the **three-phase model of Alkema et al. (2011)**, which
underlies the UN World Population Prospects (bayesTFR):

* **Phase II** (the transition): the expected 5-year decrement is a
  double-logistic function of the current TFR,
  `g(f) = d [ -1/(1+e^{-(2 ln 9/D1)(f-U+D1/2)}) + 1/(1+e^{-(2 ln 9/D3)(f-D4-D3/2)}) ]`.
  The decline starts slowly at high levels (U), is fastest in the middle and
  slows near the end level D4.
* The **pace `d`** is scaled by a modernisation index (literacy, urbanity,
  income). This reflects the Princeton European Fertility Project finding
  that declines spread along cultural-linguistic and religious lines (Coale
  & Watkins 1986; Lesthaeghe 1977). There are community pace factors:
  Greek Catholic 0.9, acculturating Jews 1.1, and Haredi 0.12, whose
  fertility drifts to its own long-run mean. The Orthodox decline at the
  Catholic pace (1.0); their higher interwar fertility is in the level
  (x 1.05), not the pace.
* **Calibration on the historical scenario** (§12.10). Run on the real
  century, the earlier settings put rural Poland at 2.4 children per woman
  in 1970 and 2.0 in 1980 (census: 2.99 and 2.92) and left the Soviet-ruled
  Kresy at 3.1 in 1970 (western Ukraine and Brest about 2.6), while the
  counterfactual Volhynia and Polesie kept 4-5 in the countryside in 1970.
  The modernisation index made the transition too fast in the advanced
  countryside and too slow in the backward one. Four changes, together:
  * the decline is under way in 1931 where fertility is high: `U` is at
    least 0.5 above the current level (`onset_offset`), so the Kresy do not
    sit at the slow start of the double logistic for decades;
  * the pace depends less on modernisation (floor 0.75 of the maximum,
    was 0.55) and is slower in the countryside (x 0.7; `pace_stratum`);
  * the transition ends higher in the countryside (D4 + 0.8;
    `D4_rural_offset`), and the rural long-run mean is 0.3 higher
    (`phase3_mu_rural_offset`).
  With the historical scenario's own period effects (war, post-war
  compensation, the pro-natalism of the 1970s-80s, the slump after 1990),
  the model then gives Poland 3.71 in 1950 (census 3.71), 2.86 (2.98) in
  1960, 2.25 (2.20) in 1970, 2.36 (2.28) in 1980, 2.04 (2.04) in 1990, 1.43
  (1.37) in 2000 and 1.38 (1.38) in 2010, and the Soviet-ruled Kresy about
  2.7 in 1970. The 1930s checks (§10.1) still pass.
* **Phase III**: once TFR reaches D4 + 0.12 the cell follows an AR(1)
  process (rho = 0.93) around a long-run mean. That mean is 1.45 for the
  Catholic/Orthodox majority, with ensemble spread; the Catholic southern
  European "lowest-low" experience is 1.2-1.5.
* **Period effects**: the Depression trough (-9 % by 1938, recovering by
  1950), a moderate baby boom centred on 1956 (+10 %, range 0-20 %). Without
  the war, the boom is only the prosperity/marriage component seen in
  non-belligerent Europe (Sweden, Switzerland, Portugal); there is no
  post-war catch-up. There is also a small AR period noise.
* **Starting levels**: 1931 regional TFRs (rural 3.5-5.25, urban 1.95-3.4)
  consistent with the religion-specific TFRs published for 1931 (Roman
  Catholic 3.3-3.7, Jewish 2.5-2.9) and regional crude rates, then scaled
  (`tfr_scale` 1.07) to match the 1932 crude birth rate.
* **Age schedules**: normalised gamma densities (Hoem et al. 1981). The mean
  age at childbearing rises with TFR (high-parity regimes), falls through the
  transition and rises again with post-1982 postponement (+0.13 yr/yr, up to
  +4).

### 4.3 The cohort-component step

Births = Σ over ages 15-49 of women x ASFR(region, urban, community) x a
group factor (Roma 1.35, Karaim 0.8). The sex ratio at birth is 1.06.
Language and community of the newborn are set by intergenerational
transmission (§6). Everyone ages one year with survival from their cell's
life table; the open interval is 100+. The accounting identity
`P(t+1) = P(t) + births - deaths - emigrants + immigrants` holds to machine
precision (`tests/test_model.py`).

## 5. Migration

All flows are age-specific, using **Rogers & Castro (1981)** model migration
schedules (pre-labour-force exponential + labour-force double exponential +
constant; peak ~20.5 for internal, ~22 for international moves).

### 5.1 Rural-urban

Each region moves towards an income-dependent urbanisation target,
`U* = 0.75 / (1 + exp(-1.2 (ln y - ln 3000)))`. That is 26 % at 1,800 GK$,
44 % at 4,000, 57 % at 8,000 and 66 % at 15,000 (cf. Davis & Henderson 2003).
Regional fixed effects (industrial Silesia, agrarian Polesie) decay over 60
years. Each year the flow closes 10 % of the gap (plus a 0.2 % floor).

This is the reduced form of the Lewis (1954) surplus-labour and Harris &
Todaro (1970) expected-income mechanisms. Interwar Poland's "agrarian
overpopulation", estimated in the 1930s at several million people, drains
to the towns as urban jobs appear.

### 5.2 Inter-regional

A production-constrained spatial-interaction model (Zipf 1946; Wilson 1971):

```
T_rj = O_r * W_j exp(-beta t_rj) Aff_gj / Σ_k W_k exp(-beta t_rk) Aff_gk
```

* **Out-migration rates** O_r rise with the income gap to the national mean
  (push elasticity 1.5).
* **Destination mass** W_j is (urban population + 0.2 x rural)^0.75 x
  relative *urban* income at the destination. Movers go mostly to towns, and
  the concave mass term keeps the capital from absorbing an implausible share.
  Calibration target: Warsaw's net in-migration of ~10-15 per 1000 per year
  in the 1930s (1921-39 city growth less natural increase); model ~15.
* **Travel time** t_rj is taken each year from the *current* transport
  network, so new lines re-route migration.
* **Affinity** Aff = (own-language share at destination + 0.02)^0.4 captures
  ethnic networks and language barriers.
* **PL<->LT moves** carry a cross-border friction of 0.1.
* **Group mobility multipliers**: Jews 1.3, Orthodox 0.7, Greek Catholics 0.6,
  Polesians 0.4, Roma 1.5.
* **Arrivals** go 78 % urban. Movers crossing into a region with a different
  dominant language arrive monolingual.

The radiation model (Simini et al. 2012) and Stouffer's (1940) intervening
opportunities are close alternatives. With 23 regions the gravity form is
easier to calibrate.

**Planned settlement** (*osadnictwo*): Polish Catholic smallholder families
move from Kraków, Kielce, Lublin, Warsaw and Lwów voivodeships to the east.
The flow is 8 k/yr in the 1930s, 12 k/yr for 1939-55 (Polesie drainage),
then zero; the `integral_nationalism` scenario raises it to 25 k/yr. The
destinations follow the military settlers of 1921-39 by voivodeship
(households): Wołyń 41.5 %, Nowogródek 21.7 %, Wilno 13.3 %, Polesie 12.6 %
and Białystok 10.9 %, the last on the estates of its Grodno-governorate
east (the Grodno and Wołkowysk counties). Earlier versions gave Polesie as
much weight as Volhynia and none to Białystok.

### 5.3 International

Net emigration follows the **migration hump** (Zelinsky 1971; Hatton &
Williamson 1998, 2005; de Haas 2010):

```
rate_g = base_g * hump(z) * openness(t) * fade(z) * push_r
hump(z) = (z/0.35)^2.5 exp(2.5 (1 - z/0.35)),  z = y / y_frontier
```

* Emigration is feasible only once incomes rise from very low levels, peaks
  around a third of the destination income and fades near z ~0.74. Beyond
  that point the country receives net immigration (up to 0.4 %/yr: returning
  diaspora, other Europeans and Ukrainians).
* **Openness** encodes destination policy: very low 1931-39 (US quotas from
  1924 with a Polish quota of ~6.5 k, the Depression), high 1946-73 (European
  guest-worker demand, re-scaled for a world without post-war
  reconstruction), lower after the 1973-74 recruitment stops (ramped over
  1973-77), higher after 1990.
* **Group channels**: Jewish emigration (to Palestine and the Americas; ~400 k
  recorded Jewish emigrants from interwar Poland) at 0.35 %/yr in the 1930s,
  declining with integration and halved for Haredim. German emigration to the
  Reich at 0.8 %/yr in the 1930s, declining.
* **1930s calibration**: net emigration ~30-40 k/yr, consistent with the small
  net outflows of the Depression years.

## 6. Language shift, bilingualism and extinction

### 6.1 Model family

The language module is a demographically explicit, multi-language
generalisation of the models below. It uses Abrams & Strogatz's
frequency-dependent attraction, a bilingual intermediate state as in Mira &
Paredes, Minett & Wang and Kandler et al., vertical transmission at birth,
and horizontal acquisition over the life course:

* **Abrams & Strogatz (2003)**:
  `dx/dt = y P_yx(x,s) - x P_xy(x,s)` with `P_yx = c x^a s`. The frequency
  dependence has an exponent a ~ 1.31 fitted to Welsh, Scottish Gaelic,
  Quechua and others.
* **Mira & Paredes (2005)**: a bilingual group and interlinguistic
  similarity.
* **Minett & Wang (2008)**: bilingualism plus vertical and horizontal
  transmission and social structure; languages can coexist only with
  status-planning intervention.
* **Kandler, Unger & Steele (2010)**: monolingual-bilingual-monolingual
  competition with internal recruitment (births, deaths, migration) of each
  pool. They estimated a Gaelic-to-bilingual shift rate of ~0.035/yr in
  Sutherland 1891-1971.
* **Cavalli-Sforza & Feldman (1981)**: vertical versus horizontal cultural
  transmission.
* **Spatial models**: Patriarca & Leppänen (2004); Kandler & Steele (2008);
  Isern & Fort (2014, linguistic fronts).

### 6.2 Intergenerational (vertical) transmission

A child of an (c, L, b) mother is raised in L unless the family shifts. The
per-birth shift probability is

```
p = sigma0(c,L) * Mod(r,u,t) * Pol(r,t) * (1 - omega(r,L))
    * Σ_K A_K / (A_L + Σ_K A_K) * (1 if b = 1 else m_mono)
A_K = s_K(r,t) * x_K^a        (Abrams-Strogatz attractiveness, a = 1.31)
```

* `s_K` is the **status** of language K in region r: policy, prestige and
  utility.
* `x_K` is the **local share of people competent in K**. For the dominant
  language this counts bilinguals.
* `sigma0` is a group's base propensity. For example: Catholic Belarusian
  speakers 0.55, acculturating Jews 0.50, Polesians 0.45, Orthodox
  Belarusians 0.22, Kashubians 0.20, Greek-Catholic Ukrainians 0.06,
  Haredim 0.02.
* `m_mono = 0.15`: monolingual mothers rarely shift. Bilingualism is the
  gateway, as in Kandler et al.
* `omega` is **institutional maintenance**: 0.5 x the share of children taught
  in their own language, plus community institutions such as the Greek
  Catholic church and Prosvita (0.3), German Protestant parishes (0.2) and
  the Haredi yeshiva world (0.5). This is the quantitative counterpart of
  Fishman's (1991) GIDS. It is scaled by **institutional completeness**
  (Breton 1964), `min(1, local own-language share / 0.25)`: churches,
  schools and a press sustain a language where its community is locally
  substantial, not in a scattered urban diaspora. Ukrainian migrants in
  Warsaw therefore shift much faster than Ukrainians in Stanisławów.
* `Mod` rises with urbanity (x1.6), modernisation (0.5 + M) and **market
  access** (x(1 + 0.15 ma)). Railways, roads, schools and the army as agents
  of national integration (Weber 1976) enter here, so the network feeds back
  on language.
* `Pol(r,t)` is the assimilation pressure of the political regime.
* **Targets** K are restricted by community (`SHIFT_TARGETS`). Catholic
  Belarusian speakers go to Polish (or Lithuanian); Orthodox ones to Polish or
  Russian; Polesians to Ukrainian, Belarusian, Polish or Russian;
  Memellanders to German; Lemkos to Ukrainian or Polish; acculturating Jews to
  Polish, Lithuanian, Russian or German. The region's dominant language is
  always admissible.

**Enclaves.** Minority speakers are spatially concentrated, so the share of
own-language speakers they meet is higher than the regional cell share. Each
language has a concentration factor k_L: Wymysorys 300 (Wilamowice), Karaim
60 (Trakai/Łuck/Halicz), Lemko 20, Czech 15, German colonists 5, Lithuanian
4, Kashubian 2.5, Yiddish 1.3. The local own share is `min(0.95, k_L x_L)`,
and the rest of the neighbourhood has the cell's non-L mix. This is a reduced
form of the spatial models: without it, every small enclave language would
face the full regional majority and vanish unrealistically fast.

### 6.3 Horizontal processes (annual hazards)

* **Schooling** (ages 7-14): acquisition of the dominant language at rate
  0.36 x enrolment x (1 - 0.7 x own-language schooling share) (history
  matched, §6.4; formerly 0.22).
* **Adult contact** (15-64): 0.022 x local dominant-language share x
  (1.8 in towns) (history matched; formerly 0.012).
* **Conscription** (men 20-21): 0.35 while conscription lasts.
* **Adult re-identification** of bilinguals: 0.25 %/yr scaled like the
  vertical term (history matched; formerly 0.3 %, then 0.21 %).
* **Marriage across languages** (bilinguals aged 20-34): a yearly rate of
  0.20 x P(partner from outside the group) x the pull of the other language,
  after which the couple's home language is the partner's. The chance of an
  outside partner follows a homogamy model of assortative mating (Kalmijn
  1998): with local own share s and homogamy odds H = 38,

      P(out) = (1 - s) / ((1 - s) + s x H)

  so a group that is half the neighbourhood marries out 2.6 % of the time and
  one that is 5 % of it 33 %. Compact minorities hardly feel it; scattered
  ones (Ukrainians and Lemkos after Operation Vistula, Belarusian and
  Lithuanian migrants in cities) lose most of their speakers within two
  generations, as the 1950-2002 Ukrainian decline shows. Jews married out
  very rarely (x0.1 for acculturating, x0 for Haredi Jews), and so did the
  Roma (x0.1) and the small faiths, Karaites and Muslim Tatars (x0.2);
  without this the baseline's Romani speakers fell to 1 thousand by 2032
  (40 thousand with it, 62 thousand before the marriage term). Half the mixed
  households (`exogamy_rite`) are counted in the partner's community, the
  community of most speakers of the contact language: in Galicia sons
  followed the father's rite and daughters the mother's, and in the west
  of People's Poland, without Greek Catholic parishes, the children of
  mixed marriages were mostly raised Roman Catholic. This moves identity,
  not language (§6.7).
* **Haredi defection** at birth: 20 % per birth in 1931, falling to 12 %.
  There is a small reverse flow.

### 6.4 Calibration: history matching on documented cases

**Why not the Polish censuses themselves?** The model starts in December
1931 and cannot run backwards. The two obvious Polish comparisons measure
something else:

* **1921 → 1931.** The 1921 census asked nationality, the 1931 census
  mother tongue and religion. 1.06 M Belarusians (1921) against 0.99 M
  Belarusian speakers plus 0.71 M "tutejszy" (1931), or 3.9 M Ukrainians
  against 4.4 M Ukrainian and "Ruthenian" speakers, measure the change of
  question and of the enumerators' practice. They do not measure ten years
  of shift. The identity layer (§6.7) now makes this explicit: the same 1931
  population read through the 1921 question gives back the 1921 shares.
* **1897 → 1931.** Between these censuses lie the 1915 evacuation (over a
  million people from the Grodno, Vilna and Minsk governorates, many of whom
  never returned), the wars of 1918-21, the departure of Russian officials,
  emigration and, again, a different question.

**Cases.** The shift rates are therefore matched to cases where the same kind
of minority language under the same kind of state language was counted the
same way at both ends (`plsim/calibration.py`):

| Case | Observed | Stands for |
|---|---|---|
| Masuria 1890 -> 1910, Polish/Masurian share by district (Prussian censuses) | Johannisburg 78.8 -> 68.0 %, Lyck 66.6 -> 51 %, Neidenburg 75.6 -> 66.6 %, Oletzko 47.7 -> 29.6 % | same-faith vernacular, no own schools: `RC:be` (with `RC:pls`, `RC:csb`) |
| Carinthian Slovenes 1880 -> 1910 (Umgangssprache) | 26.4 % -> 18.7-20.7 %, a share ratio of about 0.75 | same-faith national language with partly own schools: `RC:lt` (with `RC:uk`, `RC:de`, `RC:cs`, `RC:lv`) |
| Wales 1921 -> 1951 (aged 3+) | Welsh speakers 37.1 -> 28.9 % (ratio 0.78; home language falls faster, target 0.74); monolinguals 17 % -> 6 % of Welsh speakers | the same class; acquisition rates |
| Province of Posen 1871 -> 1910 | Polish share stable or rising despite Germanisation: shift net of migration about nil | different-faith nation with strong institutions: `GC:uk`, `OR:uk`, `PR:de` ... |
| Second generation of immigrants (Alba et al. 2002; Portes & Rumbaut 2001) | 40 % (Indian) to 76 % (Filipino) of children of immigrants spoke only English at home in 1990 | the diaspora floor `sigma_diaspora` |
| Ukrainians and Lemkos scattered over People's Poland, 1950 -> 2002 | about 170 k home-language speakers of 25.0 M after Operation Vistula; 29 k of 38.2 M at the 2002 census (share ratio about 0.11) | a different-faith group with no institutions, dispersed: the marriage term |

**Harness.** Each case is run through the model's own `LanguageModel`: vertical
transmission, acquisition and re-identification. The population is a stylised
single region with a stable age structure and the case's setting: status,
own schooling, institutions, pressure, modernisation and clustering. Minority
and majority have the same demography, so only shift moves the shares; the
diaspora case is an immigrant cohort.

**Method.** History matching (Craig et al. 1997; Vernon, Goldstein & Bower
2010):

* Twelve parameters are drawn by Latin hypercube: the three class
  propensities, a, m_mono, h0, completeness_share, sigma_diaspora, the two
  acquisition rates and the two marriage terms (exogamy, homophily).
* A draw is ruled out when any target's implausibility
  `I = |model - observed| / sqrt(sd_obs² + sd_discrepancy²)` exceeds 3. The
  discrepancy term covers migration in the cases, census definitions and the
  stylised settings.
* A second wave samples the box around the first wave's survivors. 295 of
  4,000 draws are not ruled out.

**Adopted values.** For each constrained parameter, the median of the
not-ruled-out set; this vector is itself not ruled out (worst I = 2.2,
Welsh monolinguals). Unconstrained parameters keep their values. Each class
propensity moves every group of its class by the same factor.

| Parameter | Before | Not ruled out (5-95 %) | Adopted |
|---|---|---|---|
| Parameter | First calibration | Not ruled out (5-95 %) | Adopted |
|---|---|---|---|
| sigma0, same-faith vernacular (`RC:be`) | 0.44 | 0.19-0.71 | 0.38 (class x0.86) |
| sigma0, same-faith national (`RC:lt`) | 0.37 | 0.22-0.49 | 0.37 |
| sigma0, different-faith national (`GC:uk`) | 0.06 | 0.005-0.084 | 0.036 (class x0.6) |
| sigma_diaspora | 0.53 | 0.24-0.77 | 0.54 |
| h0 (adult re-identification) | 0.0021 | 0.0004-0.008 | 0.0025 |
| acq_school | 0.36 | 0.28-0.40 | 0.36 |
| acq_adult | 0.012 | 0.011-0.029 | 0.022 |
| exogamy (new) | - | 0.06-0.37 | 0.20 |
| exogamy_homophily H (new) | - | 18-57 | 38 |
| a, m_mono, completeness_share | | not constrained | kept |

The first calibration (before the marriage term and the dispersed case) had
moved sigma0 of `RC:be` from 0.55 to 0.44 and of `RC:lt` from 0.12 to 0.37
and added sigma_diaspora. Its values leave the scattered Ukrainians at a
share ratio of 0.37 (I = 4.5). Without the marriage term, the decline can be
had only with shift propensities that miss the other cases: none of the 100
draws with exogamy below 0.02 is within I = 3 on every target. The adopted values give 0.098
(I = 0.2) and at most I = 2.2 elsewhere.

**What the history match does not do:**

* The cases constrain *classes* of minorities, not each group.
* Each case's setting is a judgement.
* The model's frequency effect is weaker than Masuria shows. There the share
  fell fastest where it was smallest (Oletzko), and the model reproduces this
  only in part (I = 2.1); German settlers and the Masurians' departure for
  the Ruhr are not in the stylised case.

The ensemble draws the calibrated parameters jointly from the
not-ruled-out set (`plsim/data/nroy_language.csv`). Rerun with
`python -m plsim calibrate [--write-nroy]`. Outputs go to
`outputs/calibration/`: all draws with their implausibilities, the
not-ruled-out set, the target and parameter tables, and a figure.

**Diaspora term (second-generation assimilation).** Where a group's local
own-language share is below `completeness_share` (0.25), its propensity
sigma0 is raised towards `sigma_diaspora` in proportion to
`1 - completeness`:

    sigma_eff = sigma0 + max(sigma_diaspora - sigma0, 0) x (1 - complete)

The same effective propensity scales adult re-identification. Scattered
speakers and migrants in cities therefore shift within two or three
generations whatever their nationality, as immigrants' children do. Earlier
versions let Ukrainian and Belarusian migrants keep their language in Warsaw
indefinitely. Haredi Yiddish, Romani, Karaim and Wymysorys are exempt; they
maintain their languages through endogamy and religion rather than local
numbers.

#### Other anchors (not fitted; checks on the baseline after calibration)

| Anchor | Evidence | Model (baseline) |
|---|---|---|
| Yiddish among acculturating Jews | Soviet Jews 70.4 % Yiddish (1926) -> ~41 % (1939) under coercion; interwar Polish-Jewish youth rapidly Polonising in state schools; Hungarian and Czech Jewry shifted in ~2 generations | 79 % (1935) -> 53 % (1960) -> 28 % (1990) -> 10 % (2030) |
| Wymysorys | 92 % of Wilamowice (1,525/1,662) spoke it in 1880, 72 % in 1890 | ~1,450 -> ~420 (1990) -> ~60 (2032): moribund even without the post-war ban |
| Catholic Belarusian vernacular | rapid Polonisation of Catholic Belarusian-speakers; the 1897 -> 1931 recording gap | 86 k (1935) -> 82 k (1960) -> 58 k (1990) -> 25 k (2030) in Wilno/Nowogródek/Białystok |
| Greek Catholic Ukrainian | strong institutions (church, Prosvita, cooperatives) | 96 % of Greek Catholics Ukrainian-speaking (1935) -> 88 % (1990) -> 79 % (2030) |
| Scottish Gaelic (Kandler et al.) | shift ~0.035/yr in an Anglophone state | Polesian and Kashubian rates of the same order once bilingual |
| Karaim | community 800-900; language maintained in Trakai in the 1930s | ~680 -> ~230 speakers (2032) |

### 6.5 Extinction diagnostics

Language counts are reported by age, so intergenerational transmission is
visible in the pyramids by language. A language with no speakers under 15 is
moribund in the sense of Fishman's GIDS and the UNESCO vitality scale. The
report tracks Kashubian, Lemko, West Polesian, Belarusian, Yiddish, Romani,
Karaim and Wymysorys with ensemble ranges.

### 6.6 Policy levers (scenarios)

Status schedules, own-language schooling shares, assimilation pressure and
each region's languages are all scenario inputs. Examples:

* Ukrainian autonomy makes Ukrainian the regional state language in
  Stanisławów, Tarnopol and Volhynia (`federal_autonomy`).
* Lithuania is part of a unitary Poland, with Polish dominant and the only
  official language there too (`unitary_union`).
* Polish and Belarusian are co-official across a smaller or larger Poland
  (`wakar_poland`, `wakar_poland_belarus`), or no language is privileged
  (`no_official_language`).
* Polish is co-official in every autonomy: in the Lithuanian member of the
  federation (all scenarios with the union), in the Ukrainian autonomy and
  in each canton of the Grand Duchy.

**Contact and official languages.** Each county has one *contact* language
(`dominant_language`) and a set of *official* languages
(`official_languages`, by default just the contact language).

* **Contact language.** This is the language the bilingual state b = 1
  refers to: the one a county's minorities learn at school, at work and in
  the army, and the default target of shift.
  `dominant_language: auto:lt,pl,be+pls` picks, per county, whichever listed
  language had the most speakers in 1931. "be+pls" counts West Polesian
  speakers with Belarusian.
* **Official languages.** Every official language gets:
  * at least the official status (`official_status`, 1.0, or a schedule);
  * schools in that language for its own speakers (`official_schooling`,
    0.9);
  * a place among the languages people may shift to.

  `official_languages: all` makes every language official, which is how
  `no_official_language` models a state that favours none.

Co-officiality therefore removes the status premium of one language and
protects each official community with its own schools. It does not remove
the pull of numbers: in the Abrams–Strogatz attraction, a bigger language
still draws speakers, now only through its local share.

### 6.7 National identity, separate from home language

Home language and national identity were never the same thing here.
Catholic Belarusian speakers mostly called themselves Poles. Many Orthodox
villagers of Polesie answered "tutejszy". Polish-speaking Jews remained Jews.
In Lithuania a large part of the Polish-speaking Catholics were entered, and
in time saw themselves, as Lithuanians. `plsim.identity` therefore tracks
identity counts `I[r, u, g, i]` for every region, rural/urban cell and
community-language group. The 14 identities are Polish, Ukrainian,
Belarusian, Lithuanian, Russian, German, Jewish, Czech, Latvian, Kashubian,
Lemko/Rusyn, "local", other and Silesian. They always add up to the population of the
cell and group; identity is not tracked by age.

* **Start (1931).** Each group has an identity mix (`identity.INITIAL`),
  with overrides for the Lithuanian member, Soviet Belarus and the west
  lands. The mixes of the Orthodox and of the Jews are **fitted to the 1921
  nationality census** (`data.census1921`, check `validate.identity_1921`):
  the 1931 population, read through the 1921 nationality question
  (`polish_1921`), against Poland's totals and the voivodeships confirmed in
  two sources. Fitted: Orthodox Ukrainian speakers 90 % Ukrainian, 6 %
  "local"; West Polesians 50 % "local", 33 % Belarusian, 10 % Ukrainian, 7 %
  Polish; Orthodox Belarusian speakers 65 % Belarusian, 26 % "local";
  Yiddish speakers 78 % Jewish by nationality; and the 1921 enumerators
  entered "locals" as Belarusian 50 %, Ruthenian 20 %, Polish 15 %,
  "tutejszy" 15 %. Result against the census (model / 1921): Poland (1921
  territory) Polish 67.6 / 69.2 %, Ukrainian and Ruthenian 15.9 / 15.2,
  Jewish 8.2 / 8.0, Belarusian 4.4 / 4.0; Polesie Belarusian 41.3 / 42.6,
  Ruthenian 20.2 / 17.7, Polish 22.7 / 24.3, "tutejszy" 5.0 / 4.4, Jewish
  8.7 / 10.5; Volhynia Ukrainian 62.4 / 68.4, Polish 19.8 / 16.6;
  Stanisławów 65.2 / 70.2 and 23.0 / 21.8; Tarnopol Polish 44.6 / 49.3,
  Ukrainian 47.1 / 45.5. The squared error over the targets fell from 1,089
  to 115 (the earlier mixes had Polesie 34 % Polish and 18 % Belarusian).
  Caveats: 1921 left out the Wilno region and Upper Silesia, ten years of
  settlement and emigration lie between the two censuses, and the
  voivodeship figures are only five; a county table can be dropped in
  (`plsim/data/census1921_powiaty.csv`) and is then checked county by
  county. For Lithuania, 42 % of Polish speakers have a Polish identity.
  Read through the 1923 question, that gives 70 thousand Poles (2.9 %),
  against the census's 65.6 thousand (3.2 % without Klaipėda) and some 150
  thousand Polish speakers. For the BSSR, nearly all Belarusian speakers
  have a Belarusian identity (the indigenisation of the 1920s). A Silesian
  identity (2002: 173 thousand) is held by part of the Upper Silesians and
  of the Poles of Cieszyn Silesia in the west lands (§12.9).
* **Births and language switches.** A child raised in its mother's language
  takes her identity. A child (or adult) who switches language takes the
  identity that goes with the new language with probability `follow` (0.6),
  and otherwise keeps the old one. "The identity that goes with" a language
  depends on faith: Polish for a Catholic speaking Belarusian or Polish,
  Belarusian for an Orthodox Belarusian speaker, Jewish for a Jew of any
  language.
* **Nation-building.** "Local" identities turn national (the identity that
  goes with the person's language and faith) at `0.02 x M` per year, where M
  is the modernisation index of the cell (schools, press, army, elections;
  Weber 1976, Hroch 1985).
* **Pull of the state nation.** Any other identity moves to the identity of
  the region's contact language at
  `0.05 x pressure x M x compat(community)` per year. The rate is cut by
  85 % when the identity is the one that goes with the person's own home
  language, but in full only where that language has a status of at least
  0.35 or own-language schooling of at least 0.3 (`anchor_status`,
  `anchor_schooling`), and in proportion below. A stigmatised, unschooled
  language anchors its speakers' identity less: in the baseline Ukrainian
  and Lithuanian (status 0.35) anchor in full, Belarusian (0.15) at 43 %,
  Kashubian (0.10) at 29 %; in People's Poland Ukrainian (0.08-0.12)
  anchored a quarter to a third, German after 1945 (0.05) a seventh. The
  "local" identity is left to nation-building. Compatibility: Catholics 1, Jews 0.6, Protestants and others
  0.5, Orthodox 0.3, Greek Catholics 0.25, Haredim 0. `pressure` is the
  language policy of the scenario. **Lithuanisation** in the Lithuanian
  member can now run through identity as well as language. How fast depends
  on the pressure and on whether Polish keeps official status. In the
  baseline federation, with Polish co-official, Polish identity in Lithuania
  falls about as fast as Polish speech (78 -> 66 thousand, against 150 ->
  119 thousand speakers, 1932-2032).
* **Migration and transfers.** Leavers take their cell's identity mix.
  Arrivals take the mix of their group's leavers, first from the same region
  (rural-urban moves), then from the whole state.

Outputs: identity by region and year, identity by home language at the
snapshot years, the nationality censuses, an identity map in the report and
the atlas's "Identity" layer (by county). The starting mixes are tied to
data (1921, 1923, 1926).

**Calibration of the pull on the 2002 census.** The rate of the pull is
fitted on the historical scenario (§12.10), against the national identities
of the 2002 census, and used in every scenario. Now that the model gets the
2002 home languages about right (Ukrainian 39 thousand speakers against the
census's 23, Belarusian 51 against 40, Lemko 7 against 6, Lithuanian 6.5
against 6; §6.3, §12.10), the identity mechanism can be tested on its own:

| `assimilation` | Lithuanian | Kashubian | Belarusian | Ukrainian | Lemko | German | Silesian |
|---|---|---|---|---|---|---|---|
| census 2002 | 6 | 5 | 49 | 31 | 6 | 153 | 173 |
| 0.035 | 7.0 | 8.4 | 75 | 120 | 18 | 118 | 154 |
| **0.05** | 5.8 | 4.1 | 64 | 101 | 15 | 97 | 133 |
| 0.08 | 4.4 | 1.0 | 49 | 73 | 11 | 71 | 105 |

(thousands, 2002). 0.05 fits the Lithuanians and Kashubians and is kept; a
faster pull would fit the Belarusians but erase the Kashubians, and no
single rate fits the Ukrainians and Lemkos, who keep their identity after
losing the language more than the census shows (identity three times the
home language, against 1.35 in the census). Part of that is the census:
the 2011 census, which allowed two identities, counted 51 thousand
Ukrainians and 11 thousand Lemkos (model 88 and 13). Part is the model:
religion is inherited from the mother, so the descendants of mixed
marriages stay Greek Catholic or Orthodox and their identity is pulled at a
quarter of the Catholic rate. Counting half the mixed households in the
partner's community (`exogamy_rite` 0.5, the Galician rule that sons follow
the father's rite and daughters the mother's) took Ukrainian identity from
119 to 101 thousand; counting all of them would give 83.

## 7. Transport networks

### 7.1 Representation

About 190 nodes: 170 towns in the union with 1931 populations and
coordinates, plus foreign gateways (Danzig, Berlin, Breslau, Upper Silesia,
Königsberg, Riga, Mińsk, Kyiv, Chernivtsi, Žilina, Ostrava, Mukachevo, Tilsit,
Liepāja).

With Soviet Belarus in the state (`include_belarus`), 23 Belarusian towns,
five gateways beyond it (Smolensk, Nevel, Unecha, Bakhmach, Ovruch) and its
c. 1931 main lines are added, and Mińsk becomes a domestic town. Otherwise
these towns do not exist in the model at all: they take no part in the road
triangulation, the gravity flows or the random draws, so the other scenarios
are unchanged (checked bit for bit against a run made before Soviet
Belarus was added).

* **Rail**: the c. 1931 trunk and secondary network (~15 k route-km of the
  ~20 k km operated by PKP in 1938; local branches and sidings omitted).
  Classes: narrow gauge, secondary, main, electrified main, high speed.
* **Roads**: a Delaunay proximity graph between towns, pruned at 130 km, with
  classes dirt, gravel/macadam, paved, expressway, motorway. Main state
  chaussées start paved.
* **Borders**: foreign-to-foreign links are dropped. Outside the federation,
  links across the Polish-Lithuanian demarcation line stay cut (the real
  1920-38 situation).

### 7.2 Speeds and travel times

Commercial speeds are set by class and era. Examples: secondary lines
36 -> 85 km/h over 1931-2020; electrified mains 58 -> 150 km/h; high speed
180 -> 280 km/h. Road speed mixes motor and horse/foot travel:

* The motor share of road trips is `min(1, bus(t) + vehicles/250)`, with bus
  coverage rising from 25 % in 1931 to 80 % in 1980.
* Effective speed is the harmonic mean of the two.
* All-pairs travel times come from Dijkstra over the multimodal graph each
  year.

### 7.3 Demand, appraisal and investment

* **Demand**: gravity flows `T_ij = tau m_i m_j exp(-0.3 t_ij)` (masses =
  population x sqrt(relative income); foreign gateways x0.12, the McCallum
  1995 border effect). `tau` is normalised to trips per head rising from 4
  (1931) to 35 (2032).
* **Candidate projects** are:
  * gauge conversion;
  * double-tracking;
  * electrification (from 1946, apart from the dated Warsaw schemes);
  * high-speed upgrades (from 1975, between large towns);
  * new secondary lines on Delaunay links with no rail;
  * road surfacing;
  * expressways (from 1950) and motorways (from 1955).
* **Unit costs** are in 1990 GK$ per km, times a terrain factor (marsh 1.45,
  hills 1.3, mountains 2.2). Examples: new line 0.85 M, electrification
  0.5 M, high speed 14 M, surfacing 0.06-0.2 M, expressway 1.6 M, motorway
  +2.4 M.
* **Benefits**:
  * *network benefit*: rule-of-half consumer surplus of time savings over
    all pairs, with induced demand and a freight uplift of +80 %. It is
    computed with the exact single-edge update
    `d'_ij = min(d_ij, d_iu + w' + d_vj, d_iv + w' + d_uj)` (tested against
    full recomputation);
  * *local road benefit*: farm-to-market trips of each town's rural
    hinterland (20 -> 100 trips/head/yr). All-weather surfacing was the main
    gain of the 1930s Road Fund and of post-war programmes. An expressway or
    motorway is a new carriageway beside the old road, which keeps most local
    traffic. It earns only a share of this benefit (`local_share_limited`:
    0.65 for expressways, 0.3 for motorways).
  * Benefits are valued at 35 % of income per hour, discounted at 5 % over
    40 years, and optionally **equity-weighted** towards poor regions (full
    weight 1940-54, the Fifteen-Year Plan's goal of erasing Poland "A" and
    "B").
* **Budgets**: 0.4 % of GDP in the early 1930s, 0.8-1.2 % after 1939. Rail
  and roads have separate accounts (as with PKP vs. the 1931 Road Fund), with
  the rail share falling from 55 % to 35-40 %. Accounts may accumulate up to
  six years' allocation for large works. Greedy selection by BCR >= 1.
* **Running costs.** Expressways and motorways also carry operation and
  maintenance costs, including periodic renewal: 1.5 % and 2 % of the
  capital cost per year, counted in present value over the 40-year life.
  This raises their cost by 26 % and 34 %.
* **Calibration of the road programme.** Earlier versions counted the full
  local benefit and no running costs. Nearly every candidate then passed
  (median BCR of the expressways built: 1.04), and the baseline had about
  22,500 km of expressway and motorway by 2032. That is about 51 km per
  1000 km², more than Germany's Autobahn network. The comparators are:
  * Czechia and Hungary about 18-21 km per 1000 km²; Poland's own 2033 plan
    about 26;
  * Spain, France and Portugal about 35; Germany about 37 (motorways only).
  Runs with local shares of 0.3/0.1, 0.5/0.2, 0.8/0.4 and 1.0/0.6 gave 8.5,
  14, 29 and 37 km per 1000 km². The adopted 0.65/0.3 aimed at about 24. In
  the recalibrated baseline (with the fertility of §4.2) it gives 19.7 km
  per 1000 km² (ensemble median 8,700 km, about 12-29 km per 1000 km² across
  the ensemble), at the level of Czechia and Hungary and in the lower half
  of the band. A plausibility
  check (15-35) guards it (§10.2).
* **Dated projects**:
  * *historical*: Coal Trunk Line completion (1933), Warszawa-Radom (1934),
    Telšiai-Kretinga (1932), Warsaw electrification (1936-37);
  * *planned in 1939*: Łapy-Ostrołęka-Przasnysz-Mława (the Wilno-Gdynia
    shortcut), Dębica-Pilzno-Jasło, the COP Łódź-Dębica trunk,
    Nestorowicz's 1939 plan for ~5,000 km of category I/II roads;
  * *federation-only*: Vilnius-Kaunas reopened, Suwałki-Marijampolė.
* **Rationalisation**: once motor vehicles exceed 180 per 1000, narrow-gauge
  and secondary lines between small towns that have a paved parallel road
  close with a small annual hazard (Beeching-type cuts).

This cost-benefit growth rule belongs to the family of Yerra & Levinson
(2005), Xie & Levinson (2009, 2011) and Louf, Jensen & Barthelemy (2013).
Those models generate realistic trunk/branch hierarchies from local
investment rules (see Barthélemy 2011 for a review). Evaluation by social
savings and market access follows Fogel (1964) and Donaldson & Hornbeck
(2016).

### 7.4 Feedbacks

* **Market access** `MA_i = Σ_j m_j exp(-0.25 t_ij)` (Harris 1954) raises
  regional income growth (elasticity 0.12) and town growth (Gibrat growth
  plus an MA premium, plus exogenous growth poles: Gdynia 1926-39, the COP
  town at Rozwadów/Stalowa Wola from 1937).
* Region-to-region **travel times drive migration**.
* **Accessibility raises language-shift pressure.**

## 8. Economic drivers

* National income per head (1990 GK$) converges to a fraction `kappa` of the
  western-European frontier at the "2 % iron law" speed (Barro 1991; Barro &
  Sala-i-Martin 1992), with normal shocks and occasional crises (mean
  corrected).
* 1932-38 growth is imposed from the historical record: Depression trough,
  then recovery.
* The frontier grows 2.5 % (1930s recovery), 1.8 % (1939-49), 2.7 %
  (1950-73), 1.9 % (1974-2007) and 0.9 % thereafter.
* `kappa` is the main growth lever: ~0.6-0.7 in the baseline (southern
  Europe). The ensembles sample the speed of convergence and the shocks,
  not `kappa` itself; set it in a scenario for a faster (Finnish, ~0.85)
  or slower (Argentine, ~0.45) path.
* Regional relative incomes start from the Poland A/B gradient (Silesia 1.9x,
  Warsaw 2.2x, Polesie 0.48x the average). They converge slowly (1.5 %/yr) to
  partially persistent targets and respond to:
  * market access;
  * programmes: the Central Industrial District (COP, launched 1936/37, 2.4 bn
    zł committed, 60 % of 1937-39 state investment), Gdynia/Pomerania;
  * the 1940-54 equalisation aim of Kwiatkowski's Fifteen-Year Plan.
* Literacy and school enrolment close their gaps at fixed hazards.
* Motorisation follows the Dargay-Gately Gompertz curve with partial
  adjustment, calibrated to 44,200 motor vehicles on 1 Jan 1938 (~1.3 per
  1000) and to southern-European ownership at 15,000 GK$.
* **Separate states** (`separate_states`; the Northwestern Krai or Lit-Bel
  beside Poland). Each state has its own national income, starting from its
  regions' share of the 1931 income (the krai at about 64 % of Poland's per
  head) and converging at the same speed to the same `kappa` (by default),
  with the same shocks. Relative incomes are normalised within each state.
  Each state has its own migration hump (emigration and immigration follow
  its own income) and its own infrastructure budget, spent on links within
  its territory or to a foreign gateway; no link across the border between
  them is built. Earlier versions gave the two states one income and one
  budget, so that Poland's results depended on which krai it was tied to.

## 9. How the parts are coupled

```
             income (convergence)  ───────────────┐
                 │        │                        │
      urbanisation target  motorisation, budget     │
                 │        │                        ▼
 fertility <─ modernisation ─> language shift  <─ market access
 mortality <─ income gap               ▲             ▲
     │                                  │             │
     ▼                                  │      network growth (appraisal,
 cohort-component ── births ── transmission            budgets, dated plans)
     │                                               ▲
     └── migration (rural-urban, inter-regional via ─┘ travel times,
                    international via the hump)
```

## 10. Calibration and validation

### 10.1 Back-validation 1932-1939 (baseline, seeded run)

| check | target (registered) | model |
|---|---|---|
| Poland population 1 Jan 1939 | 34.8-35.1 M (GUS: 35.1 M) | 34.6 M |
| CBR 1932 / 1938 | 28.8 / 24.3 | 29.7 / 25.3 |
| CDR 1932 / 1938 | 15.0 / 13.8 | 15.8 / 14.7 |
| e0 1931-32 m / f | 48.2 / 51.4 | 49.4 / 52.6 |
| motor vehicles per 1000, 1938 | 1.27 | 1.18 |
| urban share 1939 | ~30 % | ~29 % |
| Lithuania 1938: pop / CBR / CDR | 2.56 M / 22.6 / 12.6 | 2.58 M / 22.7 / 12.5 |

The modelled CDR sits ~1 point above the registered rate. Death (especially
infant death) registration in the eastern voivodeships was incomplete, so
this is the expected sign. Conversely, the official 35.1 M estimate for 1939
is probably slightly inflated.

### 10.2 Plausibility guard rails

These are not targets. They are bands from comparator countries: TFR 1960 in
2.3-3.8 and 2000 in 1.2-2.2; e0 1960 in 58-72 and 2000 in 70-81; urban share
2000 in 50-80 %; expressways and motorways in the last year 15-35 km per
1000 km² of the state (§7.3). They are checked automatically by
`python -m plsim validate`.

### 10.3 Census consistency

See §3.4. Passing the reconstructions through the 1931 observation model
reproduces the printed census to within 2-3 points in total.

### 10.4 The 1921 nationality census

`validate.identity_1921` reads the starting identity through the 1921
nationality question and checks it against the census (§6.7): Poland's
totals within 3 points, the grade-A voivodeships within 3-8 points, and a
county table when one is supplied.

### 10.5 The historical scenario

`historical` replays the real century with the shared behaviour and is
compared with the censuses of 1946-2021 (§12.10; results in SCENARIOS). It
calibrated the fertility transition (§4.2), the post-war mortality shift
(§4.1) and the pull of the state nation on national identity (§6.7). It
also shows the dispersed minorities of People's Poland (Ukrainians,
Lemkos, the Belarusians of Podlasie) keeping their home language several
times longer than they did (§6.7, §13).

## 11. Uncertainty

Monte-Carlo members (`plsim.ensemble`) re-draw the following, with separate
random streams for economy, demography and network so that scenario
comparisons use common random numbers:

* **Fertility**: TFR decline pace (d 0.45-0.8), end level D4 (1.6-1.95),
  Phase-III mean (1.45 ± 0.15), Haredi long-run TFR (2.2-4.0), baby-boom size
  (0-20 %).
* **Mortality**: post-1945 catch-up rate (0.08-0.16), minimum gap (1-3
  years).
* **Economy**: convergence speed (1.5-3 %), shock volatility.
* **Migration**: emigration propensity, position of the migration hump,
  immigration ceiling.
* **Language**: the history-matched parameters are drawn *jointly* from the
  not-ruled-out set of §6.4. These are the class propensities (scaling all
  groups of a class together), a, m_mono, h0, completeness_share,
  sigma_diaspora and the acquisition rates. Yiddish, Polesian and Orthodox
  Belarusian propensities and the Haredi exit keep independent ranges.
* **Network**: gravity decay, BCR threshold.

Reports give medians with 50 % and 90 % bands.

**Scenario ensembles.** Every scenario but `historical` also has a small
ensemble (`report`: 8 members when the baseline has 32; `ii_rp_only` 16).
Its members use the same parameter draws and seeds as the baseline's first
members (seed 7), so differences between scenarios are not sampling noise.
`outputs/scenario_ranges.csv` and the figure `scenario_ranges.png` give the
10th, 50th and 90th percentiles in 2032 of the population, the shares of
Polish (by home language and by identity), Ukrainian, Belarusian, Yiddish,
Lithuanian and German speakers, GDP per head, fertility and life
expectancy; the atlas shows them under each scenario's description.

**Probability maps.** With `cells=True` (as in `report`), each member is
also downscaled to the 3.5 km grid for 1982 and 2032. For every cell, the
share of members in which each language category is the most spoken home
language is computed (`maps.plurality_probability`). The outputs are
`outputs/ensemble_baseline_cells.npz`, the figure
`outputs/maps/map_uncertainty.png`, and the atlas's "Certainty" layer for the
baseline: the most likely leading language, paler where runs disagree. The
spatial downscaling itself (kernel widths, town seeding) is not varied, so
these maps show model-parameter uncertainty under one downscaling.

## 12. Maps: spatial downscaling and local language shift

The projection works with 271 counties (or 23 voivodeships) x rural/urban.
To draw maps, `plsim/spatial.py` places each region on a grid of 37,532
cells of 0.03125° x 0.05° (about 3.5 x 3.4 km) and carries the cells
forward year by year. The model itself uses a coarser grid of 9,383 cells
of 0.0625° x 0.1° (about 7 x 7 km) to split voivodeships into counties and
sub-regions (§12.5-12.6).
Every year the cells and towns of a region add up exactly to the main
model's figures (by region x rural/urban x language). The spatial layer adds
*where*, never *how many*.

### 12.1 Territory and regions

* **Territory.** A cell belongs to the state when its centre is on land
  (GSHHS coastline, lakes removed) and inside the borders of Poland or
  Lithuania on 1 January 1932. The borders are from CShapes 2.0 (Schvitz et
  al. 2022), with a median vertex spacing of 3.5 km. Land cells within
  2.5 km of the Polish or Lithuanian coast are also kept, because the
  GSHHS and CShapes coastlines differ by a few km on the Hel peninsula and
  the Curonian Spit. The map grid has 37,532 cells: 387,000 km² for Poland
  (official 388,600 km²) and 55,600 km² for Lithuania (official 55,750 km²).
  The 7 km model grid gives 386,800 and 55,800 km².
* **Before CShapes.** The territory used to be approximated by the
  nearest-town rule (domestic towns against about 110 foreign "mask" towns).
  That misplaced about 36,000 km² of Poland and 8,500 km² of Lithuania,
  mostly in bands up to 25 km deep along the Soviet and Latvian borders.
* **Regions.** Cells are assigned by a multiplicatively weighted Voronoi
  diagram of the domestic towns of their own state, with one weight per
  region calibrated so that cell areas match the official areas (all
  within 2.5 %). Warsaw city has 11 cells. State borders are therefore
  exact to the cell; voivodeship borders are approximations.
* **Governorates of 1897.** Where the 1931 borders followed those of the
  imperial governorates, the Voronoi may not cross them
  (`geography.GOV_ALLOWED`, polygons from the RISTAT GIS of 1897,
  `data/governorates.py`). The voivodeships of the Kingdom of Poland and
  Galicia, and Volhynia, take no land of the Vilna, Kovno, Grodno or Minsk
  governorates; Wilno, Nowogródek, Polesie and Białystok hold only their
  own governorates; Suvalkija is the Suwałki governorate. So the Bug, the
  Biebrza and the Niemen are where they were, not where the nearest town
  puts them. Inside the formerly Russian north-eastern voivodeships a place
  goes to a county whose seat lies in its own governorate (the powiaty of
  1931 mostly kept the uezd lines there). Lithuanian apskritys and Soviet
  okrugs, which did cross the old lines, are not constrained. The rule
  holds a place only where a town (or seat) of its own governorate lies
  within 30 km of its nearest one (`GOV_SLACK_KM`); and the area weights may
  not hand a place to a region whose nearest town is more than 60 km farther
  than the nearest it may join (`REACH_KM`). Without these limits, slivers
  where the 1897 and 1932 lines part went to the nearest region of their
  own governorate however far: two cells on the Courland bank of the Dvina
  by Druja fell to Biała Podlaska, 450 km away, and cells in northern
  Lithuania to Klaipėda.
* **The rest of the north-western governorates** (optional,
  `include_krai_east`; key `XK` of `borders_1932.json`, built by
  `tools/build_governorates.py`): the land of the Vilna, Kovno, Grodno,
  Minsk, Mogilev and Vitebsk governorates outside Poland, Lithuania and the
  BSSR of 1932, 31,600 km² in pieces of at least 150 km². Latgale (the
  Dvinsk, Rezhitsa and Lyutsin uezds and a strip of Drissa, now Latvia),
  the Nevel, Sebezh and Velizh uezds with a strip of Gorodok, and the
  eastern edge of the Mogilev governorate (both RSFSR) form three units
  (`data/krai_east.py`, §12.7); the uezds are their counties' borders. The
  grid reaches 57.5° N for northern Latgale, which also counts as land
  north of the base map's edge at 57.2° N.
* **Drawing.** Maps clip the cell colours to the CShapes polygons and draw
  the state border and the Polish-Lithuanian border as lines, so the
  border itself is not stair-stepped at the cell size.
* **Terrain.** Rural density is thinned in the Polesie marshes (-40 %), the
  Carpathians (-35 %) and the Hutsul highlands (-30 %), with smooth edges.

### 12.2 Initial state (spatial microsimulation)

The 1931 regional composition is downscaled by iterative proportional
fitting (IPF; Ballas et al. 2005; Lovelace & Dumont 2016):

1. **Rural population.** Each region's rural population goes to its cells
   in proportion to area x terrain x (town potential)^0.1.
2. **Seed of language shares.** County anchors (`data/geography.py`, 215
   county seats with 1931 minority shares) are interpolated with a Gaussian
   kernel (σ = 22 km) inside the region. 26 anchors are graded "A": the
   county figure comes from the 1931 tables as quoted in secondary sources
   (e.g. Sokal 55.0 % Ukrainian, Turka 70.3 %, Łuck 59.2 %, Krzemieniec
   80.7 %, Nieśwież 67.4 % Belarusian). The rest are "C" estimates from the
   known linguistic geography (Kashubian counties, German colonies, Lemko
   districts, Old Believers, Lauda), including zero anchors that mark
   counties without a given minority. Anchors only shape the pattern inside
   a region; regional totals always come from the census reconstruction. Languages without
   anchors get the regional share. The dominant language (Polish, or
   Lithuanian in the Lithuanian units) fills the remainder.
3. **Fit.** IPF fits the seed to cell totals and region x language totals.
4. **Towns.** Network towns start from the region's urban mix, multiplied
   by (0.05 + hinterland share)^0.8 and re-fitted, so a town in a
   Ukrainian district is more Ukrainian than the regional capital.
5. **Small towns.** Urban population not in network towns is spread over
   cells like the rural population.

### 12.3 Yearly update

For every region x stratum (rural cells; network towns plus small-town
population):

1. **Totals.**
   * Towns take the network model's populations.
   * Rural cells grow with their region, multiplied by
     `exp(β (ln Φ_i - mean ln Φ))`, where `Φ_i = Σ_n P_n e^{-d_in/25 km}` is
     the potential of nearby towns and β = 0.004 per year. Near growing
     towns this produces suburban rings; far from them it produces rural
     exodus. Over a century the gap between suburban and remote cells
     reaches about 3x.
2. **Language shift with a neighbourhood rule.** The main model records the
   region's net shift Δ_l, vertical plus horizontal; gainers have Δ_l > 0.
   Following Prochazka & Vogl (2017), the most important driver of shift is
   the number of speakers of each language in the village and its Gaussian
   neighbourhood. The neighbourhood share K_{i,l} is computed with a
   Gaussian kernel of σ = 10 km over all cells. Towns enter with their own,
   wider kernel, σ_n = 8 km x (P_n / 20 000)^0.3: hierarchical
   town-to-hinterland diffusion (Trudgill 1974).
   * **Losses.** A loser's losses are allocated in proportion to
     `n_{i,l} (κ0 + G_i^a)`, where `G_i = Σ_{gainers} K_{i,l'}`,
     a = 1.31 (Abrams & Strogatz 2003) and κ0 = 0.15. κ0 is the part of
     shift that does not need neighbours: school, church, army, state.
   * **Gains.** These are placed in proportion to `(κ0 + K_{i,l'})^a` and
     IPF-fitted to the regional gains.
   * **Consequences.** Language islands erode before the core. Contact
     zones retreat as fronts (Patriarca & Heinsalu 2009; Isern & Fort
     2014). The interface sharpens where one language is locally
     overwhelming, as in surface-tension models of dialect boundaries
     (Burridge 2017).
3. **Fit to the model.** The result is IPF-fitted to the new unit totals and
   to the region x language totals. Differences in fertility, mortality and
   migration between language groups therefore act evenly within the
   stratum, while shift is placed where contact happens.

The method is checked in `tests/test_spatial.py`:

* region totals are reproduced to better than 10⁻⁴;
* no cell goes negative;
* a speaker in a 90 % gainer neighbourhood is more than three times as
  likely to shift as one in a 10 % neighbourhood.

**Scale.** Prochazka & Vogl fitted, for southern Carinthia on a 1 km grid,
a front velocity of about 0.11 km per year (diffusion D = 0.136 km²/y,
growth k = 0.022/y). Over a century that is 11 km, about three of our
cells. On the 3.5 km grid, most visible change therefore comes from the regional
shift rates set by the main model (schools, cities, policy). The
neighbourhood rule decides *which* cells give way first.

### 12.4 Outputs

`python -m plsim maps` writes:

* `outputs/maps/`, the static maps:
  * plurality language, 1932-2032;
  * per-language shares;
  * share change;
  * density;
  * population change;
  * a scenario comparison;
* two GIF animations (`anim_languages.gif`, `anim_density.gif`);
* `outputs/atlas/`, an interactive atlas: every scenario, a time slider,
  language, single-language, density and growth layers, and a cell
  read-out. Frames are quantised to 8 bits every 5 years (gzip, about
  0.6 MB per scenario) and interpolated in the browser.

### 12.5 Sub-regions and federal members

The spatial layer also works in the other direction. It splits voivodeships
into counties (§12.6, the default) or, in the voivodeship model, into named
sub-regions for scenarios whose borders cut through them, such as the
Curzon line, a canton or an autonomy (`partition: [BIA, WIL, ...]`;
`plsim/partition.py`, `plsim/data/subregions.py`). At county level, a canton
or an autonomy is a `region_groups` list of counties instead.

1. **Downscale.** The 1931 reconstruction of the voivodeship is downscaled
   to the grid as in 12.2.
2. **Assign.** Each cell and town goes to the sub-region of its nearest
   county seat (a Voronoi approximation of the county borders).
3. **Sum.** Each sub-region takes the rural and urban speakers of every
   language on its cells and in its towns. Within a language, the split by
   community is the parent's. Fertility, mortality and literacy are
   inherited. Income is the parent's urban and rural income weighted by
   the sub-region's urban share (§12.6). Area is the parent's official area
   times the sub-region's share of the parent's cells.

The children add up exactly to the parent (tested).

**Pieces along the governorates of 1897** (`governorates`; scenarios
`nw_krai`, `lit_bel`). A scenario may name groups of governorates
(`governorates: {KRAI: [Vilna, Kovno, ...]}`). A unit that straddles the edge
of a group is cut along it (`partition._cut`):

* each part is the cells (and towns) of the unit in one group, or in none;
  a town takes the governorate of its unit's nearest cell (towns on a
  border river);
* a part with less than 5 % of the unit's people (or under 5,000) stays
  with the largest;
* the unit's people are shared between its pieces by the downscaled
  pattern, stratum by stratum and language by language, after the county
  fit, so the pieces add up to the county;
* each piece is coded by the governorate letters it covers
  (`BY_MOH.bobrujsk~VKGMS`, `LT_KAU.~S`), so that the map grid rebuilds the
  pieces from the codes alone (`geography.build_grid`).

With the governorate constraints of §12.1, one Polish county straddles:
Kamień Koszyrski, a county of 1930 put together partly from older Polesie
counties, reaches into the krai's governorates (11 k people go to the
krai). The other pieces are Lithuanian
apskritys (Alytus and Kaunas across the Niemen) and Soviet okrugs (Bobrujsk,
Rzeczyca, Homel and Połock across the Minsk-Mogilev-Vitebsk lines). Then `params.resolve_governorates` turns a group into its units: a
setting keyed by the group applies to each (a key for the unit, its county
or its voivodeship still wins), and units in no group are left out unless
their 1932 state is listed in `governorates_keep_outside` (Poland by
default), which drops Klaipėda, Palanga and the BSSR's slivers of other
governorates.

Region-keyed settings resolve by specificity: an exact code (`WIL.E`) beats
the county a piece was cut from (`BIA.bialystok` for `BIA.bialystok~x`),
which beats the parent code (`WIL`), which beats a wildcard (`LT_*`), which
beats `default` (`params.region_lookup`).

Two settings describe the political map:

* `dominant_language`: the contact language of each region, also its
  first official language; `official_languages` adds co-official ones
  (§6.6).
* `members`: the federal member each region belongs to. Migration between
  members is damped by `member_friction` (per pair) or by the
  Poland-Lithuania factor.

The census origin of a region (Polish 1931 or Lithuanian 1923 tables) is a
separate attribute. A Grand Duchy that includes Wilno still starts Wilno
from the Polish census.

In regions where Ukrainian or Belarusian is the official language, the
starting competence in it comes from a separate table (`BILINGUAL_0_EAST`).
Close vernaculars (West Polesian, Rusyn) start mostly competent, and so do
rural Poles of the Kresy, who usually spoke the local East Slavic speech.
Townspeople start less competent.

### 12.6 County-level projection

By default (`partition: counties`) every voivodeship runs as its 1931
powiaty, and the Lithuanian units as their apskritys. Warsaw city and Kaunas city stay whole,
which gives 271 regions in place of 23. The county table is
`plsim/data/counties.py` (sources and grades in `docs/DATA_SOURCES.md`).
It has 269 counties: 247 Polish powiaty (241 census units, since six
powiaty abolished in 1932 are printed with their successors) and 22
Lithuanian apskritys.

**County land.** Cells and towns go to the county whose seat is nearest
after a per-county weight: the distance less the weight (an additively
weighted Voronoi diagram), with the weights fitted on the model grid so
that each county's land matches its area in the 1931 census
(`county_areas_1931.csv`; the Lithuanian apskritys their area in the 1923
census, all within 1 %; `tools/build_county_weights.py`; every county
within 4 %, except Świętochłowice, about three grid cells, at 14 %; in
Nowogródek and Wilno the 1897 governorate rule below costs more: Słonim
+51 %, Brasław −22 %). With additive weights every county holds its seat and
is star-shaped around it: were seat i in county j (w_j − w_i > d_ij), every
place would be nearer j and i would have no land. The first version used a
power diagram (squared distance less the weight), which meets the areas as
well but put some seats in their neighbours (Katowice in Tarnowskie Góry,
Mińsk Mazowiecki 28 km from its own land, Lublin's town in Lubartów), and
made the governorate rule ineffective (it compared km² with a slack in km).
Before both, every place went to the nearest seat, and counties with close
seats were far off (Węgrów won no land at all). In the formerly Russian
north-east a place goes to a county of its own 1897 governorate where one
lies within 30 km of its nearest seat (the 1931 powiaty mostly kept the
uezd borders; Baranowicze, carved from two uezds, is the main exception,
hence Słonim's surplus). Where a voivodeship of the approximate map has a
detached piece (Tarnobrzeg's corner of Lwów, Działdowo's of Pomorze), the
county there is in two pieces.

**Counties on the maps.** Straight-line distances cut by a voivodeship's
edge and by the governorate rule leave many counties of the model in
several pieces (56 of 271: Brasław in four, Grójec, Opoczno and Nowogródek
with a third of their land apart), and the canton and member borders drawn
along them came out as rings and fingers. The maps therefore measure the
distance from each seat along the ground, over the cells of the voivodeship
(8 neighbours), with their own weights fitted to the same census areas
(`map_weights`, `tools/build_county_weights.py --map`,
`subregions.assign_connected`). A place on the shortest path from a seat to
a place of its county is nearer that seat still, so every county is in one
piece, except where the voivodeship itself is (Tarnobrzeg, whose seat lies
in Lwów's detached corner, has 516 km² of its 935; Kaišiadorys, whose seat
lies outside the land of its parent unit, 89). Most counties are within 1 %
of their census areas; Silesia's small town counties, Częstochowa,
Włoszczowa, Maków, Działdowo and Brody are 15-30 % off. The governorate rule
is left out here (the krai's pieces are still cut along the governorates).
The model keeps the plain rule and its weights, so the maps change only
where cells are drawn.

**Initial state.** Every Polish county is at grade A: its population and
mother tongue from the census volumes (tabl. 12 of the voivodeship volumes,
or the powiat pages of the short results), and its towns, countryside and
religions from the powiat pages (`census1931_strata.csv`). The Lithuanian
apskritys of the Kaunas state are at grade A from the 1923 census
(`census1923_apskritys.csv`): population, nationality (determined by
language; Jews counted as Yiddish speakers), religion and towns. Their
populations are of 1923 and are scaled to their unit's 1931 total; with no
town/village split printed, their religions are fitted over the whole
county, and their towns come from the downscaled pattern (Trakai apskritis,
with no town in 1923, has none). The three Kreise of the Klaipėda Territory,
not enumerated in 1923, stay at grade C.

1. **Seed.** The 1931 county count by mother tongue. Merged categories are
   split by the downscaled pattern: Belarusian + tutejszy + Russian where a
   table merges them, "other", and the unenumerated Kashubian, Lemko and
   Wymysorys speakers inside "Polish" and "Ukrainian". The census "other"
   holds only the languages the census could name elsewhere (Czech,
   Latvian, Karaim ...).
2. **Fit to the voivodeship.** IPF over (county × language), fitting the
   county populations and the voivodeship's latent language totals for the
   chosen census variant.
3. **Towns.** IPF over (county × stratum × language): each language's urban
   share in the county is the census's (from the powiat page; Kashubian and
   the other carved-out languages keep the downscaled split), and the
   voivodeship is matched by stratum. The voivodeship's split is itself
   fitted to the same pages (§3.6), so the two agree: the county urban
   shares are the census's to 0.3 points on average.
4. **Communities.** Each language's split into communities starts as the
   voivodeship's; IPF then fits, in turn, the county's census religions by
   stratum (the shares among the religions its pages print; "other
   Christian" counts as Orthodox in the north-east, where it is mostly Old
   Believers, as Protestant in Volhynia and Polesie, and as Catholic
   elsewhere), the voivodeship's totals by stratum and group, and the
   county's languages; a last run of the two latter makes both exact. The
   county religions are then the census's to 0.3 points on average (95 %
   within 1.1 points); the largest misses are towns where the census
   religion and language cannot both hold within the voivodeship's groups
   (Dubno: Orthodox Russian speakers).

The census variant therefore keeps its voivodeship totals, and the county
table decides where the speakers live, how urban they are and which church
they belong to. Under the religion-corrected variant, a county with many
Greek Catholics declaring Polish keeps more Ukrainian speakers than its
printed figure.

Seats come from the table (`lat`/`lon`). Fertility, mortality and literacy
parameters are inherited from the voivodeship.

**Income.** A county's income index uses the voivodeship's urban and rural
incomes per head, weighted by the county's own urban share:
`y_c = y_v (U_c r + 1 - U_c) / (U_v r + 1 - U_v)`, with r the urban/rural
income ratio of 1931 (2.2). A city county is therefore richer than the
rural counties around it, and the counties average to the voivodeship.
Without this, a city county would get the voivodeship's mean income. Its
urban incomes would then be too low and its rural neighbours' too high,
and mortality, fertility and migration push would all be wrong.

**What changes in the yearly loop.**

* **Language.** Shift runs on each county's own mix. A Ukrainian minority
  concentrated in a few counties is a local majority there.
* **Concentration.** The voivodeship model already allows for clustering.
  A minority's speakers experience a local share of their own language
  k_L times the regional share (§6.2, *Enclaves*: Lithuanian 4,
  Kashubian 2.5, Lemko 20, Ukrainian 1.25 ...). Counties resolve part of
  that clustering, so applying the full k_L again would count it twice.
  * **Rescaling.** For each split voivodeship, k_L is divided by the
    speakers' clustering across its counties in 1931: the mean county share
    of L that L speakers live in, over the voivodeship share (an isolation
    index ratio).
  * **Examples.** Lithuanians in wileńskie cluster 4.0× (k falls from 4 to
    1), Lemkos in lwowskie 5.9× (20 → 3.4), Kashubians in Pomorze 2.5×
    (2.5 → 1), Belarusians in wileńskie 1.9× (1.4 → 1), Ukrainians in
    lwowskie 1.6× (1.25 → 1).
  * **Floor.** k never falls below 1.
  * **Measured inside a county** (`concentration_regions`). Where the
    rescaling understates a minority's village clustering, a measured value
    replaces it: the Lithuanians of Suwałki county live in Puńsk (75 %
    Lithuanian in 2002) and the villages round Sejny, a local share of
    about 0.55 against 4.5 % of the county, so k = 10 there (the rescaling
    gave 1, and the model then married them out as if scattered).
  * **Dispersal.** A transfer marked `disperse: true` (Operation Vistula,
    which settled the deportees a few families to a village, at most 10 %
    of one) sets k = 1 for the moved groups where they were placed and
    where they were taken from. Without it the Lemkos kept their
    Carpathian clustering (20) in Masuria and Pomerania.
* **Travel times.** Regions without a modelled town reach the network
  through the nearest town, at a speed that rises from 22 km/h (1931) to
  70 km/h (2030), with a detour factor of 1.3
  (`Network.region_access_hours`).
* **Market access.** A county without a town gets the access of its nearest
  town, discounted by that travel time.
* **Migration** is nested (see `plsim/migration.py`), because its
  parameters were calibrated on voivodeships. A *unit* is the part of a
  1931 voivodeship that lies inside one federal member.
  * Urbanisation runs per unit. The unit's rural migrants are routed to the
    towns of all its counties, by urban mass and travel time. Without this,
    every rural county would grow its own small towns, and the large cities
    would stop growing.
  * In inter-regional migration, a unit draws migrants with the
    voivodeship's mass. Its counties share that pull by their own
    attractiveness, and moves inside a unit are not counted as
    inter-regional.
  * Settlement weights given for a voivodeship are shared among its
    counties by rural population; a weight given for a county is its own.

  Splitting a voivodeship therefore moves migrants between its counties
  without changing how many it sends or draws (tested: a split run stays
  within 0.4 % of the unsplit one by 1945; without nesting it is up to
  1.5 % off). The nesting also applies to named splits that stay inside one
  member, e.g. both halves of lwowskie in the Ukrainian autonomy.
  Units follow border changes: when the 1945 border cut lwowskie and
  białostockie, each part became a unit of its own state. (Until this was
  fixed the units were those of 1931, and the rural people of Soviet
  Galicia "urbanised" into Przemyśl, Rzeszów and Jarosław: Ukrainian
  speakers there grew from 24 to 106 thousand between 1948 and 1970, in a
  land the transfers had emptied.)

* **Random numbers.** Regional noise (life expectancy, phase-III
  fertility) is drawn per 1931 voivodeship and shared by its counties. A
  county run therefore sees the same shocks as the voivodeship run with the
  same seed.

**Results (baseline, seeded run, 2032).**

* **Consistency.** The county run is a consistent breakdown of the
  voivodeship model:

  | | Voivodeship run | County run |
  |---|---|---|
  | Population | 44.37 M | 44.26 M |
  | Urban share | 66.5 % | 66.6 % |
  | Ukrainian speakers | 6.82 M | 6.85 M |
  | Belarusian speakers | 1.32 M | 1.29 M |
  | Lithuanian speakers | 1.89 M | 1.88 M |
  | West Polesian speakers | 0.76 M | 0.73 M |

  Every voivodeship's 2032 language shares are within about a point of the
  voivodeship run (Klaipėda's German 1.6 points).
* **Populations.** Most voivodeship totals are within ±5 %. Two differ
  more. Pomorze is 10 % smaller, because migrants' travel times are now
  measured to each county (Gdynia included) rather than to Toruń, and the
  Kashubian counties draw fewer Polish speakers. Klaipėda is 12 % larger.
* **What the county level adds is *where*.** The plurality language
  changes in 34 of 271 counties:
  * twelve Belarusian counties turn Polish-plurality: Grodno, Wołkowysk
    and Bielsk; Głębokie, Mołodeczno, Postawy and Wilejka; and Nowogródek
    voivodeship apart from Lida, Szczuczyn and Wołożyn;
  * all nine Polesie counties move from West Polesian to Polish;
  * Kartuzy, Kościerzyna and Wejherowo lose their Kashubian plurality;
  * seven Lwów counties, Kamionka Strumiłowa and Tomaszów Lubelski turn
    from Ukrainian to Polish plurality;
  * Klaipėda turns from German to Lithuanian.

  Volhynia and the core of Stanisławów stay Ukrainian (Łuck 59 % in 1933, 58 % in 2032).
  The cities draw the rural surplus of their voivodeship: Lwów county
  grows from 460 k to 949 k, Wilno from 415 k to 872 k, and Brześć from
  227 k to 636 k.
* **Cost.** A run takes about 3 minutes, against 20 s for the voivodeship
  model.

A first county run, before any of this nesting, gave 48.6 M people. In
it, Warsaw grew only 1.06× instead of 2.4×, because every rural county
grew its own towns. Ukrainian came out 200 k higher. Different random
numbers and double-counted clustering both contributed: the concentration
rescaling alone removes about 30 k Belarusian speakers.

### 12.7 Soviet Belarus (optional)

`include_belarus: true` adds the Byelorussian SSR in its borders of December
1926 to the Polish state (scenario `wakar_poland_belarus`).

* **Territory.** Modern Belarus (Natural Earth 1:10m) minus Poland and
  Lithuania of 1932 (CShapes 2.0): 125,900 km² against the 126,800 km² of
  the 1926 census. Belarus's borders with Russia, Ukraine and Latvia are
  those the BSSR had from 1926 (`tools/build_geodata.py`).
* **Units.** Four voivodeships close to the oblasts of 1938: witebskie,
  mińskie, mohylewskie and homelskie. Their counties are the 12 okrugs of
  the 1926 census (grade A, with their own populations and languages).
* **Population.** The 1926 Soviet census by okrug and nationality, grown
  to the end of 1931 by 7.5 % (`data/bssr.py`): 5.36 M people, 15.6 %
  urban.
* **From nationality to home language.**
  * Belarusians speak Belarusian (91 %; in 1926, 94 % of rural and 54 % of
    urban Belarusians named it their native language), the rest Russian.
  * Jews speak Yiddish (90.7 %, as in 1926) or Russian.
  * Poles: 40 % Polish, 55 % Belarusian, 5 % Russian. In 1926 only a third
    to a half named Polish.
  * In the Homel and Rzeczyca okrugs, two thirds of the recorded Russians
    (37 % and 26 % of the population, recorded a week after the transfer
    from the RSFSR) are taken as Belarusian speakers, a correction of the
    same kind as Tomaszewski's.
  * The result: 77 % Belarusian, 13 % Russian, 7.6 % Yiddish, 0.8 % Polish
    at home.
* **Other inputs** (incomes, vital rates, literacy, urban shares) are set
  like those of the neighbouring Polish north-east, as befits a premise in
  which these lands were Polish from 1921.

**The rest of the north-western governorates** (`include_krai_east`, only in
`nw_krai`; `data/krai_east.py`). Three units, grade E (estimates built on
the 1897 census):

* **Latgale** (`LV_LAT`): counties Dyneburg (Dvinsk uezd and the Drissa
  strip), Rzeżyca (Rezhitsa) and Lucyn (Lyutsin). 1897: 249,000, 136,445 and
  128,155 people. Carried to 1931 x 1.02, which with the Pytalovo strip of
  the Pskov governorate reaches the 567,000 people of Latgale in the 1935
  Latvian census. Home languages: the 1897 shares (Dvinsk 39 % Latvian, 15
  Russian, 14 Belarusian, 9 Polish; Rezhitsa 58 % Latvian, 24 Russian;
  Lyutsin 64 % Latvian, 21 Belarusian), with Yiddish cut to the Jewish
  numbers of the 1930s (about 27,000 in 1935) and the rest scaled up.
  Latvian speakers are Catholic Latgalians (92 %); Russians Orthodox and
  Old Believers.
* **Nevel, Sebezh and Velizh** (`RU_VIT`): 1897 110,394 (with a strip of
  Gorodok, 124,000), 92,055 and 91,000 (the part of Velizh outside the BSSR);
  x 1.22 to 1931. 1897 speech: Nevel 84 % Belarusian, Sebezh 47 % Belarusian
  and 47 % Russian, Velizh 86 % Belarusian. The Soviet censuses recorded
  most of these Belarusian speakers as Russians by nationality; the speech
  of 1897 is kept, as in §12.7 for Homel.
* **The eastern edge of the Mogilev governorate** (`RU_MOH`, 4,600 km² of
  the Mstislavl, Orsha, Klimovichi, Gorki and Gomel uezds): 35 people per
  km² in 1897, x 1.22, 91 % Belarusian.
* Incomes, vital rates and literacy like Soviet Belarus; Latgale a little
  richer and more literate. Towns (Dyneburg 43 k, Rzeżyca 13 k, Newel 15 k,
  Wieliż 12 k ...) and the railways of c. 1931 (Riga-Orel, Petersburg-Warsaw,
  Moscow-Windau, Bologoye-Polotsk) join the network; Daugavpils and Nevel
  stop being foreign gateways. Latvian is drawn on the maps with the
  regional languages (as Latgalian).

### 12.8 The equal-exchange Curzon line

For each atlas frame (1932, every 5 years, 2032), `plsim.curzon` draws a
continuous line across the whole state of the scenario (Poland, with
Lithuania in the union scenarios and Soviet Belarus where it is part of the
state), from one point of its outer border to another. The line follows
county borders: every county (powiat, apskritis, okrug) lies wholly on one
side. It divides the state into a Polish side and an other side, each in one
piece, and leaves:

* as many **non-Poles on the Polish side** as **Poles on the other side**,
  to within one county (the **residual** is reported);
* among all such lines, the most Poles on the Polish side.

**Who is counted.**

* Poles are speakers of Polish at home.
* Kashubians, Wymysorys speakers, Germans and Jews (by community, whatever
  their home language) are left out of the count altogether: they are
  neither Poles nor non-Poles. For a language other than Yiddish, the share
  of its speakers who are Jewish comes from the region's
  community-by-language table in the model run, applied to every cell of
  the region.
* Everyone else (Ukrainians, Belarusians, West Polesians, Lithuanians,
  Russians, Lemkos ...) is a non-Pole.

**Reformulation.** Non-Poles on the Polish side plus Poles on the Polish
side are the people counted there, and the Poles on both sides are all
Poles. The condition is therefore that the Polish side holds as many
counted people as there are Poles. The task is to find the most Polish
connected set of counties of about that size whose complement is connected
too; the line is their common border. If both sides are in one piece and
touch the outer border, that border is a single line from edge to edge.

**Search** (a heuristic: the exact problem is a hard graph-partitioning
problem). Counties are neighbours when their cells touch edge to edge on the
3.5 km grid.

1. *Growth.* The Polish side grows from its most Polish large county (the
   top quarter by people), always taking the most Polish county on its edge,
   until it holds the target number of people. A county whose taking would
   cut the other side in two is skipped, unless every piece cut off is
   Polish-majority; such pieces then join the Polish side. A remote Polish
   district (the Wilno lands, cut off by the Polish side's advance) can be
   taken in this way; a whole Lithuania or Polesie cannot.
2. *One piece.* Any piece of the other side still cut off joins the Polish
   side.
3. *Exchange.* While the Polish side is too large, it gives away its least
   Polish county on the line; while too small, it takes the most Polish
   county on the other side of the line. A county moves only if the side
   it leaves stays in one piece, and not within six moves of its last move
   (a "tabu" that stops two counties swapping back and forth).
4. *Scoring.* Each time the exchange crosses the target, the state is
   scored by the Poles the Polish side would hold at exact balance (the
   last county moved counted pro rata). Of the two whole-county states
   around the best crossing, the one nearer to balance is kept. The
   exchange stops when 60 crossings in a row bring no better score.
5. *Islands.* Counties that touch no other part of the state (none at
   present) stay on the side of their majority.
6. A test checks on a synthetic grid of 36 counties that every county lies
   on one side, the line is one curve, and the residual is within one
   county.

`curzon.split` without `units` still draws the line cell by cell, with exact
balance (the earlier method of the atlas). That line wound through counties
in strips one cell wide, which made it hard to read.

**Properties of the optimum.**

* The line is as jagged as the county borders, no more.
* The residual is at most the people of one border county: under 70
  thousand in most frames, up to 0.36 M where a large county lies on the
  line, against flows of 1.1-4.3 million each way.
* Whole counties cost nothing in practice. In the baseline of 1932 the
  line that wound cell by cell left 1.89 M each way, the county line
  1.83 M. Both searches are heuristics, and the one on cells, with
  far more moves open to it, stopped at a poorer solution.
* Remote Polish districts join the Polish side only if a chain of counties
  to them pays its way. In the union scenarios of 1932 the western Wilno
  lands come in through Grodno and Lida, and Tarnopol through Lwów county.

**Outputs.**

* The atlas overlay ("Equal-exchange line", magenta), with the counts on
  each side.
* `outputs/maps/<scenario>_curzon.csv`: the counts, the people not counted
  and the line, by frame.
* `outputs/maps/map_curzon.png` for the baseline.

**The historical Curzon line.** `curzon.HISTORICAL_LINE` is the line of the
Allied declaration of 8 December 1919 and Curzon's note of 11 July 1920. In
Eastern Galicia it follows "line A", which leaves Lwów on the other side;
"line B" would have given Lwów and Drohobych to Poland. It is digitised
approximately (to about 10 km) from the published description, north to
south:

* from the East Prussian border along the eastern and northern boundary of
  the Suwałki district to the Niemen;
* down the Niemen past Grodno;
* up the Łosośna to its source;
* south-west past Jałówka and east of Hajnówka to the Bug at Niemirów;
* up the Bug past Brest, Włodawa, Dorohusk and Uściług to Kryłów;
* then west of Rawa Ruska and east of Przemyśl to the Carpathians.

The same people as for the computed line are counted on each side of it
(the `hist_*` columns of the CSV, and the atlas overlay "Curzon line of
1919-20", dashed). This shows how far the equal-exchange line, which follows
the modelled population, lies from the diplomats' line, which followed the
ethnographic maps of 1919. In the baseline of 1932 the historical line leaves
0.96 M non-Poles on its west side and 3.26 M Poles on its east side (the
Wilno lands, Lwów and the eastern towns); the computed line leaves 1.83 M
on either side. By 2032 the historical line's imbalance grows to 2.1 M
against 7.9 M as the east Polonises. In the autonomy scenarios it comes
closer to balance (2.7 M against 3.7 M).

**Counting Poles by identity.** With `curzon_count: identity` the line
is drawn on national identity instead of home language: each cell's
speakers of a language take their region's identity mix for that language
(`curzon.identity_cells`), and Jews, Germans and Kashubians by identity are
left out. (Two exchange scenarios along the line were removed in this
version; the real transfers of 1944-47 are replayed in `historical`, §12.10.)

### 12.9 The German, Danzig and Czechoslovak lands (optional)

Two scenarios need land outside Poland and Lithuania of 1932: the
plebiscite lands with Danzig (`plebiscite_poland`) and the German land
Poland received in 1945 (`historical`). `include_west` lists the regions a
run holds (`data.west`):

* **Land.** `DE` is Germany on 1 January 1932 intersected with Poland of
  1946-2019 (CShapes 2.0): Silesia and Pomerania east of the Oder and the
  Lusatian Neisse, the Neumark, the Grenzmark, Stettin and Swinemünde, and
  southern East Prussia; `DZ` is the Free City of Danzig; `CS` is
  Czechoslovakia within hand-drawn outlines of the Czechoslovak parts of the
  Cieszyn, Spiš and Orava plebiscite areas (`tools/build_west.py`). On the
  grid: 99,790, 2,078 and 2,571 km². The territory of Poland and Lithuania
  does not change when these lands are available (four shore cells by
  Danzig, once given to Poland by the 2.5 km coast rule, are the Free
  City's).
* **Regions.** Fourteen, on the Regierungsbezirke: Oppeln, Breslau,
  Liegnitz east of the Neisse, the Neumark, the Grenzmark, Köslin, Stettin,
  and East Prussia split by faith and speech into Warmia (Catholic, with the
  Warmian Poles), Masuria with the Barten land (Lutheran, with the
  Masurians), Elbing and the Oberland, and the Marienwerder plebiscite area;
  Danzig; Cieszyn Silesia west of the Olza; Upper Orava and Zamagurie. 78
  units (groups of Kreise and districts) are their counties (grade E).
  Their regions are drawn like the voivodeships, by the weighted Voronoi of
  their towns fitted to their areas.
* **People.** 1933 German census totals, 1929 Danzig, 1930 Czechoslovak;
  latent home language and faith by unit (DATA_SOURCES). Upper Silesian,
  Masurian, Warmian, Kashubian and Goral speech are Polish (or Kashubian)
  home language; identity separates Polish, German, Silesian and "local"
  (§6.7). In 1932 the land Poland got in 1945 holds 8.1 M people and Danzig
  0.41 M; the model has 8.89 M together in 1939 (8.86 M).
* **Towns and lines.** 109 towns with their 1933 populations, under their
  Polish names, and the main and secondary railways of c. 1931; the
  Prussian roads between them start paved. They exist only when their land
  is in the run; a town whose region is left out is a foreign town of the
  run (Wrocław in `plebiscite_poland`). The 1932 gateways that are towns of
  these lands (Breslau, Gleiwitz-Beuthen, Stettin, Gdańsk) give way to the
  towns, and lines that crossed the land (Szamotuły-Stettin, Zbąszyń-Berlin,
  Działdowo-Königsberg, Grajewo-Königsberg, Gdańsk-Gdynia, Cieszyn-Ostrava)
  to its own lines.
* **Income.** About 1.45 times Poland's per head (Danzig 1.9; Cieszyn 1.3,
  Spiš and Orava 0.6). `y0_1931` is Poland's and Lithuania's income: a state
  that holds land from outside them starts with its own mean.

### 12.10 The historical scenario: events and calibration

`historical` replays the real century so that the behaviour shared by all
scenarios can be checked against what happened (`plsim.history`,
`plsim.history_check`, `scenarios/historical.yaml`).

**Three states, then two.** From 1932 the run holds the 1931 Polish state,
the German land of 1945 as a separate state `DE` and Danzig as `DZ`, each
with its own economy (Germany's eastern provinces follow Germany's income
path at about three quarters of its level), German as the contact language
there and Germanisation pressure. At the start of 1945 the German land and
Danzig pass to Poland, and the counties whose land lies mostly outside
Poland's post-war border (`borders_1932.json` key `PL1946`) pass to a
Soviet state `SU` that stays in the run: closed border, Ukrainian,
Belarusian or Lithuanian as contact language with Russian official, its
own income path. A border change resets competence in the new contact
language to the 1931 levels for it; the resettled German land takes the
vital rates, schooling and mean relative income of the rest of Poland
(`like`), since the people who will live there come from it.

**Events.** A list of dated events, each selecting people by region,
community, home language, national identity, sex and age:

| Kind | What it does |
|---|---|
| `border` | regions change state, contact and official languages |
| `deaths` | a share or a number of the selected die |
| `emigrate` | they leave the territory |
| `transfer` | they move to other regions, by weight or to the homes earlier events vacated (`@vacated`) |
| `immigrate` | a number arrive from outside, with a group and identity |
| `away` | they leave for a while (forced labour in the Reich) and come back to the same region and stratum in the given shares of later years, aged and thinned by a yearly survival |
| `identity` | a share change national identity |

Removals take people in proportion to their cohorts; with an identity
filter, in proportion to that identity's share of each cell. Movers keep
their age, sex, group and identity. Every event enters the year's
accounts (deaths, emigrants, immigrants, inter-regional flows), so the
accounting identity of the projection still holds. The events of the
scenario: the September campaign, Soviet deportations and the resettlement
of the Volhynian Germans; forced labour in the Reich (2.1 M Poles of the
post-war territory taken in 1940-44, 68 % back in 1945, 24 % in 1946-48 with
the UNRRA repatriation, the rest stay abroad or die there; the census of
February 1946 counted none of those still away); deaths under occupation (60 %
of them spread over everyone, the rest on men of 16-60), Volhynia 1943 and
the flight of 150,000 Poles from Volhynia and Eastern Galicia into the
General Government, the Warsaw Uprising and the emptying of Warsaw; no
voluntary moves between regions in 1940-44 (demarcation lines, the General
Government's controls); the Holocaust (about 95 % of the Jews who did not
flee east); Wehrmacht losses and deaths in the flight of 1945; flight and
expulsion of the Germans (62 % in 1945, most of the rest by 1950), the
autochthons fleeing at lower rates and leaving later as Aussiedler (by
rate, 1951-1992); the repatriation of Poles from the Soviet Union (1.5 M
in 1945-47, 0.25 M in 1956-58) and from its interior; settlers from central
Poland (2.5 M in 1945-50) into the vacated homes; the transfer of the
Greek Catholic and Orthodox Ukrainian and Lemko speakers of the Lublin,
Rzeszów and Kraków voivodeships to the Soviet Union (482,880 in 1944-46) and
Operation Vistula (140,660 in 1947) (selected by faith, as the authorities did,
not by declared nationality; scattered over the German land a few families
to a village, so the transferred groups lose their clustering, §12.6); the
Jewish emigration waves; and, after 1989, the German minority and a
Silesian identity declared again.

**People's Poland.** Income per head follows Maddison's series (1990 GK$)
from 1939 to 2019, then converges as elsewhere; a fertility period effect
(war -20 %, post-war compensation +25-38 % in 1946-60, the pro-natalism of
the 1970s-80s +12-18 %, the slump after 1990 -14-22 %); a socialist
mortality regime (§4.1); emigration closed in 1940-45 and 1949-55,
partly open in 1956-58 and the 1970s, open in the 1980s and after 2004;
faster urbanisation at low income (forced industrialisation) that levels
off at about 62 %; German banned, Ukrainian schools closed until 1956,
stronger assimilation pressure.

**Results against the censuses** (`outputs/history/historical_checks.csv`;
updated with each build): see SCENARIOS, "Results: historical". The
fertility and mortality settings of §4.1-4.2 come from this comparison.

### 12.11 What the maps cannot show

* Towns use their region's urban mix, tilted by the hinterland. Strongly
  Jewish shtetls (Pińsk, Brody) therefore appear more mixed than they were.
* Internal borders are approximate. A cell averages several villages, so
  single Lauda manors or the Karaim of Troki are below the resolution.
* Region-level differences in shift rates show up as edges along
  voivodeship lines, e.g. Polesian ("tutejszy") shift inside the Polesie
  voivodeship, where the census category was defined.

## 13. Limitations

* **Spatial grain.** The unit of the projection is the powiat/apskritis
  (x urban/rural). Its borders and the borders of the voivodeships are
  approximated from the county seats (§12.1). Only the eight eastern
  voivodeships have county census figures by language; elsewhere counties
  are downscaled from the voivodeship. The enclave factors are a
  reduced-form substitute for village-level geography. The 3.5 km maps
  (section 12) are a downscaling of the county results, not an independent
  spatial model.
* **Starting data.** Some regional inputs (religion-by-voivodeship shares,
  regional income indices, urban shares, Lithuanian unit breakdowns) are
  rounded reconstructions and are graded in `DATA_SOURCES.md`.
* **Network.** The network is stylised: ~15 k modelled route-km versus
  ~20 k in reality, straight-line lengths x detour factors, and no freight
  flows beyond a uniform uplift.
* **No endogenous politics.** No other wars, coups, Soviet or German
  aggression, or border changes. Policies are scenario inputs, not outcomes.
  The fate of Klaipėda (annexed by Germany in March 1939 in reality) is held
  at the federal status quo.
* **Jewish demography.** This is the most counterfactual component: the
  future of Palestine/Israel as a destination, the strength of Haredi
  fertility without the Holocaust and interwar-style secularisation are all
  very uncertain. Ranges are wide on purpose.
* **Economy.** It is a driver, not a model: there are no sectors, prices or
  trade policy.
* **Language.** Language use is binary per person (home vernacular plus
  competence in the dominant language). Diglossia, dialect levelling and
  literacy in a third language are not represented.
* **Mixed marriages** are a yearly hazard on young bilingual adults (§6.3),
  not a marriage market: the partner's language and religion are not
  tracked, and religion is otherwise inherited from the mother. The
  historical scenario gets the 2002 and 2011 home languages of the eastern
  minorities about right, but keeps Ukrainian and Lemko identity two to
  three times the census's (§6.7). German is the opposite: the model has
  74 thousand German speakers in 2002 and 49 in 2011, against census
  counts of 205 and 96 thousand that include second home languages; the
  Upper Silesian natives married among themselves across the German and
  Silesian-Polish line, which the model counts as marrying out.

## 14. References

**Data**

* Główny Urząd Statystyczny (1936-38). *Drugi Powszechny Spis Ludności z
  dn. 9 XII 1931 r.* (voivodeship volumes); *Mały Rocznik Statystyczny 1939*.
* Centralinis statistikos biuras (1926). *Lietuvos gyventojai. Pirmojo 1923 m.
  rugsėjo 17 d. visuotinojo gyventojų surašymo duomenys* (Tables I, III and IV
  by apskritis read for this model); 1925 Klaipėda census.
* *Первая всеобщая перепись населения Российской империи 1897 г.*
  (native-language tables, Vilna, Kovno, Grodno, Volhynia governorates).
* Tomaszewski, J. (1985). *Rzeczpospolita wielu narodów*. Warsaw: Czytelnik.
* Kubijovyč, V. (1983). *Etnichni hrupy pivdennozakhidnoi Ukrainy (Halychyny)
  na 1.1.1939*. Wiesbaden.
* Maddison, A. (2003). *The World Economy: Historical Statistics*. OECD;
  Bolt, J. & van Zanden, J. L. (Maddison Project Database).

**Demography**

* Alkema, L., Raftery, A. E., Gerland, P., Clark, S. J., Pelletier, F.,
  Buettner, T., & Heilig, G. K. (2011). Probabilistic projections of the
  total fertility rate for all countries. *Demography* 48(3), 815-839.
* Raftery, A. E., Chunn, J. L., Gerland, P., & Ševčíková, H. (2013). Bayesian
  probabilistic projections of life expectancy for all countries.
  *Demography* 50(3), 777-801.
* Oeppen, J., & Vaupel, J. W. (2002). Broken limits to life expectancy.
  *Science* 296, 1029-1031.
* Torri, T., & Vaupel, J. W. (2012). Forecasting life expectancy in an
  international context. *International Journal of Forecasting* 28(2),
  519-531.
* Preston, S. H. (1975). The changing relation between mortality and level of
  economic development. *Population Studies* 29(2), 231-248.
* Siler, W. (1979). A competing-risk model for animal mortality. *Ecology*
  60(4), 750-757.
* Coale, A. J., & Watkins, S. C. (eds.) (1986). *The Decline of Fertility in
  Europe*. Princeton UP.
* Lesthaeghe, R. (1977). *The Decline of Belgian Fertility, 1800-1970*.
  Princeton UP.
* Hoem, J. M., et al. (1981). Experiments in modelling recent Danish
  fertility curves. *Demography* 18(2), 231-244.

**Migration**

* Rogers, A., & Castro, L. J. (1981). *Model Migration Schedules*. IIASA
  RR-81-30.
* Zipf, G. K. (1946). The P1P2/D hypothesis. *American Sociological Review*
  11(6), 677-686.
* Stouffer, S. A. (1940). Intervening opportunities. *American Sociological
  Review* 5(6), 845-867.
* Wilson, A. G. (1971). A family of spatial interaction models.
  *Environment and Planning A* 3(1), 1-32.
* Simini, F., González, M. C., Maritan, A., & Barabási, A.-L. (2012). A
  universal model for mobility and migration patterns. *Nature* 484, 96-100.
* Lewis, W. A. (1954). Economic development with unlimited supplies of
  labour. *The Manchester School* 22(2), 139-191.
* Harris, J. R., & Todaro, M. P. (1970). Migration, unemployment and
  development. *American Economic Review* 60(1), 126-142.
* Zelinsky, W. (1971). The hypothesis of the mobility transition.
  *Geographical Review* 61(2), 219-249.
* Hatton, T. J., & Williamson, J. G. (1998). *The Age of Mass Migration*.
  Oxford UP; (2005) *Global Migration and the World Economy*. MIT Press.
* de Haas, H. (2010). Migration transitions. IMI Working Paper 24, Oxford.
* Davis, J. C., & Henderson, J. V. (2003). Evidence on the political economy
  of the urbanization process. *Journal of Urban Economics* 53(1), 98-125.

**Borders**

* Schvitz, G., Girardin, L., Rüegger, S., Weidmann, N. B., Cederman, L.-E.,
  & Gleditsch, K. S. (2022). Mapping the international system, 1886-2019:
  The CShapes 2.0 dataset. *Journal of Conflict Resolution* 66(1), 144-161.
  Data from the R package cshapes 2.0 (CRAN).

**Language: spatial models and downscaling**

* Prochazka, K., & Vogl, G. (2017). Quantifying the driving factors for
  language shift in a bilingual region. *PNAS* 114(17), 4365-4369.
  https://www.pnas.org/doi/10.1073/pnas.1617252114
* Kandler, A., & Steele, J. (2017). Modeling language shift. *PNAS*
  114(19), 4851-4853. https://doi.org/10.1073/pnas.1703509114
* Patriarca, M., & Heinsalu, E. (2009). Influence of geography on language
  competition. *Physica A* 388(2), 174-186.
* Isern, N., & Fort, J. (2014). Language extinction and linguistic fronts.
  *Journal of the Royal Society Interface* 11, 20140028.
* Burridge, J. (2017). Spatial evolution of human dialects. *Physical Review
  X* 7, 031008.
* Trudgill, P. (1974). Linguistic change and diffusion: description and
  explanation in sociolinguistic dialect geography. *Language in Society*
  3(2), 215-246.
* Ballas, D., Rossiter, D., Thomas, B., Clarke, G., & Dorling, D. (2005).
  *Geography Matters: Simulating the Local Impacts of National Social
  Policies*. York: Joseph Rowntree Foundation.
* Lovelace, R., & Dumont, M. (2016). *Spatial Microsimulation with R*.
  CRC Press.
* Wessel, P., & Smith, W. H. F. (1996). A global, self-consistent,
  hierarchical, high-resolution shoreline database. *Journal of Geophysical
  Research* 101(B4), 8741-8743 (GSHHS, via basemap-data).

**Language**

* Abrams, D. M., & Strogatz, S. H. (2003). Modelling the dynamics of language
  death. *Nature* 424, 900.
* Mira, J., & Paredes, Á. (2005). Interlinguistic similarity and language
  death dynamics. *Europhysics Letters* 69(6), 1031-1034.
* Minett, J. W., & Wang, W. S.-Y. (2008). Modelling endangered languages: the
  effects of bilingualism and social structure. *Lingua* 118(1), 19-45.
* Kandler, A., Unger, R., & Steele, J. (2010). Language shift, bilingualism
  and the future of Britain's Celtic languages. *Phil. Trans. R. Soc. B* 365,
  3855-3864.
* Kandler, A., & Steele, J. (2008). Ecological models of language
  competition. *Biological Theory* 3(2), 164-173.
* Castelló, X., Eguíluz, V. M., & San Miguel, M. (2006). Ordering dynamics
  with two non-excluding options: bilingualism in language competition.
  *New Journal of Physics* 8, 308.
* Patriarca, M., & Leppänen, T. (2004). Modeling language competition.
  *Physica A* 338, 296-299.
* Isern, N., & Fort, J. (2014). Language extinction and linguistic fronts.
  *J. R. Soc. Interface* 11, 20140028.
* Cavalli-Sforza, L. L., & Feldman, M. W. (1981). *Cultural Transmission and
  Evolution*. Princeton UP.
* Fishman, J. A. (1991). *Reversing Language Shift*. Multilingual Matters.
* Breton, R. (1964). Institutional completeness of ethnic communities and the
  personal relations of immigrants. *American Journal of Sociology* 70(2),
  193-205.
* Weber, E. (1976). *Peasants into Frenchmen*. Stanford UP.

**Networks and economy**

* Yerra, B. M., & Levinson, D. M. (2005). The emergence of hierarchy in
  transportation networks. *Annals of Regional Science* 39(3), 541-553.
* Xie, F., & Levinson, D. (2009). Modeling the growth of transportation
  networks: a comprehensive review. *Networks and Spatial Economics* 9(3),
  291-307; (2011) *Evolving Transportation Networks*. Springer.
* Louf, R., Jensen, P., & Barthelemy, M. (2013). Emergence of hierarchy in
  cost-driven growth of spatial networks. *PNAS* 110(22), 8824-8829.
* Barthélemy, M. (2011). Spatial networks. *Physics Reports* 499, 1-101.
* Harris, C. D. (1954). The market as a factor in the localization of
  industry in the United States. *Annals AAG* 44(4), 315-348.
* Donaldson, D., & Hornbeck, R. (2016). Railroads and American economic
  growth: a "market access" approach. *QJE* 131(2), 799-858.
* Fogel, R. W. (1964). *Railroads and American Economic Growth*. Johns
  Hopkins.
* Atack, J., Bateman, F., Haines, M., & Margo, R. A. (2010). Did railroads
  induce or follow economic growth? *Social Science History* 34(2), 171-197.
* McCallum, J. (1995). National borders matter. *American Economic Review*
  85(3), 615-623.
* Barro, R. J. (1991). Economic growth in a cross section of countries. *QJE*
  106(2), 407-443.
* Barro, R. J., & Sala-i-Martin, X. (1992). Convergence. *JPE* 100(2),
  223-251.
* Dargay, J., & Gately, D. (1999). Income's effect on car and vehicle
  ownership, worldwide: 1960-2015. *Transportation Research A* 33(2),
  101-138.
* Dargay, J., Gately, D., & Sommer, M. (2007). Vehicle ownership and income
  growth, worldwide: 1960-2030. *The Energy Journal* 28(4), 143-170.
