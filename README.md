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
pytest -q                               # 41 tests
```

A 100-year run takes about 20 s. The full report takes about 7 minutes on 4
cores.

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

* **Starting points** (`census_variant`):
  * `official`: the 1931 census as printed.
  * `religion_corrected`: Tomaszewski-style. It reproduces his ~64.7 % ethnic
    Poles.
  * `vernacular`: the upper bound for minority speech, anchored on the 1897
    imperial Russian native-language census.
* **Lithuania's Polish-speakers** (`lt_variant`): 65.6 k in the 1923 census,
  the ~202 k Polish claim of 1923, or the ~9 % Polish share of the 1897 Kovno
  governorate.
* **Census observation model.** It re-expresses any latent state as a
  1931-type Polish census, the 1897 imperial census, the 1923 Lithuanian
  census or a modern self-identification census would have recorded it.
  Passing the corrected reconstructions through the 1931 regime reproduces
  the printed national shares to within 2-3 points in total. In other words,
  the published census is consistent with a considerably less Polish-speaking
  population.
* **Lauda** (Kėdainiai-Panevėžys-Ukmergė-Raseiniai) is its own unit. The
  Polish-speaking petty gentry there survive under the federal bilingual
  baseline, are Lithuanised under `forced_lithuanization`, and Polish spreads
  under a `polonizing_union`.

## Headline results (baseline, 32-member ensemble)

Medians, with 5-95 % ranges in brackets. The whole union is 17 Polish units
plus 6 Lithuanian units.

| Year | Population (M) | TFR | e0 m / f | Urban % | GDP/head (1990 GK$) |
|---|---|---|---|---|---|
| 1939 | 37.2 (Poland 34.6) | 3.27 | 50.7 / 54.3 | 28 | 2,070 |
| 1960 | 44.5 [43.1-46.2] | 2.91 | 59.4 / 64.3 | 39 | 3,830 |
| 1990 | 51.0 [46.8-55.9] | 1.91 | 68.1 / 74.6 | 57 | 9,500 |
| 2032 | 51.8 [43.0-63.0] | 1.58 | 79.5 / 84.3 | 67 | 18,200 |

**Demography**

* The population peaks at ~53 M around 2014.
* The Polish voivodeships alone reach ~49-50 M (the Second Republic alone:
  48.3 M [39-61] in 2032).
* Net emigration of ~100-120 k/yr in the guest-worker era gives way to net
  immigration only in the high-convergence runs.

**Languages** (home vernacular, shares of the whole union)

| Language | 1933 | 2032 |
|---|---|---|
| Polish | 63.8 % | 67.4 % |
| Ukrainian | 12.7 % | 16.3 % (~8.4 M speakers, roughly doubling) |
| Yiddish | 8.2 % | 4.5 % |
| Belarusian | 2.9 % | 2.6 % |
| Lithuanian | 5.9 % | 4.4 % |

* **Ukrainian** grows faster than the population as a whole: high Galician
  and Volhynian fertility plus robust Greek-Catholic institutions.
* **Yiddish** declines among acculturating Jews, from 78 % Yiddish-speaking
  in 1935 to 12 % in 2030. It survives through a growing Haredi population
  (~1.7 M in 2030; very uncertain).
* **Kashubian**: 200 k -> 115 k [77-165 k].
* **Lemko**: 120 k -> 106 k.
* **West Polesian**: persists in villages (0.9 M) as a declining share.
* **Wymysorys**: 1,500 -> ~60 speakers, moribund even without the post-war
  ban.
* **Karaim**: ~680 -> ~230 speakers.

**Infrastructure**

* Almost all inter-town roads are paved by ~1960.
* By 2032: ~6,400 km of motorway, 9,600 km of expressway, ~10,300 km of
  electrified trunk railway and ~1,000 km of high-speed line.
* The 1939 plans are completed in the early 1940s: the Wilno-Gdynia shortcut
  Łapy-Ostrołęka-Przasnysz-Mława, Dębica-Jasło, and the COP Łódź-Dębica
  trunk.

## Scenarios (single seeded run each, 2032)

| Scenario | Polish-unit pop. (M) | Polish % | Ukrainian % | Yiddish % | Belarusian % | Lithuanian % | W. Polesian (k) |
|---|---|---|---|---|---|---|---|
| baseline | 46.2 | 67.5 | 16.9 | 3.9 | 2.9 | 4.4 | 950 |
| ii_rp_only | 46.3 | 70.3 | 17.9 | 4.1 | 3.1 | 0.2 | 993 |
| federal_autonomy | 46.2 | 62.6 | 18.2 | 4.6 | 4.2 | 4.4 | 1,570 |
| integral_nationalism | 45.7 | 71.5 | 15.7 | 3.2 | 2.1 | 4.3 | 547 |
| forced_lithuanization | 46.2 | 67.4 | 16.9 | 3.9 | 2.9 | 4.5 | 949 |
| polonizing_union | 46.1 | 67.9 | 16.9 | 3.9 | 2.9 | 3.9 | 949 |
| census_religion_corrected | 46.2 | 64.9 | 18.5 | 3.9 | 3.9 | 4.3 | 951 |
| census_vernacular | 46.3 | 64.2 | 19.0 | 3.9 | 4.2 | 4.2 | 951 |
| finnish_path | 49.1 | 67.8 | 16.4 | 3.8 | 2.7 | 4.3 | 915 |
| stagnation | 39.0 | 65.7 | 17.2 | 4.4 | 3.1 | 4.6 | 1,006 |

Polish-speakers in the Lithuanian units in 2032:

| Scenario | Polish-speakers (from ~80 k in 1932) |
|---|---|
| baseline (federal) | ~70 k |
| forced_lithuanization | ~28 k |
| polonizing_union | ~310 k |
| starting from the 1923 Polish claim | 181 k -> ~140 k |

The full table is in `outputs/scenario_summary.csv`; the assumptions are in
`docs/SCENARIOS.md`.

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
  cli.py                 command-line interface
scenarios/*.yaml         12 scenarios (extends/override)
docs/                    METHODOLOGY, DATA_SOURCES (with reliability grades), SCENARIOS
outputs/                 report.html, figures/, scenario_summary.csv, ensemble CSVs, baseline run CSVs
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
