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
    regions, (new, comp, nodes), p = split
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
    _, (new, comp, _), _ = split
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
    assert len(sim.codes) == 27
    assert sim.P.sum() == pytest.approx(base.P.sum(), rel=1e-9)
    assert sim.dominant[sim.codes.index("NOW.E")] == "be"
    assert sim.dominant[sim.codes.index("LWO.W")] == "pl"
    assert sim.member[sim.codes.index("POL")] == "GD-B"
    assert (sim.net.region >= 0).sum() == (base.net.region >= 0).sum()
    res = sim.run()
    assert np.isfinite(np.array(res.pop)).all() and np.array(res.pop).min() >= 0
