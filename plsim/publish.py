"""Build the results page (standalone ``report.html`` and a fragment for
publishing) from the files written by ``python -m plsim report``."""
from __future__ import annotations

import base64
import csv
import html
import os

import pandas as pd

LANG_NAMES = {"pl": "Polish", "uk": "Ukrainian", "be": "Belarusian", "pls": "West Polesian", "yi": "Yiddish",
              "de": "German", "ru": "Russian", "lt": "Lithuanian", "csb": "Kashubian", "rue": "Lemko-Rusyn",
              "cs": "Czech", "lv": "Latvian", "rom": "Romani", "kdr": "Karaim", "wym": "Wymysorys", "oth": "Other"}

SCENARIO_NOTES = {
    "baseline": "Polish-Lithuanian federation, easing assimilation pressure, 1939 plans executed, southern-European convergence",
    "ii_rp_only": "The Second Republic alone in its 1938 borders",
    "federal_autonomy": "Ukrainian autonomy in Stanisławów, Tarnopol and Volhynia; Belarusian schools",
    "integral_nationalism": "Coercive Polonisation, emigrationist policy towards Jews, heavy eastern settlement",
    "polonizing_union": "Unitary union with Polish dominant in the Lithuanian lands too",
    "census_official": "Baseline from the 1931 and 1923 censuses as printed",
    "census_vernacular": "Baseline from an upper-bound start (Kubijovyč; Catholic Belarusian speech as in 1897)",
    "ukraine_autonomy_tricantonal": "Ukrainian autonomy (Lwów, Tarnopol, Stanisławów, Volhynia) and a Grand Duchy of "
                                    "Lithuanian, Polish and Belarusian cantons east of the Curzon line",
    "autonomy_grand_duchy_coofficial": "Ukrainian autonomy and an autonomous Grand Duchy with Lithuanian, Polish "
                                       "and Belarusian co-official",
    "wakar_poland": "Wakar's Poland: without Volhynia, Stanisławów, Tarnopol and the Lithuanian-claimed Wilno "
                    "lands; Polish and Belarusian co-official",
    "wakar_poland_belarus": "Wakar's Poland-Belarus: Wakar's Poland together with all of Soviet Belarus; Polish and "
                            "Belarusian co-official",
    "no_official_language": "Poland with no official language (all languages equal); Lithuania as in the baseline",
    "curzon_exchange": "Baseline with an equal population exchange in 1946 along that year's computed Curzon line",
}
ID_NAMES = {"pl": "Polish", "uk": "Ukrainian", "be": "Belarusian", "lt": "Lithuanian", "jw": "Jewish",
            "de": "German", "loc": "Local ('tutejszy')"}

CSS = """
/* Layout: one reading column for prose, a wider column for figure plates and tables. */
:root {
  --bg: #f4f5f2; --fg: #15171b; --muted: #595e66; --rule: #d6d9d2; --accent: #a3271c;
  --plate: #fcfcfb; --plate-ink: #15171b; --chip: #e7e9e3; --good: #1d7a2e; --bad: #b3261e;
  --display: "IBM Plex Sans Condensed", "Arial Narrow", system-ui, sans-serif;
  --body: "Source Serif 4", Georgia, "Times New Roman", serif;
  --data: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #121418; --fg: #e9eae6; --muted: #a4a9b0; --rule: #2c3036; --accent: #e57a6a;
    --plate: #fcfcfb; --plate-ink: #15171b; --chip: #22262c; --good: #6cc47a; --bad: #f08a7e; color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #121418; --fg: #e9eae6; --muted: #a4a9b0; --rule: #2c3036; --accent: #e57a6a;
  --plate: #fcfcfb; --plate-ink: #15171b; --chip: #22262c; --good: #6cc47a; --bad: #f08a7e; color-scheme: dark;
}
body { background: var(--bg); color: var(--fg); font-family: var(--body); font-size: 17px; line-height: 1.55;
  margin: 0; }
.wrap { max-width: 76rem; margin: 0 auto; padding-inline: 16px; padding-block: 40px 72px;
  display: flex; flex-direction: column; gap: 28px; }
.prose { max-width: 66ch; }
header.mast { display: flex; flex-direction: column; gap: 10px; border-bottom: 2px solid var(--fg); padding-bottom: 20px; }
.eyebrow { font-family: var(--data); font-size: 12.5px; letter-spacing: .08em; text-transform: uppercase; color: var(--accent); }
h1 { font-family: var(--display); font-weight: 600; font-size: clamp(2rem, 4.5vw, 3.1rem); line-height: 1.05;
  margin: 0; text-wrap: balance; letter-spacing: -.01em; }
h2 { font-family: var(--display); font-weight: 600; font-size: 1.6rem; margin: 0; text-wrap: balance; }
h3 { font-family: var(--display); font-weight: 600; font-size: 1.15rem; margin: 0; }
section { display: flex; flex-direction: column; gap: 14px; padding-top: 22px; border-top: 1px solid var(--rule); }
p { margin: 0; }
.lede { font-size: 1.2rem; color: var(--fg); }
.meta { font-family: var(--data); font-size: 13px; color: var(--muted); }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr)); gap: 12px; }
.tile { background: var(--chip); padding: 14px 16px; display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.tile .k { font-family: var(--data); font-size: 12px; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
.tile .v { font-family: var(--display); font-weight: 600; font-size: 1.9rem; line-height: 1.1; }
.tile .s { font-size: 14px; color: var(--muted); }
figure { margin: 0; display: flex; flex-direction: column; gap: 8px; }
figure .plate { background: var(--plate); color: var(--plate-ink); padding: 10px; border: 1px solid var(--rule); }
figure img { display: block; width: 100%; height: auto; max-width: 100%; }
figcaption { font-size: 15px; color: var(--muted); max-width: 70ch; }
.tablebox { overflow-x: auto; border-top: 1px solid var(--fg); }
table { border-collapse: collapse; width: 100%; font-family: var(--data); font-size: 13px; font-variant-numeric: tabular-nums; }
caption { caption-side: top; text-align: left; font-family: var(--body); font-size: 14px; color: var(--muted); padding: 8px 0; }
th, td { padding: 6px 10px; border-bottom: 1px solid var(--rule); text-align: right; white-space: nowrap; }
th { font-weight: 600; color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }
th:first-child, td:first-child { text-align: left; white-space: normal; }
td.pass { color: var(--good); font-weight: 600; } td.fail { color: var(--bad); font-weight: 600; }
.two { display: grid; grid-template-columns: repeat(auto-fit, minmax(20rem, 1fr)); gap: 24px; }
.two > * { min-width: 0; }
ul { margin: 0; padding-left: 1.2em; display: flex; flex-direction: column; gap: 6px; }
code, pre { font-family: var(--data); font-size: 13.5px; }
pre { background: var(--chip); padding: 12px 14px; overflow-x: auto; margin: 0; }
a { color: var(--accent); }
a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.note { font-size: 15px; color: var(--muted); }
"""


def _img(path: str, alt: str) -> str:
    with open(path, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode()
    return f'<img alt="{html.escape(alt)}" loading="lazy" src="data:image/png;base64,{b64}">'


def _fig(figdir: str, name: str, alt: str, caption: str) -> str:
    path = os.path.join(figdir, name)
    if not os.path.exists(path):
        return ""
    return (f'<figure><div class="plate">{_img(path, alt)}</div>'
            f"<figcaption>{caption}</figcaption></figure>")


def _table(header, rows, caption="", classes=None) -> str:
    h = "".join(f"<th>{html.escape(str(x))}</th>" for x in header)
    body = []
    for r in rows:
        cells = []
        for j, x in enumerate(r):
            cls = ""
            if classes and j in classes:
                cls = f' class="{classes[j](x)}"'
            cells.append(f"<td{cls}>{html.escape(str(x))}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    cap = f"<caption>{html.escape(caption)}</caption>" if caption else ""
    return f'<div class="tablebox"><table>{cap}<thead><tr>{h}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def _read_csv(path):
    with open(path, encoding="utf-8") as fh:
        return list(csv.reader(fh))


def _csv_or_none(path):
    return _read_csv(path) if os.path.exists(path) else None


def _extra_sections(outroot: str, end: int) -> dict:
    """HTML of the sections on calibration, identity, ensemble certainty and the
    Curzon line (empty strings where the inputs are missing)."""
    out = {}
    mapdir, caldir = os.path.join(outroot, "maps"), os.path.join(outroot, "calibration")
    # calibration
    tg = _csv_or_none(os.path.join(caldir, "targets.csv"))
    pr = _csv_or_none(os.path.join(caldir, "parameters.csv"))
    if tg and pr:
        trows = [[r[1], r[2], r[3], r[5], r[6], r[7], r[8]] for r in tg[1:]]
        ttab = _table(["Case", "Measure", "Observed", "Before", "I", "Now", "I"], trows,
                      "History-matching targets: observed value, the model before and after calibration, and the "
                      "implausibility I (distance in standard deviations of observation and model error; > 3 rules out)")
        prows = [[r[0], r[1], f"{r[2]}-{r[4]}", r[5], "yes" if r[6] == "1" else "no (kept)"] for r in pr[1:]]
        ptab = _table(["Parameter", "Before", "Not ruled out (5-95 %)", "Now", "Constrained"], prows,
                      "Language-shift parameters before and after history matching")
        out["calibration"] = f"""
<section>
  <h2>Calibrating language shift on history</h2>
  <p class="prose">The model starts in 1931 and cannot be run backwards. The obvious Polish comparisons also measure
  something else. Between the 1921 nationality census and the 1931 mother-tongue census the question changed. Between
  1897 and 1931 came the 1915 evacuations, two wars and another change of question. So the shift rates were matched to
  cases where a minority language was counted the same way at both ends:</p>
  <ul class="prose">
    <li><b>Masurian districts, 1890-1910:</b> a same-faith vernacular under a modern state language, like the Catholic
    Belarusian speakers.</li>
    <li><b>Carinthian Slovenes, 1880-1910:</b> a standardised same-faith national language, like the Lithuanians.</li>
    <li><b>Wales, 1921-1951:</b> Welsh speakers and Welsh monolinguals.</li>
    <li><b>Prussian Poles, 1871-1910:</b> a different-faith nation with strong institutions; almost no shift.</li>
    <li><b>Second-generation immigrants:</b> from US census evidence.</li>
  </ul>
  <p class="prose">4,000 parameter draws in two waves were run through the model's own language code on stylised
  populations. 279 were not ruled out by any case. The adopted values are the medians of that set:</p>
  <ul class="prose">
    <li>Same-faith national minorities shift about three times faster than assumed before.</li>
    <li>Catholic Belarusian speakers shift a little slower.</li>
    <li>A new diaspora term makes scattered speakers and migrants' children shift within two or three generations.</li>
    <li>Schools teach the state language faster.</li>
  </ul>
  <p class="prose">The ensemble draws its language parameters jointly from the not-ruled-out set.</p>
  {_fig(caldir, "history_matching.png", "History matching", "Grey: all draws; blue: draws not ruled out; red: previous value; green: adopted.")}
  <div class="two">{ttab}{ptab}</div>
  <p class="note prose">The model's frequency effect is weaker than in Masuria, where the share fell fastest where it was
  smallest (Oletzko). German settlement and the Masurians' own departure for the Ruhr concentrated there too, and are not
  in the stylised case.</p>
</section>"""
    # identity
    idt = _csv_or_none(os.path.join(outroot, "identity_summary.csv"))
    if idt:
        bl = [r for r in idt[1:] if r[0] == "baseline"]           # start and end rows
        facts = ""
        if len(bl) == 2 and bl[0][10]:
            s0, s1 = bl
            facts = (f" In the baseline, Polish is the home language of {s1[9]} % in {s1[1]} but the identity of {s1[2]} %: "
                     f"many who switch to Polish keep a Ukrainian, Belarusian or Jewish identity. Jewish identity "
                     f"({s0[6]} -> {s1[6]} %) outlasts Yiddish, and 'local' identities give way to Belarusian and "
                     f"Ukrainian ({s0[8]} -> {s1[8]} % local). In the Lithuanian member, with Polish co-official, the pull "
                     f"of the Lithuanian state on identity is weak: Polish identity ({s0[11]} -> {s1[11]} thousand) falls "
                     f"about as fast as Polish speech ({s0[10]} -> {s1[10]} thousand speakers).")
        rows = []
        for r in idt[1:]:
            rows.append([r[0], r[1]] + r[2:9] + [r[9]] + ([f"{r[10]} / {r[11]}"] if r[10] else ["-"]))
        itab = _table(["Scenario", "Year"] + [ID_NAMES[k] for k in ["pl", "uk", "be", "lt", "jw", "de", "loc"]]
                      + ["Polish at home", "Lithuania: Polish speakers / Polish identity (k)"], rows,
                      "National identity (% of residents) against home language, one seeded run per scenario")
        out["identity"] = f"""
<section>
  <h2>National identity, apart from language</h2>
  <p class="prose">Identity is tracked separately from home language. Catholic Belarusian speakers mostly call
  themselves Poles, Polesian villagers "local", Polish-speaking Jews Jews. A language switcher keeps the old identity
  four times in ten. "Local" identities turn national as schools and newspapers arrive. The state nation pulls slowly,
  and much more slowly when identity and home language agree. Nationality censuses (1921, 1923, today) read identity;
  mother-tongue censuses read language.{facts}</p>
  {_fig(mapdir, "map_identity.png", "Identity map", "Top: most common home language of each 3.5 km cell. Bottom: most common national identity of each county.")}
  {itab}
</section>"""
    # ensemble certainty
    if os.path.exists(os.path.join(mapdir, "map_uncertainty.png")):
        out["uncertainty"] = f"""
<section>
  <h2>How certain are the maps?</h2>
  <p class="prose">Every member of the baseline ensemble was downscaled to the 3.5 km grid. The left maps show the
  language most likely to lead each cell, paler where the runs disagree. The others give the share of runs in which
  Belarusian, Ukrainian or Lithuanian still leads. About one cell in twenty has a leader that fewer than 80 % of the
  runs agree on. They lie on two frontiers: the Belarusian-Polish transition in the north-east, where by 2032 Belarusian
  keeps its lead only in parts of Nowogródek and the eastern Wilno lands and in only some runs, and the mixed Polish-Ukrainian
  belt of western Galicia between the San and Lwów. In 1982 the Polesian marshes are a third: whether West Polesian or
  Polish leads there depends on the run. Lithuanian leads the same cells in every run.</p>
  {_fig(mapdir, "map_uncertainty.png", "Ensemble certainty", "Ensemble certainty, 1982 and 2032.")}
</section>"""
    # Curzon line
    cz = _csv_or_none(os.path.join(mapdir, "baseline_curzon.csv"))
    ex = _csv_or_none(os.path.join(outroot, "exchange_summary.csv"))
    if cz and "hist_west_others" in cz[0]:
        h = cz[0]
        ix = {k: h.index(k) for k in h if k != "line_lon_lat"}
        crows = []
        for r in cz[1:]:
            if int(r[0]) not in (1932, 1950, 1970, 1990, 2010, end):
                continue
            M = lambda k: f"{float(r[ix[k]]) / 1e6:.2f}"  # noqa: E731
            crows.append([r[0], M("west_others"), M("east_poles"), M("hist_west_others"), M("hist_east_poles"),
                          M("hist_east_others")])
        ctab = _table(["Year", "Computed line: non-Poles west (M)", "Poles east (M)", "1919-20 line: non-Poles west (M)",
                       "Poles east (M)", "non-Poles east (M)"], crows,
                      "Baseline: people on the 'wrong' side of the computed equal-exchange line and of the historical "
                      "Curzon line (Kashubians, Wymysorys speakers, Germans and Jews not counted)")
        etab = ""
        if ex and len(ex) > 1:
            erows = [[r[2], LANG_NAMES.get(r[3], r[3]), f"{int(float(r[4])):,}"] for r in ex[1:]]
            etab = _table(["Moves", "Home language", "Persons"], erows,
                          f"Population exchange of 1 January {ex[1][1]} along the computed line (scenario curzon_exchange)")
        out["curzon"] = f"""
<section>
  <h2>The Curzon line: computed, historical, and an exchange</h2>
  <p class="prose">The equal-exchange line splits the state so that as many non-Poles stay on its Polish side as Poles
  on the other side, with the most Poles on the Polish side. It follows the modelled population cell by cell. The
  historical line of 1919-20 followed the ethnographic maps of its day, with "line A" in Galicia. The table counts the
  same people on the wrong side of each.</p>
  {_fig(mapdir, "map_curzon.png", "Curzon line", "The computed equal-exchange line in 1932, 1982 and 2032.")}
  {ctab}
  <p class="prose">The scenario <b>curzon_exchange</b> carries out the exchange on 1 January 1946. Every Pole beyond that
  year's line moves to the Polish side, and every counted non-Pole on the Polish side moves to the other side. Each
  takes the place of someone who left, weighted towards counties of their own language. The economy and policy are
  untouched.</p>
  {_fig(mapdir, "curzon_exchange_before_after.png", "Exchange", "Most widely spoken home language before and after the exchange.")}
  {etab}
</section>"""
    return out


def build_page(outroot: str, standalone: bool = True) -> str:
    figdir = os.path.join(outroot, "figures")
    nat = pd.read_csv(os.path.join(outroot, "ensemble_baseline", "ensemble_national.csv"))
    lang = pd.read_csv(os.path.join(outroot, "ensemble_baseline", "ensemble_languages.csv"))
    km = pd.read_csv(os.path.join(outroot, "ensemble_baseline", "ensemble_network_km.csv"))
    n_members = "32"
    end = int(nat.year.max())
    r_end = nat[nat.year == end].iloc[0]
    peak_i = nat.pop_total_p50.idxmax()
    l0, l1 = lang.iloc[0], lang.iloc[-1]
    t0 = nat.iloc[0].pop_total_p50
    t1 = r_end.pop_total_p50

    def share(row, code, tot):
        return row[f"{code}_p50"] / tot * 100

    k_end = km.iloc[-1]
    tiles = [
        ("Population, 2032", f"{t1 / 1e6:.1f} M", f"5-95 %: {r_end.pop_total_p5 / 1e6:.0f}-{r_end.pop_total_p95 / 1e6:.0f} M; "
                                                   f"peak {nat.pop_total_p50[peak_i] / 1e6:.1f} M in {int(nat.year[peak_i])}"),
        ("Speak Polish at home", f"{share(l1, 'pl', t1):.0f} %", f"from {share(l0, 'pl', t0):.0f} % in 1933, union-wide"),
        ("Speak Ukrainian", f"{share(l1, 'uk', t1):.0f} %", f"{l1['uk_p50'] / 1e6:.1f} M speakers, from {l0['uk_p50'] / 1e6:.1f} M"),
        ("Speak Yiddish", f"{l1['yi_p50'] / 1e6:.1f} M", "kept alive mainly by a growing Haredi population"),
        ("Motorway and expressway", f"{(k_end.road_motorway_p50 + k_end.road_express_p50) / 1e3:.0f}k km",
         f"{k_end.rail_hsr_p50:,.0f} km of high-speed rail"),
    ]
    tile_html = "".join(f'<div class="tile"><span class="k">{html.escape(k)}</span><span class="v">{html.escape(v)}</span>'
                        f'<span class="s">{html.escape(s)}</span></div>' for k, v, s in tiles)

    krows = []
    for y in [1939, 1950, 1960, 1970, 1990, 2010, end]:
        r = nat[nat.year == y].iloc[0]
        krows.append([y, f"{r.pop_total_p50 / 1e6:.1f}", f"{r.pop_total_p5 / 1e6:.1f}-{r.pop_total_p95 / 1e6:.1f}",
                      f"{r.pop_pl_p50 / 1e6:.1f}", f"{r.pop_lt_p50 / 1e6:.2f}", f"{r.tfr_p50:.2f}",
                      f"{r.e0_male_p50:.1f} / {r.e0_female_p50:.1f}", f"{r.urban_share_p50 * 100:.0f}",
                      f"{r.y_nat_p50:,.0f}", f"{(r.emig_p50 - r.immig_p50) / 1e3:+.0f}k".replace("+", "-", 1)
                      if r.emig_p50 >= r.immig_p50 else f"+{(r.immig_p50 - r.emig_p50) / 1e3:.0f}k"])
    ktab = _table(["Year", "Pop. (M)", "5-95 %", "Polish units", "Lithuanian units", "TFR", "e0 m / f", "Urban %",
                   "GDP/head", "Net migration"], krows,
                  f"Baseline ensemble, {n_members} members: medians unless stated. GDP in 1990 Geary-Khamis dollars; "
                  "net migration is international, per year.")

    lrows = []
    for code in ["pl", "uk", "yi", "lt", "be", "pls", "de", "ru", "csb", "rue", "rom", "cs", "lv", "kdr", "wym"]:
        a, b = l0[f"{code}_p50"], l1[f"{code}_p50"]
        lrows.append([LANG_NAMES[code], f"{a:,.0f}", f"{b:,.0f}", f"{l1[f'{code}_p5']:,.0f}-{l1[f'{code}_p95']:,.0f}",
                      f"{(b / a - 1) * 100:+.0f} %" if a > 0 else "-"])
    ltab = _table(["Home language", "1933", str(end), f"{end} 5-95 %", "Change"], lrows,
                  "Home speakers, whole union, baseline ensemble medians")

    val = _read_csv(os.path.join(outroot, "validation.csv"))
    vtab = _table(val[0], val[1:], "Seeded baseline run against registered 1930s statistics and comparator guard rails",
                  classes={0: lambda x: "pass" if x == "PASS" else "fail"})
    cc = _read_csv(os.path.join(outroot, "census_consistency.csv"))
    ctab = _table(cc[0], cc[1:], "National shares (%) implied by each reconstruction, read directly or through the "
                                 "1931 census observation model, against the printed census")

    ss = _read_csv(os.path.join(outroot, "scenario_summary.csv"))
    head = ["Scenario", "Polish units (M)", "Lithuanian units (M)", "Polish %", "Ukrainian %", "Yiddish %",
            "Belarusian %", "Lithuanian %", "W. Polesian (k)", "Kashubian (k)", "GDP/head", "Electrified + HSR km",
            "Expressway + motorway km"]
    srows = [r for r in ss[1:]]
    stab = _table(head, srows, f"End-year ({end}) outcomes, one seeded run per scenario with common random numbers")
    scen_list = "".join(f"<li><b>{html.escape(n)}</b>: {html.escape(d)}</li>" for n, d in SCENARIO_NOTES.items())

    proj = pd.read_csv(os.path.join(outroot, "runs", "baseline", "network_projects.csv"))
    dated = proj[proj.source != "appraisal"].head(24)
    prows = [[int(r.open), r["mode"], f"{r['from']} - {r['to']}", r["class"], r.source] for _, r in dated.iterrows()]
    ptab = _table(["Opens", "Mode", "Link", "Class", "Source"], prows, "Dated projects in the baseline run")
    newl = proj[(proj.source == "appraisal") & (proj.kind == "new")].head(20)
    nrows = [[int(r.open), f"{r['from']} - {r['to']}", f"{r.km:.0f}", f"{r.bcr:.2f}"] for _, r in newl.iterrows()]
    ntab = _table(["Opens", "New rail link", "km", "Benefit-cost"], nrows, "New lines chosen by the appraisal model")

    F = lambda n, alt, cap: _fig(figdir, n, alt, cap)  # noqa: E731
    X = _extra_sections(outroot, end)
    n_scen = len(ss) - 1
    body = f"""
<div class="wrap">
<header class="mast">
  <span class="eyebrow">Counterfactual simulation · census of 9 December 1931 → 2032</span>
  <h1>Poland-Lithuania without the Second World War</h1>
  <p class="lede prose">The interwar Polish state, in federal union with Lithuania, simulated for a century
  with no war: births, deaths and migration, the languages people speak at home, and the rail and road networks.</p>
  <p class="meta">plsim 1.0 · about 270 counties × urban/rural × 43 community-language groups × single years of age
  · national identity · {n_members}-member Monte-Carlo ensemble · {n_scen} scenarios</p>
</header>

<div class="tiles">{tile_html}</div>

<section>
  <h2>Population and vital rates</h2>
  <p class="prose">The 1930s are reproduced from the census and the registered vital statistics.
  The model gives Poland 34.6 million on 1 January 1939; the official estimate was 35.1 million.
  After 1945, mortality falls quickly as antibiotics arrive; fertility follows a Catholic southern-European transition.
  Emigration peaks in the guest-worker era and fades as incomes converge.</p>
  {F("population.png", "Population fan charts", "Whole union, Polish voivodeships and Lithuanian units. Line: median; bands: 50 % and 90 % of ensemble members.")}
  {ktab}
  {F("vital_rates.png", "Vital rates", "Fertility, life expectancy, urbanisation, net international migration, income relative to the western frontier, and motorisation.")}
  {F("pyramids.png", "Age pyramids by language", "Age pyramids coloured by home language. The notch at ages 11-16 in 1932 is the First World War birth deficit; it moves up the pyramid over time.")}
</section>

<section>
  <h2>Languages</h2>
  <p class="prose">Children usually inherit their mother's language. A family shifts when the mother is bilingual,
  the other language has more status, more speakers nearby, more schools and churches, and when roads, railways
  and towns bring people into contact. Ukrainian grows with high Galician fertility and strong Greek Catholic
  institutions. Most acculturating Jews move to Polish; Yiddish survives chiefly in Haredi families.
  Small languages erode unevenly: Kashubian and Lemko slowly, Wymysorys and Karaim towards extinction.</p>
  {F("languages_baseline.png", "Home-language composition", "Share of the population by home language, seeded baseline run.")}
  {ltab}
  {F("region_languages.png", "Languages by region", "Home language by region, 1932 and 2032.")}
  {F("endangered.png", "Minority and endangered languages", "Home speakers on a log scale, ensemble median with 50 % and 90 % bands.")}
</section>
{X.get("calibration", "")}
{X.get("identity", "")}
{X.get("uncertainty", "")}

<section>
  <h2>What the censuses would have said</h2>
  <p class="prose">The 1931 census counted mother tongue, offered 'tutejszy' ('local') and 'ruski'
  ('Ruthenian') as answers, and recorded hundreds of thousands of Orthodox and Greek Catholic people as Polish-speaking.
  The model therefore tracks what people speak at home. A separate observation layer shows what a 1931-type Polish
  census, the 1897 imperial Russian census or a modern self-identification census would have printed.
  The religion-corrected and 1897-anchored starting points both reproduce the printed 1931 figures once the
  census's recording habits are applied. Nationality censuses (1921-type and modern self-identification) read
  the modelled national identity instead.</p>
  <div class="two">
  {F("census_regimes_1932.png", "Census regimes 1932", "The 1932 population under five recording regimes.")}
  {F("census_regimes_2032.png", "Census regimes 2032", "The 2032 population under the same regimes.")}
  </div>
  {ctab}
</section>

<section>
  <h2>Scenarios</h2>
  <ul class="prose">{scen_list}</ul>
  {stab}
  {F("scenario_languages.png", "Language shares by scenario", "Share of each language in 2032 by scenario; baseline highlighted.")}
  <div class="two">
  {F("scenario_population.png", "Population by scenario", "Population of the Polish voivodeships by scenario.")}
  {F("lithuania_poles.png", "Polish speakers in Lithuania", "The Lauda question: Polish home speakers in the Lithuanian units by scenario.")}
  </div>
</section>
{X.get("curzon", "")}

<section>
  <h2>Migration and regional development</h2>
  {F("migration.png", "Internal migration", "Net inter-regional migration per 1000 per year by decade: Warsaw, Silesia and Kaunas gain; the Kresy lose.")}
  <div class="two">
  {F("regional.png", "Regional change", "Population, urban share and relative income by region, 1932 and 2032.")}
  {F("towns.png", "Largest towns", "The twenty largest towns in 2032 against their 1932 size.")}
  </div>
</section>

<section>
  <h2>Railways and roads</h2>
  <p class="prose">Each year the network is appraised pair by pair: travel-time savings for gravity flows between
  about 170 towns, plus local trips for road surfacing. Projects are built under a budget tied to GDP.
  Expressways and motorways count their running costs and only part of the local traffic, which stays on the old
  road. This is calibrated so that the union ends with about 20 km of them per 1000 km², close to Czechia and
  Hungary; earlier versions built more than twice that.
  Historical works (the Coal Trunk Line, Warszawa-Radom, the Samogitian railway) open on their real dates.
  Projects still unfinished in 1939 open in the early 1940s: the Wilno-Gdynia shortcut, Dębica-Jasło and the COP
  Łódź-Dębica trunk.</p>
  {F("networks.png", "Networks", "Rail and road networks in 1932, 1970 and 2032. Foreign gateways such as Königsberg and Danzig are drawn as straight links.")}
  {F("network_km.png", "Network length", "Modelled route-km by class; local branch lines are not represented.")}
  <div class="two">{ptab}{ntab}</div>
</section>

<section>
  <h2>Checks</h2>
  {vtab}
  <p class="note prose">Modelled death rates sit about one point above the registered ones. Infant deaths in the
  eastern voivodeships were under-registered, so this is the expected direction.</p>
</section>

<section>
  <h2>Method and reproduction</h2>
  <ul class="prose">
    <li><b>Demography</b>: cohort-component by single year of age. Alkema et al. (2011) fertility transition;
    best-practice-gap mortality (Oeppen & Vaupel 2002) with a post-1945 catch-up.</li>
    <li><b>Migration</b>: Rogers-Castro age schedules; income-driven urbanisation; spatial interaction over network
    travel times; the migration hump for emigration.</li>
    <li><b>Language</b>: multi-language Abrams-Strogatz attraction with a bilingual state (Minett & Wang 2008;
    Kandler, Unger & Steele 2010), enclave concentration and institutional completeness.</li>
    <li><b>Networks</b>: cost-benefit growth in the family of Levinson and Louf et al., with market access feeding
    back to regional growth.</li>
  </ul>
  <pre>pip install -r requirements.txt
python -m plsim report -n 32     # all scenarios, ensembles, figures, this page
python -m plsim census           # 1931 census consistency test
pytest -q</pre>
  <p class="note prose">This is a counterfactual simulation, not a forecast. Political choices are scenarios;
  parameter uncertainty is in the ensemble ranges. Full equations, sources and data grades are in
  docs/METHODOLOGY.md and docs/DATA_SOURCES.md.</p>
</section>
</div>
"""
    fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
             '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
             '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600'
             '&family=IBM+Plex+Sans+Condensed:wght@500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600'
             '&display=swap">')
    title = "<title>Poland-Lithuania without WW2</title>"
    if standalone:
        return (f"<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
                f"<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">{title}{fonts}"
                f"<style>{CSS}</style></head><body>{body}</body></html>")
    return f"{title}\n{fonts}\n<style>{CSS}</style>\n{body}"


def write_pages(outroot: str) -> None:
    with open(os.path.join(outroot, "report.html"), "w", encoding="utf-8") as fh:
        fh.write(build_page(outroot, standalone=True))
    with open(os.path.join(outroot, "report_artifact.html"), "w", encoding="utf-8") as fh:
        fh.write(build_page(outroot, standalone=False))
