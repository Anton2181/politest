# Scenarios

Every scenario shares the premise: **no Second World War**. There is no
German-Soviet partition, no Holocaust, no deportations, no post-1945 border
shifts or population transfers (but for the hypothetical exchanges of
`curzon_exchange` and `curzon_exchange_identity`), and no communist regime. Everything else that
cannot be measured is a scenario choice. Scenarios are YAML files in
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
| `curzon_exchange` | The baseline, plus a **population exchange on 1 January 1946 along that year's equal-exchange Curzon line**. Every Pole (Polish at home) beyond the line moves to the Polish side and every counted non-Pole on the Polish side moves to the other side. The line follows county borders, so whole counties move and the two flows are equal to within one county. Movers take the places of those who left, weighted towards counties of their own language. Jews, Germans, Kashubians and Wymysorys speakers do not move. Nothing else changes (METHODOLOGY §12.8, `plsim/exchange.py`). | A thought experiment on the transfers of 1944-46 (Poles and Jews west; Ukrainians, Belarusians and Lithuanians east), but along a line drawn on the population and without the war that drove them. |
| `curzon_exchange_identity` | The same exchange **by declared nationality**: the line of 1946 is counted on national identity (Poles by Polish identity, whatever their home language), and every Pole by identity beyond it moves west and every counted non-Pole by identity on the Polish side moves east, each with home language and identity. Jews, Germans and Kashubians by identity do not move. | The agreements of 1944-46 went by nationality, not speech: Polish-identity speakers of Lithuanian or Belarusian were "Poles", and Ukrainian-identity speakers of Polish were "Ukrainians". |

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

35 of 270 counties change their plurality language by 2032, all of them
towards Polish except Klaipėda (German to Lithuanian):

* Belarusian → Polish in 12: Grodno, Wołkowysk, Bielsk Podlaski, Głębokie,
  Mołodeczno, Postawy, Wilejka, Baranowicze, Nieśwież, Nowogródek, Słonim,
  Stołpce.
* West Polesian → Polish in all nine Polesie counties. Polesie goes from
  12 to 69 % Polish.
* Kashubian → Polish in Kartuzy, Kościerzyna and Wejherowo.
* Ukrainian → Polish in nine Lwów counties (Dobromil, Drohobycz, Gródek,
  Lesko, Lubaczów, Rawa Ruska, Rudki, Sambor, Sokal) and Kamionka
  Strumiłowa.

The Lithuanian units' Poles fall from 152 k to 112 k, and the Lauda Poles
from 54 k to 37 k, although Polish is co-official in Lithuania. Polish
*identity* there falls about as fast, from 79 k to 62 k: with Polish
co-official, the Lithuanian state's pull on identity is weak (§6.7 of the
methodology).

**Migrants' children now assimilate** (the diaspora term, calibrated on
second-generation immigrants). Warsaw city ends 7 % Ukrainian-speaking
(13 % before the recalibration) and Silesia 4.5 % (8 %). A steady stream of
first-generation migrants keeps these shares from falling further.

**Identity and language part ways.** In 2032, Polish is the home language
of 70 % but the identity of 65.5 %: many who switch to Polish keep a
Ukrainian, Belarusian or Jewish identity. Jewish identity (7.2 %) outlasts
Yiddish (4.1 %). "Local" identities fall from 4.0 to 2.6 % as nation-building
turns Polesians and Belarusian speakers Belarusian, Ukrainian or Polish.

### Results: `ukraine_autonomy_tricantonal`

| Member | 1933 | 2032 | Home languages 1933 → 2032 |
|---|---|---|---|
| Poland (crown lands, 154 counties) | 20.1 M | 25.8 M | Polish 84 → 84 %, Yiddish 9 → 6 %, Ukrainian 1 → 5 % |
| Ukrainian autonomy (66) | 8.4 M | 9.6 M | Ukrainian 55 → 67 %, Polish 35 → 27 % |
| Lithuanian canton (23) | 2.42 M | 2.05 M | Lithuanian 78 → 82 %, Polish 6 → 8 % |
| Polish canton (Wilno–Lida–Grodno, 7) | 1.35 M | 1.68 M | Polish 58 → 57 %, Belarusian 23 → 29 % |
| Belarusian canton (20) | 2.56 M | 4.83 M | Belarusian 36 → 57 %, West Polesian 28 → 18 %, Polish 23 → 17 % |

* **Belarusian** speakers number 3.8 M in 2032, against 1.3 M in the
  baseline. They come from Belarusian schooling, from West Polesian
  speakers shifting to Belarusian instead of Polish, and from high Polesian
  fertility. Belarusian leads 9 of the canton's 20 counties in 1933 and 19
  in 2032: the nine Polesie counties, plus Wołożyn from Polish. Only
  Brasław stays Polish.
* **Ukrainian** speakers number 8.0 M, against 6.8 M in the baseline.
  Ukrainian leads 49 of the autonomy's 66 counties in 1933 and 56 in 2032.
  * Seven turn from Polish to Ukrainian: Lwów, Mościska, Przemyśl,
    Przemyślany, Skałat, Tarnopol and Trembowla.
  * The ten Polish-plurality counties left are all on or west of the San
    (Jarosław, Rzeszów, Sanok, Krosno ...).
  * Tarnopol voivodeship goes from 42 % Polish and 53 % Ukrainian to 32 and
    62 %; lwowskie as a whole from 37 to 47 % Ukrainian.
  * In those ten counties, Polish falls from 84 to 64 % and Ukrainian rises
    from 7 to 27 %. Both halves of lwowskie lie in the autonomy and form one
    migration unit, so rural migrants from either half settle in the towns
    of both.
* **In the crown lands**, Ukrainian rises from 1 to 5 % of speakers: the
  Chełm and Podlasie Ukrainians of Lublin (9 → 14 % of the voivodeship)
  and migrants to Warsaw, Silesia and Łódź. The baseline shows the same,
  slightly weaker.
* **Lithuanian Poles** rise from 153 k to 162 k; the Lauda Poles go from 54 k
  to 47 k (11 % of a shrinking Lauda). In the baseline they end at 37 k.
* **Polish** falls to 59.8 % of the whole union, against 70.1 % in the
  baseline. Wilno county grows to 495 k (708 k in the baseline), as the
  capital of a canton rather than of a large Polish province.

### Results: `autonomy_grand_duchy_coofficial`

The same Ukrainian autonomy, with an undivided Grand Duchy of 50 counties
working in Lithuanian, Polish and Belarusian. In 1933, Lithuanian leads 22
of its counties, Belarusian 11 (Grodno and Wołkowysk among them), Polish 7
and West Polesian 9.

| Grand Duchy | 1933 | 2032 |
|---|---|---|
| Population | 6.33 M | 8.67 M |
| Belarusian | 19 % | 38 % |
| Polish | 24 % | 23 % |
| Lithuanian | 31 % | 20 % |
| West Polesian | 11 % | 11 % |
| Yiddish | 8 % | 3 % |

* **Belarusian** becomes the Duchy's largest language (3.3 M speakers). It
  leads 22 counties in 2032: the nine Polesie counties, plus Lida and
  Wołożyn, which turn from Polish.
* **Polish** holds its share. It leads five counties (Wilno, Oszmiana,
  Święciany, Brasław, Szczuczyn) and spreads in the Lithuanian lands: their
  Poles grow from 154 k to 327 k (Polish identity from 81 k to 240 k), the
  Lauda Poles from 54 k to 77 k.
* **Lithuanian** keeps the plurality in its 23 counties, but the Lithuanian
  lands become mixed: Kaunas and the north-east fall from 71 to 60 %
  Lithuanian, Samogitia from 88 to 78 %. Migrants from the fast-growing
  east keep Belarusian, which is official there too, and Polish gains
  Lithuanian speakers. The number of Lithuanian speakers in the union
  (1.89 M) is the same as in the baseline.
* **Against the cantons:** one Duchy with free movement and three languages
  everywhere spreads Polish and Belarusian into the Lithuanian lands. The
  cantons keep each language's core (the Lithuanian canton is 82 %
  Lithuanian in 2032).

### Results: `wakar_poland` (Wakar's Poland)

Poland without Volhynia, Stanisławów, Tarnopol and the Vilnius region has
199 counties and 25.7 M people in 1933, 30.3 M in 2032. Belarusian is the
working language of 19 of them: Polesie, eastern Nowogródek, Głębokie,
Mołodeczno, Wilejka, Wołkowysk and Bielsk.

* **Belarusian** grows from 1.1 M speakers (4.2 %) to 3.4 M (11.2 %). It
  leads 18 counties in 2032 (10 in 1933): the nine Polesie counties pass
  from West Polesian, Wołożyn from Polish, and Bielsk and Wołkowysk turn
  Polish. Polesie goes from 7 to 48 % Belarusian (West Polesian 62 → 26 %,
  Polish 11 → 18 %).
* **Polish** goes from 73.9 to 74.5 % of the state.
* **Ukrainian** (lwowskie and Lublin, 5.9 %) has no official status here.
  Twelve Lwów counties turn Polish, three more than in the baseline, and
  Ukrainian falls from 37 to 28 % in lwowskie. It rises a little in Lublin
  (9 → 10 %).

### Results: `no_official_language`

* **Shares of the union in 2032:** Polish 57.6 % (70.1 % in the baseline),
  Ukrainian 18.9 %, Belarusian 8.2 % (3.6 M), Yiddish 5.7 % (2.5 M, against
  1.8 M), West Polesian 2.8 % (1.2 M). About 5 M more people speak a
  minority language at home than in the baseline.
* **Only 19 counties change their plurality language**, the fewest of any
  scenario:
  * Tarnopol, Trembowla and Przemyślany turn Ukrainian; Lubaczów turns
    Polish;
  * Lida and Wołożyn turn Belarusian; Bielsk Podlaski and Grodno turn
    Polish;
  * seven Polesie counties go from West Polesian to Belarusian. Kamień
    Koszyrski and Stolin stay West Polesian.
* **Shift still happens**, towards whichever language is large locally.
  Nowogródek goes from 52 to 59 % Belarusian, and Polesie from 7 to 37 %
  Belarusian (69 % Polish in the baseline). Towns and the west still pull
  towards Polish.
* **Migrants** keep their languages longer: their languages are official
  everywhere, so a city's Ukrainian or Belarusian community soon counts as
  complete and the diaspora term weakens. Warsaw city is 12 %
  Ukrainian-speaking in 2032 (7 % in the baseline) and 5 % Belarusian;
  Silesia 7 % Ukrainian.

### Results: `wakar_poland_belarus` (Wakar's Poland-Belarus)

Wakar's Poland plus Soviet Belarus has 211 counties and 31.1 M people in
1933 (5.4 M of them in Soviet Belarus), and 44.7 M in 2032.

| | 1933 | 2032 |
|---|---|---|
| Population | 31.1 M | 44.7 M |
| Polish | 61.1 % | 52.8 % |
| Belarusian | 17.0 % | 34.1 % (15.2 M speakers) |
| Ukrainian | 5.0 % | 3.3 % |
| Yiddish | 8.3 % | 4.1 % |
| West Polesian | 2.3 % | 2.0 % |
| Soviet Belarus: population | 5.4 M | 11.3 M |
| Soviet Belarus: Belarusian / Russian / Polish | 77 / 13 / 0.8 % | 85 / 8 / 4 % |

* **A Polish-Belarusian state.** Belarusian leads 31 counties in 2032 (22 in
  1933): all of Soviet Belarus, Polesie, eastern Nowogródek with Wołożyn,
  Wołkowysk and Głębokie–Mołodeczno–Wilejka.
* **Soviet Belarus** grows from 5.4 M to 11.3 M people under Polish-north-
  eastern vital rates. Russian, the language of its towns in 1926, falls from
  13 to 8 % as Belarusian and Polish (both official) take over. Polish rises
  from under 1 % to 4 %, mainly in the towns.
* **Polesie** goes from West Polesian (62 %) to Belarusian (53 %), as in
  Wakar's Poland.
* **Migration** carries Belarusian west. Warsaw city is 18 % Belarusian-
  speaking in 2032, Silesia 9 % and Lublin 5 %. The diaspora term does not
  bring this down: Belarusian is co-official throughout, and a community of
  this size in Warsaw counts as institutionally complete (its own schools,
  churches and press). In a Polish-Belarusian state that is a defensible
  outcome, comparable with the Swedish-speaking minority of interwar
  Helsinki.
* **Lwów** grows from 458 k to 707 k.

### Results: `nw_krai` and `lit_bel` (two states in one run)

Both runs hold two states: Poland without the krai, and the krai (or
Lit-Bel) as a separate state with Lithuanian, Belarusian, Polish, Yiddish and
Russian official (and Latvian in Latgale). The borders are those of the 1897
governorates: units that straddle them are cut (Kaunas and Alytus on the
Niemen, Kamień Koszyrski, and in Lit-Bel the Połock, Bobrujsk, Homel and
Rzeczyca okrugs on the Minsk governorate's border).

| | 1933 | 2032 |
|---|---|---|
| **`nw_krai`**: Poland (224 units, with the Suwałki governorate) | 28.34 M | 34.75 M |
| Northwestern Krai (65 units) | 12.85 M | 27.43 M |
| of which the Soviet-Belarusian lands | 5.46 M | 13.67 M |
| of which Latgale, Nevel-Sebezh-Velizh and eastern Mogilev | 1.11 M | 2.68 M |
| **`lit_bel`**: Poland (216 units) | 27.78 M | 34.49 M |
| Lit-Bel (60 units, with the Suwałki governorate) | 9.33 M | 17.69 M |
| of which the Soviet-Belarusian lands (Minsk governorate) | 2.50 M | 6.20 M |

Home languages in the krai states:

| | Krai 1933 | Krai 2032 | Lit-Bel 1933 | Lit-Bel 2032 |
|---|---|---|---|---|
| Belarusian | 47.6 % | 66.6 % | 35.3 % | 55.4 % |
| Polish | 15.0 % (1.93 M) | 11.2 % (3.07 M) | 21.7 % (2.03 M) | 18.3 % (3.23 M) |
| Lithuanian | 12.4 % (1.59 M) | 5.9 % (1.62 M) | 20.4 % (1.90 M) | 11.2 % (1.97 M) |
| Russian | 7.9 % | 7.5 % | 4.9 % | 4.6 % |
| Yiddish | 7.8 % | 3.3 % | 8.4 % | 3.8 % |
| West Polesian | 5.1 % | 3.4 % | 7.0 % | 5.3 % |
| Latvian | 2.5 % | 1.2 % | - | - |
| Units led by Belarusian / Lithuanian / Polish / W. Polesian / Latvian | 28 / 16 / 9 / 9 / 3 | 42 / 16 / 6 / 0 / 1 | 20 / 20 / 11 / 9 / - | 32 / 20 / 8 / 0 / - |

* **The krai becomes a Belarusian state.** Belarusian is the language of
  the majority and the standard of the Polesians. The Polesie counties go
  from West Polesian to Belarusian, and so do Lida, Szczuczyn and Wołożyn,
  from Polish. In Latgale, Dyneburg and Lucyn turn from Latvian to
  Belarusian (Latvian 54 → 29 % of Latgale, Belarusian 15 → 32 %): Latvian
  is official there, but the krai's majority language draws the migrants
  and the mixed families. Rzeżyca stays Latvian. By identity the krai is
  60 % Belarusian, 13 % Polish, 9 % Russian and 6 % Lithuanian in 2032.
* **Cities.** Wilno county grows from 417 k to 806 k and stays
  Polish-plurality, but falls from 71 to 49 % Polish, with Belarusian
  from 5 to 33 %: migrants from its Belarusian hinterland settle there
  instead of going to Warsaw. Białystok county (Grodno governorate) falls
  from 65 to 46 % Polish (Belarusian 9 to 38 %). Mińsk okrug grows from
  593 k to 1.93 M. The Lithuanian counties stay Lithuanian.
* **Polish holds on in absolute numbers.** As an official language with its
  own schools, Polish grows from 1.9 to 3.1 M speakers in the krai, though
  its share falls. In the krai's Lithuanian lands, Polish speakers grow
  from 145 k to 329 k, and those with a Polish identity from 72 k to
  238 k (Lit-Bel, which also holds Suvalkija: 155 k to 454 k and 79 k to
  346 k): Polish is official there and Wilno is next door. Lithuanian
  barely grows (1.59 to 1.62 M in the krai), as in the baseline: the model
  gives the Lithuanian lands an earlier fall in fertility and slightly more
  emigration.
* **Suvalkija in Poland** (`nw_krai`). The Suwałki governorate belonged to
  the Kingdom of Poland, so Marijampolė, Vilkaviškis, Šakiai, Lazdijai and
  the west banks at Alytus and Kaunas go to Poland, with Lithuanian
  co-official: 0.55 M people in 1933, 0.52 M in 2032. They stay
  Lithuanian-plurality, except Kaunas's small west bank (Aleksotas), which
  turns Polish.
* **Fast growth.** The krai grows 2.1-fold, its Soviet-Belarusian part
  2.5-fold and its eastern lands 2.4-fold, against 1.23-fold for Poland.
  Two causes:
  * the fertility transition is late in these lands: 3.2 children per woman
    in the krai in 1970 and 2.3 in 1990 (3.4 and 2.35 in its
    Soviet-Belarusian part), against 2.4 and 1.9 in Poland. This was
    checked against rural eastern Poland in the real 1970s and 1980s
    (about 2.9 in 1970, 2.4-2.6 in 1990), the closest analogue to these
    lands without Soviet industrialisation; the real BSSR, urbanised fast,
    had about 2.3 and 1.9. The model's fertility transition was tightened
    for this (METHODOLOGY §4.2): before, the krai's Soviet-Belarusian part
    still had 3.6 in 1970 and 2.7 in 1990;
  * as a separate state the krai sends few migrants to Polish cities
    (friction 0.03): its lands that are Polish in the baseline grow from
    4.4 to 8.7 M, against 4.4 to 7.4 M in the baseline.

  This growth is the least certain result of these scenarios.
* **Separate economies.** Each state has its own income, converging at the
  same rate to the same target. The krai starts at about two-thirds of
  Poland's income per head (1,230 against 1,930 GK$ in 1931) and closes most
  of the gap by 2032 (16,300 against 17,500). Its lower income keeps its
  emigration hump later and its transport budget smaller.
* **Poland** is 68.7 % Polish in 1933 and 73.6 % in 2032, with Ukrainian
  17.0 → 19.4 % (`nw_krai`; `lit_bel` alike). Without the krai it is the
  baseline's Poland less its north-east: the same nine Ukrainian counties
  of lwowskie turn Polish. Poland ends at 34.7 M in `nw_krai` and 34.5 M in
  `lit_bel`; the first holds 0.5 M more in the Suwałki governorate, and the
  rest of the difference is the noise of single seeded runs (an earlier
  pair of runs, with slightly different county pieces, put it at 1.5 M the
  other way).

### Results: `curzon_exchange` and `curzon_exchange_identity`

On 1 January 1946 the equal-exchange line of that year moves **2.35 M Poles
to the Polish side and 2.33 M others to the other side**; the line follows
county borders, so the two flows differ by up to one county's worth. The
Poles settle where the non-Poles left. The others (Ukrainian 1.31 M,
Belarusian 0.59 M, Lemko 0.12 M, Lithuanian 0.10 M, Russian 0.09 M, West
Polesian 0.04 M, Romani 0.03 M, 0.05 M of other languages and a few Czechs,
Karaims and Latvians) settle where the Poles left, mostly in counties of
their own language.

In 1946 the line keeps on the Polish side all of Lublin, the Białystok
lands but for Wołkowysk, the western Wilno lands (Wilno, Oszmiana,
Święciany, Postawy) with Lida, Szczuczyn and Wołożyn, seventeen counties of
lwowskie with Lwów, and five of Tarnopol's (Tarnopol, Trembowla,
Przemyślany, Zborów, Kamionka Strumiłowa). Polesie, Volhynia, Stanisławów,
the eastern Wilno and Nowogródek lands and Lithuania are on the other side.

**By declared nationality** (`curzon_exchange_identity`). The agreements of
1944-46 went by nationality, not language, and so does this variant
(`curzon_count: identity`, `population_exchange.by: identity`): the line is
drawn counting people of Polish identity as Poles, and those who move are
the people of Polish identity on the other side and of the other
identities on the Polish side; Jews, Germans and Kashubians stay. It moves
**2.43 M to the Polish side** (1.96 M of them Polish-speaking, 0.27 M
Ukrainian-speaking and 0.13 M Belarusian-speaking Poles: Latin-rite
Ruthenian speakers and Catholic Belarusian speakers) and **2.56 M to the
other side**: by identity 1.42 M Ukrainians, 0.40 M Belarusians, 0.34 M
"locals" (tutejsi, mostly Polesians), 0.13 M Lithuanians, 0.12 M
Russians and 0.08 M Lemkos (Rusyns). Among them are 95 k Polish speakers of
another identity, Polish-speaking Lithuanians, Belarusians and Ukrainians,
who move east, not west. The line keeps Wołkowysk, Sambor, Brzeżany,
Podhajce and Złoczów on the Polish side as well.

| | baseline 2032 | exchange by language | by nationality |
|---|---|---|---|
| Polish speakers | 31.04 M | 30.50 M | 30.70 M |
| Ukrainian speakers | 6.85 M | 7.13 M | 7.04 M |
| Belarusian speakers | 1.29 M | 1.37 M | 1.32 M |
| Lithuanian speakers | 1.88 M | 1.92 M | 1.91 M |
| Lwów voivodeship, Polish | 60 % | 70 % | 70 % |
| Lublin voivodeship, Ukrainian | 12 % | 2 % | 3 % |
| Volhynia, Polish | 33 % | 24 % | 24 % |
| Lithuanian units: Polish speakers | 112 k | 15 k | 64 k |
| of whom Lauda | 37 k | 3 k | 21 k |
| Lithuanian units: Polish identity | 62 k | 28 k | 12 k |

* **Clean lines, smaller assimilation.** After the exchange the minorities
  live in compact areas where they are the majority, so fewer of their
  children grow up as a scattered minority. By 2032 there are slightly
  *more* minority speakers than without the exchange, and slightly fewer
  Polish speakers. This is the opposite of the exchange's demographic
  intention.
* **Who counts as a Pole.** Counted by language, Polish-speaking
  Lithuanians by identity, such as many Lauda gentry, move west with the
  Poles (the Lauda Poles fall from 54 k to 3 k: all of Lithuania lies on the
  other side). Counted by nationality, they stay: 64 k Polish speakers
  remain in Lithuania (21 k of them in Lauda), but only 12 k people of
  Polish identity. Conversely, the Latin-rite Ukrainian speakers and
  Catholic Belarusian speakers of Polish identity move west, and the
  exchange by nationality leaves slightly fewer minority speakers than the
  exchange by language (Ukrainian 7.04 against 7.13 M in 2032).

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
| baseline | 1.84 / 1.85 M | 4.39 / 4.33 M | 0.96 / 3.27 M | 2.38 / 9.02 M | 91 / 86 % |
| ii_rp_only | 1.71 / 1.74 M | 4.28 / 4.14 M | 0.95 / 3.13 M | 2.33 / 8.88 M | 92 / 87 % |
| federal_autonomy | 1.84 / 1.86 M | 4.99 / 4.55 M | 0.96 / 3.28 M | 3.54 / 6.84 M | 91 / 83 % |
| integral_nationalism | 1.84 / 1.85 M | 4.78 / 4.91 M | 0.96 / 3.27 M | 1.80 / 10.80 M | 91 / 86 % |
| polonizing_union | 1.84 / 1.85 M | 4.97 / 4.93 M | 0.96 / 3.27 M | 2.36 / 9.25 M | 91 / 85 % |
| census_official | 1.80 / 1.82 M | 3.91 / 3.93 M | 0.72 / 3.81 M | 1.84 / 9.60 M | 92 / 88 % |
| census_vernacular | 1.69 / 1.68 M | 4.54 / 4.48 M | 1.14 / 2.44 M | 2.60 / 8.77 M | 91 / 86 % |
| ukraine_autonomy_tricantonal | 1.84 / 1.86 M | 3.28 / 3.30 M | 0.96 / 3.28 M | 3.03 / 4.07 M | 91 / 88 % |
| autonomy_grand_duchy_coofficial | 1.84 / 1.86 M | 3.56 / 3.54 M | 0.96 / 3.28 M | 3.09 / 4.12 M | 91 / 87 % |
| no_official_language | 1.84 / 1.86 M | 4.23 / 4.21 M | 0.96 / 3.28 M | 4.20 / 4.44 M | 91 / 84 % |
| wakar_poland | 1.20 / 1.13 M | 2.27 / 2.08 M | 0.91 / 1.13 M | 2.25 / 1.94 M | 94 / 90 % |
| wakar_poland_belarus | 1.20 / 1.17 M | 3.32 / 3.33 M | 0.91 / 1.17 M | 3.72 / 2.51 M | 94 / 86 % |
| nw_krai | 1.83 / 1.88 M | 4.89 / 4.74 M | 0.96 / 3.32 M | 2.58 / 6.97 M | 91 / 83 % |
| lit_bel | 1.83 / 1.86 M | 4.48 / 4.48 M | 0.96 / 3.30 M | 2.49 / 6.69 M | 91 / 84 % |
| curzon_exchange | 1.84 / 1.85 M | 3.53 / 3.48 M | 0.96 / 3.27 M | 1.79 / 8.33 M | 91 / 89 % |

The two numbers of the computed line differ by the residual of whole
counties: under 70 k in most frames, up to 0.19 M (Wakar's Poland, 2032)
and 0.44 M (`federal_autonomy`, 2032), where a large county lies on the
line. The historical columns count the same people on either side of the
Curzon line of 1919-20 (line A in Galicia), which is not balanced: it leaves
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
* **Over the century** the Polish side spreads east as Polesie (seven of
  its nine counties by 2032) and the north-east shift to Polish, while
  Tarnopol's Polish counties fall to the other side. The exchange grows to
  4.4 M each way, because both sides grow more mixed.
* **With the autonomies**, Belarusian and Ukrainian schooling slow the
  shift to Polish in the east, and the exchange grows less (3.3-3.6 M). By
  2032 Lwów and Przemyśl, turned Ukrainian-plurality, are on the other
  side.
* **Wakar's Poland** starts with the smallest exchange (1.2 M).
* **Whole counties against free lines.** The earlier line, which could
  wind cell by cell through counties, needed 1.89 M each way in 1932. The
  county line needs slightly fewer (1.84-1.85 M), because the cell search,
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
