import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def short_run():
    """Baseline 1932-1941 on the 23 voivodeships (fast; mechanics tests)."""
    from plsim.model import Simulation
    from plsim.params import load_scenario
    p = load_scenario("baseline")
    p["partition"] = []
    p["end_year"] = 1941
    return Simulation(p).run()


@pytest.fixture(scope="session")
def county_run():
    """Baseline 1932-1941 at county level (the default)."""
    from plsim.model import Simulation
    from plsim.params import load_scenario
    p = load_scenario("baseline")
    p["end_year"] = 1941
    return Simulation(p).run()
