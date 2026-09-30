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
import os
import sys
import time

import numpy as np

from .data.languages import LANG_INDEX
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
    write_checks(outroot, base)
    from .publish import write_pages
    write_pages(outroot)
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


def write_checks(outroot, base):
    """validation.csv and census_consistency.csv for the results page."""
    import csv
    checks = historical_checks(base) + plausibility_checks(base)
    with open(os.path.join(outroot, "validation.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Result", "Type", "Check", "Model", "Accepted range"])
        for c in checks:
            w.writerow(["PASS" if c.ok else "FAIL", c.kind, c.name, f"{c.value:.2f}", f"{c.lo} - {c.hi}"])
    with open(os.path.join(outroot, "census_consistency.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Reconstruction", "Read as", *PUBLISHED_1931.keys(), "Total abs. error"])
        w.writerow(["printed 1931 census", "-", *[f"{v:.1f}" for v in PUBLISHED_1931.values()], "0.0"])
        for row in census_consistency():
            w.writerow(row)


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
