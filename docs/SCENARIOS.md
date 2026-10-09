# Scenarios

Every scenario but one shares the premise: **no Second World War**. There is
no German-Soviet partition, no Holocaust, no deportations, no post-1945
border shifts or population transfers, and no communist regime. Everything
else that cannot be measured is a scenario choice. The exception is
`historical`, which replays the real century for calibration (below). Scenarios are YAML files in
`scenarios/`. A scenario can `extends:` another one and overrides only the
parameters it names. A mapping containing `_replace: true` replaces the parent
mapping instead of being merged into it.

All scenarios run at **county level** (270 regions; 211 for Wakar's
Poland-Belarus, 289 and 276 for the Northwestern Krai and Lit-Bel, with
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
  12 to 69 % Polish.
* Kashubian → Polish in Kartuzy, Kościerzyna and Wejherowo.
* Ukrainian → Polish in eight Lwów counties (Dobromil, Drohobycz, Gródek,
  Lesko, Lubaczów, Rudki, Sambor, Sokal) and Kamionka Strumiłowa.

The Lithuanian units' Poles hold at about 150 k (152 k → 154 k), and the
Lauda Poles at 53-54 k, with Polish co-official in Lithuania. Polish
*identity* there rises a little, from 79 k to 85 k (§6.7 of the
methodology).

**Migrants' children assimilate** (the diaspora term, calibrated on
second-generation immigrants). Warsaw city ends 6 % Ukrainian-speaking and
Silesia 4 %. A steady stream of first-generation migrants keeps these
shares from falling further.

**Identity and language part ways.** In 2032, Polish is the home language
of 72 % but the identity of 67 %: many who switch to Polish keep a
Ukrainian, Belarusian or Jewish identity. Jewish identity (6.7 %) outlasts
Yiddish (3.8 %). "Local" identities fall from 2.8 to 1.3 % as nation-building
turns Polesians and Belarusian speakers Belarusian, Ukrainian or Polish.

### Results: `ukraine_autonomy_tricantonal`

| Member | 1933 | 2032 | Home languages 1933 → 2032 |
|---|---|---|---|
| Poland (crown lands, 154 counties) | 20.1 M | 31.2 M | Polish 84 → 86 %, Yiddish 9 → 5 %, Ukrainian 1 → 4 % |
| Ukrainian autonomy (66) | 8.4 M | 10.4 M | Ukrainian 55 → 64 %, Polish 35 → 29 % |
| Lithuanian canton (23) | 2.42 M | 2.81 M | Lithuanian 78 → 84 %, Polish 6 → 8 % |
| Polish canton (Wilno–Lida–Grodno, 7) | 1.35 M | 1.92 M | Polish 58 → 60 %, Belarusian 23 → 27 % |
| Belarusian canton (20) | 2.56 M | 4.29 M | Belarusian 36 → 55 %, West Polesian 28 → 16 %, Polish 23 → 21 % |

* **Belarusian** speakers number 3.45 M in 2032, against 1.26 M in the
  baseline. They come from Belarusian schooling, from West Polesian
  speakers shifting to Belarusian instead of Polish, and from high Polesian
  fertility. Belarusian leads 9 of the canton's 20 counties in 1933 and 19
  in 2032: the nine Polesie counties, plus Wołożyn from Polish. One county
  stays Polish.
* **Ukrainian** speakers number 8.2 M, against 7.0 M in the baseline.
  Ukrainian leads 49 of the autonomy's 66 counties in 1933 and 56 in 2032.
  * Seven turn from Polish to Ukrainian: Lwów, Mościska, Przemyśl,
    Przemyślany, Skałat, Tarnopol and Trembowla.
  * The ten Polish-plurality counties left are all on or west of the San
    (Jarosław, Rzeszów, Sanok, Krosno ...).
  * Tarnopol voivodeship goes from 42 % Polish and 53 % Ukrainian to 32 and
    62 %; lwowskie as a whole from 37 to 48 % Ukrainian.
  * In those ten counties, Polish falls from 84 to 64 % and Ukrainian rises
    from 7 to 28 %. Both halves of lwowskie lie in the autonomy and form one
    migration unit, so rural migrants from either half settle in the towns
    of both.
* **In the crown lands**, Ukrainian rises from 1 to 4 % of speakers: the
  Chełm and Podlasie Ukrainians of Lublin (9 → 11 % of the voivodeship)
  and migrants to Warsaw, Silesia and Łódź. The baseline shows the same,
  slightly weaker.
* **Lithuanian Poles** rise from 153 k to 216 k; the Lauda Poles from 54 k
  to 65 k. In the baseline they hold at 154 k and 53 k.
* **Polish** falls to 63.7 % of the whole union, against 71.9 % in the
  baseline. Wilno county grows to 599 k (871 k in the baseline), as the
  capital of a canton rather than of a large Polish province.

### Results: `autonomy_grand_duchy_coofficial`

The same Ukrainian autonomy, with an undivided Grand Duchy of 50 counties
working in Lithuanian, Polish and Belarusian. In 1933, Lithuanian leads 22
of its counties, Belarusian 11 (Grodno and Wołkowysk among them), Polish 7
and West Polesian 9.

| Grand Duchy | 1933 | 2032 |
|---|---|---|
| Population | 6.33 M | 9.11 M |
| Belarusian | 19 % | 33 % |
| Polish | 24 % | 26 % |
| Lithuanian | 31 % | 26 % |
| West Polesian | 11 % | 8 % |
| Yiddish | 8 % | 3 % |

* **Belarusian** becomes the Duchy's largest language (3.0 M speakers). It
  leads 21 counties in 2032: the nine Polesie counties, plus Wołożyn, which
  turns from Polish.
* **Polish** holds its share. It leads six counties and spreads in the
  Lithuanian lands: their Poles grow from 154 k to 414 k (Polish identity
  from 81 k to 289 k), the Lauda Poles from 54 k to 102 k. Wilno county
  grows to 827 k and falls from 71 to 57 % Polish, with Belarusian from 4
  to 26 %.
* **Lithuanian** keeps the plurality in its 23 counties, but the Lithuanian
  lands become mixed: Kaunas and the north-east fall from 71 to 64 %
  Lithuanian, Samogitia from 88 to 81 %. Migrants from the fast-growing
  east keep Belarusian, which is official there too, and Polish gains
  Lithuanian speakers. The number of Lithuanian speakers in the union
  (2.61 M) is the same as in the baseline (2.60 M).
* **Against the cantons:** one Duchy with free movement and three languages
  everywhere spreads Polish and Belarusian into the Lithuanian lands. The
  cantons keep each language's core (the Lithuanian canton is 84 %
  Lithuanian in 2032).

### Results: `wakar_poland` (Wakar's Poland)

Poland without Volhynia, Stanisławów, Tarnopol and the Vilnius region has
199 counties and 25.7 M people in 1933, 35.9 M in 2032. Belarusian is the
working language of 19 of them: Polesie, eastern Nowogródek, Głębokie,
Mołodeczno, Wilejka, Wołkowysk and Bielsk.

* **Belarusian** grows from 1.1 M speakers (4.2 %) to 3.0 M (8.3 %). It
  leads 18 counties in 2032 (10 in 1933): the nine Polesie counties pass
  from West Polesian, Wołożyn from Polish, and Bielsk and Wołkowysk turn
  Polish. Polesie goes from 7 to 45 % Belarusian (West Polesian 62 → 25 %,
  Polish 11 → 20 %).
* **Polish** goes from 73.9 to 78.6 % of the state.
* **Ukrainian** (lwowskie and Lublin, 5.9 %) has no official status here.
  Nine Lwów counties turn Polish, one more (Rawa Ruska) than in the
  baseline, and Ukrainian falls from 37 to 30 % in lwowskie and from 9 to
  8 % in Lublin.

### Results: `no_official_language`

* **Shares of the union in 2032:** Polish 61.6 % (71.9 % in the baseline),
  Ukrainian 16.6 %, Belarusian 6.6 % (3.3 M), Yiddish 5.3 % (2.7 M, against
  1.95 M), West Polesian 2.0 % (1.0 M). About 5 M more people speak a
  minority language at home than in the baseline.
* **Only 19 counties change their plurality language** (34 in the
  baseline):
  * Tarnopol, Trembowla, Skałat and Przemyślany turn Ukrainian;
  * Wołożyn turns Belarusian; Bielsk Podlaski, Grodno and Wołkowysk turn
    Polish;
  * seven Polesie counties go from West Polesian to Belarusian. Kamień
    Koszyrski and Stolin stay West Polesian;
  * the three Kashubian counties turn Polish, and Klaipėda Lithuanian.
* **Shift still happens**, towards whichever language is large locally.
  Polesie goes from 7 to 35 % Belarusian (69 % Polish in the baseline).
  Towns and the west still pull towards Polish.
* **Migrants** keep their languages longer: their languages are official
  everywhere, so a city's Ukrainian or Belarusian community soon counts as
  complete and the diaspora term weakens. Warsaw city is 10 %
  Ukrainian-speaking in 2032 (6 % in the baseline) and 4 % Belarusian;
  Silesia 6.5 % Ukrainian.

### Results: `wakar_poland_belarus` (Wakar's Poland-Belarus)

Wakar's Poland plus Soviet Belarus has 211 counties and 31.1 M people in
1933 (5.4 M of them in Soviet Belarus), and 48.2 M in 2032.

| | 1933 | 2032 |
|---|---|---|
| Population | 31.1 M | 48.2 M |
| Polish | 61.1 % | 60.5 % |
| Belarusian | 17.0 % | 26.8 % (12.9 M speakers) |
| Ukrainian | 5.0 % | 3.6 % |
| Yiddish | 8.3 % | 4.1 % |
| West Polesian | 2.3 % | 1.5 % |
| Soviet Belarus: population | 5.4 M | 9.5 M |
| Soviet Belarus: Belarusian / Russian / Polish | 77 / 13 / 0.8 % | 84 / 8 / 5 % |

* **A Polish-Belarusian state.** Belarusian leads 30 counties in 2032 (22 in
  1933): all of Soviet Belarus, Polesie and eastern Nowogródek with
  Wołożyn; Bielsk and Wołkowysk turn Polish.
* **Soviet Belarus** grows from 5.4 M to 9.5 M people under Polish-north-
  eastern vital rates. Russian, the language of its towns in 1926, falls from
  13 to 8 % as Belarusian and Polish (both official) take over. Polish rises
  from under 1 % to 5 %, mainly in the towns. Mińsk okrug grows from 591 k
  to 1.49 M.
* **Polesie** goes from West Polesian (62 %) to Belarusian (51 %), as in
  Wakar's Poland.
* **Migration** carries Belarusian west. Warsaw city is 15 % Belarusian-
  speaking in 2032, Silesia 7 % and Lublin 4 %. The diaspora term does not
  bring this down: Belarusian is co-official throughout, and a community of
  this size in Warsaw counts as institutionally complete (its own schools,
  churches and press). In a Polish-Belarusian state that is a defensible
  outcome, comparable with the Swedish-speaking minority of interwar
  Helsinki.
* **Lwów** county grows from 459 k to 888 k.

### Results: `nw_krai` and `lit_bel` (two states in one run)

Both runs hold two states: Poland without the krai, and the krai (or
Lit-Bel) as a separate state with Lithuanian, Belarusian, Polish, Yiddish and
Russian official (and Latvian in Latgale). The borders are those of the 1897
governorates: units that straddle them are cut (Kaunas and Alytus on the
Niemen, Kamień Koszyrski, and in Lit-Bel the Połock, Bobrujsk, Homel and
Rzeczyca okrugs on the Minsk governorate's border).

| | 1933 | 2032 |
|---|---|---|
| **`nw_krai`**: Poland (224 units, with the Suwałki governorate) | 28.33 M | 40.35 M |
| Northwestern Krai (65 units) | 12.85 M | 25.69 M |
| of which the Soviet-Belarusian lands | 5.45 M | 11.59 M |
| of which Latgale, Nevel-Sebezh-Velizh and eastern Mogilev | 1.11 M | 2.48 M |
| **`lit_bel`**: Poland (216 units) | 27.78 M | 39.37 M |
| Lit-Bel (60 units, with the Suwałki governorate) | 9.33 M | 17.35 M |
| of which the Soviet-Belarusian lands (Minsk governorate) | 2.50 M | 5.31 M |

Home languages in the krai states:

| | Krai 1933 | Krai 2032 | Lit-Bel 1933 | Lit-Bel 2032 |
|---|---|---|---|---|
| Belarusian | 47.6 % | 60.7 % | 35.3 % | 49.0 % |
| Polish | 15.0 % (1.93 M) | 13.9 % (3.57 M) | 21.7 % (2.03 M) | 21.4 % (3.71 M) |
| Lithuanian | 12.4 % (1.59 M) | 8.8 % (2.26 M) | 20.4 % (1.90 M) | 15.5 % (2.70 M) |
| Russian | 7.9 % | 7.2 % | 4.9 % | 4.2 % |
| Yiddish | 7.8 % | 3.8 % | 8.4 % | 4.2 % |
| West Polesian | 5.1 % | 2.9 % | 7.0 % | 4.3 % |
| Latvian | 2.5 % | 1.7 % | - | - |
| Units led by Belarusian / Lithuanian / Polish / W. Polesian / Latvian | 28 / 16 / 9 / 9 / 3 | 40 / 16 / 7 / 0 / 2 | 20 / 20 / 11 / 9 / - | 30 / 20 / 10 / 0 / - |

* **The krai becomes a Belarusian state.** Belarusian is the language of
  the majority and the standard of the Polesians. The Polesie counties go
  from West Polesian to Belarusian, and so do Lida and Wołożyn, from
  Polish. In Latgale, Dyneburg turns from Latvian to Belarusian (Latvian
  54 → 32 % of Latgale, Belarusian 15 → 29 %): Latvian is official there,
  but the krai's majority language draws the migrants and the mixed
  families. Rzeżyca and Lucyn stay Latvian. By identity the krai is 56 %
  Belarusian, 15 % Polish, 9 % Lithuanian and 9 % Russian in 2032.
* **Cities.** Wilno county grows from 416 k to 973 k and stays
  Polish-plurality, but falls from 71 to 50 % Polish, with Belarusian
  from 5 to 32 %: migrants from its Belarusian hinterland settle there
  instead of going to Warsaw. Białystok county (Grodno governorate) falls
  from 65 to 49 % Polish (Belarusian 9 to 36 %). Mińsk okrug grows from
  593 k to 1.81 M. The Lithuanian counties stay Lithuanian.
* **Polish holds on in absolute numbers.** As an official language with its
  own schools, Polish grows from 1.9 to 3.6 M speakers in the krai, and
  holds its share in Lit-Bel. In the krai's Lithuanian lands, Polish
  speakers grow from 141 k to 425 k, and those with a Polish identity from
  69 k to 296 k (Lit-Bel, which also holds Suvalkija: 150 k to 567 k and
  76 k to 414 k): Polish is official there and Wilno is next door.
  Lithuanian grows from 1.59 to 2.26 M speakers in the krai, but its share
  falls.
* **Suvalkija in Poland** (`nw_krai`). The Suwałki governorate belonged to
  the Kingdom of Poland, so Marijampolė, Vilkaviškis, Šakiai, Lazdijai and
  the west banks at Alytus and Kaunas go to Poland, with Lithuanian
  co-official: 0.36 M people in 1933, 0.44 M in 2032. They stay
  Lithuanian-plurality, except Kaunas's small west bank (Aleksotas), which
  turns Polish.
* **Fast growth.** The krai doubles (Soviet-Belarusian part 2.1-fold, its
  eastern lands 2.2-fold), against 1.42-fold for Poland. Two causes:
  * the fertility transition is late in these lands: 2.7 children per woman
    in the krai in 1970 and 2.1 in 1990 (2.75 and 2.2 in its
    Soviet-Belarusian part), against 2.4 and 1.9 in Poland. Rural eastern
    Poland in the real 1970s and 1980s, the closest analogue to these lands
    without Soviet industrialisation, had about 2.9 in 1970 and 2.4-2.6 in
    1990; the real BSSR, urbanised fast, had about 2.3 and 1.9. The
    fertility defaults are calibrated on historical Poland (METHODOLOGY
    §4.2);
  * as a separate state the krai sends few migrants to Polish cities
    (friction 0.03): its lands that are Polish in the baseline grow from
    4.4 to 8.6 M, against 4.4 to 7.2 M in the baseline.

  This growth is the least certain result of these scenarios.
* **Separate economies.** Each state has its own income, converging at the
  same rate to the same target. The krai starts at about two-thirds of
  Poland's income per head (1,230 against 1,930 GK$ in 1933) and closes most
  of the gap by 2032 (16,300 against 17,500). Its lower income keeps its
  emigration hump later and its transport budget smaller.
* **Poland** is 68.7 % Polish in 1933 and 75.9 % in 2032, with Ukrainian
  17.0 → 17.3 % (`nw_krai`; `lit_bel` alike). Without the krai it is the
  baseline's Poland less its north-east. Poland ends at 40.4 M in `nw_krai`
  and 39.4 M in `lit_bel`; the first holds 0.4 M more in the Suwałki
  governorate, and the rest of the difference is the noise of single seeded
  runs.

### Results: `historical` (calibration)

Poland in each year's borders against the censuses (model / recorded;
`outputs/history/historical_checks.csv`):

| | 1946 | 1950 | 1960 | 1970 | 1988 | 2002 | 2021 |
|---|---|---|---|---|---|---|---|
| Population (M) | 22.83 / 23.93 | 23.74 / 25.01 | 28.33 / 29.80 | 30.90 / 32.64 | 36.05 / 37.88 | 36.34 / 38.23 | 35.24 / 38.04 |
| Urban (%) | | 38.0 / 36.9 | 45.4 / 48.3 | 51.0 / 52.3 | 57.0 / 61.0 | 59.0 / 61.8 | 62.4 / 60.2 |

| | 1950 | 1960 | 1970 | 1980 | 1990 | 2000 | 2010 | 2020 |
|---|---|---|---|---|---|---|---|---|
| Total fertility | 3.76 / 3.71 | 2.97 / 2.98 | 2.19 / 2.20 | 2.29 / 2.28 | 1.99 / 2.04 | 1.41 / 1.37 | 1.37 / 1.38 | 1.41 / 1.39 |

Life expectancy (men, women): 1952-53 60.1/65.7 against 58.6/64.2;
1960-61 64.9/70.7 against 64.8/70.5; 1970-72 66.5/73.6 against 66.8/73.8;
1990 67.3/76.4 against 66.2/75.2; 2019 76.0/83.7 against 74.1/81.8.

The German land and Danzig: 8.89 M in 1939 (8.86 M), 4.59 M in 1946
(5.02 M), 5.51 M in 1950 (5.94 M).

The 2002 census (thousands; model / census): Silesian identity 131 / 173,
German 101 / 153, Belarusian 140 / 49, Ukrainian 283 / 31, Lemko 36 / 6,
Lithuanian 5.8 / 6, Kashubian 4.7 / 5, Jewish 10 / 1; German at home 163 /
205, Belarusian 223 / 40, Ukrainian 337 / 23, Lemko 75 / 6, Kashubian 167 /
53, Lithuanian 9 / 6.

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
* **Population** is 1.1 M (5 %) short in 1946 and 1.3-2.0 M after, and
  the gap opens before 1946: interwar Poland is about 0.35 M short in 1939,
  and the old territory loses more in the war than it did. The scenario now
  carries forced labour in the Reich (2.1 M taken, most back in 1945, the
  rest with the UNRRA repatriation of 1946-48, none of them counted by the
  1946 census), the flight of Poles from Volhynia and Eastern Galicia into
  the General Government, no voluntary moves between regions under the
  occupation, and the 1944-46 transfer of Ukrainians from the south-east
  alone. After 1950 growth follows the record (fertility and mortality
  match).
* **National identity** is calibrated here: the pull of the state nation
  (METHODOLOGY §6.7) is fitted on the 2002 census, on the Lithuanians and
  Kashubians, whose home language the model gets about right, and is used
  by every scenario. A stigmatised, unschooled language anchors its
  speakers' identity less. Germans and Silesians come out 25-35 % low (the
  events of 1989-91 that brought them back are given, not modelled).
  Ukrainians, Belarusians and Lemkos stay several times too many because
  their home language does: after Operation Vistula the scattered
  Ukrainians' children are raised in Polish at 70-80 % per birth, but
  adults learn Polish and switch slowly, and the model has no term for the
  mixed marriages that carried most of the real shift. The counterfactual
  scenarios share this behaviour, so minority home languages there are, if
  anything, too persistent where a minority is scattered; where it is
  compact, as in the eastern voivodeships, the model's shift rates come
  from the history-matched cases (METHODOLOGY §6.4).

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
| baseline | 1.83 / 1.83 M | 4.03 / 3.89 M | 0.96 / 3.26 M | 2.24 / 8.13 M | 91 / 88 % |
| ii_rp_only | 1.73 / 1.71 M | 3.72 / 3.73 M | 0.94 / 3.11 M | 2.14 / 7.91 M | 92 / 89 % |
| federal_autonomy | 1.83 / 1.84 M | 4.43 / 4.28 M | 0.96 / 3.26 M | 3.30 / 6.38 M | 91 / 86 % |
| integral_nationalism | 1.83 / 1.83 M | 3.81 / 3.81 M | 0.96 / 3.26 M | 1.73 / 9.51 M | 91 / 89 % |
| polonizing_union | 1.83 / 1.83 M | 4.09 / 4.10 M | 0.96 / 3.26 M | 2.22 / 8.42 M | 91 / 88 % |
| census_official | 1.76 / 1.80 M | 3.61 / 3.61 M | 0.72 / 3.79 M | 1.79 / 8.65 M | 92 / 90 % |
| census_vernacular | 1.69 / 1.77 M | 4.17 / 4.09 M | 1.14 / 2.43 M | 2.47 / 7.86 M | 91 / 88 % |
| ukraine_autonomy_tricantonal | 1.83 / 1.84 M | 3.16 / 3.26 M | 0.96 / 3.27 M | 2.82 / 4.21 M | 91 / 90 % |
| autonomy_grand_duchy_coofficial | 1.83 / 1.84 M | 3.46 / 3.47 M | 0.96 / 3.27 M | 2.91 / 4.27 M | 91 / 89 % |
| no_official_language | 1.83 / 1.84 M | 4.03 / 4.08 M | 0.96 / 3.27 M | 3.87 / 4.66 M | 91 / 87 % |
| wakar_poland | 1.16 / 1.14 M | 2.20 / 2.09 M | 0.91 / 1.11 M | 2.03 / 2.05 M | 94 / 92 % |
| wakar_poland_belarus | 1.20 / 1.16 M | 3.18 / 3.21 M | 0.91 / 1.15 M | 3.35 / 2.55 M | 93 / 89 % |
| nw_krai | 1.88 / 1.83 M | 4.65 / 4.64 M | 0.96 / 3.35 M | 2.42 / 7.10 M | 91 / 86 % |
| lit_bel | 1.83 / 1.86 M | 4.47 / 4.43 M | 0.96 / 3.29 M | 2.39 / 6.85 M | 91 / 86 % |
| plebiscite_poland | 1.95 / 1.91 M | 3.88 / 3.95 M | 1.20 / 3.26 M | 2.38 / 7.69 M | 91 / 89 % |

The two numbers of the computed line differ by the residual of whole
counties: under 70 k in most frames, up to 0.15 M (`federal_autonomy` and
the baseline, 2032), where a large county lies on the line. In
`plebiscite_poland` the new lands lie on the Polish side, and the exchange
starts slightly larger (1.95 M). The historical columns count the same
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
  north-east shift to Polish. The exchange grows to about 4.3 M each way
  around 2005 and 4.0 M in 2032, because both sides grow more mixed.
* **With the autonomies**, Belarusian and Ukrainian schooling slow the
  shift to Polish in the east, and the exchange grows less (3.2-3.5 M).
* **Wakar's Poland** starts with the smallest exchange (1.2 M).
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
