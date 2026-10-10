# Scenarios

Every scenario but one shares the premise: **no Second World War**. There is
no German-Soviet partition, no Holocaust, no deportations, no post-1945
border shifts or population transfers, and no communist regime. Everything
else that cannot be measured is a scenario choice. The exception is
`historical`, which replays the real century for calibration (below). Scenarios are YAML files in
`scenarios/`. A scenario can `extends:` another one and overrides only the
parameters it names. A mapping containing `_replace: true` replaces the parent
mapping instead of being merged into it.

All scenarios run at **county level** (271 regions; 212 for Wakar's
Poland-Belarus, 290 and 276 for the Northwestern Krai and Lit-Bel, with
the pieces of the counties cut along the governorates) and start from the
**research estimate of 1931**, not the census as printed: Tomaszewski's
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
| `nw_krai` | **Poland and the Northwestern Krai.** Poland without the lands of the six "north-western" governorates of the Russian Empire in their **borders of 1897** (Vilna, Kovno, Grodno, Minsk, Mogilev, Vitebsk), which form a **separate state** simulated in the same run, **with its own economy** (national income, emigration, transport budget). The krai holds Lithuania without Klaipėda (Prussian) and Palanga (Courland); the north-east of 1931 Poland; the whole BSSR; and the governorates' land outside the 1932 states: **Latgale** (Latvia), **Nevel, Sebezh and Velizh**, and the eastern edge of the Mogilev governorate (RSFSR), from the 1897 census. Counties that straddle a governorate border are cut along it. **Suvalkija** (Suwałki governorate, part of the Kingdom of Poland) **goes to Poland** with Suwałki and Augustów, Lithuanian co-official there. In the krai Lithuanian, Belarusian, Polish, Yiddish and Russian are official (and Latvian in Latgale); each county works in its largest of Lithuanian, Polish, Belarusian (with West Polesian), Latvian and Russian; pressure is low (0.6). Migration across the border is international (friction 0.03); Polish settlement goes to Volhynia only. | The Northwestern Krai (Северо-Западный край) of 1794-1915; the Belarusian and Lithuanian national projects of 1918-19, had they not been partitioned. |
| `lit_bel` | **Poland and Lit-Bel.** The same, in the borders the Lithuanian-Belorussian republic claimed in 1919: the **five governorates of Vilna, Kovno, Grodno, Minsk and Suwałki** (1897 borders). Lit-Bel takes the Polish Suwałki and Augustów counties and the Minsk-governorate part of the BSSR (okrugs cut along the Minsk governorate's border); the Mogilev and Vitebsk lands are left out as Soviet territory, and so are Klaipėda and Palanga. Own economy, languages and policy as in `nw_krai`. | Litbel (February-July 1919), whose capital was Vilnius and whose five governorates were Vilna, Grodno, Kovno, Suwałki and Minsk. |
| `plebiscite_poland` | **Plebiscite Poland.** The baseline federation, with every plebiscite of 1920-21 won and Danzig given to Poland: Upper Silesia (RB Oppeln without Neisse, Grottkau and Falkenberg), the Allenstein area (Allenstein, Rößel and Masuria with Oletzko), the Marienwerder area east of the Vistula, Cieszyn Silesia west of the Olza, Upper Orava and Zamagurie, and the Free City (German co-official there). 2.9 M more people in 1932, about 1.9 M of them German speakers and 0.6 M speakers of Upper Silesian, Masurian, Warmian or Goral Polish (`plsim/data/west.py`, METHODOLOGY §12.9). | The Polish case at Versailles and Spa: Danzig as Poland's port, the plebiscite areas where Polish speech was strong (eastern Upper Silesia voted 60 % for Poland in places; Masuria and Warmia spoke Polish at home; Cieszyn Silesia was Polish-speaking west of the Olza). |
| `historical` | **Historical Poland (calibration).** The real century: the 1931 state with the German land of 1945 (a separate German state until then) and Danzig; the war, the Holocaust and occupation deaths; the border change of 1945 (the east to a Soviet state that stays in the run); flight and expulsion of the Germans, repatriation, settlement of the west, the transfer of the Ukrainians and Operation Vistula; People's Poland's economy (Maddison), mortality, pro-natalism, emigration regime and policy; after 1989 the German minority and the Silesian identity. Compared with the censuses of 1946-2021 (`plsim/history_check.py`, METHODOLOGY §12.10). | Not a counterfactual: a test of the shared behaviour (fertility, mortality, migration, language and identity) against what happened. |

## Counties, cantons and federal members

Every scenario runs on the 271 counties (1931 powiaty and Lithuanian
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

34 of 271 counties change their plurality language by 2032, all of them
towards Polish except Klaipėda (German to Lithuanian):

* Belarusian → Polish in 12: Grodno, Wołkowysk, Bielsk Podlaski, Głębokie,
  Mołodeczno, Postawy, Wilejka, Baranowicze, Nieśwież, Nowogródek, Słonim,
  Stołpce.
* West Polesian → Polish in all nine Polesie counties. Polesie goes from
  11 to 69 % Polish.
* Kashubian → Polish in Kartuzy, Kościerzyna and Wejherowo.
* Ukrainian → Polish in seven Lwów counties (Drohobycz, Gródek, Lubaczów,
  Mościska, Przemyśl, Rudki, Sambor), Kamionka Strumiłowa and Tomaszów
  Lubelski.

The Lithuanian units' Poles slip from 148 k to 142 k and the Lauda Poles
from 57 k to 52 k, with Polish co-official in Lithuania. Polish *identity*
there falls from 75 k to 55 k: under the Lithuanian state's pull, Polish
speakers take a Lithuanian identity before they change language (§6.7 of
the methodology).

**Migrants' children assimilate** (the diaspora term, calibrated on
second-generation immigrants). Warsaw city ends 6 % Ukrainian-speaking and
Silesia 4 %. A steady stream of first-generation migrants keeps these
shares from falling further.

**Identity and language.** In 2032 Polish is both the home language and
the identity of 72 %. Those who switch to Polish often keep a Ukrainian,
Belarusian or Jewish identity, but with the pull of the state nation
calibrated on the 2002 census (METHODOLOGY §6.7) a minority language
without status or schools anchors its speakers' identity less: Belarusian
identity (2.0 %) falls below Belarusian speech (2.4 %). Jewish identity
(6.0 %) outlasts Yiddish (3.9 %). "Local" identities fall from 2.8 to 0.9 %
as nation-building turns Polesians and Belarusian speakers Belarusian,
Ukrainian or Polish.

### Results: `ukraine_autonomy_tricantonal`

| Member | 1933 | 2032 | Home languages 1933 → 2032 |
|---|---|---|---|
| Poland (crown lands, 155 counties) | 20.1 M | 31.1 M | Polish 84 → 86 %, Yiddish 9 → 5 %, Ukrainian 1 → 4 % |
| Ukrainian autonomy (66) | 8.4 M | 10.5 M | Ukrainian 56 → 65 %, Polish 34 → 29 % |
| Lithuanian canton (23) | 2.42 M | 2.82 M | Lithuanian 79 → 85 %, Polish 6 → 7 % |
| Polish canton (Wilno–Lida–Grodno, 7) | 1.35 M | 1.90 M | Polish 59 → 61 %, Belarusian 22 → 25 % |
| Belarusian canton (20) | 2.56 M | 4.36 M | Belarusian 35 → 54 %, West Polesian 28 → 16 %, Polish 24 → 22 % |

* **Belarusian** speakers number 3.38 M in 2032, against 1.22 M in the
  baseline. They come from Belarusian schooling, from West Polesian
  speakers shifting to Belarusian instead of Polish, and from high Polesian
  fertility. Belarusian leads 9 of the canton's 20 counties in 1933 and 19
  in 2032: the nine Polesie counties, plus Wołożyn from Polish. One county
  stays Polish.
* **Ukrainian** speakers number 8.3 M, against 7.2 M in the baseline.
  Ukrainian leads 51 of the autonomy's 66 counties in 1933 and 56 in 2032.
  * Five turn from Polish to Ukrainian: Lwów, Przemyślany, Skałat,
    Tarnopol and Trembowla.
  * The ten Polish-plurality counties left are all on or west of the San
    (Jarosław, Rzeszów, Sanok, Krosno ...).
  * Tarnopol voivodeship goes from 41 % Polish and 54 % Ukrainian to 32 and
    63 %; lwowskie as a whole from 40 to 49 % Ukrainian.
  * In those ten counties, Polish falls from 82 to 63 % and Ukrainian rises
    from 8 to 28 %. Both halves of lwowskie lie in the autonomy and form one
    migration unit, so rural migrants from either half settle in the towns
    of both.
* **In the crown lands**, Ukrainian rises from 1 to 4 % of speakers: the
  Chełm and Podlasie Ukrainians of Lublin (9 → 12 % of the voivodeship)
  and migrants to Warsaw, Silesia and Łódź. The baseline shows the same,
  slightly weaker.
* **Lithuanian Poles** rise from 149 k to 204 k; the Lauda Poles from 57 k
  to 65 k. In the baseline they slip to 142 k and 52 k.
* **Polish** falls to 63.5 % of the whole union, against 71.6 % in the
  baseline. Wilno county grows to 582 k (872 k in the baseline), as the
  capital of a canton rather than of a large Polish province.

### Results: `autonomy_grand_duchy_coofficial`

The same Ukrainian autonomy, with an undivided Grand Duchy of 50 counties
working in Lithuanian, Polish and Belarusian. In 1933, Lithuanian leads 22
of its counties, Belarusian 11 (Grodno and Wołkowysk among them), Polish 7
and West Polesian 9.

| Grand Duchy | 1933 | 2032 |
|---|---|---|
| Population | 6.33 M | 9.15 M |
| Belarusian | 19 % | 32 % |
| Polish | 24 % | 26 % |
| Lithuanian | 31 % | 26 % |
| West Polesian | 11 % | 8 % |
| Yiddish | 8 % | 3 % |

* **Belarusian** becomes the Duchy's largest language (2.9 M speakers). It
  leads 21 counties in 2032: the nine Polesie counties, plus Wołożyn, which
  turns from Polish.
* **Polish** holds its share. It leads six counties and spreads in the
  Lithuanian lands: their Poles grow from 150 k to 402 k (Polish identity
  from 76 k to 232 k), the Lauda Poles from 57 k to 103 k. Wilno county
  grows to 822 k and falls from 73 to 59 % Polish, with Belarusian from 3
  to 25 %.
* **Lithuanian** keeps the plurality in its 23 counties, but the Lithuanian
  lands become mixed: Kaunas and the north-east fall from 74 to 66 %
  Lithuanian, Samogitia from 87 to 82 %. Migrants from the fast-growing
  east keep Belarusian, which is official there too, and Polish gains
  Lithuanian speakers. The number of Lithuanian speakers in the union
  (2.65 M) is the same as in the baseline (2.64 M).
* **Against the cantons:** one Duchy with free movement and three languages
  everywhere spreads Polish and Belarusian into the Lithuanian lands. The
  cantons keep each language's core (the Lithuanian canton is 84 %
  Lithuanian in 2032).

### Results: `wakar_poland` (Wakar's Poland)

Poland without Volhynia, Stanisławów, Tarnopol and the Vilnius region has
200 counties and 25.7 M people in 1933, 35.8 M in 2032. Belarusian is the
working language of 19 of them: Polesie, eastern Nowogródek, Głębokie,
Mołodeczno, Wilejka, Wołkowysk and Bielsk.

* **Belarusian** grows from 1.05 M speakers (4.1 %) to 2.9 M (8.2 %). It
  leads 18 counties in 2032 (10 in 1933): the nine Polesie counties pass
  from West Polesian, Wołożyn from Polish, and Bielsk and Wołkowysk turn
  Polish. Polesie goes from 7 to 44 % Belarusian (West Polesian 62 → 25 %,
  Polish 11 → 21 %).
* **Polish** goes from 73.6 to 78.3 % of the state.
* **Ukrainian** (lwowskie and Lublin, 6.2 %) has no official status here.
  Eleven Lwów counties turn Polish, four more than in the baseline
  (Dobromil, Lesko, Sokal and Żółkiew), and Tomaszów Lubelski; Ukrainian
  falls from 40 to 32 % in lwowskie and stays at 9 % in Lublin.

### Results: `no_official_language`

* **Shares of the union in 2032:** Polish 61.3 % (71.6 % in the baseline),
  Ukrainian 16.9 %, Belarusian 6.4 % (3.2 M), Yiddish 5.4 % (2.7 M, against
  2.0 M), West Polesian 2.0 % (1.0 M). About 5 M more people speak a
  minority language at home than in the baseline.
* **Only 18 counties change their plurality language** (34 in the
  baseline):
  * Tarnopol, Trembowla, Skałat and Przemyślany turn Ukrainian, and
    Tomaszów Lubelski Polish;
  * Wołożyn turns Belarusian; Bielsk Podlaski and Grodno turn Polish;
  * five Polesie counties go from West Polesian to Belarusian and Kobryń
    to Ukrainian. Drohiczyn, Kamień Koszyrski and Łuniniec stay West
    Polesian;
  * the three Kashubian counties turn Polish, and Klaipėda Lithuanian.
* **Shift still happens**, towards whichever language is large locally.
  Polesie goes from 7 to 34 % Belarusian (69 % Polish in the baseline).
  Towns and the west still pull towards Polish.
* **Migrants** keep their languages longer: their languages are official
  everywhere, so a city's Ukrainian or Belarusian community soon counts as
  complete and the diaspora term weakens. Warsaw city is 10 %
  Ukrainian-speaking in 2032 (6 % in the baseline) and 4 % Belarusian;
  Silesia 6 % Ukrainian.

### Results: `wakar_poland_belarus` (Wakar's Poland-Belarus)

Wakar's Poland plus Soviet Belarus has 212 counties and 31.1 M people in
1933 (5.4 M of them in Soviet Belarus), and 48.2 M in 2032.

| | 1933 | 2032 |
|---|---|---|
| Population | 31.1 M | 48.2 M |
| Polish | 60.9 % | 60.3 % |
| Belarusian | 16.9 % | 26.7 % (12.9 M speakers) |
| Ukrainian | 5.2 % | 3.9 % |
| Yiddish | 8.3 % | 4.1 % |
| West Polesian | 2.3 % | 1.5 % |
| Soviet Belarus: population | 5.4 M | 9.5 M |
| Soviet Belarus: Belarusian / Russian / Polish | 77 / 13 / 0.8 % | 83 / 8 / 5 % |

* **A Polish-Belarusian state.** Belarusian leads 31 counties in 2032 (22 in
  1933): all of Soviet Belarus, Polesie and eastern Nowogródek with
  Wołożyn; Bielsk and Wołkowysk turn Polish.
* **Soviet Belarus** grows from 5.4 M to 9.5 M people under Polish-north-
  eastern vital rates. Russian, the language of its towns in 1926, falls from
  13 to 8 % as Belarusian and Polish (both official) take over. Polish rises
  from under 1 % to 5 %, mainly in the towns. Mińsk okrug grows from 591 k
  to 1.49 M.
* **Polesie** goes from West Polesian (62 %) to Belarusian (50 %), as in
  Wakar's Poland.
* **Migration** carries Belarusian west. Warsaw city is 15 % Belarusian-
  speaking in 2032, Silesia 6 % and Lublin 4 %. The diaspora term does not
  bring this down: Belarusian is co-official throughout, and a community of
  this size in Warsaw counts as institutionally complete (its own schools,
  churches and press). In a Polish-Belarusian state that is a defensible
  outcome, comparable with the Swedish-speaking minority of interwar
  Helsinki.
* **Lwów** county grows from 459 k to 869 k.

### Results: `nw_krai` and `lit_bel` (two states in one run)

Both runs hold two states: Poland without the krai, and the krai (or
Lit-Bel) as a separate state with Lithuanian, Belarusian, Polish, Yiddish and
Russian official (and Latvian in Latgale). The borders are those of the 1897
governorates: units that straddle them are cut (Kaunas and Alytus on the
Niemen, Kamień Koszyrski, and in Lit-Bel the Połock, Bobrujsk, Homel and
Rzeczyca okrugs on the Minsk governorate's border).

| | 1933 | 2032 |
|---|---|---|
| **`nw_krai`**: Poland (225 units, with the Suwałki governorate) | 28.36 M | 40.43 M |
| Northwestern Krai (65 units) | 12.82 M | 25.68 M |
| of which the Soviet-Belarusian lands | 5.45 M | 11.58 M |
| of which Latgale, Nevel-Sebezh-Velizh and eastern Mogilev | 1.11 M | 2.48 M |
| **`lit_bel`**: Poland (217 units) | 27.79 M | 39.44 M |
| Lit-Bel (59 units, with the Suwałki governorate) | 9.32 M | 17.35 M |
| of which the Soviet-Belarusian lands (Minsk governorate) | 2.50 M | 5.31 M |

Home languages in the krai states:

| | Krai 1933 | Krai 2032 | Lit-Bel 1933 | Lit-Bel 2032 |
|---|---|---|---|---|
| Belarusian | 47.5 % | 60.4 % | 34.9 % | 48.5 % |
| Polish | 15.1 % (1.94 M) | 14.1 % (3.63 M) | 21.9 % (2.04 M) | 21.8 % (3.78 M) |
| Lithuanian | 12.4 % (1.59 M) | 9.0 % (2.31 M) | 20.6 % (1.92 M) | 15.7 % (2.73 M) |
| Russian | 8.0 % | 7.2 % | 5.0 % | 4.2 % |
| Yiddish | 7.8 % | 3.9 % | 8.5 % | 4.3 % |
| West Polesian | 5.1 % | 2.8 % | 7.0 % | 4.2 % |
| Latvian | 2.5 % | 1.7 % | - | - |
| Units led by Belarusian / Lithuanian / Polish / W. Polesian / Latvian | 28 / 17 / 9 / 8 / 3 | 38 / 17 / 8 / 0 / 2 | 20 / 20 / 11 / 8 / - | 29 / 20 / 10 / 0 / - |

* **The krai becomes a Belarusian state.** Belarusian is the language of
  the majority and the standard of the Polesians. The Polesie counties go
  from West Polesian to Belarusian, and so does Wołożyn, from Polish
  (Kamień Koszyrski, cut by the governorate border, stays with Poland). In
  Latgale, Dyneburg turns from Latvian to Belarusian (Latvian 54 → 32 % of
  Latgale, Belarusian 15 → 29 %): Latvian is official there,
  but the krai's majority language draws the migrants and the mixed
  families. Rzeżyca and Lucyn stay Latvian. By identity the krai is 60 %
  Belarusian, 14 % Polish, 9 % Lithuanian and 7 % Russian in 2032.
* **Cities.** Wilno county grows from 417 k to 950 k and stays
  Polish-plurality, but falls from 73 to 52 % Polish, with Belarusian
  from 3 to 30 %: migrants from its Belarusian hinterland settle there
  instead of going to Warsaw. Białystok county (Grodno governorate) falls
  from 65 to 48 % Polish (Belarusian 9 to 37 %). Mińsk okrug grows from
  593 k to 1.80 M. The Lithuanian counties stay Lithuanian.
* **Polish holds on in absolute numbers.** As an official language with its
  own schools, Polish grows from 1.9 to 3.6 M speakers in the krai, and
  holds its share in Lit-Bel. In the krai's Lithuanian lands, Polish
  speakers grow from 137 k to 419 k, and those with a Polish identity from
  67 k to 266 k (Lit-Bel, which also holds Suvalkija: 151 k to 554 k and
  75 k to 332 k): Polish is official there and Wilno is next door.
  Lithuanian grows from 1.59 to 2.31 M speakers in the krai, but its share
  falls.
* **Suvalkija in Poland** (`nw_krai`). The Suwałki governorate belonged to
  the Kingdom of Poland, so Marijampolė, Vilkaviškis, Šakiai, Lazdijai and
  the west banks at Alytus and Kaunas go to Poland, with Lithuanian
  co-official: 0.38 M people in 1933, 0.45 M in 2032. They stay
  Lithuanian-plurality, except Alytus's west bank, which turns Polish.
* **Fast growth.** The krai doubles (Soviet-Belarusian part 2.1-fold, its
  eastern lands 2.2-fold), against 1.43-fold for Poland. Two causes:
  * the fertility transition is late in these lands: 2.8 children per woman
    in the krai in 1970 and 2.15 in 1990 (2.85 and 2.2 in its
    Soviet-Belarusian part), against 2.4 and 1.9 in Poland. Rural eastern
    Poland in the real 1970s and 1980s, the closest analogue to these lands
    without Soviet industrialisation, had about 2.9 in 1970 and 2.4-2.6 in
    1990; the real BSSR, urbanised fast, had about 2.3 and 1.9. The
    fertility defaults are calibrated on historical Poland (METHODOLOGY
    §4.2);
  * as a separate state the krai sends few migrants to Polish cities
    (friction 0.03): its lands that are Polish in the baseline grow from
    4.4 to 8.6 M, against 4.4 to 7.1 M in the baseline.

  This growth is the least certain result of these scenarios.
* **Separate economies.** Each state has its own income, converging at the
  same rate to the same target. The krai starts at about two-thirds of
  Poland's income per head (1,230 against 1,930 GK$ in 1933) and closes most
  of the gap by 2032 (16,300 against 17,500). Its lower income keeps its
  emigration hump later and its transport budget smaller.
* **Poland** is 68.2 % Polish in 1933 and 75.3 % in 2032, with Ukrainian
  17.4 → 17.7 % (`nw_krai`; `lit_bel` alike). Without the krai it is the
  baseline's Poland less its north-east. Poland ends at 40.4 M in `nw_krai`
  and 39.4 M in `lit_bel`; the first holds 0.4 M more in the Suwałki
  governorate, and the rest of the difference is the noise of single seeded
  runs.

### Results: `historical` (calibration)

Poland in each year's borders against the censuses (model / recorded;
`outputs/history/historical_checks.csv`):

| | 1946 | 1950 | 1960 | 1970 | 1988 | 2002 | 2021 |
|---|---|---|---|---|---|---|---|
| Population (M) | 22.85 / 23.93 | 23.78 / 25.01 | 28.39 / 29.80 | 30.97 / 32.64 | 36.12 / 37.88 | 36.39 / 38.23 | 35.26 / 38.04 |
| Urban (%) | | 37.9 / 36.9 | 45.3 / 48.3 | 50.9 / 52.3 | 57.0 / 61.0 | 59.1 / 61.8 | 62.6 / 60.2 |

| | 1950 | 1960 | 1970 | 1980 | 1990 | 2000 | 2010 | 2020 |
|---|---|---|---|---|---|---|---|---|
| Total fertility | 3.76 / 3.71 | 2.98 / 2.98 | 2.19 / 2.20 | 2.29 / 2.28 | 1.99 / 2.04 | 1.41 / 1.37 | 1.37 / 1.38 | 1.41 / 1.39 |

Life expectancy (men, women): 1952-53 60.1/65.7 against 58.6/64.2;
1960-61 64.9/70.7 against 64.8/70.5; 1970-72 66.5/73.6 against 66.8/73.8;
1990 67.3/76.4 against 66.2/75.2; 2019 76.0/83.7 against 74.1/81.8.

The German land and Danzig: 8.89 M in 1939 (8.86 M), 4.59 M in 1946
(5.02 M), 5.51 M in 1950 (5.94 M).

The 2002 census (thousands; model / census): Silesian identity 133 / 173,
German 97 / 153, Belarusian 64 / 49, Ukrainian 101 / 31, Lemko 15 / 6,
Lithuanian 5.8 / 6, Kashubian 4.1 / 5, Jewish 10 / 1; German at home 74 /
205, Belarusian 51 / 40, Ukrainian 39 / 23, Lemko 7 / 6, Kashubian 111 /
53, Lithuanian 6.5 / 6. The 2011 census (home language, up to two
answers): German 49 / 96, Belarusian 39 / 26, Ukrainian 23 / 25, Lemko
4 / 6, Kashubian 93 / 108, Lithuanian 5.4 / 5.3.

What this says about the model:

* **Fertility** now follows the record from 1950 to 2020, once the
  scenario adds its period effects (war, compensation, pro-natalism, the
  slump after 1990). Rural Poland kept about three children per woman in
  1970-80; the Soviet-ruled east fell to about 2.6 by 1970. The defaults
  of every scenario were recalibrated on this (METHODOLOGY §4.2): the
  counterfactual Volhynia and Polesie no longer keep 4 children per woman
  in 1970.
* **Mortality** follows within about 1.5 years once the post-war shift of
  the income-mortality curve is in the defaults (§4.1) and People's
  Poland's own regime (fast gains, then stagnation) is in the scenario.
* **Population** is 1.1 M (5 %) short in 1946 and 1.2-1.8 M by 2002, and
  the gap opens before 1946: interwar Poland is about 0.35 M short in 1939,
  and the old territory loses more in the war than it did. The scenario now
  carries forced labour in the Reich (2.1 M taken, most back in 1945, the
  rest with the UNRRA repatriation of 1946-48, none of them counted by the
  1946 census), the flight of Poles from Volhynia and Eastern Galicia into
  the General Government, no voluntary moves between regions under the
  occupation, and the 1944-46 transfer of Ukrainians from the south-east
  alone. After 1950 growth follows the record (fertility and mortality
  match).
* **Minority languages** of People's Poland come out about right in 2002
  and 2011, from three changes made against this scenario:
  * marriage across languages, history-matched with the dispersed
    Ukrainians as a case (METHODOLOGY §6.3-6.4);
  * the dispersal of Operation Vistula (the deportees lose their village
    clustering);
  * migration units that follow the 1945 border. Before this fix, rural
    Soviet Galicia "urbanised" into Przemyśl and Rzeszów.

  Before these changes the model kept 431 k Ukrainian speakers in 2002
  against 23 k. German at home is low (74 k against 205 k; 49 k against
  96 k in 2011): the Upper Silesian natives married among themselves
  across the German and Silesian-Polish line, which the model counts as
  marrying out.
* **National identity** is calibrated here: the pull of the state nation
  (METHODOLOGY §6.7) is fitted on the 2002 census and used by every
  scenario. It fits the Lithuanians and Kashubians. A faster pull would fit
  the Belarusians (64 k against 49 k) but erase the Kashubians. Germans and
  Silesians come out 25-45 % low (the events of 1989-91 that brought them
  back are given, not modelled). Ukrainian and Lemko identity outlasts the
  language more than the census shows (101 k against 31 k, though 51 k in
  2011); half the mixed households take the partner's religion, and with
  it a Catholic's pull.
* **The counterfactual scenarios** share these mechanisms. Where a minority
  is scattered (migrants in cities, settlers), it now marries out and
  shifts within two or three generations. Where it is compact, as in the
  eastern voivodeships, marrying out is rare and the shift rates come from
  the history-matched cases (METHODOLOGY §6.4).

## The equal-exchange Curzon line

The atlas overlay "Curzon line" (magenta; method in METHODOLOGY §12.8)
draws, for every 5-year frame, a continuous line across the whole state
(Lithuania and Soviet Belarus included where they are part of it), from one
point of its border to another, along county borders: every county lies
wholly on one side, and each side is in one piece. It leaves as many
non-Poles on its Polish side as Poles on its other side, to within one
county, with the most Poles on the Polish side. Poles are speakers of Polish
at home; Kashubians, Wymysorys speakers, Germans and Jews (4.4 M in 1932)
are not counted. In `nw_krai` and `lit_bel` the line runs across both
states.

| Scenario | 1932: non-Poles on the Polish side / Poles on the other | 2032 | 1919-20 line, 1932: non-Poles west / Poles east | 2032 | Polish side % Polish, 1932 / 2032 |
|---|---|---|---|---|---|
| baseline | 1.79 / 1.84 M | 3.94 / 3.99 M | 1.00 / 3.19 M | 2.31 / 8.08 M | 91 / 89 % |
| ii_rp_only | 1.85 / 1.83 M | 3.75 / 3.72 M | 0.99 / 3.04 M | 2.21 / 7.86 M | 91 / 89 % |
| federal_autonomy | 1.79 / 1.84 M | 4.34 / 4.36 M | 1.00 / 3.19 M | 3.35 / 6.35 M | 91 / 86 % |
| integral_nationalism | 1.79 / 1.84 M | 3.78 / 3.79 M | 1.00 / 3.19 M | 1.82 / 9.45 M | 91 / 89 % |
| polonizing_union | 1.79 / 1.84 M | 4.14 / 4.02 M | 1.00 / 3.19 M | 2.29 / 8.36 M | 91 / 88 % |
| census_official | 1.81 / 1.75 M | 3.59 / 3.61 M | 0.72 / 3.77 M | 1.82 / 8.69 M | 92 / 90 % |
| census_vernacular | 1.70 / 1.72 M | 4.15 / 4.13 M | 1.19 / 2.36 M | 2.53 / 7.79 M | 91 / 88 % |
| ukraine_autonomy_tricantonal | 1.79 / 1.84 M | 3.17 / 3.27 M | 1.00 / 3.19 M | 2.88 / 4.23 M | 91 / 90 % |
| autonomy_grand_duchy_coofficial | 1.79 / 1.84 M | 3.49 / 3.45 M | 1.00 / 3.19 M | 2.97 / 4.28 M | 91 / 89 % |
| no_official_language | 1.79 / 1.84 M | 3.96 / 4.07 M | 1.00 / 3.19 M | 3.91 / 4.64 M | 91 / 87 % |
| wakar_poland | 1.03 / 1.07 M | 2.17 / 2.04 M | 0.94 / 1.07 M | 2.09 / 2.02 M | 94 / 92 % |
| wakar_poland_belarus | 1.08 / 1.06 M | 3.02 / 3.08 M | 0.94 / 1.11 M | 3.38 / 2.53 M | 94 / 89 % |
| nw_krai | 1.84 / 1.83 M | 4.73 / 4.71 M | 1.00 / 3.27 M | 2.53 / 7.13 M | 91 / 85 % |
| lit_bel | 1.87 / 1.81 M | 4.52 / 4.53 M | 1.00 / 3.21 M | 2.49 / 6.88 M | 91 / 86 % |
| plebiscite_poland | 1.92 / 1.91 M | 3.95 / 3.88 M | 1.24 / 3.19 M | 2.46 / 7.63 M | 91 / 89 % |

The two numbers of the computed line differ by the residual of whole
counties: under 70 k in most frames, up to 0.13 M (`wakar_poland` and
`polonizing_union`, 2032), where a large county lies on the line. In
`plebiscite_poland` the new lands lie on the Polish side, and the exchange
starts slightly larger (1.92 M). The historical columns count the same
people on either side of the Curzon line of 1919-20 (line A in Galicia), which is not balanced: it leaves
far more Poles east than non-Poles west, and more so as the east Polonises.
In the scenarios with a Ukrainian autonomy, a Grand Duchy or no official
language the east keeps its languages, and the historical line comes close
to balance by 2032.

* **1932, union scenarios.**
  * Lithuania, Polesie, Volhynia, Stanisławów, most of Tarnopol and the
    eastern Wilno and Nowogródek lands are on the other side.
  * The Polish-speaking western Wilno lands (with Wilno) stay on the Polish
    side, joined to it through Grodno and Lida.
  * So do Lwów and seventeen of the 26 counties of lwowskie, and through
    them Tarnopol and six more counties of its voivodeship.
* **Over the century** the Polish side spreads east as Polesie and the
  north-east shift to Polish. The exchange grows to about 4.2 M each way
  around 2000 and 4.0 M in 2032, because both sides grow more mixed.
* **With the autonomies**, Belarusian and Ukrainian schooling slow the
  shift to Polish in the east, and the exchange grows less (3.2-3.5 M).
* **Wakar's Poland** starts with the smallest exchange (1.05 M).
* **Whole counties against free lines.** The earlier line, which could
  wind cell by cell through counties, needed 1.89 M each way in 1932. The
  county line needs slightly fewer (1.83 M), because the cell search,
  a heuristic like the county one, stopped at a poorer solution. A version
  that allowed only straight lines needed 2.75 M.

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
