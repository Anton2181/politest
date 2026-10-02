# Scenarios

Every scenario shares the premise: **no Second World War**. There is no
German-Soviet partition, no Holocaust, no deportations, no post-1945 border
shifts or population transfers, and no communist regime. Everything else that
cannot be measured is a scenario choice. Scenarios are YAML files in
`scenarios/`. A scenario can `extends:` another one and overrides only the
parameters it names. A mapping containing `_replace: true` replaces the parent
mapping instead of being merged into it.

All scenarios run at **county level** (270 regions; 211 for Wakar's
Poland-Belarus) and start from the **research estimate of 1931**, not the census as printed: Tomaszewski's
(1985) correction for Poland and ~150 k Poles in Lithuania. The exceptions
are `census_official` and `census_vernacular`, which start from the printed
censuses and from the upper bound (see `docs/DATA_SOURCES.md`).

| Scenario | What changes | Why it is plausible |
|---|---|---|
| `baseline` | Polish-Lithuanian **federation**: Lithuania and Klaipėda form a unit with Lithuanian as its state language and Polish as the federal language, co-official in Lithuania (status and schools for its speakers). Sanacja-style assimilation pressure eases after 1950. The 1939 plans are executed. Southern-European convergence (kappa 0.55 -> 0.70). | The federal idea (Piłsudski's *Międzymorze*) was the main alternative to the incorporation of Wilno. 1930s policy was assimilationist but not genocidal. Catholic agrarian peripheries without communism (Spain, Portugal, Italy's South) are the natural comparators. |
| `ii_rp_only` | The Second Republic alone, in its 1938 borders. Lithuania is a foreign state; the Vilnius-Kaunas links stay cut. | The literal "surviving interwar Poland". |
| `federal_autonomy` | Ukrainian territorial autonomy with Ukrainian as the regional state and school language in Stanisławów, Tarnopol and Volhynia, Polish co-official. Belarusian schooling. Equal Lithuanian status. Lower pressure. | The 1938 Ukrainian autonomy proposals, the Volhynian experiment of H. Józewski and the federalist tradition. |
| `integral_nationalism` | Endecja/OZON policies harden after 1937: minority schools closed, status of minority languages cut, emigrationist policy towards Jews (up to 1.2 %/yr), pressure on Germans, 25 k/yr settlers in the Kresy. | The trajectory of 1937-39 politics (the OZON programme, the 1938 destruction of Orthodox churches in Chełm, emigrationist diplomacy). |
| `polonizing_union` | Unitary union: Polish is the dominant language in the Lithuanian lands too; Lithuanian schooling declines. | The nineteenth-century pattern in which Lithuanian-speaking gentry and townspeople drifted to Polish; a weakened national revival. |
| `census_official` | Baseline dynamics started from the 1931 Polish and 1923 Lithuanian censuses as printed. | Shows what the printed census, taken at face value, implies. |
| `census_vernacular` | Baseline dynamics from the upper bound for minority speech: Kubijovyč's (1983) Latin-rite Ukrainians and Catholic Belarusian speech at 1897 proportions, plus the 1897-based share of Polish speakers in Lithuania. | Ukrainian-side estimates and imperial Russian native-language data. |
| `ukraine_autonomy_tricantonal` | From 1938: (1) a **Ukrainian autonomy** of the lwowskie, tarnopolskie and stanisławowskie voivodeships plus Volhynia, with Ukrainian schools and a Ukrainian university; the official language follows the district majority (Ukrainian east of the San, Polish in western lwowskie). (2) A **tri-cantonal Lithuania** (a Grand Duchy) holding everything east of the later Curzon line and north of Volhynia, in Lithuanian, Polish (Wilno–Lida–Grodno) and Belarusian (eastern Wilno lands, eastern Nowogródek, Polesie) cantons, each schooling its minorities. Polish is co-official in the autonomy and in every canton. No forced Lithuanisation of the Lauda Poles; Polish settlement in the east stops. | The voivodeship self-government statute of 26 Sep 1922 for Lwów, Tarnopol and Stanisławów (passed, never implemented); the Hymans plan of 1921 for a two-canton Lithuania (Kaunas and Vilnius) in union with Poland; Belarusian national claims of 1918-20; the Moravian (1905) and Bukovinian (1910) compromises, which gave language rights by district majority. |
| `autonomy_grand_duchy_coofficial` | From 1938: the Ukrainian autonomy above, and an **autonomous Grand Duchy of Lithuania** over the same lands as the cantons, but undivided, with **Lithuanian, Polish and Belarusian co-official** throughout (Polish is co-official in the Ukrainian autonomy too). Each county works in whichever of the three had most speakers in 1931 (West Polesian counting with Belarusian). | The Grand Duchy's own tradition (Ruthenian, Polish and Latin as chancery languages); Finland's Finnish-Swedish and Switzerland's multilingual cantons. |
| `wakar_poland` | **Wakar's Poland**: Poland alone, **without Volhynia, Stanisławów and Tarnopol**, and without the lands Lithuania claimed under the 1920 Soviet-Lithuanian treaty (Wilno-Troki, Święciany, Oszmiana, Brasław, Postawy, Lida, Szczuczyn, Grodno counties). In what remains, **Polish and Belarusian are co-official**. No military settlement. | A Poland that came out of 1919–21 with a more ethnographic eastern border, leaving Volhynia and the Ukrainian core of Galicia to a Ukrainian state and the Vilnius region to Lithuania, and that accommodated its Belarusians. Named after Włodzimierz Wakar (1885–1933), whose ethnographic studies of the Polish lands (*Rozwój terytorialny narodowości polskiej*, 1917–18) argued for borders drawn on where Poles lived. |
| `wakar_poland_belarus` | **Wakar's Poland-Belarus**: Wakar's Poland together with **all of Soviet Belarus** (the BSSR of 1926: Mińsk, Witebsk, Mohylew, Homel), as four more voivodeships. Polish and Belarusian co-official throughout; each county works in whichever of the two had more speakers in 1931. Soviet Belarus starts from the 1926 Soviet census (METHODOLOGY §12.7). | A Riga peace that gave Poland the Belarusian lands it held in 1919–20 (Mińsk was Polish-held from August 1919 to July 1920) instead of Volhynia and eastern Galicia: a Polish-Belarusian state. |
| `no_official_language` | Poland with **no official language**, i.e. all languages official: equal status and schools in every language. Each county's working language is its largest of Polish, Ukrainian and Belarusian. Low assimilation pressure; no settlement. Lithuania as in the baseline, with Polish co-official. | A civic, linguistically neutral state (in the spirit of the 1921 March Constitution's minority clauses, taken much further). |

## Counties, cantons and federal members

Every scenario runs on the 270 counties (1931 powiaty and Lithuanian
apskritys; `plsim/data/counties.py`, method in METHODOLOGY §12.6). A
canton, an autonomy or a language district is a list of counties:

```yaml
region_groups:                       # named lists of counties
  WIL.W: [WIL.wilno, WIL.oszmiana, WIL.swieciany]
  WIL.E: [WIL.braslaw, WIL.glebokie, WIL.molodeczno, WIL.postawy, WIL.wilejka]
members: {default: PL, "LT_*": GD-L, WIL.W: GD-P, WIL.E: GD-B, LWO: UA, ...}
dominant_language: {default: pl, WIL.E: be, LWO.E: uk, POL: "auto:pl,be+pls"}
official_languages: {WIL: [lt, pl, be]}
exclude: [WOL, STA, TAR]
migration:
  member_friction: {"PL|UA": 0.5, "GD-L|GD-P": 0.4}
```

* **Codes.** A county is `PARENT.seat` (e.g. `LWO.przemysl`). A setting for
  a voivodeship (`LWO`) applies to all its counties unless a group or a
  county overrides it. A `region_groups` name can be used wherever a region
  code can.
* **Members** are the units of the federation (Poland, the Ukrainian
  autonomy, each canton of the Grand Duchy). Migration between members is
  damped by `member_friction`. Pairs not listed get the baseline
  Poland-Lithuania factor (0.10). The listed values are assumptions:
  autonomy and cantons are closer than separate states, and pairs sharing a
  language are closer than others.
* **Contact and official languages.**
  * `dominant_language` is the contact language: the one bilinguals learn
    and the default target of shift. `auto:pl,be+pls` picks, county by
    county, whichever listed language had most speakers in 1931 (`be+pls`
    counts West Polesian with Belarusian).
  * `official_languages` gives languages official status (`official_status`,
    a floor on their status), schools in them for their own speakers
    (`official_schooling`), and lets speakers of other languages shift to
    any of them. `all` makes every language official.
* **Territory.** `exclude` drops counties or groups from the state. The
  maps draw them as foreign land.
* **Voivodeship mode.** `partition: []` runs the 23-voivodeship model
  instead (20 s rather than 4 minutes). There `partition: [BIA, WIL, NOW,
  LWO]` splits those voivodeships along county lines via the 7 km model grid
  (`plsim/data/subregions.py`).

The results below are single seeded runs, from the research start of 1931.
Shares are of home languages.

### Results: `baseline`

34 of 270 counties change their plurality language by 2032, all of them
towards Polish except Klaipėda (German to Lithuanian):

* Belarusian → Polish in 12: Grodno, Wołkowysk, Bielsk Podlaski, Głębokie,
  Mołodeczno, Postawy, Wilejka, Baranowicze, Nieśwież, Nowogródek, Słonim,
  Stołpce.
* West Polesian → Polish in all nine Polesie counties. Polesie goes from
  12 to 63 % Polish.
* Kashubian → Polish in Kartuzy, Kościerzyna and Wejherowo.
* Ukrainian → Polish in eight Lwów counties (Dobromil, Drohobycz, Gródek,
  Lesko, Lubaczów, Rudki, Sambor, Sokal) and Kamionka Strumiłowa.

The Lithuanian units' Poles fall from 152 k to 127 k, and the Lauda Poles
from 54 k to 38 k, although Polish is co-official in Lithuania (without
that status they fall to 120 k and 36 k).

### Results: `ukraine_autonomy_tricantonal`

| Member | 1933 | 2032 | Home languages 1933 → 2032 |
|---|---|---|---|
| Poland (crown lands, 154 counties) | 20.1 M | 27.2 M | Polish 84 → 81 %, Yiddish 9 → 5 %, Ukrainian 2 → 8 % |
| Ukrainian autonomy (66) | 8.4 M | 10.8 M | Ukrainian 55 → 68 %, Polish 35 → 25 % |
| Lithuanian canton (23) | 2.42 M | 2.17 M | Lithuanian 78 → 79 %, Polish 6 → 8 % |
| Polish canton (Wilno–Lida–Grodno, 7) | 1.35 M | 1.91 M | Polish 58 → 52 %, Belarusian 23 → 32 % |
| Belarusian canton (20) | 2.56 M | 5.82 M | Belarusian 36 → 55 %, West Polesian 28 → 19 %, Polish 23 → 17 % |

* **Belarusian** speakers number 4.6 M in 2032, against 1.9 M in the
  baseline. They come from Belarusian schooling, from West Polesian
  speakers shifting to Belarusian instead of Polish, and from high Polesian
  fertility. Belarusian leads 9 of the canton's 20 counties in 1933 and 19
  in 2032: the nine Polesie counties, plus Wołożyn from Polish. Only
  Brasław stays Polish.
* **Ukrainian** speakers number 9.7 M, against 9.1 M in the baseline.
  Ukrainian leads 49 of the autonomy's 66 counties in 1933 and 56 in 2032.
  * Seven turn from Polish to Ukrainian: Lwów, Mościska, Przemyśl,
    Przemyślany, Skałat, Tarnopol and Trembowla.
  * The ten Polish-plurality counties left are all west of the San
    (Jarosław, Rzeszów, Sanok, Krosno ...).
  * Tarnopol voivodeship goes from 42 % Polish and 53 % Ukrainian to 32 and
    62 %; eastern lwowskie from 52 to 55 % Ukrainian.
  * West of the San, Polish falls from 79 to 58 % and Ukrainian rises from
    12 to 32 %. Both halves of lwowskie lie in the autonomy and form one
    migration unit, so rural migrants from either half settle in the towns
    of both.
* **In the crown lands**, Ukrainian rises from 0.26 M to 2.0 M speakers:
  the Chełm and Podlasie Ukrainians of Lublin (232 k → 740 k) and migrants
  to Warsaw, Silesia and Łódź. The baseline shows the same.
* **Lithuanian Poles** rise from 153 k to 178 k; the Lauda Poles go from 54 k
  to 49 k (10 → 11 % of a shrinking Lauda). In the baseline they end at
  38 k.
* **Polish** falls to 55.8 % of the whole union, against 64.6 % in the
  baseline. Wilno county grows to 551 k (803 k in the baseline), as the
  capital of a canton rather than of a large Polish province.

### Results: `autonomy_grand_duchy_coofficial`

The same Ukrainian autonomy, with an undivided Grand Duchy of 50 counties
working in Lithuanian, Polish and Belarusian. In 1933, Lithuanian leads 22
of its counties, Belarusian 11 (Grodno and Wołkowysk among them), Polish 7
and West Polesian 9.

| Grand Duchy | 1933 | 2032 |
|---|---|---|
| Population | 6.33 M | 10.01 M |
| Belarusian | 19.5 % | 38.8 % |
| Polish | 24.2 % | 22.2 % |
| Lithuanian | 31.1 % | 17.8 % |
| West Polesian | 11.3 % | 11.7 % |
| Yiddish | 8.0 % | 2.8 % |

* **Belarusian** becomes the Duchy's largest language (3.9 M speakers). It
  leads 23 counties in 2032: the nine Polesie counties, plus Lida,
  Szczuczyn and Wołożyn, which turn from Polish.
* **Polish** holds its share. It leads four counties (Wilno, Oszmiana,
  Święciany, Brasław) and spreads in the Lithuanian lands: their Poles grow
  from 154 k to 347 k, the Lauda Poles from 54 k to 80 k.
* **Lithuanian** keeps the plurality in its 23 counties, but the Lithuanian
  lands become mixed: Kaunas falls from 64 to 51 % Lithuanian, Žemaitija
  from 88 to 75 %. Migrants from the fast-growing east keep Belarusian,
  which is official there too, and Polish gains Lithuanian speakers. The
  number of Lithuanian speakers in the union (2.1 M) is about the same as
  in the baseline.
* **Against the cantons:** one Duchy with free movement and three languages
  everywhere spreads Polish and Belarusian into the Lithuanian lands. The
  cantons keep each language's core (the Lithuanian canton is 80 %
  Lithuanian in 2032).

### Results: `wakar_poland` (Wakar's Poland)

Poland without Volhynia, Stanisławów, Tarnopol and the Vilnius region has
199 counties and 25.7 M people in 1933, 32.7 M in 2032. Belarusian is the
working language of 19 of them: Polesie, eastern Nowogródek, Głębokie,
Mołodeczno, Wilejka, Wołkowysk and Bielsk.

* **Belarusian** grows from 1.1 M speakers (4.2 %) to 4.1 M (12.5 %). It
  leads 19 counties in 2032: the nine Polesie counties pass from West
  Polesian, Wołożyn from Polish, and Bielsk turns Polish. Polesie goes from
  7 to 45 % Belarusian (West Polesian 62 → 26 %, Polish 11 → 17 %).
* **Polish** goes from 73.9 to 70.1 % of the state.
* **Ukrainian** (lwowskie and Lublin, 6.4 %) has no official status here.
  Nine Lwów counties turn Polish as in the baseline, and Ukrainian falls
  from 37 to 30 % in lwowskie. It rises in Lublin (9 → 15 %).
* **Lwów** is a border city: its county grows from 459 k to 714 k, against
  840 k in the baseline.

### Results: `no_official_language`

* **Shares of the union in 2032:** Polish 54.0 % (64.6 % in the baseline),
  Ukrainian 21.1 %, Belarusian 9.2 % (4.4 M), Yiddish 5.4 % (2.6 M, against
  1.9 M), West Polesian 3.2 % (1.5 M). About 5 M more people speak a
  minority language at home than in the baseline.
* **Only 18 counties change their plurality language**, the fewest of any
  scenario:
  * Tarnopol, Trembowla, Skałat and Przemyślany turn Ukrainian;
  * Lida and Wołożyn turn Belarusian;
  * six Polesie counties go from West Polesian to Belarusian. Drohiczyn,
    Kamień Koszyrski and Stolin stay West Polesian.
* **Shift still happens**, towards whichever language is large locally.
  Volhynia goes from 69 to 77 % Ukrainian, Nowogródek from 52 to 60 %
  Belarusian, and Polesie from 7 to 35 % Belarusian (63 % Polish in the
  baseline). Towns and the west still pull towards Polish.
* **Migrants** keep their languages longer without assimilation pressure.
  Warsaw voivodeship is 14 % Ukrainian-speaking in 2032, Silesia 9 %.

### Results: `wakar_poland_belarus` (Wakar's Poland-Belarus)

Wakar's Poland plus Soviet Belarus has 211 counties and 31.1 M people in
1933 (5.4 M of them in Soviet Belarus), and 49.4 M in 2032.

| | 1933 | 2032 |
|---|---|---|
| Population | 31.1 M | 49.4 M |
| Polish | 61.1 % | 48.1 % |
| Belarusian | 17.0 % | 36.3 % (18.0 M speakers) |
| Ukrainian | 5.4 % | 4.8 % |
| Yiddish | 8.3 % | 3.8 % |
| West Polesian | 2.3 % | 2.2 % |
| Soviet Belarus: population | 5.4 M | 13.5 M |
| Soviet Belarus: Belarusian / Russian / Polish | 77 / 13 / 0.8 % | 84 / 8 / 4 % |

* **A Polish-Belarusian state.** Belarusian leads 31 counties in 2032 (22 in
  1933): all of Soviet Belarus, Polesie, eastern Nowogródek with Wołożyn,
  Wołkowysk and Głębokie–Mołodeczno–Wilejka.
* **Soviet Belarus** grows from 5.4 M to 13.5 M people under Polish-north-
  eastern vital rates. Russian, the language of its towns in 1926, falls from
  13 to 8 % as Belarusian and Polish (both official) take over. Polish rises
  from under 1 % to 4 %, mainly in the towns.
* **Polesie** goes from West Polesian (62 %) to Belarusian (50 %), as in
  Wakar's Poland.
* **Migration** carries Belarusian west. Warsaw city is 20 % Belarusian-
  speaking in 2032 and Lublin 6 %. This is probably too high: migrants keep
  their language in the model unless regional shift moves them (see
  `docs/ROADMAP.md`).
* **Lwów** grows from 458 k to 754 k.

## The equal-exchange Curzon line

The atlas overlay "Curzon line" (magenta; method in METHODOLOGY §12.8)
draws, for every 5-year frame, a continuous line across the whole state
(Lithuania and Soviet Belarus included where they are part of it), from one
point of its border to another. The line may wind cell by cell through
counties, and each side is in one piece. It leaves as many non-Poles on its
Polish side as Poles on its other side, with the most Poles on the Polish
side. Poles are speakers of Polish at home; Kashubians, Wymysorys speakers,
Germans and Jews (4.4 M in 1932) are not counted.

| Scenario | 1932: moved each way | 2032: moved each way |
|---|---|---|
| baseline | 1.89 M | 5.16 M |
| ii_rp_only | 1.76 M | 5.03 M |
| federal_autonomy | 1.89 M | 5.31 M |
| integral_nationalism | 1.89 M | 4.86 M |
| polonizing_union | 1.89 M | 5.22 M |
| census_official | 1.79 M | 5.86 M |
| census_vernacular | 1.64 M | 5.26 M |
| ukraine_autonomy_tricantonal | 1.89 M | 3.83 M |
| autonomy_grand_duchy_coofficial | 1.89 M | 3.90 M |
| no_official_language | 1.90 M | 4.51 M |
| wakar_poland | 0.90 M | 2.49 M |
| wakar_poland_belarus | 0.92 M | 3.74 M |

"Moved each way" is the number of non-Poles left on the Polish side, equal
to the number of Poles left on the other side. In 1932 the Polish side of
the baseline is 91 % Polish; in 2032, 83 %.

* **1932, union scenarios.**
  * Lithuania, the Belarusian lands (Grodno, Nowogródek, Polesie),
    Volhynia, Tarnopol and Stanisławów are on the other side.
  * The Polish-speaking Wilno lands stay on the Polish side, joined to it
    by a strip along Lithuania's frontier.
  * So does Lwów, through a corridor from the San.
* **Over the century** the Polish side spreads east as Polesie and the
  north-east shift to Polish. The line winds around the Belarusian and
  Ukrainian islands left there, and the exchange grows to 5.2 M, because
  both sides grow more mixed.
* **With the autonomies**, Belarusian and Ukrainian schooling slow the
  shift to Polish in the east, and the exchange grows less (3.8-3.9 M).
* **Wakar's Poland** starts with the smallest exchange (0.9 M).
* **The straight line** is a poorer answer to the same question: an earlier
  version that allowed only straight lines needed 2.75 M each way in 1932.

## What scenarios do *not* vary

These are fixed across all scenarios:

* the peace itself: no other wars;
* the USSR and Germany as fixed neighbours;
* the external borders of 1932, except for the union with Lithuania, the
  lands the two Wakar scenarios leave out, and Soviet Belarus in
  `wakar_poland_belarus`.

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
