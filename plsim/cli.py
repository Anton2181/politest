"""Command-line interface.

    python -m plsim run baseline                  # one seeded run -> outputs/runs/baseline/
    python -m plsim validate baseline             # 1932-39 back-validation + plausibility
    python -m plsim ensemble baseline -n 24       # Monte-Carlo ensemble
    python -m plsim census                        # 1931 census-reconstruction consistency
    python -m plsim report -n 24                  # everything + outputs/report.html
"""
from __future__ import annotations

import argparse
import glob
import html
import os
import sys
import time

import numpy as np

from .data.languages import LANG_INDEX, LANGUAGES
from .ensemble import run_ensemble, save
from .export import export_ensemble, export_run
from .language import CENSUS_CATEGORIES, census_view
from .model import Simulation
from .params import load_scenario
from . import report as rp
from .validate import historical_checks, plausibility_checks

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCEN_DIR = os.path.join(ROOT, "scenarios")

PUBLISHED_1931 = {  # national mother-tongue shares, 1931 census (%); Ukrainian incl. 'Ruthenian', Yiddish incl. Hebrew
    "pl": 68.9, "uk+ruth": 13.9, "yi+he": 8.6, "be": 3.1, "de": 2.3, "tut": 2.2, "ru": 0.4, "lt": 0.3,
}
_MERGE = {"pl": ["pl", "csb", "wym"], "uk+ruth": ["uk", "ruth", "rue"], "yi+he": ["yi", "he"], "be": ["be"],
          "de": ["de"], "tut": ["tut"], "ru": ["ru"], "lt": ["lt"]}


def all_scenarios() -> list[str]:
    return sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(SCEN_DIR, "*.yaml")))


def run_one(name: str, outroot: str, seed: int | None = None):
    p = load_scenario(name)
    if seed is not None:
        p["seed"] = seed
    t = time.time()
    res = Simulation(p).run()
    export_run(res, os.path.join(outroot, "runs", name))
    print(f"  {name}: {time.time() - t:.1f}s")
    return res


def census_consistency() -> list[list]:
    """Apply the 1931 Polish census observation model to each latent
    reconstruction and compare with the published national shares."""
    rows = []
    for variant in ["official", "religion_corrected", "vernacular"]:
        p = load_scenario("baseline")
        p["census_variant"] = variant
        p["include_lithuania"] = False
        sim = Simulation(p)
        rugb = sim.P.sum(axis=(4, 5))
        for regime in ["latent", "polish_1931"]:
            tab = census_view(rugb, regime, sim.codes).sum(axis=0)
            tot = tab.sum()
            row = [variant, regime]
            err = 0.0
            for cat, pub in PUBLISHED_1931.items():
                v = sum(tab[CENSUS_CATEGORIES.index(x)] for x in _MERGE[cat]) / tot * 100
                row.append(f"{v:.1f}")
                err += abs(v - pub)
            row.append(f"{err:.1f}")
            rows.append(row)
    return rows


def build_report(outroot: str, n_ens: int, scenarios: list[str] | None = None, workers: int | None = None):
    figdir = os.path.join(outroot, "figures")
    os.makedirs(figdir, exist_ok=True)
    scenarios = scenarios or all_scenarios()
    print("single seeded runs:")
    results = {n: run_one(n, outroot) for n in scenarios}
    base = results["baseline"]
    print(f"ensemble (n={n_ens}) for baseline ...")
    t = time.time()
    ens = run_ensemble(load_scenario("baseline"), n=n_ens, workers=workers)
    save(ens, os.path.join(outroot, "ensemble_baseline.npz"))
    export_ensemble(ens, os.path.join(outroot, "ensemble_baseline"))
    print(f"  {time.time() - t:.1f}s")
    ens_ii = None
    if "ii_rp_only" in scenarios and n_ens >= 8:
        ens_ii = run_ensemble(load_scenario("ii_rp_only"), n=max(8, n_ens // 2), workers=workers, seed=11)
        export_ensemble(ens_ii, os.path.join(outroot, "ensemble_ii_rp_only"))
    F = lambda n: os.path.join(figdir, n)  # noqa: E731
    rp.fig_population(ens, F("population.png"))
    rp.fig_vitals(ens, F("vital_rates.png"))
    rp.fig_language_area(base, F("languages_baseline.png"))
    rp.fig_endangered(ens, F("endangered.png"))
    rp.fig_pyramids(base, F("pyramids.png"))
    rp.fig_census_regimes(base, F("census_regimes_2032.png"), base.years[-1])
    rp.fig_census_regimes(base, F("census_regimes_1932.png"), base.years[0] - 1 if (("latent", base.years[0] - 1) in base.census) else 1932)
    rp.fig_networks(base, F("networks.png"))
    rp.fig_network_km(ens, F("network_km.png"))
    rp.fig_regional(base, F("regional.png"))
    rp.fig_region_languages(base, F("region_languages.png"))
    rp.fig_migration(base, F("migration.png"))
    rp.fig_towns(base, F("towns.png"))
    rp.fig_scenario_population(results, F("scenario_population.png"))
    rp.fig_language_scenarios(results, F("scenario_languages.png"), base.years[-1])
    lt_sc = {k: results[k] for k in ["baseline", "forced_lithuanization", "polonizing_union", "lt_polish_claim",
                                      "census_vernacular", "wilno_lithuanian"] if k in results}
    rp.fig_lithuania_poles(lt_sc, F("lithuania_poles.png"))
    for k in ["federal_autonomy", "integral_nationalism"]:
        if k in results:
            rp.fig_language_area(results[k], F(f"languages_{k}.png"),
                                 f"Home language, scenario '{k}'")
    write_scenario_summary(outroot, results)
    write_html(outroot, results, ens, ens_ii)
    print("report:", os.path.join(outroot, "report.html"))


def _scenario_rows(results):
    rows = []
    for n, res in results.items():
        A = res.arrays()
        i = len(res.years) - 1
        w = A["pop"][i].sum(axis=(1, 2))
        pl = np.array([not c.startswith("LT") for c in res.region_codes])
        lt = rp.lang_totals(res)[i]
        tot = lt.sum()
        km = res.km[i]
        rows.append([n, f"{w[pl].sum() / 1e6:.1f}", f"{w[~pl].sum() / 1e6:.2f}",
                     f"{lt[LANG_INDEX['pl']] / tot * 100:.1f}", f"{lt[LANG_INDEX['uk']] / tot * 100:.1f}",
                     f"{lt[LANG_INDEX['yi']] / tot * 100:.1f}", f"{lt[LANG_INDEX['be']] / tot * 100:.1f}",
                     f"{lt[LANG_INDEX['lt']] / tot * 100:.1f}", f"{lt[LANG_INDEX['pls']] / 1e3:,.0f}",
                     f"{lt[LANG_INDEX['csb']] / 1e3:,.0f}",
                     f"{res.econ[i]['y_nat']:,.0f}", f"{km['rail_main_el'] + km['rail_hsr']:,.0f}",
                     f"{km['road_motorway'] + km['road_express']:,.0f}"])
    return rows


SUMMARY_HEADER = ["scenario", "pop_pl_units_M", "pop_lt_units_M", "polish_pct", "ukrainian_pct", "yiddish_pct",
                  "belarusian_pct", "lithuanian_pct", "west_polesian_k", "kashubian_k", "gdp_per_head_1990gk",
                  "electrified_plus_hsr_km", "expressway_plus_motorway_km"]


def write_scenario_summary(outroot, results):
    import csv
    with open(os.path.join(outroot, "scenario_summary.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(SUMMARY_HEADER)
        for row in _scenario_rows(results):
            w.writerow([c.replace(",", "") for c in row])


def write_html(outroot, results, ens, ens_ii=None):
    base = results["baseline"]
    figdir = os.path.join(outroot, "figures")
    img = lambda n, alt: rp.img_tag(os.path.join(figdir, n), alt)  # noqa: E731
    checks = historical_checks(base) + plausibility_checks(base)
    vrows = [["PASS" if c.ok else "FAIL", c.kind, c.name, f"{c.value:.2f}", f"{c.lo} - {c.hi}"] for c in checks]
    lh, lrows = rp.language_table(base)
    yrs = ens["years"]
    key_years = [1939, 1950, 1970, 1990, 2010, int(yrs[-1])]
    krows = []
    for y in key_years:
        i = list(yrs).index(y)
        q = lambda k: np.percentile(ens[k][:, i], [5, 50, 95])  # noqa: E731
        p = q("pop_total") / 1e6
        t = q("tfr")
        e0 = np.percentile(ens["e0"][:, i].mean(axis=1), [5, 50, 95])
        u = q("urban_share") * 100
        krows.append([y, f"{p[1]:.1f} ({p[0]:.1f}-{p[2]:.1f})", f"{t[1]:.2f} ({t[0]:.2f}-{t[2]:.2f})",
                      f"{e0[1]:.1f} ({e0[0]:.1f}-{e0[2]:.1f})", f"{u[1]:.0f} ({u[0]:.0f}-{u[2]:.0f})"])
    cc = census_consistency()
    srows = _scenario_rows(results)
    scen_desc = "".join(f"<li><b>{html.escape(n)}</b>: {html.escape(r.params['meta']['description'])}</li>"
                        for n, r in results.items())
    proj = [d for d in base.project_log if d["source"] != "appraisal"][:40]
    prow = [[d["open"], d["mode"], f"{d['from']} - {d['to']}", d["class"], d["source"]] for d in proj]
    big = sorted([d for d in base.project_log if d["source"] == "appraisal" and d["kind"] == "new"],
                 key=lambda d: d["open"])
    brow = [[d["open"], f"{d['from']} - {d['to']}", d["class"], d["km"], d["bcr"]] for d in big]
    css = """
    :root{--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;--grid:#e1e0d9}
    body{background:var(--surface);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",sans-serif;
         max-width:1180px;margin:0 auto;padding:24px 16px;line-height:1.5}
    h1{font-size:1.7rem;margin-bottom:.2rem} h2{margin-top:2.4rem;border-bottom:1px solid var(--grid);padding-bottom:.3rem}
    p.lead{color:var(--ink2)} img{max-width:100%;height:auto;margin:.6rem 0}
    table{border-collapse:collapse;margin:.8rem 0;font-size:.85rem;font-variant-numeric:tabular-nums}
    th,td{border-bottom:1px solid var(--grid);padding:.25rem .6rem;text-align:right} th:first-child,td:first-child{text-align:left}
    caption{caption-side:top;text-align:left;color:var(--ink2);font-size:.85rem;padding-bottom:.3rem}
    details{margin:.5rem 0} summary{cursor:pointer;color:var(--ink2)} .note{color:var(--ink2);font-size:.9rem}
    """
    parts = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
             f"<title>Poland-Lithuania without WW2</title><style>{css}</style></head><body>",
             "<h1>Poland-Lithuania without the Second World War, 1932-2032</h1>",
             "<p class='lead'>A coupled simulation of demography, migration, language shift and transport networks, "
             "started from the December 1931 census and run with no war. Baseline: a Polish-Lithuanian federation. "
             "See <code>docs/METHODOLOGY.md</code> for the models and sources and <code>docs/SCENARIOS.md</code> for scenario assumptions.</p>",
             "<h2>Headline numbers (baseline ensemble)</h2>",
             rp.table_html(["Year", "Population, M (90% range)", "TFR", "Life expectancy", "Urban %"], krows,
                           f"Median and 5-95 % range over {ens['pop_total'].shape[0]} Monte-Carlo members"),
             img("population.png", "Population fan charts"),
             img("vital_rates.png", "Vital rates, migration and economy"),
             "<h2>Back-validation 1932-1939 and plausibility guard rails</h2>",
             rp.table_html(["", "Type", "Check", "Model", "Accepted range"], vrows),
             "<p class='note'>Crude death rates are 'true' modelled rates; registered interwar rates were lower because "
             "infant deaths in the eastern voivodeships were under-registered.</p>",
             "<h2>Languages</h2>",
             img("languages_baseline.png", "Home-language composition, baseline"),
             rp.table_html(lh, lrows, "Home speakers by language, baseline seeded run"),
             img("region_languages.png", "Home language by region 1932 and 2032"),
             img("endangered.png", "Minority and endangered languages"),
             img("pyramids.png", "Age pyramids by language"),
             "<h2>What the censuses would have said</h2>",
             "<p>The model tracks the vernacular actually spoken at home. An observation model translates it into what a "
             "given census would have printed. The 1931 Polish census, the 1897 imperial Russian census and a modern "
             "self-identification census give very different pictures of the same population.</p>",
             img("census_regimes_1932.png", "Census regimes 1932"),
             img("census_regimes_2032.png", "Census regimes 2032"),
             rp.table_html(["Reconstruction", "Recorded as", *PUBLISHED_1931.keys(), "abs. error"],
                           [["published 1931 census", "-", *[f"{v:.1f}" for v in PUBLISHED_1931.values()], "0"]] + cc,
                           "1931 consistency: national shares (%) implied by each latent reconstruction, read directly "
                           "(latent) or through the 1931 census observation model"),
             "<h2>Scenarios</h2>", f"<ul>{scen_desc}</ul>",
             rp.table_html(["Scenario", "Pop. PL units 2032 (M)", "Pop. LT units (M)", "Polish %", "Ukrainian %",
                            "Yiddish %", "Belarusian %", "Lithuanian %", "W. Polesian (k)", "Kashubian (k)",
                            "GDP/head (1990 GK$)", "Electrified + HSR km", "Expressway + motorway km"], srows,
                           "End-year outcomes, one seeded run per scenario"),
             img("scenario_population.png", "Population by scenario"),
             img("scenario_languages.png", "Language shares by scenario"),
             img("lithuania_poles.png", "Polish speakers in Lithuania by scenario"),
             ]
    for k in ["federal_autonomy", "integral_nationalism"]:
        if os.path.exists(os.path.join(figdir, f"languages_{k}.png")):
            parts.append(img(f"languages_{k}.png", k))
    parts += ["<h2>Migration and regional development</h2>",
              img("migration.png", "Net internal migration"),
              img("regional.png", "Regional change"),
              img("towns.png", "Largest towns"),
              "<h2>Infrastructure</h2>",
              img("networks.png", "Rail and road networks 1932, 1970, 2032"),
              img("network_km.png", "Network length by class"),
              rp.table_html(["Opens", "Mode", "Link", "Class", "Source"], prow, "Dated historical / planned / federation projects"),
              "<details><summary>New rail links chosen by the appraisal model</summary>",
              rp.table_html(["Opens", "Link", "Class", "km", "BCR"], brow), "</details>",
              "<h2>Reading the results</h2><p class='note'>This is a counterfactual simulation, not a forecast. "
              "The 1931 starting point and 1930s behaviour are anchored to data. After 1939 the trajectories follow "
              "explicit, published model structures whose parameters come from comparator societies. Monte-Carlo "
              "ranges cover parameter uncertainty and shocks, not the political assumptions: those are the scenarios. "
              "All numbers can be regenerated with <code>python -m plsim report</code>.</p>",
              "</body></html>"]
    with open(os.path.join(outroot, "report.html"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="plsim", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("run")
    a.add_argument("scenario")
    a.add_argument("--out", default=os.path.join(ROOT, "outputs"))
    a.add_argument("--seed", type=int)
    b = sub.add_parser("validate")
    b.add_argument("scenario", nargs="?", default="baseline")
    c = sub.add_parser("ensemble")
    c.add_argument("scenario")
    c.add_argument("-n", type=int, default=24)
    c.add_argument("--workers", type=int)
    c.add_argument("--out", default=os.path.join(ROOT, "outputs"))
    sub.add_parser("census")
    d = sub.add_parser("report")
    d.add_argument("-n", type=int, default=24)
    d.add_argument("--workers", type=int)
    d.add_argument("--out", default=os.path.join(ROOT, "outputs"))
    d.add_argument("--scenarios", nargs="*")
    sub.add_parser("list")
    args = ap.parse_args(argv)
    if args.cmd == "run":
        res = run_one(args.scenario, args.out, args.seed)
        for ch in historical_checks(res) + plausibility_checks(res):
            print(ch.row())
    elif args.cmd == "validate":
        res = Simulation(load_scenario(args.scenario)).run()
        for ch in historical_checks(res) + plausibility_checks(res):
            print(ch.row())
    elif args.cmd == "ensemble":
        ens = run_ensemble(load_scenario(args.scenario), n=args.n, workers=args.workers)
        save(ens, os.path.join(args.out, f"ensemble_{args.scenario}.npz"))
        export_ensemble(ens, os.path.join(args.out, f"ensemble_{args.scenario}"))
    elif args.cmd == "census":
        print("variant, regime, " + ", ".join(PUBLISHED_1931) + ", abs error")
        print("published, -, " + ", ".join(str(v) for v in PUBLISHED_1931.values()))
        for row in census_consistency():
            print(", ".join(row))
    elif args.cmd == "report":
        build_report(args.out, args.n, args.scenarios, args.workers)
    elif args.cmd == "list":
        for n in all_scenarios():
            print(n, "-", load_scenario(n)["meta"]["description"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
