import numpy as np

from plsim.data.languages import GROUP_INDEX, GROUPS
from plsim.language import REGIMES, census_mapping
from plsim.model import Simulation
from plsim.params import load_scenario


def _sim():
    p = load_scenario("baseline")
    p["partition"] = []
    p["end_year"] = 1933
    return Simulation(p)


def test_transmission_bounds():
    sim = _sim()
    M = sim.econ.modernisation(sim.urban_share())
    p_shift, dist, frac, mod, pol, omega = sim.lang.transmission(1932, sim.P, M, np.zeros(sim.R))
    assert p_shift.min() >= 0 and p_shift.max() <= sim.params["language"]["max_shift"] + 1e-12
    rows = dist.sum(axis=3)
    assert np.all((np.abs(rows - 1) < 1e-9) | (rows == 0))
    # monolingual mothers shift less than bilingual ones
    assert np.all(p_shift[..., 0] <= p_shift[..., 1] + 1e-12)


def test_enclave_protection():
    sim = _sim()
    sL, xK = sim.lang.local_environment(sim.P)
    kra = sim.codes.index("KRA")
    g = GROUP_INDEX[("RC", "wym")]
    # Wilamowice speakers see a far higher own-language share than the regional cell share
    cell_share = sim.P[kra, 0, g].sum() / sim.P[kra, 0].sum()
    assert sL[kra, 0, g] > 100 * cell_share


def test_horizontal_conserves_population():
    sim = _sim()
    before = sim.P.sum()
    sim.lang.horizontal(1932, sim.P, sim.econ.enrollment, sim.econ.modernisation(sim.urban_share()), np.zeros(sim.R))
    assert abs(sim.P.sum() - before) / before < 1e-9


def test_census_mappings_are_distributions():
    for regime in REGIMES:
        for (c, l) in GROUPS:
            for b in (0, 1):
                d = census_mapping(regime, c, l, b, 0, "WIL")
                assert abs(sum(d.values()) - 1) < 1e-9
