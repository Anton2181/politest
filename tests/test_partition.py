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
    assert len(sim.codes) == len(base.codes) == 270
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
        if c.lang:
            assert sum(c.lang.values()) <= c.pop * 1.01, c.code      # summaries carry small slips
        east = c.parent.startswith(("BY_", "LV_", "RU_"))
        assert 47.5 < c.lat < (57.5 if east else 56.6) and 15.5 < c.lon < (33.0 if east else 28.5), c.code


@pytest.mark.parametrize("parent", ["TAR", "STA", "LWO", "WIL", "NOW", "BIA", "WOL", "POM", "BY_WIT", "BY_MIN", "BY_MOH",
                                    "BY_HOM", "LV_LAT", "RU_VIT"])
def test_grade_a_counties_add_up_to_the_voivodeship(parent):
    """The county tables reproduce the 1931 voivodeship populations."""
    tot = sum(c.pop for c in BY_PARENT[parent])
    assert tot == pytest.approx(REGION_POP[parent], rel=0.004)


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
    assert L[LANG_INDEX["uk"]] / L.sum() == pytest.approx(0.844, abs=0.02)        # census 84.4 %
    j = codes.index("WIL.swieciany")
    L = lang_totals(comp[j]).sum(axis=0)
    assert L[LANG_INDEX["lt"]] / L.sum() == pytest.approx(0.315, abs=0.03)         # census 31.5 %
    assert nodes["Lwów"] == "LWO.lwow" and nodes["Pińsk"] == "POL.pinsk"
