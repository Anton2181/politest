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
downscaled. Powiaty merged in 1932 have one census row for the group
(``data.counties.GROUPS``): the group's population is split by the
downscaled pattern, and each member takes the group's language shares.

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
from .data.counties import GROUPS as COUNTY_GROUPS
from .data.census1931 import build_initial_composition
from .data.geography import MODEL_DLAT, MODEL_DLON, build_grid, haversine_matrix
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
# a piece of a unit cut along a governorate border is kept only if it holds
# at least 5 % of the unit and this many people (smaller ones are slivers of
# the 300 m governorate outlines against the 1932 borders)
MIN_PIECE = 5000.0


def _census_seed(cty, ds: np.ndarray, pop: float) -> np.ndarray:
    """Latent-language seed (NL,) from a county's declared mother tongue.
    ``ds`` is the downscaled language pattern of the county (NL,)."""
    share = ds / max(ds.sum(), 1e-9)
    seed = np.zeros(NL)
    named = {"pl", "uk", "yi", "be", "pls", "ru", "lt", "de"}
    covered = set()
    tot = sum(cty.lang.values())
    f = pop / tot if cty.pop is None and tot > 0 else 1.0      # shares only (a 1932 group, a page missing)
    for key, n in cty.lang.items():
        n = n * f
        if key == "bepr":
            idx = [_L["be"], _L["pls"], _L["ru"]]
            w = share[idx] + 1e-6
            seed[idx] += n * w / w.sum()
            covered |= set(idx)
        elif key == "oth":
            # languages the census hid inside Polish or Ukrainian are not "other"
            idx = [j for c, j in _L.items() if c not in named and _HOST.get(c, "oth") not in named]
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


def _fit_counties(parent_lang: np.ndarray, child_lang: dict, n_iter: int = 60, absorbed: dict | None = None) -> dict:
    """Replace the downscaled county pattern by the 1931 county tables where
    known, fitted to the voivodeship's latent totals (see module docstring).
    ``absorbed`` {county: [counties without cells]}: a county that wins no
    cell hands its census population and languages to its neighbour."""
    kids = list(child_lang)
    absorbed = absorbed or {}
    ds = np.array([child_lang[k].sum(axis=0) for k in kids])                 # (K, NL)
    total = parent_lang.sum()
    known = {k: COUNTY_BY_CODE[k].pop for k in kids if k in COUNTY_BY_CODE and COUNTY_BY_CODE[k].pop}
    for k, gone in absorbed.items():
        extra = [COUNTY_BY_CODE[d].pop for d in gone if d in COUNTY_BY_CODE]
        if k in known and all(extra):
            known[k] += sum(extra)
    pops = ds.sum(axis=1).copy()
    # powiaty merged in 1932: one census population, split by the downscaled pattern
    for j, k in enumerate(kids):
        if k in COUNTY_GROUPS and k not in known:
            members, gpop = COUNTY_GROUPS[k]
            idx = [kids.index(m) for m in members if m in kids]
            known[k] = gpop * pops[j] / max(pops[idx].sum(), 1e-9)
    if known:
        kn = np.array([k in known for k in kids])
        given = np.array([known.get(k, 0.0) for k in kids])
        rem = total - given.sum()
        if (~kn).any() and rem > 0.02 * total:
            pops = np.where(kn, given, pops / max(pops[~kn].sum(), 1e-9) * rem)
        else:
            pops = np.where(kn, given, pops)
    pops *= total / pops.sum()
    def seed_of(k, j, pop):
        if k in COUNTY_BY_CODE and COUNTY_BY_CODE[k].lang:
            return _census_seed(COUNTY_BY_CODE[k], ds[j], pop)
        return ds[j] / max(ds[j].sum(), 1e-9) * pop

    seed = []
    for j, k in enumerate(kids):
        gone = [d for d in absorbed.get(k, []) if d in COUNTY_BY_CODE and COUNTY_BY_CODE[d].pop]
        own = pops[j] - sum(COUNTY_BY_CODE[d].pop for d in gone) * pops[j] / max(known.get(k, pops[j]), 1e-9)
        s_k = seed_of(k, j, max(own, 0.0))
        for d in gone:
            share = COUNTY_BY_CODE[d].pop * pops[j] / max(known.get(k, pops[j]), 1e-9)
            s_k = s_k + (_census_seed(COUNTY_BY_CODE[d], ds[j], share) if COUNTY_BY_CODE[d].lang
                         else ds[j] / max(ds[j].sum(), 1e-9) * share)
        seed.append(s_k)
    seed = np.array(seed)
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


def _cut(code, lang, cells, towns, g, ds, C, groups):
    """Pieces of a unit along the edges of the scenario's governorate groups
    (``data.governorates``). ``lang`` (2, NL) is the unit's latent language
    totals, ``cells`` and ``towns`` its places. Returns
    [(code, lang, cell mask, town mask, group)], the largest piece first. A
    unit that is not cut keeps its code; the pieces of a cut unit are coded by
    the letters they cover (``data.governorates.piece_code``), the largest
    taking every letter the others do not. A piece smaller than 5 % of the
    unit (or 2,000 people) stays with the largest."""
    from .data.governorates import letter, piece_code, piece_letters
    lets = piece_letters(groups)
    grp_of = {c: gname for gname, ls in lets.items() for c in ls}
    Nc = ds.Nc
    cg = np.array([grp_of.get(c) for c in letter(g.lat[cells], g.lon[cells])], dtype=object)
    # a town takes the governorate of its unit's nearest place (towns on a border river)
    if len(cells) and len(towns):
        near = haversine_matrix(ds.town_lat[towns], ds.town_lon[towns], g.lat[cells], g.lon[cells]).argmin(axis=1)
        tg = cg[near]
    else:
        tg = np.array([grp_of.get(c) for c in letter(ds.town_lat[towns], ds.town_lon[towns])], dtype=object)
    # downscaled people by (stratum, language) in each group's part
    part = {}
    for gname in dict.fromkeys(list(cg) + list(tg)):
        mc, mt = cells[cg == gname], towns[tg == gname]
        part[gname] = np.stack([C[mc].sum(axis=0), C[Nc + mc].sum(axis=0) + C[2 * Nc + mt].sum(axis=0)])
    size = {k: v.sum() for k, v in part.items()}
    total = sum(size.values())
    main = max(size, key=size.get) if size else None
    kept = [k for k in size if k != main and size[k] >= max(0.05 * total, MIN_PIECE)]
    if not kept:
        return [(code, lang, np.ones(len(cells), bool), np.ones(len(towns), bool), main)]
    own = {k: np.isin(cg, [k]) for k in kept}
    town_own = {k: np.isin(tg, [k]) for k in kept}
    rest_c = ~np.any(list(own.values()), axis=0)
    rest_t = ~np.any(list(town_own.values()), axis=0) if len(towns) else np.zeros(0, bool)
    whole = sum(part.values())
    # every piece is named by the letters it covers (the largest takes the rest),
    # so no piece inherits a setting resolved for another
    taken = "".join(lets[k] for k in kept)
    main_lets = "".join(c for c in "VKGMOTSx" if c not in taken)
    out = []
    for k, mc, mt in [(main, rest_c, rest_t)] + [(k, own[k], town_own[k]) for k in kept]:
        if k == main:
            pc = whole - sum(part[j] for j in kept)
        else:
            pc = part[k]
        share = np.where(whole > 0, pc / np.maximum(whole, 1e-12), mc.mean())
        out.append((piece_code(code, main_lets if k == main else lets[k]), lang * share, mc, mt, k))
    return out


def apply_partition(regions, params: dict):
    """Return (regions, composition (R,2,G), node -> region code overrides,
    unit -> governorate group). With ``governorates`` set, units that straddle
    the edge of a group are cut into pieces (``_cut``)."""
    codes = [r.code for r in regions]
    parents, mode = _parents(params.get("partition", []), codes)
    groups = params.get("governorates") or {}
    comp = build_initial_composition(regions, params["census_variant"], params["lt_variant"]).pop
    if not parents and not groups:
        return regions, comp, {}, {}
    ds, C = _initial_units(regions, comp, params)
    g = ds.grid
    Nc = ds.Nc
    group_lang = np.array([LANG_INDEX[l] for _, l in GROUPS])
    ur_ratio = piecewise(1931, params["economy"]["urban_rural_ratio"])
    new_regions, new_comp, node_region, labels = [], [], {}, {}
    for i, reg in enumerate(regions):
        cells = np.where(g.region == i)[0]
        towns = np.where(ds.town_region == i)[0]
        parent_lang = lang_totals(comp[i])                                # (2, NL)
        if reg.code not in parents:
            pieces = _cut(reg.code, parent_lang, cells, towns, g, ds, C, groups) if groups else [(reg.code, None, None, None, None)]
            if len(pieces) == 1:
                new_regions.append(reg)
                new_comp.append(comp[i])
                labels[reg.code] = pieces[0][4]
                continue
            seat = {reg.code: (reg.lat, reg.lon)}
            units = [(pc, pl, cells[mc], towns[mt], gname) for pc, pl, mc, mt, gname in pieces]
            base_of = {pc: reg.code for pc, *_ in pieces}
        else:
            kids = subregions.children(reg.code, mode)
            cell_child = subregions.assign(reg.code, g.lat[cells], g.lon[cells], kids)
            town_child = subregions.assign(reg.code, ds.town_lat[towns], ds.town_lon[towns], kids)
            seat = {c: (la, lo) for la, lo, c in subregions.seat_table(reg.code, kids)}
            child_lang, gone = {}, []
            for k in kids:
                mc = cells[cell_child == k]
                mt = towns[town_child == k]
                if not len(mc) and not len(mt):
                    gone.append(k)               # a seat that wins neither land nor towns
                    continue
                child_lang[k] = np.stack([C[mc].sum(axis=0), C[Nc + mc].sum(axis=0) + C[2 * Nc + mt].sum(axis=0)])
            if mode == "county":
                absorbed: dict = {}
                for d in gone:                   # its people go to the nearest county
                    la0, lo0 = seat[d]
                    near = min(child_lang, key=lambda k: (seat[k][0] - la0) ** 2 + ((seat[k][1] - lo0) * 0.63) ** 2)
                    absorbed.setdefault(near, []).append(d)
                child_lang = _fit_counties(parent_lang, child_lang, absorbed=absorbed)
            units, base_of = [], {}
            for k, cl in child_lang.items():
                mc, mt = cells[cell_child == k], towns[town_child == k]
                pieces = _cut(k, cl, mc, mt, g, ds, C, groups) if groups else [(k, cl, None, None, None)]
                for pc, pl, pmc, pmt, gname in pieces:
                    units.append((pc, pl, mc if pmc is None else mc[pmc], mt if pmt is None else mt[pmt], gname))
                    base_of[pc] = k
        area_all = g.cell_km2[cells].sum()
        u_par = comp[i][1].sum() / max(comp[i].sum(), 1e-9)
        for k, cl, mc, mt, gname in units:
            labels[k] = gname
            for n in mt:
                node_region[ds.town_names[n]] = str(k)
            ratio = np.where(parent_lang > 0, cl / np.maximum(parent_lang, 1e-12), 0.0)
            cc = comp[i] * ratio[:, group_lang]                           # (2, G)
            total = cc.sum()
            base = base_of[k]
            if base == k and (mode == "county" or reg.code not in parents) and base in seat:
                lat, lon = seat[base]
            elif not len(mc):
                lat, lon = seat.get(base, (reg.lat, reg.lon))
            else:
                w = C[mc].sum(axis=1) + C[Nc + mc].sum(axis=1) + 1e-9
                lat, lon = float((g.lat[mc] * w).sum() / w.sum()), float((g.lon[mc] * w).sum() / w.sum())
            cty = COUNTY_BY_CODE.get(base)
            src = (f"1931 county census, grade {cty.grade}" if cty is not None and cty.grade in "ABE"
                   else "1931 population downscaled from the voivodeship")
            name = subregions.child_name(base) if base != reg.code else reg.name
            if k != base:
                from .data.governorates import NAMES, split_code
                govs = [NAMES[c] for c in split_code(k)[1] if c in NAMES]
                name = f"{name} ({', '.join(govs) if gname is not None else 'outside'} part)"
                src += "; the part of it in the " + (", ".join(govs) + " governorate(s) of 1897" if gname is not None
                                                      else "governorates outside the scenario's groups")
            u_k = cc[1].sum() / max(total, 1e-9)
            income = reg.income_index * (u_k * ur_ratio + 1 - u_k) / (u_par * ur_ratio + 1 - u_par)
            new_regions.append(dataclasses.replace(
                reg, code=k, name=name, income_index=float(income),
                area_km2=max(reg.area_km2 * g.cell_km2[mc].sum() / max(area_all, 1e-9), 20.0),
                pop_1931=float(total), urban_1931=float(u_k),
                lat=lat, lon=lon, notes=f"sub-region of {reg.code} ({reg.name}); {src}"))
            new_comp.append(cc)
    return new_regions, np.array(new_comp), node_region, labels
