"""Command-line interface.

    python -m plsim run baseline                  # one seeded run -> outputs/runs/baseline/
    python -m plsim validate baseline             # 1932-39 back-validation + plausibility
    python -m plsim ensemble baseline -n 24       # Monte-Carlo ensemble
    python -m plsim census                        # 1931 census-reconstruction consistency
    python -m plsim report -n 24                  # everything + outputs/report.html
    python -m plsim maps                          # spatial layer: maps, GIFs, outputs/atlas/
    python -m plsim calibrate                     # history matching of the language-shift rates
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import multiprocessing as mp_ctx
import os
import pickle
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from .data.languages import GROUPS, LANG_INDEX
from .ensemble import CELL_YEARS, run_ensemble, save
from .export import export_ensemble, export_run
from .language import CENSUS_CATEGORIES, census_view
from .model import Simulation
from . import curzon, maps as mp
from . import webmap
from .spatial import downscale
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


# modules whose code does not change a run's results (presentation, reporting)
_NOT_IN_FINGERPRINT = {"cli.py", "maps.py", "webmap.py", "report.py", "publish.py", "export.py", "validate.py",
                       "ensemble.py", "curzon.py", "calibration.py", "__main__.py"}


def _code_fingerprint() -> str:
    h = hashlib.sha1()
    here = os.path.dirname(os.path.abspath(__file__))
    for path in sorted(glob.glob(os.path.join(here, "**", "*.py"), recursive=True)
                       + glob.glob(os.path.join(here, "data", "*.json"))
                       + glob.glob(os.path.join(here, "data", "*.geojson"))):
        if os.path.basename(path) in _NOT_IN_FINGERPRINT and os.path.dirname(path) == here:
            continue
        with open(path, "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()


def _run_cached(name: str, p: dict, cache_dir: str | None, write: bool = True):
    """Run a scenario, or load the run from ``cache_dir`` when the same
    parameters were run by the same code (``maps`` and ``report`` share runs)."""
    key = hashlib.sha1((json.dumps(p, sort_keys=True, default=str) + _code_fingerprint()).encode()).hexdigest()
    path = os.path.join(cache_dir, f"{name}.pkl") if cache_dir else None
    if path and os.path.exists(path):
        try:
            with open(path, "rb") as fh:
                k, res = pickle.load(fh)
            if k == key:
                return res, True
        except (EOFError, pickle.UnpicklingError, ValueError):
            pass                         # a cache file still being written by a parallel job
    res = Simulation(p).run()
    if path and write:
        os.makedirs(cache_dir, exist_ok=True)
        tmp = f"{path}.{os.getpid()}.tmp"
        with open(tmp, "wb") as fh:
            pickle.dump((key, res), fh, protocol=pickle.HIGHEST_PROTOCOL)
        os.replace(tmp, path)            # atomic: readers see the old file or the whole new one
    return res, False


def with_exchange_plan(p: dict, outroot: str) -> dict:
    """Scenarios with a ``population_exchange``: compute who moves from the
    equal-exchange line of the exchange year in the run of ``line_from``
    (identical to this scenario's run up to that year)."""
    ex = p.get("population_exchange")
    if not ex or ex.get("plan"):
        return p
    base = load_scenario(ex["line_from"])
    base["snapshot_years"] = p["snapshot_years"]
    if p.get("seed") != base.get("seed"):
        base["seed"] = p["seed"]
    res, _ = _run_cached(ex["line_from"], base, os.path.join(outroot, ".runcache"), write=False)
    sr = downscale(res, frame_years=[ex["year"]])
    p["population_exchange"] = dict(ex, plan=curzon.exchange_plan(sr, res, ex["year"], ex.get("by", "language")))
    return p


def _pool(workers: int | None, n: int):
    """Process pool for scenario-level parallelism; one BLAS thread per worker."""
    w = max(1, min(workers or os.cpu_count() or 1, n))
    for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[v] = "1"
    return ProcessPoolExecutor(max_workers=w, mp_context=mp_ctx.get_context("spawn"))


def _report_job(args):
    name, outroot, seed = args
    p = load_scenario(name)
    if seed is not None:
        p["seed"] = seed
    p["snapshot_years"] = sorted(set(p["snapshot_years"]) | set(webmap.FRAMES))    # same runs as the maps
    t = time.time()
    p = with_exchange_plan(p, outroot)
    res, cached = _run_cached(name, p, os.path.join(outroot, ".runcache"))
    export_run(res, os.path.join(outroot, "runs", name))
    return res, f"  {name}: {time.time() - t:.1f}s" + (" (cached run)" if cached else "")


def run_one(name: str, outroot: str, seed: int | None = None):
    res, msg = _report_job((name, outroot, seed))
    print(msg)
    return res


SCENARIO_TITLES = {
    "baseline": "Baseline federation",
    "federal_autonomy": "Ukrainian autonomy",
    "integral_nationalism": "Integral nationalism",
    "polonizing_union": "Polonising unitary union",
    "census_official": "1931 census as printed",
    "census_vernacular": "Upper-bound minority speech in 1931",
    "ii_rp_only": "Poland alone, no union",
    "ukraine_autonomy_tricantonal": "Ukrainian autonomy + tri-cantonal Lithuania",
    "autonomy_grand_duchy_coofficial": "Ukrainian autonomy + trilingual Grand Duchy",
    "wakar_poland": "Wakar's Poland",
    "wakar_poland_belarus": "Wakar's Poland-Belarus",
    "no_official_language": "No official language",
    "curzon_exchange": "Curzon-line population exchange",
    "curzon_exchange_identity": "Curzon-line exchange by nationality",
    "nw_krai": "Poland and the Northwestern Krai",
    "lit_bel": "Poland and Lit-Bel",
}


def _map_job(args):
    """Run one scenario, downscale it and write its maps and atlas data."""
    name, outroot, gifs = args
    t = time.time()
    mapdir, atlasdir = os.path.join(outroot, "maps"), os.path.join(outroot, "atlas")
    p = load_scenario(name)
    p["snapshot_years"] = sorted(set(p["snapshot_years"]) | set(webmap.FRAMES))   # network frames
    p = with_exchange_plan(p, outroot)
    res, cached = _run_cached(name, p, os.path.join(outroot, ".runcache"))
    # the baseline animations need every year; the others only the atlas frames
    # (and the exchange year, for the before/after map)
    ex_year = (p.get("population_exchange") or {}).get("year")
    frames = sorted(set(webmap.FRAMES) | ({ex_year, ex_year + 1} if ex_year else set()))
    sr = downscale(res, frame_years=None if name == "baseline" else frames)
    full = webmap.full_grid()
    title = SCENARIO_TITLES.get(name, name)
    if name == "baseline":
        mp.write_maps(sr, mapdir, gifs=gifs)
    else:
        mp.fig_plurality(sr, os.path.join(mapdir, f"{name}_map_plurality.png"), title=title)
    last = (sr.grid, mp.display_shares(sr.display(sr.frame(sr.years[-1]))))
    lines = curzon.lines_for(sr, res, webmap.FRAMES)
    curzon.write_csv(lines, os.path.join(mapdir, f"{name}_curzon.csv"))
    if name == "baseline":
        mp.fig_curzon(sr, lines, os.path.join(mapdir, "map_curzon.png"), title="Equal-exchange Curzon line, baseline")
        mp.fig_identity(sr, res, os.path.join(mapdir, "map_identity.png"),
                        title="Home language (cells) and national identity (counties), baseline")
    if name.startswith("curzon_exchange"):
        mp.fig_plurality(sr, os.path.join(mapdir, f"{name}_before_after.png"),
                         years=(1932, ex_year, ex_year + 1, 1970, 2000, 2032),
                         title=f"Population exchange on 1 January {ex_year} along that year's equal-exchange line "
                               f"({ex_year}: before, {ex_year + 1}: after)")
    # ensemble certainty (baseline): written by ``report`` when it ran the ensemble
    uncert, unc_meta = b"", None
    cells_path = os.path.join(outroot, "ensemble_baseline_cells.npz")
    if name == "baseline" and os.path.exists(cells_path):
        z = np.load(cells_path)
        prob = {int(y): z[f"prob_{int(y)}"].astype(np.float32) for y in z["years"]}
        if all(len(v) == len(sr.grid.lat) for v in prob.values()):
            uncert = webmap.encode_uncert(prob, sr.grid, full)
            unc_meta = {"years": sorted(prob), "n": int(z["n"])}
    blob = webmap.encode_frames(sr, full, ident=webmap.identity_frames(res), uncert=uncert)
    webmap.write_data(atlasdir, name, blob)
    entry = {"name": name, "title": title, "description": p["meta"]["description"],
             "series": webmap.national_series(res), "towns": webmap.town_series(sr),
             "net": webmap.network_payload(res), "geo": webmap.geometry_payload(res, sr, full),
             "curzon": webmap.curzon_payload(lines), "ident": webmap.identity_series(res)}
    if unc_meta:
        entry["uncert"] = unc_meta
    if getattr(res, "exchange", None):
        ex = res.exchange
        entry["exchange"] = {"year": ex["year"], "west": round(ex["to_polish_side"] / 1e3),
                             "east": round(ex["to_other_side"] / 1e3),
                             "byLang": {k: round(v / 1e3) for k, v in ex["by_language"].items()},
                             "lines": ex["lines"]}
    return name, entry, last, f"  {name}: {time.time() - t:.1f}s" + (" (cached run)" if cached else "")


def build_maps(outroot: str, scenarios: list[str] | None = None, gifs: bool = True,
               workers: int | None = None) -> None:
    """Run each scenario, downscale it to the map grid and write the static
    maps, the GIF animations (baseline) and the data of the interactive atlas.
    Scenarios run in parallel; the runs are cached for ``report``."""
    names = scenarios or [n for n in SCENARIO_TITLES if n in all_scenarios()]
    names += [n for n in all_scenarios() if n not in names and not scenarios]
    os.makedirs(os.path.join(outroot, "maps"), exist_ok=True)
    os.makedirs(os.path.join(outroot, "atlas"), exist_ok=True)
    done = {}
    with _pool(workers, len(names)) as ex:
        for name, entry, last, msg in ex.map(_map_job, [(n, outroot, gifs) for n in names]):
            done[name] = (entry, last)
            print(msg, flush=True)
    entries = [done[n][0] for n in names]
    last = {n: done[n][1] for n in names}
    atlasdir = os.path.join(outroot, "atlas")
    path = os.path.join(atlasdir, "scenarios.json")
    if scenarios and os.path.exists(path):
        # some scenarios only: update their atlas entries, keep the others
        with open(path, encoding="utf-8") as fh:
            old = json.load(fh)
        new = {e["name"]: e for e in entries}
        entries = [new.pop(e["name"], e) for e in old] + list(new.values())
    else:
        mp.fig_scenarios_plurality(last, os.path.join(outroot, "maps", "scenarios_plurality_2032.png"),
                                   labels={n: SCENARIO_TITLES.get(n, n) for n in last})
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(webmap.dumps(entries))
    webmap.build_atlas(atlasdir)


def census_consistency() -> list[list]:
    """Apply the 1931 Polish census observation model to each latent
    reconstruction and compare with the published national shares."""
    rows = []
    for variant in ["official", "religion_corrected", "vernacular"]:
        p = load_scenario("baseline")
        p["census_variant"] = variant
        p["include_lithuania"] = False
        p["partition"] = []
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


def run_digest(res) -> str:
    """Fingerprint of a seeded run's results (population, vital events, towns,
    identity): equal digests mean the run came out bit for bit the same."""
    h = hashlib.sha1()
    for k in ("pop", "births", "deaths", "town_pop", "identity"):
        h.update(np.ascontiguousarray(np.asarray(getattr(res, k), dtype=np.float64)).tobytes())
    return h.hexdigest()


def _ensemble(name: str, n: int, workers, seed: int, outroot: str, digest: str, reuse: bool, cells: bool = False):
    """Run (or, with ``reuse``, load) the ensemble of a scenario. A saved
    ensemble is reused only if it has as many members and was made when the
    scenario's seeded run had the same digest, i.e. when nothing that changes
    the scenario's results has changed since (presentation, other scenarios,
    Soviet Belarus geometry ...). Returns (ensemble, map cells or None)."""
    from .ensemble import load
    path = os.path.join(outroot, f"ensemble_{name}.npz")
    if reuse and os.path.exists(path):
        old = load(path)
        if str(old.get("run_digest", "")) == digest and len(old["pop_total"]) == n:
            print(f"  reusing {path}: the seeded {name} run is unchanged", flush=True)
            return old, None
        print(f"  {path} is stale; running the ensemble", flush=True)
    ens = run_ensemble(load_scenario(name), n=n, workers=workers, seed=seed, cells=cells)
    out = {y: ens.pop(f"cells_{y}") for y in CELL_YEARS if f"cells_{y}" in ens}
    ens["run_digest"] = np.array(digest)
    save(ens, path)
    return ens, (out or None)


def build_report(outroot: str, n_ens: int, scenarios: list[str] | None = None, workers: int | None = None,
                 reuse_ensemble: bool = False):
    figdir = os.path.join(outroot, "figures")
    os.makedirs(figdir, exist_ok=True)
    scenarios = scenarios or all_scenarios()
    print("single seeded runs:", flush=True)
    results = {}
    with _pool(workers, len(scenarios)) as ex:
        for n, (res, msg) in zip(scenarios, ex.map(_report_job, [(n, outroot, None) for n in scenarios])):
            results[n] = res
            print(msg, flush=True)
    base = results["baseline"]
    print(f"ensemble (n={n_ens}) for baseline ...")
    t = time.time()
    ens, cells = _ensemble("baseline", n_ens, workers, 7, outroot, run_digest(base), reuse_ensemble, cells=True)
    if cells:
        # probability maps: in how many runs each language leads each cell
        prob = {y: mp.plurality_probability(c) for y, c in cells.items()}
        np.savez_compressed(os.path.join(outroot, "ensemble_baseline_cells.npz"), years=np.array(sorted(prob)),
                            n=n_ens, **{f"prob_{y}": p.astype(np.float16) for y, p in prob.items()})
        from .data.geography import build_grid
        mp.fig_uncertainty(build_grid(base.region_codes), prob, os.path.join(outroot, "maps", "map_uncertainty.png"),
                           n_ens, title="How certain is the map? The baseline across the ensemble")
        del cells
    export_ensemble(ens, os.path.join(outroot, "ensemble_baseline"))
    print(f"  {time.time() - t:.1f}s")
    ens_ii = None
    if "ii_rp_only" in scenarios and n_ens >= 8:
        ens_ii, _ = _ensemble("ii_rp_only", max(8, n_ens // 2), workers, 11, outroot,
                              run_digest(results["ii_rp_only"]), reuse_ensemble)
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
    lt_sc = {k: results[k] for k in ["baseline", "polonizing_union", "census_official", "census_vernacular",
                                      "ukraine_autonomy_tricantonal", "autonomy_grand_duchy_coofficial"] if k in results}
    rp.fig_lithuania_poles(lt_sc, F("lithuania_poles.png"))
    for k in ["federal_autonomy", "integral_nationalism"]:
        if k in results:
            rp.fig_language_area(results[k], F(f"languages_{k}.png"),
                                 f"Home language, scenario '{k}'")
    write_scenario_summary(outroot, results)
    write_extras(outroot, results)
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


ID_SHOW = ["pl", "uk", "be", "lt", "jw", "de", "loc"]


def write_extras(outroot, results):
    """identity_summary.csv (national identity against home language, by
    scenario) and exchange_summary.csv (scenarios with a population exchange)."""
    import csv
    from .identity import ID_INDEX
    rows = []
    for n, res in results.items():
        if not getattr(res, "identity", None):
            continue
        lt = np.array([c.startswith("LT") for c in res.region_codes])
        for label, y in (("start", res.params["start_year"]), ("end", res.years[-1])):
            I = mp.identity_at(res, y)
            P = np.asarray(res.pop0 if label == "start" else res.pop[-1])            # (R,2,G)
            tot = I.sum()
            pl_speak = sum(P[:, :, g].sum() for g, (_c, l) in enumerate(GROUPS) if l == "pl")
            row = [n, y] + [f"{I[:, ID_INDEX[k]].sum() / tot * 100:.1f}" for k in ID_SHOW]
            row.append(f"{pl_speak / tot * 100:.1f}")
            if lt.any():
                lt_pl_speak = sum(P[lt][:, :, g].sum() for g, (_c, l) in enumerate(GROUPS) if l == "pl")
                row += [f"{lt_pl_speak / 1e3:.0f}", f"{I[lt, ID_INDEX['pl']].sum() / 1e3:.0f}"]
            else:
                row += ["", ""]
            rows.append(row)
    with open(os.path.join(outroot, "identity_summary.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["scenario", "year"] + [f"identity_{k}_pct" for k in ID_SHOW]
                   + ["polish_speakers_pct", "lithuania_polish_speakers_k", "lithuania_polish_identity_k"])
        w.writerows(rows)
    ex_rows = []
    for n, res in results.items():
        ex = getattr(res, "exchange", None)
        if ex:
            by = ex.get("by", "language")
            for lang, v in sorted(ex["by_language"].items(), key=lambda kv: -kv[1]):
                ex_rows.append([n, ex["year"], by, "to the other side", "home language", lang, round(v)])
            for lang, v in sorted((ex.get("west_languages") or {"pl": ex["to_polish_side"]}).items(),
                                  key=lambda kv: -kv[1]):
                ex_rows.append([n, ex["year"], by, "to the Polish side", "home language", lang, round(v)])
            for ident, v in sorted((ex.get("by_identity") or {}).items(), key=lambda kv: -kv[1]):
                ex_rows.append([n, ex["year"], by, "to the other side", "identity", ident, round(v)])
    with open(os.path.join(outroot, "exchange_summary.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["scenario", "year", "counted_by", "direction", "kind", "category", "persons"])
        w.writerows(ex_rows)


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
    d.add_argument("--reuse-ensemble", action="store_true",
                   help="reuse a saved ensemble when the scenario's seeded run is unchanged")
    m = sub.add_parser("maps")
    m.add_argument("--out", default=os.path.join(ROOT, "outputs"))
    m.add_argument("--scenarios", nargs="*")
    m.add_argument("--no-gifs", action="store_true")
    m.add_argument("--workers", type=int)
    k = sub.add_parser("calibrate")
    k.add_argument("-n", type=int, default=2000, help="draws per wave")
    k.add_argument("--workers", type=int)
    k.add_argument("--out", default=os.path.join(ROOT, "outputs"))
    k.add_argument("--write-nroy", action="store_true", help="replace plsim/data/nroy_language.csv")
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
        build_report(args.out, args.n, args.scenarios, args.workers, args.reuse_ensemble)
    elif args.cmd == "maps":
        build_maps(args.out, args.scenarios, gifs=not args.no_gifs, workers=args.workers)
    elif args.cmd == "calibrate":
        from . import calibration as cb
        hm = cb.history_match(n=args.n, workers=args.workers or os.cpu_count() or 1)
        outdir = os.path.join(args.out, "calibration")
        cb.write_outputs(hm, outdir)
        cb.figure(hm, os.path.join(outdir, "history_matching.png"))
        with open(os.path.join(outdir, "summary.txt"), "w", encoding="utf-8") as fh:
            fh.write(cb.summary(hm) + "\n")
        if args.write_nroy:
            cb.write_nroy(hm)
        print(cb.summary(hm))
    elif args.cmd == "list":
        for n in all_scenarios():
            print(n, "-", load_scenario(n)["meta"]["description"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
