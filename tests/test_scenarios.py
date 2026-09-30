import pytest

from plsim.cli import all_scenarios
from plsim.data.regions import select_regions
from plsim.params import load_scenario


@pytest.mark.parametrize("name", all_scenarios())
def test_scenario_loads(name):
    p = load_scenario(name)
    assert p["meta"]["name"] == name
    assert p["start_year"] == 1932


def test_ii_rp_only_excludes_lithuania():
    p = load_scenario("ii_rp_only")
    assert len(select_regions(p["include_lithuania"])) == 17


def test_polonizing_union_replaces_dominant_language():
    assert load_scenario("polonizing_union")["dominant_language"] == {"default": "pl"}
