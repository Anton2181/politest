"""The west lands (data.west), border changes and events (plsim.history)."""
import numpy as np
import pytest

from plsim.data.regions import REGIONS, select_regions, state_of_code
from plsim.data.west import REGION_POP, UNITS, region_groups


def test_west_regions_and_units_add_up():
    west = [r for r in REGIONS if r.country in ("DE", "DZ", "CS")]
    assert {r.code for r in west} == set(REGION_POP)
    for r in west:
        assert state_of_code(r.code) == r.country
        g = region_groups(r.code)
        assert abs(sum(g.values()) - 1) < 1e-9
        assert any(u[2] == r.code for u in UNITS)
    # the land Poland got in 1945 had about 8.1 M people in 1933 and Danzig 0.4 M
    de = sum(v for k, v in REGION_POP.items() if k.startswith("DE_"))
    assert 7.9e6 < de < 8.3e6
    assert select_regions(include_west=["DE_*"])[-1].code.startswith("DE_")
    assert not any(r.country == "DE" for r in select_regions())


def test_west_land_on_the_grid():
    from plsim.data.geography import state_of
    # Breslau, Danzig, Allenstein, Karviná, Stettin; Warsaw and Berlin
    st = state_of([51.11, 54.35, 53.78, 49.86, 53.43, 52.23, 52.52], [17.03, 18.65, 20.49, 18.54, 14.55, 21.01, 13.40])
    assert list(st) == ["DE", "DZ", "DE", "CS", "DE", "PL", ""]


@pytest.fixture(scope="module")
def hist_run():
    """The historical scenario at voivodeship level, 1932-1950 (fast)."""
    from plsim.model import Simulation
    from plsim.params import load_scenario
    p = load_scenario("historical")
    p["partition"] = []
    p["end_year"] = 1950
    return Simulation(p).run()


def test_history_keeps_the_accounts(hist_run):
    A = hist_run.arrays()
    tot = A["pop"].sum(axis=(1, 2, 3))
    for i in range(1, len(tot)):
        exp = tot[i - 1] + A["births"][i].sum() - A["deaths"][i].sum() - A["emig"][i].sum() + A["immig"][i].sum()
        assert abs(tot[i] - exp) / tot[i] < 1e-6, hist_run.years[i]
    I = np.array(hist_run.identity).sum(axis=(1, 2))
    assert np.allclose(I, tot, rtol=1e-5)


def test_border_change_and_war(hist_run):
    from plsim.history import members_at
    from plsim.data.languages import GROUPS
    codes = hist_run.region_codes
    m44, m46 = members_at(hist_run, 1944), members_at(hist_run, 1946)
    assert m44[codes.index("DE_WRO")] == "DE" and m46[codes.index("DE_WRO")] == "PL"
    assert m44[codes.index("WOL")] == "PL" and m46[codes.index("WOL")] == "SU"
    assert m46[codes.index("KRA")] == "PL"
    pop = np.array(hist_run.pop)
    jews = [g for g, (c, _) in enumerate(GROUPS) if c in ("JW", "JH")]
    j39 = pop[hist_run.years.index(1939)][:, :, jews].sum()
    j46 = pop[hist_run.years.index(1946)][:, :, jews].sum()
    assert j46 < 0.15 * j39
    # the German land is resettled: German speakers fall, Polish speakers rise
    de = [g for g, (_, l) in enumerate(GROUPS) if l == "de"]
    pl = [g for g, (_, l) in enumerate(GROUPS) if l == "pl"]
    rt = [i for i, c in enumerate(codes) if c[:3] in ("DE_", "DZ_")]
    t44, t50 = hist_run.years.index(1944), hist_run.years.index(1950)
    assert pop[t50][rt][:, :, de].sum() < 0.15 * pop[t44][rt][:, :, de].sum()
    assert pop[t50][rt][:, :, pl].sum() > 3 * pop[t44][rt][:, :, pl].sum()


def test_forced_labour_comes_back(hist_run):
    """``away`` events: 2.1 M taken in 1940-44, 92 % of them due back in
    1945-48, fewer for the deaths abroad."""
    log = hist_run.history_log
    away = sum(e["people"] for e in log if e["kind"] == "away")
    back = sum(e["people"] for e in log if e["kind"] == "return")
    assert abs(away - 2.1e6) < 1e3
    assert 0.80 * away < back < 0.92 * away
    assert {e["year"] for e in log if e["kind"] == "return"} == {1945, 1946, 1947, 1948}


def test_identity_1921(short_run):
    from plsim.validate import identity_1921
    failed = [c.row() for c in identity_1921(short_run) if not c.ok]
    assert not failed, "\n".join(failed)


def test_economy_reassign():
    from plsim.economy import Economy
    from plsim.params import DEFAULTS
    regs = select_regions(include_lithuania=False, include_west=["DE_OPO"])
    e = Economy(DEFAULTS["economy"], regs, np.random.default_rng(0))
    pop = np.array([r.pop_1931 for r in regs])
    state = np.array([1 if r.country == "DE" else 0 for r in regs])
    e.set_states(state, pop, names=["PL", "DE"], n_states=2)
    assert e.y_state[1] > e.y_state[0]               # German Upper Silesia richer
    inc = e.region_income().copy()
    e.reassign([len(regs) - 1], 0, pop)
    assert np.isclose(e.region_income()[-1] / inc[-1], 1.0, rtol=0.25)
    assert (e.state == 0).all()


def test_plebiscite_lands():
    from plsim.model import Simulation
    from plsim.params import load_scenario
    sim = Simulation(load_scenario("plebiscite_poland"))
    codes = set(sim.codes)
    assert "DZ_GDA.gdansk" in codes and "DE_OPO.gliwice" in codes and "CS_CIE.karwina" in codes
    assert not codes & {"DE_OPO.nysa", "DE_WAR.braniewo", "DE_MAZ.goldap", "DE_WRO.wroclaw"}
    assert set(sim.member) <= {"PL", "LT"}
    # towns of land left out are foreign towns of the run; Breslau is Wrocław
    names = sim.net.names
    assert sim.net.region[names.index("Wrocław")] < 0 and sim.net.dormant[names.index("Breslau")]
    assert sim.net.region[names.index("Gdańsk")] >= 0 and sim.net.dormant[names.index("Gdańsk (Free City)")]
