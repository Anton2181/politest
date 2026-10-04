"""Sub-regions, region-keyed settings and federal members."""
import numpy as np
import pytest

from plsim.data.regions import select_regions
from plsim.migration import MigrationModel
from plsim.model import Simulation
from plsim.params import load_scenario, region_lookup
from plsim.partition import apply_partition


def test_region_lookup_specificity():
    spec = {"default": 1, "LT_*": 4, "WIL": 2, "WIL.E": 3}
    assert region_lookup(spec, "WIL.E") == 3
    assert region_lookup(spec, "WIL.W") == 2
    assert region_lookup(spec, "WIL") == 2
    assert region_lookup(spec, "LT_KAU") == 4
    assert region_lookup(spec, "POZ") == 1


@pytest.fixture(scope="module")
def split():
    p = load_scenario("baseline")
    p["partition"] = ["BIA", "WIL", "NOW", "LWO"]
    regions = select_regions(True)
    return regions, apply_partition(regions, p), p


def test_children_add_up_to_parents(split):
    regions, (new, comp, nodes, _), p = split
    from plsim.data.census1931 import build_initial_composition
    old = build_initial_composition(regions, p["census_variant"], p["lt_variant"]).pop
    codes = [r.code for r in new]
    assert len(new) == len(regions) + 4
    for i, r in enumerate(regions):
        kids = [j for j, c in enumerate(codes) if c.split(".")[0] == r.code]
        assert np.allclose(comp[kids].sum(axis=0), old[i], rtol=1e-6, atol=1e-3), r.code
    assert nodes["Lwów"] == "LWO.E" and nodes["Wilno"] == "WIL.W" and nodes["Grodno"] == "BIA.E"
    assert nodes["Rzeszów"] == "LWO.W" and nodes["Baranowicze"] == "NOW.E"


def test_children_areas_and_languages(split):
    _, (new, comp, _, _), _ = split
    by = {r.code: (r, c) for r, c in zip(new, comp)}
    assert sum(by[c][0].area_km2 for c in ("WIL.W", "WIL.E")) == pytest.approx(29011, rel=1e-6)
    from plsim.spatial import lang_totals
    from plsim.data.languages import LANG_INDEX
    def share(code, lang):
        L = lang_totals(by[code][1]).sum(axis=0)
        return L[LANG_INDEX[lang]] / L.sum()
    # the Belarusian-speaking east of nowogródzkie vs the Polish-speaking Lida area
    assert share("NOW.E", "be") > 2 * share("NOW.W", "be")
    # Ukrainian east vs Polish west of the San
    assert share("LWO.E", "uk") > 2.5 * share("LWO.W", "uk")


def test_member_friction():
    regions = select_regions(True)
    p = load_scenario("baseline")["migration"]
    p = dict(p, member_friction={"PL|UA": 0.5})
    m = MigrationModel(p, regions, ["pl"] * len(regions))
    codes = [r.code for r in regions]
    m.member = np.array(["UA" if c in ("STA", "TAR") else ("LT" if c.startswith("LT") else "PL") for c in codes])
    f = m._member_friction()
    i, j, k = codes.index("STA"), codes.index("TAR"), codes.index("KRA")
    l = codes.index("LT_KAU")
    assert f[i, j] == 1.0 and f[i, k] == 0.5 and f[k, i] == 0.5
    assert f[k, l] == p["cross_border_factor"] and f[i, l] == p["cross_border_factor"]


def test_cantonal_scenario_short_run():
    p = load_scenario("ukraine_autonomy_tricantonal")
    p["end_year"] = 1935
    sim = Simulation(p)
    base = Simulation(load_scenario("baseline"))
    assert len(sim.codes) == len(base.codes) == 271
    assert sim.P.sum() == pytest.approx(base.P.sum(), rel=1e-9)
    dom = dict(zip(sim.codes, sim.dominant))
    mem = dict(zip(sim.codes, sim.member))
    assert dom["NOW.nieswiez"] == "be" and dom["LWO.przemysl"] == "pl" and dom["LWO.lwow"] == "uk"
    assert mem["POL.pinsk"] == "GD-B" and mem["WIL.wilno"] == "GD-P" and mem["BIA.bielskpodlaski"] == "PL"
    assert (sim.net.region >= 0).sum() == (base.net.region >= 0).sum()
    res = sim.run()
    assert np.isfinite(np.array(res.pop)).all() and np.array(res.pop).min() >= 0


def test_coofficial_languages():
    """Lithuanian, Polish and Belarusian co-official in the Grand Duchy from 1938."""
    from plsim.data.languages import GROUP_INDEX, LANG_INDEX
    sim = Simulation(load_scenario("autonomy_grand_duchy_coofficial"))
    i, k = sim.codes.index("WIL.wilno"), sim.codes.index("KRA.krakow")
    assert set(sim.official[i]) == {"lt", "pl", "be"} and sim.official[k] == ["pl"]
    assert sim.dominant[i] == "pl" and sim.dominant[sim.codes.index("POL.pinsk")] == "be"
    s37, s40 = sim.lang.status(1937), sim.lang.status(1940)
    assert s40[i, LANG_INDEX["be"]] == 1.0 and s37[i, LANG_INDEX["be"]] < 1.0
    assert s40[k, LANG_INDEX["be"]] < 1.0
    o = sim.lang.own_schooling(1940)
    assert o[i, GROUP_INDEX[("OR", "be")]] >= 0.9 and o[i, GROUP_INDEX[("RC", "pl")]] == 0.0   # Polish is the contact language
    assert sim.lang.targets[i, GROUP_INDEX[("RC", "pl")], GROUP_INDEX[("RC", "be")]]


def test_excluded_territory():
    """wakar_poland: Volhynia, Stanisławów, Tarnopol and the Lithuanian-claimed counties are foreign."""
    from plsim.data.geography import build_grid
    sim = Simulation(load_scenario("wakar_poland"))
    gone = [c for c in sim.codes if c.split(".")[0] in ("WOL", "STA", "TAR") or c.startswith("LT")]
    assert not gone and "WIL.wilno" not in sim.codes and "NOW.lida" not in sim.codes
    assert "WIL.glebokie" in sim.codes and "LWO.lwow" in sim.codes
    names = list(sim.net.names)
    assert sim.net.region[names.index("Wilno")] < 0 and sim.net.region[names.index("Łuck")] < 0
    assert sim.net.region[names.index("Lwów")] >= 0
    g = build_grid(sim.codes)
    full = build_grid(Simulation(load_scenario("ii_rp_only")).codes)          # Poland alone, whole
    assert 0.6 < len(g.lat) / len(full.lat) < 0.8 and set(np.unique(g.region)) == set(range(len(sim.codes)))
    assert {o for os_ in sim.official for o in os_} == {"pl", "be"}


def test_units_nest_counties_within_members(split):
    _, (new, _, _, _), _ = split
    codes = [r.code for r in new]
    m = MigrationModel(load_scenario("baseline")["migration"], new, ["pl"] * len(new))
    m.member = np.array(["GD-B" if c == "WIL.E" else ("LT" if c.startswith("LT") else "PL") for c in codes])
    unit = m.units()
    assert unit[codes.index("BIA.W")] == unit[codes.index("BIA.E")] != unit[codes.index("WAR")]
    assert unit[codes.index("WIL.W")] != unit[codes.index("WIL.E")]         # different members
    assert unit.max() + 1 == len(new) - 3


def test_split_voivodeships_migrate_like_the_whole():
    """Split into sub-regions of one member, a voivodeship sends and draws
    migrants as one unit: its total stays close to the unsplit run."""
    p = load_scenario("baseline")
    p["end_year"] = 1945
    p["partition"] = []
    q = load_scenario("baseline")
    q["end_year"] = 1945
    q["partition"] = ["BIA", "WIL", "NOW", "LWO"]
    a, b = Simulation(p).run(), Simulation(q).run()

    def totals(res):
        x = np.asarray(res.pop[-1], float).reshape(len(res.region_codes), -1).sum(axis=1)
        out = {}
        for c, v in zip(res.region_codes, x):
            out[c.split(".")[0]] = out.get(c.split(".")[0], 0.0) + v
        return out
    ta, tb = totals(a), totals(b)
    for c in ["BIA", "WIL", "NOW", "LWO", "WAW", "WAR"]:
        assert tb[c] == pytest.approx(ta[c], rel=0.006), c      # unnested: up to 1.5 % off by 1945


# ---------------------------------------------------------------- county level
from plsim.data.counties import BY_PARENT, COUNTIES  # noqa: E402
from plsim.data.regions import REGIONS  # noqa: E402

REGION_POP = {r.code: r.pop_1931 for r in REGIONS}


def test_county_table_integrity():
    codes = [c.code for c in COUNTIES]
    assert len(codes) == len(set(codes))
    for c in COUNTIES:
        if c.lang and c.pop:
            assert sum(c.lang.values()) <= c.pop * 1.01, c.code      # summaries carry small slips
        east = c.parent.startswith(("BY_", "LV_", "RU_"))
        west = c.parent.startswith(("DE_", "DZ_", "CS_"))
        assert 47.5 < c.lat < (57.5 if east else 56.6) and (14.0 if west else 15.5) < c.lon < (33.0 if east else 28.5), \
            c.code


@pytest.mark.parametrize("parent", ["TAR", "STA", "LWO", "WIL", "NOW", "BIA", "WOL", "POM", "POL", "LUB", "KIE", "LOD",
                                    "POZ", "SLA", "KRA", "BY_WIT", "BY_MIN", "BY_MOH", "BY_HOM", "LV_LAT", "RU_VIT"])
def test_grade_a_counties_add_up_to_the_voivodeship(parent):
    """The county tables reproduce the 1931 voivodeship populations."""
    from plsim.data.counties import GROUPS
    tot = sum(c.pop for c in BY_PARENT[parent] if c.pop)
    tot += sum({m[0]: g for m, g in GROUPS.values() if m[0].split(".")[0] == parent}.values())
    assert tot == pytest.approx(REGION_POP[parent], rel=0.004)


def test_census_1931_rows_add_up():
    """Every row of the census table adds up to its printed total, and the
    voivodeships read whole reproduce their census populations."""
    import collections
    import csv
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "plsim", "data", "census1931_powiaty.csv")
    cols = ["pl", "uk", "rue", "be", "ru", "cs", "lt", "de", "yi", "he", "oth", "pls", "unk"]
    tot = collections.Counter()
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(l for l in fh if not l.startswith("#")):
            assert sum(int(r[c] or 0) for c in cols) == int(r["pop"]), r["county"]
            if not r["county"].endswith("*"):
                tot[r["county"].split(".")[0]] += int(r["pop"])
    for par in ("LOD", "KIE", "LUB", "NOW", "POL", "POZ", "SLA", "KRA"):
        assert tot[par] == pytest.approx(REGION_POP[par], abs=50), par
    assert REGION_POP["WAR"] - tot["WAR"] == 128144          # Płock with its city: the city's page is missing


def test_tarnopol_counties_reproduce_declared_languages():
    rows = BY_PARENT["TAR"]
    tot = sum(c.pop for c in rows)
    pl = sum(c.lang.get("pl", 0) for c in rows) / tot
    uk = sum(c.lang.get("uk", 0) for c in rows) / tot
    assert pl == pytest.approx(0.493, abs=0.002) and uk == pytest.approx(0.455, abs=0.002)


@pytest.fixture(scope="module")
def county_split():
    p = load_scenario("baseline")
    p["partition"] = "counties"
    p["census_variant"], p["lt_variant"] = "official", "census_1923"    # compared with the printed tables below
    regions = select_regions(True)
    return regions, apply_partition(regions, p), p


def test_counties_add_up_and_follow_the_census(county_split):
    regions, (new, comp, nodes, _), p = county_split
    from plsim.data.census1931 import build_initial_composition
    from plsim.data.languages import LANG_INDEX
    from plsim.spatial import lang_totals
    old = build_initial_composition(regions, p["census_variant"], p["lt_variant"]).pop
    codes = [r.code for r in new]
    assert len(new) > 250
    for i, r in enumerate(regions):
        kids = [j for j, c in enumerate(codes) if c.split(".")[0] == r.code]
        assert np.allclose(comp[kids].sum(axis=0), old[i], rtol=1e-5, atol=1.0), r.code
    j = codes.index("LWO.turka")
    L = lang_totals(comp[j]).sum(axis=0)
    assert L[LANG_INDEX["uk"]] / L.sum() == pytest.approx(0.704, abs=0.02)        # census 70.4 %
    j = codes.index("WIL.swieciany")
    L = lang_totals(comp[j]).sum(axis=0)
    assert L[LANG_INDEX["lt"]] / L.sum() == pytest.approx(0.315, abs=0.03)         # census 31.5 %
    assert nodes["Lwów"] == "LWO.lwow" and nodes["Pińsk"] == "POL.pinsk"


def test_census_strata_add_up():
    """census1931_strata.csv: every voivodeship adds up to its census population (Warsaw voivodeship is short
    the city of Płock, whose page is missing) and every row's religions and languages to its population."""
    import collections
    import csv
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "plsim", "data", "census1931_strata.csv")
    tot = collections.Counter()
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(l for l in fh if not l.startswith("#")):
            pop = int(r["pop"])
            tot[r["county"][:3]] += pop
            for cols in (("rc", "gc", "or", "ev", "xc", "jw", "xn", "ro"),
                         ("pl", "uk", "rue", "be", "pls", "ru", "cs", "lt", "de", "yi", "he", "oth", "unk")):
                s = sum(int(r[c] or 0) for c in cols)
                assert pop - 0.02 * pop <= s <= pop + max(0.001 * pop, 100), (r["county"], r["page"], cols[0])
    census = {"WAR": 2_529_228 - 32_998, "LOD": 2_632_010, "KIE": 2_935_697, "LUB": 2_464_936, "BIA": 1_643_844,
              "WIL": 1_275_939, "NOW": 1_057_147, "POL": 1_131_939, "WOL": 2_085_574, "POZ": 2_106_500,
              "POM": 1_080_138, "SLA": 1_295_027, "KRA": 2_297_807, "LWO": 3_127_409, "STA": 1_480_285,
              "TAR": 1_600_406}
    assert dict(tot) == census


def test_counties_follow_the_census_religions_and_towns(county_split):
    """The county split reproduces the census religions by stratum (shares among the printed religions) and
    the census urban share of every county."""
    from plsim.data.census1931 import OTHER_CHRISTIAN_BIN, RELIGION_BIN, BIN_COMMUNITIES
    from plsim.data.counties import STRATA
    from plsim.data.languages import COMM_INDEX, GROUPS
    from plsim.partition import _strata_key
    regions, (new, comp, nodes, _), p = county_split
    comm = np.array([COMM_INDEX[c] for c, _ in GROUPS])
    rel_err, urb_err = [], []
    for j, r in enumerate(new):
        st = STRATA.get(_strata_key(r.code))
        if st is None:
            continue
        cens_u = st["urban"][0] / sum(v[0] for v in st.values()) if "urban" in st else 0.0
        urb_err.append(abs(comp[j][1].sum() / comp[j].sum() - cens_u))
        rb = dict(RELIGION_BIN, xc=OTHER_CHRISTIAN_BIN.get(r.code[:3], "RC"))
        for s, name in enumerate(("rural", "urban")):
            if name not in st:
                continue
            _, _, rel, printed = st[name]
            bins = {rb[c] for c in printed if c in rb}
            cen = {b: sum(v for c, v in rel.items() if rb.get(c) == b) for b in bins}
            mod = {b: comp[j][s][np.isin(comm, [COMM_INDEX[c] for c in BIN_COMMUNITIES[b]])].sum() for b in bins}
            if len(bins) > 1 and sum(cen.values()) > 0:
                rel_err += [abs(mod[b] / sum(mod.values()) - cen[b] / sum(cen.values())) for b in bins]
    assert np.mean(rel_err) < 0.01 and np.percentile(rel_err, 95) < 0.03
    assert np.mean(urb_err) < 0.01 and np.max(urb_err) < 0.1


def test_voivodeship_towns_follow_the_census():
    """The reconstruction's urban share of each census language and religion is the census strata's."""
    from plsim.data.census1931 import CENSUS_CATEGORY, URBAN_TARGETS_1931, build_initial_composition
    from plsim.data.languages import LANG_INDEX
    from plsim.spatial import lang_totals
    regions = select_regions(True)
    comp = build_initial_composition(regions, "official", "census_1923").pop
    for i, r in enumerate(regions):
        if r.code not in URBAN_TARGETS_1931:
            continue
        u, lang, rel = URBAN_TARGETS_1931[r.code]
        assert comp[i][1].sum() / comp[i].sum() == pytest.approx(u, abs=0.002), r.code
        L = lang_totals(comp[i])
        for cat in ("pl", "uk", "yi", "de", "be"):
            idx = [LANG_INDEX[l] for l, c in CENSUS_CATEGORY.items() if c == cat]
            if lang.get(cat, 0) > 0 and L[:, idx].sum() > 0.02 * L.sum():
                assert L[1, idx].sum() / L[:, idx].sum() == pytest.approx(lang[cat], abs=0.02), (r.code, cat)


def test_every_county_holds_its_seat_and_its_town():
    """The weighted diagram keeps each county's seat, and the town of that name, inside the county."""
    from plsim.data import subregions as sr
    from plsim.data.network import NODES
    weights = sr.county_weights()
    for par in {c.parent for c in COUNTIES if c.parent in REGION_POP}:
        kids = sr.children(par, "county")
        if len(kids) < 2 or not any(k in weights for k in kids):      # the Polish voivodeships
            continue
        seats = {c: (la, lo) for c, _, la, lo in sr.county_seats(par)}
        got = sr.assign(par, [seats[k][0] for k in kids], [seats[k][1] for k in kids], kids)
        assert list(got) == kids, par
        towns = [n for n in NODES if n.region == par and f"{par}.{sr.slug(n.name)}" in kids]
        got = sr.assign(par, [n.lat for n in towns], [n.lon for n in towns], kids)
        assert [f"{par}.{sr.slug(n.name)}" for n in towns] == list(got), par
