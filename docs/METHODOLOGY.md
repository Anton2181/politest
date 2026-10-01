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
| `official` | the census as printed | 68.7 | 14.0 | 3.1 |
| `religion_corrected` | Tomaszewski-style: 80 % of Polish-declared Greek Catholics -> Ukrainian, 85 % of Polish-declared Orthodox -> Belarusian/Ukrainian by region | 66.4 | 15.4 | 4.1 |
| `vernacular` | the above, plus Catholic Belarusian/Lithuanian vernaculars in rural Wilno, Nowogródek and Białystok and latynnyky in Galicia/Lublin, anchored on 1897 proportions (upper bound) | 64.0 | 16.2 | 5.6 |

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
* `lithuanian_1923`: a nationality census that entered many Catholic
  Polish-speakers in Lithuania as Lithuanian;
* `modern_selfid`: bilingual minority speakers partly identify with the
  dominant language.

**Consistency test** (`python -m plsim census`). If you pass the
religion-corrected or vernacular reconstruction through the 1931 regime, you
get back the published national shares, with a total absolute error of 2.0
and 2.8 points across the eight categories. So a population that really spoke
the corrected languages at home would have produced the census that was
actually printed. That is the quantitative form of the argument in §3.2. The
model reports its results both as latent home languages and as a given census
regime would have recorded them.

### 3.5 Lithuania

The 1923 Lithuanian census (2.03 M without Klaipėda) and the 1925 Klaipėda
census (141.6 k: 43.5 % German, 27.6 % Lithuanian, 25.2 % "Memellanders")
are carried forward to end-1931 (~2.39 M) and split into six units. Klaipėda's
Memellanders become Lutheran Lithuanian-vernacular speakers who are highly
bilingual in German. The Polish-speaking population has three variants
(`lt_variant`):

| variant | Polish-speakers | source |
|---|---|---|
| `census_1923` | 65.6 k (3.2 %) | Lithuanian census |
| `polish_claim_1923` | ~176 k (7.3 %) | Polish electoral committee's 1923 claim (202 k, ~10 %), from the Polish vote |
| `imperial_1897` | ~160 k (6.8 %) | 1897 Kovno governorate native-language tables (~9 %) |

The **Lauda** country (Kėdainiai-Panevėžys-Ukmergė-Raseiniai), home of the
Polish-speaking petty gentry, is a separate unit (`LT_LAU`). Lithuanisation
there was not inevitable: the scenarios switch between a federal bilingual
regime (baseline), the historical forced Lithuanisation, and a Polonising
unitary union (§6.6).

### 3.6 Urban/rural split, ages, bilingualism

* **Urban split.** Groups differ by fixed urban-residence odds ratios (Jews
  ~12-22x the local baseline; Polish-speakers in the Kresy 1.5-3x;
  Polesians, Lemkos and Ukrainian peasants 0.1-0.25x). A per-region base
  odds is solved so that the regional urban share matches the census and the
  Polish total matches 27.4 %.
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
  of 1.5-12 years.
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
  Orthodox 0.85, Greek Catholic 0.9, acculturating Jews 1.1, and Haredi 0.12,
  whose fertility drifts to its own long-run mean.
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
move from Kraków, Kielce, Lublin, Warsaw and Lwów voivodeships to Volhynia,
Polesie, Nowogródek and Wilno. The flow is 8 k/yr in the 1930s, 12 k/yr for
1939-55 (Polesie drainage), then zero. The `integral_nationalism` scenario
raises it to 25 k/yr.

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
  0.22 x enrolment x (1 - 0.7 x own-language schooling share).
* **Adult contact** (15-64): 0.012 x local dominant-language share x
  (1.8 in towns).
* **Conscription** (men 20-21): 0.35 while conscription lasts.
* **Adult re-identification** of bilinguals: 0.3 %/yr scaled like the
  vertical term.
* **Haredi defection** at birth: 20 % per birth in 1931, falling to 12 %.
  There is a small reverse flow.

### 6.4 Calibration anchors

| Anchor | Evidence | Model (baseline) |
|---|---|---|
| Yiddish among acculturating Jews | Soviet Jews 70.4 % Yiddish (1926) -> ~41 % (1939) under coercion; interwar Polish-Jewish youth rapidly Polonising in state schools; Hungarian and Czech Jewry shifted in ~2 generations | 78 % (1935) -> 51 % (1960) -> 28 % (1990) -> 12 % (2030) |
| Wymysorys | 92 % of Wilamowice (1,525/1,662) spoke it in 1880, 72 % in 1890 | ~1,500 -> ~250 (2000) -> ~60 (2032): moribund even without the post-war ban |
| Catholic Belarusian vernacular | rapid Polonisation of Catholic Belarusian-speakers; the 1897 -> 1931 recording gap | 85 k (1935) -> 75 k (1960) -> 48 k (1990) -> 18 k (2030) in Wilno/Nowogródek/Białystok |
| Greek Catholic Ukrainian | strong institutions (church, Prosvita, cooperatives) | 85 % of Greek Catholics Ukrainian-speaking (1935) -> 82 % (1990) -> 79 % (2030) |
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
each region's dominant language are all scenario inputs. Examples:

* Ukrainian autonomy makes Ukrainian the regional state language in
  Stanisławów, Tarnopol and Volhynia (`federal_autonomy`).
* The Lithuanian unit closes Polish schools (`forced_lithuanization`).
* Polish becomes dominant in the Lithuanian lands too (`polonizing_union`).
* Vilnius becomes the Lithuanian federal capital (`wilno_lithuanian`).

## 7. Transport networks

### 7.1 Representation

About 190 nodes: 170 towns in the union with 1931 populations and
coordinates, plus foreign gateways (Danzig, Berlin, Breslau, Upper Silesia,
Königsberg, Riga, Minsk, Kyiv, Chernivtsi, Žilina, Ostrava, Mukachevo, Tilsit,
Liepāja).

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
    gain of the 1930s Road Fund and of post-war programmes.
  * Benefits are valued at 35 % of income per hour, discounted at 5 % over
    40 years, and optionally **equity-weighted** towards poor regions (full
    weight 1940-54, the Fifteen-Year Plan's goal of erasing Poland "A" and
    "B").
* **Budgets**: 0.4 % of GDP in the early 1930s, 0.8-1.2 % after 1939. Rail
  and roads have separate accounts (as with PKP vs. the 1931 Road Fund), with
  the rail share falling from 55 % to 35-40 %. Accounts may accumulate up to
  six years' allocation for large works. Greedy selection by BCR >= 1.
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
  Europe), 0.8-0.88 in `finnish_path`, 0.45-0.5 in `stagnation`.
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
2000 in 50-80 %. They are checked automatically by `python -m plsim validate`.

### 10.3 Census consistency

See §3.4. Passing the reconstructions through the 1931 observation model
reproduces the printed census to within 2-3 points in total.

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
* **Language**: Abrams-Strogatz exponent (1.1-1.5), the monolingual damping,
  and the key shift propensities (Yiddish, Polesian, Catholic Belarusian,
  Greek-Catholic Ukrainian, Kashubian, Haredi exit).
* **Network**: gravity decay, BCR threshold.

Reports give medians with 50 % and 90 % bands.

## 12. Maps: spatial downscaling and local language shift

The projection works with 23 regions x rural/urban. To draw maps,
`plsim/spatial.py` places each region on a grid of 9,383 cells of
0.0625° x 0.1° (about 7 x 7 km) and carries the cells forward year by year.
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
  the Curonian Spit. The grid has 9,383 cells: 386,700 km² for Poland
  (official 388,600 km²) and 55,600 km² for Lithuania (official 55,750 km²).
* **Before CShapes.** The territory used to be approximated by the
  nearest-town rule (domestic towns against about 110 foreign "mask" towns).
  That misplaced about 36,000 km² of Poland and 8,500 km² of Lithuania,
  mostly in bands up to 25 km deep along the Soviet and Latvian borders.
* **Regions.** Cells are assigned by a multiplicatively weighted Voronoi
  diagram of the domestic towns of their own state, with one weight per
  region calibrated so that cell areas match the official areas (all
  within 2.5 %). Warsaw city has two cells. State borders are therefore
  exact to the cell; voivodeship borders are approximations.
* **Drawing.** Maps clip the cell colours to the CShapes polygons and draw
  the state border and the Polish-Lithuanian border as lines, so the
  border itself is not stair-stepped at 7 km.
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
growth k = 0.022/y). Over a century that is 11 km, under two of our cells.
On the 7 km grid, most visible change therefore comes from the regional
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
* `outputs/atlas/`, an interactive atlas: 12 scenarios, a time slider,
  language, single-language, density and growth layers, and a cell
  read-out. Frames are quantised to 8 bits every 5 years (gzip, about
  0.6 MB per scenario) and interpolated in the browser.

### 12.5 Sub-regions and federal members

The spatial layer also works in the other direction. It splits voivodeships
for scenarios whose borders cut through them, such as the Curzon line, a
canton or an autonomy (`plsim/partition.py`, `plsim/data/subregions.py`).

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

Region-keyed settings resolve by specificity: an exact code (`WIL.E`) beats
the parent code (`WIL`), which beats a wildcard (`LT_*`), which beats
`default` (`params.region_lookup`).

Two settings describe the political map:

* `dominant_language`: the official language of each region.
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

`partition: counties` runs every voivodeship as its 1931 powiaty, and the
Lithuanian units as their apskritys. Warsaw city and Kaunas city stay whole,
which gives 270 regions in place of 23. The county table is
`plsim/data/counties.py` (sources and grades in `docs/DATA_SOURCES.md`).
It has 269 counties. Węgrów's seat wins no cell on the approximate
voivodeship map, so it is merged into its neighbours.

**Initial state.** Cells and towns are assigned to the nearest county seat,
as for the named splits. The county's population and languages are then
set by its grade:

* **Grade A** (97 counties: the eight eastern voivodeships). The seed is
  the 1931 county count by mother tongue. Merged categories are split by the
  downscaled pattern: Belarusian + tutejszy + Russian in Nowogródek and
  Polesie, "other", and the unenumerated Kashubian, Lemko and Wymysorys
  speakers inside "Polish" and "Ukrainian". Two IPFs follow:
  1. Over (county × language), fitting the county populations and the
     voivodeship's latent language totals for the chosen census variant.
  2. Over (county × stratum × language), splitting rural and urban by the
     downscaled split of each language in each county, and matching the
     voivodeship by stratum.

  The census variant therefore keeps its voivodeship totals, and the county
  table decides where the speakers live. Under the religion-corrected
  variant, a county with many Greek Catholics declaring Polish keeps more
  Ukrainian speakers than its printed figure.
* **Grade B** (19: Lublin, part of Polesie). The county population is
  known. Its languages come from the downscaled pattern.
* **Grade C** (153: centre, west, Lithuania). Fully downscaled from the
  voivodeship.

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
    counties by rural population.

  Splitting a voivodeship therefore moves migrants between its counties
  without changing how many it sends or draws (tested: a split run stays
  within 0.4 % of the unsplit one by 1945; without nesting it is up to
  1.5 % off). The nesting also applies to named splits that stay inside one
  member, e.g. both halves of lwowskie in the Ukrainian autonomy.

* **Random numbers.** Regional noise (life expectancy, phase-III
  fertility) is drawn per 1931 voivodeship and shared by its counties. A
  county run therefore sees the same shocks as the voivodeship run with the
  same seed.

**Results (baseline, seeded run, 2032).**

* **Consistency.** The county run is a consistent breakdown of the
  voivodeship model:

  | | Voivodeship run | County run |
  |---|---|---|
  | Population | 48.25 M | 48.15 M |
  | Urban share | 66.1 % | 66.2 % |
  | Ukrainian speakers | 8.17 M | 8.20 M |
  | Belarusian speakers | 1.39 M | 1.40 M |
  | Lithuanian speakers | 2.10 M | 2.09 M |
  | West Polesian speakers | 0.95 M | 0.92 M |

  Every voivodeship's 2032 language shares are within about a point of the
  voivodeship run.
* **Populations.** Most voivodeship totals are within ±5 %. Two differ
  more. Pomorze is 10 % smaller, because migrants' travel times are now
  measured to each county (Gdynia included) rather than to Toruń, and the
  Kashubian counties draw fewer Polish speakers. Klaipėda is 13 % larger.
* **What the county level adds is *where*.** The plurality language
  changes in 34 of 268 counties:
  * the Belarusian blocks of eastern wileńskie (Głębokie, Mołodeczno,
    Wilejka) and of Nowogródek (Nieśwież, Nowogródek, Słonim) turn
    Polish-plurality;
  * all nine Polesie counties move from West Polesian to Polish;
  * Kartuzy, Kościerzyna and Wejherowo lose their Kashubian plurality;
  * nine Lwów counties and six Tarnopol counties turn from Ukrainian to
    Polish plurality.

  Volhynia and the core of Stanisławów stay Ukrainian (Łuck 60 → 65 %).
  The cities draw the rural surplus of their voivodeship: Lwów county
  grows from 460 k to 829 k, Wilno from 415 k to 782 k, and Brześć from
  227 k to 1.03 M.
* **Cost.** A run takes about 4 minutes, against 25 s for the voivodeship
  model.

A first county run, before any of this nesting, gave 48.6 M people. In
it, Warsaw grew only 1.06× instead of 2.4×, because every rural county
grew its own towns. Ukrainian came out 200 k higher. Different random
numbers and double-counted clustering both contributed: the concentration
rescaling alone removes about 30 k Belarusian speakers.

### 12.7 What the maps cannot show

* Towns use their region's urban mix, tilted by the hinterland. Strongly
  Jewish shtetls (Pińsk, Brody) therefore appear more mixed than they were.
* Internal borders are approximate. A cell averages several villages, so
  single Lauda manors or the Karaim of Troki are below the resolution.
* Region-level differences in shift rates show up as edges along
  voivodeship lines, e.g. Polesian ("tutejszy") shift inside the Polesie
  voivodeship, where the census category was defined.

## 13. Limitations

* **Spatial grain.** The unit of the projection is the voivodeship/apskritis
  (x urban/rural), not the powiat. The enclave factors are a reduced-form
  substitute for village-level geography. The 7 km maps (section 12) are a
  downscaling of those regional results, not an independent spatial model.
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

## 14. References

**Data**

* Główny Urząd Statystyczny (1936-38). *Drugi Powszechny Spis Ludności z
  dn. 9 XII 1931 r.* (voivodeship volumes); *Mały Rocznik Statystyczny 1939*.
* Centralinis statistikos biuras (1926). *Lietuvos gyventojai. Pirmojo 1923 m.
  rugsėjo 17 d. visuotinojo gyventojų surašymo duomenys*; 1925 Klaipėda
  census.
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
