"""Initial population of sub-regions (see ``data.subregions``).

The 1931 census is tabulated by voivodeship.  To start a split voivodeship,
its census reconstruction is first downscaled to the 7 km grid
(``spatial.Downscaler.initial_state``: county anchors + IPF).  The cells and
towns of each sub-region are then summed.

* **Languages.** Each sub-region gets the rural and urban speakers of every
  language found on its cells and in its towns.
* **Communities.** Within a language, the split between communities
  (Catholic, Orthodox, Greek Catholic ...) is the parent's.
* **Other inputs.** Fertility, mortality and literacy are the parent's.
  Area is the parent's official area times the sub-region's share of the
  parent's cells. Income: see the end of this docstring.

The children of a voivodeship therefore always add up to the parent, by
rural/urban stratum and language.

County mode (``partition: counties``) splits every voivodeship into its
powiaty (``data.counties``). Where the 1931 county table is known (grade A),
the county's population and declared mother tongue replace the downscaled
pattern:

1. **Seed.** The seed for each county is its census counts. Merged census
   categories are split by the downscaled pattern: Belarusian + tutejszy +
   Russian, "other", and the unenumerated Kashubian, Lemko and Wymysorys
   speakers inside "Polish" and "Ukrainian".
2. **Fit to the voivodeship.** IPF fits the seeds to the county populations
   and to the voivodeship's latent language totals. The census variants
   (official, religion-corrected, vernacular) therefore keep their
   voivodeship totals, and the county table decides where speakers live.
3. **Rural/urban split.** Rural and urban come from the downscaled split of
   each language in the county, then a final IPF matches the voivodeship by
   stratum.

Counties with only a population (grade B) use the downscaled language
pattern at that population. Counties with neither (grade C) are fully
downscaled.

Income. A sub-region's income index is the parent's at the parent's urban
and rural incomes per head, weighted by its own urban share: a city county
is richer than the rural counties around it, and the population-weighted
mean of the children is the parent's.
"""
from __future__ import annotations

import dataclasses
from types import SimpleNamespace

import numpy as np

from .data import subregions
from .data.counties import BY_CODE as COUNTY_BY_CODE
from .data.census1931 import build_initial_composition
from .data.geography import MODEL_DLAT, MODEL_DLON, build_grid
from .data.languages import GROUPS, LANG_INDEX, NL
from .data.network import NODES
from .economy import piecewise
from .spatial import Downscaler, lang_totals


def _initial_units(regions, comp: np.ndarray, params: dict):
    codes = [r.code for r in regions]
    reg_idx = {c: i for i, c in enumerate(codes)}
    grid = build_grid(codes, MODEL_DLAT, MODEL_DLON)       # model grid: results independent of the map grid
    ns = SimpleNamespace(
        region_codes=codes, params=params,
        node_region=[reg_idx.get(n.region, -1) for n in NODES],
        node_lat=[n.lat for n in NODES], node_lon=[n.lon for n in NODES], node_names=[n.name for n in NODES],
        years=[], pop0=comp, pop=[], shift_net=[], town_pop0=np.array([n.pop_1931 for n in NODES], float),
        town_pop=[])
    ds = Downscaler(ns, grid=grid)
    return ds, ds.initial_state()


_L = LANG_INDEX
_HOST = {"csb": "pl", "wym": "pl", "rom": "pl", "rue": "uk", "kdr": "oth"}   # unenumerated -> census category


def _census_seed(cty, ds: np.ndarray, pop: float) -> np.ndarray:
    """Latent-language seed (NL,) from a county's declared mother tongue.
    ``ds`` is the downscaled language pattern of the county (NL,)."""
    share = ds / max(ds.sum(), 1e-9)
    seed = np.zeros(NL)
    named = {"pl", "uk", "yi", "be", "pls", "ru", "lt", "de"}
    covered = set()
    for key, n in cty.lang.items():
        if key == "bepr":
            idx = [_L["be"], _L["pls"], _L["ru"]]
            w = share[idx] + 1e-6
            seed[idx] += n * w / w.sum()
            covered |= set(idx)
        elif key == "oth":
            idx = [j for c, j in _L.items() if c not in named]
            w = share[idx] + 1e-9
            seed[idx] += n * w / w.sum()
            covered |= set(idx)
        else:
            seed[_L[key]] += n
            covered.add(_L[key])
    rest = pop - seed.sum()
    free = [j for j in range(NL) if j not in covered]
    if rest > 0 and free:
        w = share[free] + 1e-9
        seed[free] += rest * w / w.sum()
    # unenumerated languages: keep the downscaled speakers, taken from their census category
    for lang, host in _HOST.items():
        n = share[_L[lang]] * pop
        if n <= 0:
            continue
        h = _L[host] if host in _L else None
        if h is not None and _L[lang] in covered:
            continue
        seed[_L[lang]] = max(seed[_L[lang]], n)
        if h is not None:
            seed[h] = max(seed[h] - n, 0.0)
    return seed


def _fit_counties(parent_lang: np.ndarray, child_lang: dict, n_iter: int = 60) -> dict:
    """Replace the downscaled county pattern by the 1931 county tables where
    known, fitted to the voivodeship's latent totals (see module docstring)."""
    kids = list(child_lang)
    ds = np.array([child_lang[k].sum(axis=0) for k in kids])                 # (K, NL)
    total = parent_lang.sum()
    known = {k: COUNTY_BY_CODE[k].pop for k in kids if k in COUNTY_BY_CODE and COUNTY_BY_CODE[k].pop}
    pops = ds.sum(axis=1).copy()
    if known:
        kn = np.array([k in known for k in kids])
        given = np.array([known.get(k, 0.0) for k in kids])
        rem = total - given.sum()
        if (~kn).any() and rem > 0.02 * total:
            pops = np.where(kn, given, pops / max(pops[~kn].sum(), 1e-9) * rem)
        else:
            pops = np.where(kn, given, pops)
    pops *= total / pops.sum()
    seed = np.array([_census_seed(COUNTY_BY_CODE[k], ds[j], pops[j])
                     if k in COUNTY_BY_CODE and COUNTY_BY_CODE[k].lang else ds[j] / max(ds[j].sum(), 1e-9) * pops[j]
                     for j, k in enumerate(kids)])
    col = parent_lang.sum(axis=0)
    seed += 1e-4 * pops[:, None] * col[None, :] / total
    X = seed
    for _ in range(n_iter):
        X *= np.where(X.sum(axis=0) > 0, col / np.maximum(X.sum(axis=0), 1e-12), 0.0)[None, :]
        X *= (pops / np.maximum(X.sum(axis=1), 1e-12))[:, None]
    # rural / urban split by language from the downscaled pattern, then fit the strata
    ru = np.array([child_lang[k] for k in kids])                             # (K, 2, NL)
    frac = np.where(ru.sum(axis=1, keepdims=True) > 0, ru / np.maximum(ru.sum(axis=1, keepdims=True), 1e-12),
                    (parent_lang / np.maximum(parent_lang.sum(axis=0), 1e-12))[None])
    Y = X[:, None, :] * frac
    for _ in range(n_iter):
        Y *= np.where(Y.sum(axis=0) > 0, parent_lang / np.maximum(Y.sum(axis=0), 1e-12), 0.0)[None]
        Y *= (pops / np.maximum(Y.sum(axis=(1, 2)), 1e-12))[:, None, None]
    return {k: Y[j] for j, k in enumerate(kids)}


def _parents(spec, codes):
    """``partition`` is a list of voivodeships with named splits (see
    ``data.subregions.SPLITS``), or ``counties`` / {"counties": [...]} to split
    voivodeships (all, or the listed ones) into their counties."""
    if spec == "counties" or (isinstance(spec, dict) and "counties" in spec):
        listed = spec["counties"] if isinstance(spec, dict) else "all"
        par = [c for c in codes if (listed == "all" or c in listed) and len(subregions.county_seats(c)) > 1]
        return par, "county"
    return [c for c in (spec or []) if c in codes and c in subregions.SPLITS], "named"


def apply_partition(regions, params: dict):
    """Return (regions, composition (R,2,G), node -> region code overrides)."""
    codes = [r.code for r in regions]
    parents, mode = _parents(params.get("partition", []), codes)
    comp = build_initial_composition(regions, params["census_variant"], params["lt_variant"]).pop
    if not parents:
        return regions, comp, {}
    ds, C = _initial_units(regions, comp, params)
    g = ds.grid
    Nc = ds.Nc
    group_lang = np.array([LANG_INDEX[l] for _, l in GROUPS])
    ur_ratio = piecewise(1931, params["economy"]["urban_rural_ratio"])
    new_regions, new_comp, node_region = [], [], {}
    for i, reg in enumerate(regions):
        if reg.code not in parents:
            new_regions.append(reg)
            new_comp.append(comp[i])
            continue
        kids = subregions.children(reg.code, mode)
        cells = np.where(g.region == i)[0]
        cell_child = subregions.assign(reg.code, g.lat[cells], g.lon[cells], kids)
        towns = np.where(ds.town_region == i)[0]
        town_child = subregions.assign(reg.code, ds.town_lat[towns], ds.town_lon[towns], kids)
        for n, k in zip(towns, town_child):
            node_region[ds.town_names[n]] = str(k)
        parent_lang = lang_totals(comp[i])                                # (2, NL)
        area_all = g.cell_km2[cells].sum()
        u_par = comp[i][1].sum() / max(comp[i].sum(), 1e-9)
        seat = {c: (la, lo) for la, lo, c in subregions.seat_table(reg.code, kids)}
        child_lang = {}
        for k in kids:
            mc = cells[cell_child == k]
            mt = towns[town_child == k]
            if not len(mc) and not len(mt):
                continue                     # a seat that wins neither land nor towns
            child_lang[k] = np.stack([C[mc].sum(axis=0), C[Nc + mc].sum(axis=0) + C[2 * Nc + mt].sum(axis=0)])
        if mode == "county":
            child_lang = _fit_counties(parent_lang, child_lang)
        for k, cl in child_lang.items():
            mc = cells[cell_child == k]
            ratio = np.where(parent_lang > 0, cl / np.maximum(parent_lang, 1e-12), 0.0)
            cc = comp[i] * ratio[:, group_lang]                           # (2, G)
            total = cc.sum()
            if mode == "county" or not len(mc):
                lat, lon = seat[k]
            else:
                w = C[mc].sum(axis=1) + C[Nc + mc].sum(axis=1) + 1e-9
                lat, lon = float((g.lat[mc] * w).sum() / w.sum()), float((g.lon[mc] * w).sum() / w.sum())
            cty = COUNTY_BY_CODE.get(k)
            src = (f"1931 county census, grade {cty.grade}" if cty is not None and cty.grade in "AB"
                   else "1931 population downscaled from the voivodeship")
            u_k = cc[1].sum() / max(total, 1e-9)
            income = reg.income_index * (u_k * ur_ratio + 1 - u_k) / (u_par * ur_ratio + 1 - u_par)
            new_regions.append(dataclasses.replace(
                reg, code=k, name=subregions.child_name(k), income_index=float(income),
                area_km2=max(reg.area_km2 * g.cell_km2[mc].sum() / max(area_all, 1e-9), 20.0),
                pop_1931=float(total), urban_1931=float(u_k),
                lat=lat, lon=lon, notes=f"sub-region of {reg.code} ({reg.name}); {src}"))
            new_comp.append(cc)
    return new_regions, np.array(new_comp), node_region
