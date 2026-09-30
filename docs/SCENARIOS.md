# Scenarios

Every scenario shares the premise: **no Second World War**. There is no
German-Soviet partition, no Holocaust, no deportations, no post-1945 border
shifts or population transfers, and no communist regime. Everything else that
cannot be measured is a scenario choice. Scenarios are YAML files in
`scenarios/`. A scenario can `extends:` another one and overrides only the
parameters it names. A mapping containing `_replace: true` replaces the parent
mapping instead of being merged into it.

| Scenario | What changes | Why it is plausible |
|---|---|---|
| `baseline` | Polish-Lithuanian **federation**: Lithuania and Klaipėda form a unit with Lithuanian as its state language and Polish as the federal language. Sanacja-style assimilation pressure eases after 1950. The 1939 plans are executed. Southern-European convergence (kappa 0.55 -> 0.70). | The federal idea (Piłsudski's *Międzymorze*) was the main alternative to the incorporation of Wilno. 1930s policy was assimilationist but not genocidal. Catholic agrarian peripheries without communism (Spain, Portugal, Italy's South) are the natural comparators. |
| `ii_rp_only` | The Second Republic alone, in its 1938 borders. Lithuania is a foreign state; the Vilnius-Kaunas links stay cut. | The literal "surviving interwar Poland". |
| `federal_autonomy` | Ukrainian territorial autonomy with Ukrainian as the regional state and school language in Stanisławów, Tarnopol and Volhynia. Belarusian schooling. Equal Lithuanian status. Lower pressure. | The 1938 Ukrainian autonomy proposals, the Volhynian experiment of H. Józewski and the federalist tradition. |
| `integral_nationalism` | Endecja/OZON policies harden after 1937: minority schools closed, status of minority languages cut, emigrationist policy towards Jews (up to 1.2 %/yr), pressure on Germans, 25 k/yr settlers in the Kresy. | The trajectory of 1937-39 politics (the OZON programme, the 1938 destruction of Orthodox churches in Chełm, emigrationist diplomacy). |
| `forced_lithuanization` | Federation, but the Lithuanian unit keeps the Kaunas government's policy: Polish schools and parishes closed, strong registration pressure. | What actually happened in interwar Lithuania, including in the Lauda country. |
| `polonizing_union` | Unitary union: Polish is the dominant language in the Lithuanian lands too; Lithuanian schooling declines. | The nineteenth-century pattern in which Lithuanian-speaking gentry and townspeople drifted to Polish; a weakened national revival. |
| `wilno_lithuanian` | Federation with Vilnius as the Lithuanian capital: Lithuanian is the dominant language of the Wilno voivodeship. | The Lithuanian claim to Vilnius, resolved inside a federation. |
| `census_religion_corrected` | Baseline dynamics from a Tomaszewski-style religion-corrected 1931 starting point. | The census counted mother tongue, not nationality, and was politically shaped (see DATA_SOURCES). |
| `census_vernacular` | Baseline dynamics from the vernacular (1897-anchored) upper-bound starting point, including the 1897-based share of Polish speakers in Lithuania. | Imperial Russian native-language data. |
| `lt_polish_claim` | Baseline, but Lithuania starts with the Polish electoral committee's 1923 estimate of Poles (~10 %). | Contested Lithuanian census. |
| `finnish_path` | Fast convergence (kappa up to 0.88), larger infrastructure budgets, less emigration. | Finland and Austria: agrarian successor states that converged fast. |
| `stagnation` | Low convergence (kappa ~0.45), 1939 plans not executed, no Poland-A/B equalisation, heavy emigration. | Interwar Argentina and the Latin-American middle-income trap; the chronic 1930s budget constraint. |

## What scenarios do *not* vary

These are fixed across all scenarios:

* the peace itself: no other wars;
* the USSR and Germany as fixed neighbours;
* no change to the external borders except the union with Lithuania.

Parameter uncertainty (fertility and mortality transition speeds, the
language-shift propensities, migration elasticities, network appraisal) is
**not** a scenario. It is sampled in the Monte-Carlo ensembles.

## Writing your own

```yaml
extends: baseline
meta:
  name: my_scenario
  description: "..."
economy:
  kappa: [[1931, 0.55], [1960, 0.75], [2032, 0.80]]   # [[year, value], ...] schedules are interpolated
language:
  status_regions:
    POL: {uk: [[1931, 0.3], [1945, 0.6]]}                 # region-specific language status
  own_schooling:
    be: [[1931, 0.03], [1940, 0.5]]                       # share of Belarusian children in Belarusian schools
dominant_language: {default: pl, "LT_*": lt, NOW: be}     # a Belarusian autonomous unit
migration:
  jewish_channel: [[1931, 0.0035], [1945, 0.010], [1960, 0.002]]
infrastructure:
  enable_planned: false
```

Then run `python -m plsim run my_scenario` (or pass a path to the YAML).
