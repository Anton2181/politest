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
| `ukraine_autonomy_tricantonal` | From 1938: (1) a **Ukrainian autonomy** of the lwowskie, tarnopolskie and stanisławowskie voivodeships plus Volhynia, with Ukrainian schools and a Ukrainian university; the official language follows the district majority (Ukrainian east of the San, Polish in western lwowskie). (2) A **tri-cantonal Lithuania** (a Grand Duchy) holding everything east of the later Curzon line and north of Volhynia, in Lithuanian, Polish (Wilno–Lida–Grodno) and Belarusian (eastern Wilno lands, eastern Nowogródek, Polesie) cantons, each schooling its minorities. No forced Lithuanisation of the Lauda Poles; Polish settlement in the east stops. | The voivodeship self-government statute of 26 Sep 1922 for Lwów, Tarnopol and Stanisławów (passed, never implemented); the Hymans plan of 1921 for a two-canton Lithuania (Kaunas and Vilnius) in union with Poland; Belarusian national claims of 1918-20; the Moravian (1905) and Bukovinian (1910) compromises, which gave language rights by district majority. |
| `ukraine_autonomy_tricantonal_rc` | The same settlement, started from the religion-corrected 1931 census reading. | Many Catholic Belarusians and Greek-Catholic Ukrainians were recorded as Polish speakers in 1931. |

## Sub-regions, cantons and federal members

The 1931 voivodeships are too coarse for some settlements: the Curzon line
cuts białostockie, and a Belarusian canton would take eastern wileńskie but
not Wilno. A scenario can therefore split voivodeships along county lines:

```yaml
partition: [BIA, WIL, NOW, LWO]       # see plsim/data/subregions.py
members: {default: PL, "LT_*": GD-L, WIL.W: GD-P, WIL.E: GD-B, ...}
dominant_language: {default: pl, WIL.E: be, LWO.E: uk, ...}
migration:
  member_friction: {"PL|UA": 0.5, "GD-L|GD-P": 0.4, ...}
```

* **Splitting.** The voivodeship's 1931 reconstruction is downscaled to the
  7 km grid (county anchors + IPF), and each sub-region takes the people on
  its own cells and in its own towns. Sub-regions are named `PARENT.CHILD`
  and inherit every setting given for the parent unless one is given for
  them.
* **Members** are the units of the federation (Poland, the Ukrainian
  autonomy, each canton of the Grand Duchy). Migration between members is
  damped by `member_friction`. Pairs not listed get the baseline
  Poland-Lithuania factor (0.10). The listed values are assumptions:
  autonomy and cantons are closer than separate states, and pairs sharing a
  language are closer than others.

### Results: `ukraine_autonomy_tricantonal` (seeded run)

| Member | 1933 | 2032 | Home languages 1933 → 2032 |
|---|---|---|---|
| Poland (crown lands) | 20.1 M | 27.2 M | Polish 85 → 84 %, Yiddish 9 → 5 % |
| Ukrainian autonomy | 8.4 M | 10.9 M | Ukrainian 51 → 65 %, Polish 39 → 28 % |
| Lithuanian canton | 2.42 M | 2.18 M | Lithuanian 82 → 83 %, Polish 3.2 → 5.8 % |
| Polish canton (Wilno–Lida–Grodno) | 1.41 M | 2.01 M | Polish 67 → 63 %, Belarusian 16 → 22 % |
| Belarusian canton | 2.47 M | 5.51 M | Belarusian 27 → 49 %, West Polesian 29 → 20 %, Polish 31 → 24 % |

* **Belarusian** speakers number 3.8 M in 2032, against 1.4 M in the
  baseline. They come from Belarusian schooling, from West Polesian
  speakers shifting to Belarusian instead of Polish, and from high Polesian
  fertility.
* **Ukrainian** speakers number 8.7 M, against 8.2 M in the baseline.
  * Tarnopol turns from a Polish to a Ukrainian plurality (49/46 → 38/56).
  * Eastern lwowskie, with Lwów, goes from 45 to 50 % Ukrainian.
  * West of the San, Polish holds (77 → 60 %), and the Ukrainian minority
    grows from 13 to 30 %. Both halves of lwowskie lie in the autonomy and
    form one migration unit, so rural migrants from either half settle in
    the towns of both, Lwów included.
* **Lauda Poles** rise from 5 to 6 % of the Lauda unit (23 k → 27 k). In
  the baseline they end at 4 %. Under `forced_lithuanization` they fall to
  1.5 %, from 23 k to 6 k speakers.
* **Polish** falls to 59 % of the whole union, from 68 % in the baseline.

## County level

Two scenarios run on the counties (powiaty, apskritys; 270 regions)
instead of the 23 voivodeships (`plsim/data/counties.py`; method in
METHODOLOGY §12.6):

```yaml
extends: ukraine_autonomy_tricantonal
partition: counties
region_groups:                       # a canton or district made of counties
  WIL.W: [WIL.wilno, WIL.oszmiana, WIL.swieciany]
  WIL.E: [WIL.braslaw, WIL.glebokie, WIL.molodeczno, WIL.postawy, WIL.wilejka]
  ...
```

`region_groups` lets settings written for the named sub-regions (`WIL.E`,
`LWO.W`, ...) apply to a list of counties. A county code is
`PARENT.seat` (e.g. `LWO.przemysl`). A setting for the voivodeship
(`LWO`) applies to all its counties unless a group or a county overrides it.

### `baseline_counties`

The baseline at county level. It reproduces the voivodeship run (48.15 M
against 48.25 M in 2032; every voivodeship's language shares within about
a point) and adds where things happen. 34 counties change their plurality
language:

* Belarusian → Polish in Głębokie, Mołodeczno, Wilejka, Nieśwież,
  Nowogródek and Słonim.
* West Polesian → Polish in all nine Polesie counties.
* Kashubian → Polish in Kartuzy, Kościerzyna and Wejherowo.
* Ukrainian → Polish in nine Lwów counties (Bóbrka, Dobromil, Gródek,
  Jaworów, Lesko, Rawa Ruska, Sambor, Sokal, Żółkiew) and six Tarnopol
  counties (Borszczów, Brody, Brzeżany, Buczacz, Czortków, Kopyczyńce).
* German → Lithuanian in Klaipėda.

### `ukraine_autonomy_tricantonal_counties`

The cantons and the autonomy are the same counties as in the
voivodeship-level scenario. Each county now starts from its own 1931
make-up, and the canton populations come from the county census rather
than the grid. The Polish canton had 1.35 M people in 1933, against 1.41 M
from the grid approximation.

| Member | 1933 | 2032 | Home languages 1933 → 2032 |
|---|---|---|---|
| Poland (crown lands) | 20.1 M | 27.3 M | Polish 85 → 83 %, Yiddish 9 → 5 % |
| Ukrainian autonomy | 8.4 M | 10.8 M | Ukrainian 51 → 65 %, Polish 39 → 28 % |
| Lithuanian canton | 2.42 M | 2.17 M | Lithuanian 82 → 82 %, Polish 3.2 → 5.9 % |
| Polish canton | 1.35 M | 1.89 M | Polish 67 → 64 %, Belarusian 15 → 20 % |
| Belarusian canton | 2.56 M | 5.69 M | Belarusian 29 → 48 %, West Polesian 28 → 19 %, Polish 31 → 25 % |

The member totals agree with the voivodeship-level scenario. The county
level shows where the shift happens:

* **Ukrainian autonomy.** Polish leads 25 of its 66 counties in 1933 and
  12 in 2032. Thirteen turn Ukrainian:
  * Tarnopol, Trembowla, Zbaraż, Zborów, Złoczów, Skałat, Podhajce,
    Przemyślany and Kamionka Strumiłowa;
  * Drohobycz, Lubaczów, Mościska and Rudki.

  The Polish-plurality counties left are those west of the San
  (Jarosław, Przemyśl, Sanok, Rzeszów ...) and Lwów itself. In the
  baseline, six Tarnopol counties go the other way, from Ukrainian to
  Polish.
* **Belarusian canton.** Belarusian leads 6 of its 20 counties in 1933 and
  18 in 2032. All nine Polesie counties pass from West Polesian to
  Belarusian, and Postawy, Baranowicze and Stołpce from Polish. Brasław
  and Wołożyn stay Polish-plurality.
* **Polish canton.** All seven counties stay Polish-plurality.

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
