"""Initial population of sub-regions (see ``data.subregions``).

The 1931 census is tabulated by voivodeship.  To start a split voivodeship,
its census reconstruction is first downscaled to the 7 km grid
(``spatial.Downscaler.initial_state``: county anchors + IPF).  The cells and
towns of each sub-region are then summed.

* **Languages.** Each sub-region gets the rural and urban speakers of every
  language found on its cells and in its towns.
* **Communities.** Within a language, the split between communities
  (Catholic, Orthodox, Greek Catholic ...) is the parent's.
* **Other inputs.** Fertility, mortality, income and literacy are the
  parent's. Area is the parent's official area times the sub-region's share
  of the parent's cells.

The children of a voivodeship therefore always add up to the parent, by
rural/urban stratum and language.
"""
from __future__ import annotations

import dataclasses
from types import SimpleNamespace

import numpy as np

from .data import subregions
from .data.census1931 import build_initial_composition
from .data.geography import build_grid
from .data.languages import GROUPS, LANG_INDEX
from .data.network import NODES
from .spatial import Downscaler, lang_totals


def _initial_units(regions, comp: np.ndarray, params: dict):
    codes = [r.code for r in regions]
    reg_idx = {c: i for i, c in enumerate(codes)}
    grid = build_grid(codes)
    ns = SimpleNamespace(
        region_codes=codes, params=params,
        node_region=[reg_idx.get(n.region, -1) for n in NODES],
        node_lat=[n.lat for n in NODES], node_lon=[n.lon for n in NODES], node_names=[n.name for n in NODES],
        years=[], pop0=comp, pop=[], shift_net=[], town_pop0=np.array([n.pop_1931 for n in NODES], float),
        town_pop=[])
    ds = Downscaler(ns, grid=grid)
    return ds, ds.initial_state()


def apply_partition(regions, params: dict):
    """Return (regions, composition (R,2,G), node -> region code overrides)."""
    codes = [r.code for r in regions]
    parents = [c for c in params.get("partition", []) if c in codes and c in subregions.SPLITS]
    comp = build_initial_composition(regions, params["census_variant"], params["lt_variant"]).pop
    if not parents:
        return regions, comp, {}
    ds, C = _initial_units(regions, comp, params)
    g = ds.grid
    Nc = ds.Nc
    group_lang = np.array([LANG_INDEX[l] for _, l in GROUPS])
    new_regions, new_comp, node_region = [], [], {}
    for i, reg in enumerate(regions):
        if reg.code not in parents:
            new_regions.append(reg)
            new_comp.append(comp[i])
            continue
        kids = subregions.children(reg.code)
        cells = np.where(g.region == i)[0]
        cell_child = subregions.assign(reg.code, g.lat[cells], g.lon[cells])
        towns = np.where(ds.town_region == i)[0]
        town_child = subregions.assign(reg.code, ds.town_lat[towns], ds.town_lon[towns])
        for n, k in zip(towns, town_child):
            node_region[ds.town_names[n]] = str(k)
        parent_lang = lang_totals(comp[i])                                # (2, NL)
        area_all = g.cell_km2[cells].sum()
        for k in kids:
            mc = cells[cell_child == k]
            mt = towns[town_child == k]
            rural = C[mc].sum(axis=0)
            urban = C[Nc + mc].sum(axis=0) + C[2 * Nc + mt].sum(axis=0)
            child_lang = np.stack([rural, urban])                         # (2, NL)
            ratio = np.where(parent_lang > 0, child_lang / np.maximum(parent_lang, 1e-12), 0.0)
            cc = comp[i] * ratio[:, group_lang]                           # (2, G)
            total = cc.sum()
            w = C[mc].sum(axis=1) + C[Nc + mc].sum(axis=1) + 1e-9
            new_regions.append(dataclasses.replace(
                reg, code=k, name=subregions.NAMES.get(k, k),
                area_km2=reg.area_km2 * g.cell_km2[mc].sum() / max(area_all, 1e-9),
                pop_1931=float(total), urban_1931=float(cc[1].sum() / max(total, 1e-9)),
                lat=float((g.lat[mc] * w).sum() / w.sum()), lon=float((g.lon[mc] * w).sum() / w.sum()),
                notes=f"sub-region of {reg.code} ({reg.name}); 1931 population downscaled from the voivodeship"))
            new_comp.append(cc)
    return new_regions, np.array(new_comp), node_region
