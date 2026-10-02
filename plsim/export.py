"""CSV export of single runs and ensembles."""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

from .data.languages import GROUPS, LANG_INDEX, LANGUAGES
from .data.network import NODES
from .ensemble import KM_KEYS, QUANTILES
from .language import CENSUS_CATEGORIES
from .model import Results
from .report import lang_totals


def export_run(res: Results, outdir: str) -> None:
    os.makedirs(outdir, exist_ok=True)
    A = res.arrays()
    yrs = res.years
    codes = res.region_codes
    # population by region x urban
    rows = []
    for i, y in enumerate(yrs):
        for r, c in enumerate(codes):
            rows.append({"year": y, "region": c, "rural": A["pop"][i][r, 0].sum(), "urban": A["pop"][i][r, 1].sum(),
                         "births": A["births"][i][r], "deaths": A["deaths"][i][r], "tfr": A["tfr"][i][r],
                         "e0_male": A["e0"][i][r, 0], "e0_female": A["e0"][i][r, 1],
                         "emigrants": A["emig"][i][r].sum(), "immigrants": A["immig"][i][r].sum(),
                         "internal_in": A["internal"][i][:, r].sum(), "internal_out": A["internal"][i][r, :].sum(),
                         "rel_income": res.rel_income[i][r], "market_access": res.access[i][r]})
    pd.DataFrame(rows).to_csv(os.path.join(outdir, "regions.csv"), index=False, float_format="%.4g")
    # groups by region (every 5 years)
    rows = []
    for i, y in enumerate(yrs):
        if y % 5 and y != yrs[-1]:
            continue
        for r, c in enumerate(codes):
            for g, (cc, l) in enumerate(GROUPS):
                v = A["pop"][i][r, :, g].sum()
                if v < 0.5:
                    continue
                rows.append({"year": y, "region": c, "community": cc, "language": l,
                             "rural": A["pop"][i][r, 0, g], "urban": A["pop"][i][r, 1, g],
                             "bilingual": A["bil"][i][r, :, g].sum()})
    pd.DataFrame(rows).to_csv(os.path.join(outdir, "groups_by_region.csv"), index=False, float_format="%.6g")
    # national languages
    lt = lang_totals(res)
    df = pd.DataFrame(lt, columns=[l.code for l in LANGUAGES])
    df.insert(0, "year", yrs)
    df.to_csv(os.path.join(outdir, "languages_national.csv"), index=False, float_format="%.6g")
    # language-shift flows (births raised in another language than the mother's)
    rows = []
    for i, y in enumerate(yrs):
        m = A["shifts"][i]
        for a in range(m.shape[0]):
            for b in range(m.shape[1]):
                if m[a, b] > 0.5:
                    rows.append({"year": y - 1, "from": LANGUAGES[a].code, "to": LANGUAGES[b].code, "births": m[a, b]})
    pd.DataFrame(rows).to_csv(os.path.join(outdir, "shift_flows.csv"), index=False, float_format="%.5g")
    # economy
    df = pd.DataFrame(res.econ)
    df.insert(0, "year", yrs)
    df.to_csv(os.path.join(outdir, "economy.csv"), index=False, float_format="%.5g")
    # network
    df = pd.DataFrame(res.km)
    df.insert(0, "year", yrs)
    df.to_csv(os.path.join(outdir, "network_km.csv"), index=False, float_format="%.1f")
    pd.DataFrame(res.project_log).to_csv(os.path.join(outdir, "network_projects.csv"), index=False)
    towns = pd.DataFrame(np.array(res.town_pop), columns=[n.name for n in NODES])
    towns.insert(0, "year", yrs)
    towns.to_csv(os.path.join(outdir, "towns_thousands.csv"), index=False, float_format="%.2f")
    # census views
    rows = []
    for (rg, y), tab in sorted(res.census.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        for r, c in enumerate(codes):
            for k, cat in enumerate(CENSUS_CATEGORIES):
                if tab[r, k] > 0.5:
                    rows.append({"year": y, "regime": rg, "region": c, "category": cat, "persons": tab[r, k]})
    pd.DataFrame(rows).to_csv(os.path.join(outdir, "census_views.csv"), index=False, float_format="%.6g")
    # pyramids
    rows = []
    for y, pyr in res.pyramids.items():
        for li, l in enumerate(LANGUAGES):
            for s, sex in enumerate(("male", "female")):
                for a in range(101):
                    if pyr[li, s, a] > 0.5:
                        rows.append({"year": y, "language": l.code, "sex": sex, "age": a, "persons": pyr[li, s, a]})
    pd.DataFrame(rows).to_csv(os.path.join(outdir, "pyramids.csv"), index=False, float_format="%.5g")


def export_ensemble(ens: dict, outdir: str) -> None:
    os.makedirs(outdir, exist_ok=True)
    yrs = ens["years"]
    cols = {}
    for key in ["pop_total", "pop_pl", "pop_lt", "urban_share", "tfr", "births", "deaths", "emig", "immig",
                "y_nat", "vehicles"]:
        q = np.percentile(ens[key], QUANTILES, axis=0)
        for qq, v in zip(QUANTILES, q):
            cols[f"{key}_p{qq}"] = v
    for s, sex in enumerate(("male", "female")):
        q = np.percentile(ens["e0"][:, :, s], QUANTILES, axis=0)
        for qq, v in zip(QUANTILES, q):
            cols[f"e0_{sex}_p{qq}"] = v
    df = pd.DataFrame(cols)
    df.insert(0, "year", yrs)
    df.to_csv(os.path.join(outdir, "ensemble_national.csv"), index=False, float_format="%.5g")
    cols = {}
    for l in LANGUAGES:
        q = np.percentile(ens["pop_lang"][:, :, LANG_INDEX[l.code]], QUANTILES, axis=0)
        for qq, v in zip(QUANTILES, q):
            cols[f"{l.code}_p{qq}"] = v
    df = pd.DataFrame(cols)
    df.insert(0, "year", yrs)
    df.to_csv(os.path.join(outdir, "ensemble_languages.csv"), index=False, float_format="%.6g")
    cols = {}
    for k, key in enumerate(KM_KEYS):
        q = np.percentile(ens["km"][:, :, k], QUANTILES, axis=0)
        for qq, v in zip(QUANTILES, q):
            cols[f"{key}_p{qq}"] = v
    df = pd.DataFrame(cols)
    df.insert(0, "year", yrs)
    df.to_csv(os.path.join(outdir, "ensemble_network_km.csv"), index=False, float_format="%.1f")
    if "identity" in ens:
        from .identity import IDENTITIES
        cols = {}
        for i, k in enumerate(IDENTITIES):
            q = np.percentile(ens["identity"][:, :, i], QUANTILES, axis=0)
            for qq, v in zip(QUANTILES, q):
                cols[f"{k}_p{qq}"] = v
        df = pd.DataFrame(cols)
        df.insert(0, "year", yrs)
        df.to_csv(os.path.join(outdir, "ensemble_identity.csv"), index=False, float_format="%.6g")
