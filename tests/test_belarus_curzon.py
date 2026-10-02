"""Soviet Belarus (optional fourth set of voivodeships) and the equal-exchange Curzon line."""
import numpy as np
import pytest

from plsim.curzon import split
from plsim.data import bssr
from plsim.data.census1931 import build_initial_composition
from plsim.data.languages import GROUPS, LANG_INDEX
from plsim.data.regions import REGIONS, select_regions


def test_bssr_1926_census():
    """The okrug table reproduces the 1926 census of the BSSR."""
    pop = sum(o[5] for o in bssr.OKRUGS)
    assert pop == pytest.approx(4_983_240, rel=0.001)
    share = lambda k: sum(o[5] * o[6][k] for o in bssr.OKRUGS) / pop  # noqa: E731
    for k, v in enumerate((.806, .077, .082, .020)):              # Belarusians, Russians, Jews, Poles
        assert share(k) == pytest.approx(v, abs=0.003)


def test_belarus_home_languages():
    regions = [r for r in REGIONS if r.country == "BY"]
    comp = build_initial_composition(regions, "religion_corrected", "research").pop
    lang = np.zeros(len(LANG_INDEX))
    for g, (_, l) in enumerate(GROUPS):
        lang[LANG_INDEX[l]] += comp[:, :, g].sum()
    tot = lang.sum()
    assert tot == pytest.approx(4_983_240 * bssr.GROWTH_1926_1931, rel=0.001)
    assert 0.74 < lang[LANG_INDEX["be"]] / tot < 0.80                # Belarusian at home
    assert 0.10 < lang[LANG_INDEX["ru"]] / tot < 0.15                # Russian (Homel corrected)
    assert lang[LANG_INDEX["yi"]] / tot == pytest.approx(0.082 * 0.907, abs=0.003)
    assert 0.11 < comp[:, 1].sum() / tot < 0.20                      # urban


def test_belarus_only_on_request():
    from plsim.infrastructure import Network
    from plsim.params import load_scenario
    assert not any(r.country == "BY" for r in select_regions())
    assert sum(r.country == "BY" for r in select_regions(include_belarus=True)) == 4
    p = load_scenario("baseline")["infrastructure"]
    net = Network(p, [r.code for r in select_regions()], federation=True, rng=np.random.default_rng(0))
    i = net.names.index("Mińsk")
    assert net.foreign[i] and not net.dormant[i]                     # the old gateway
    assert net.dormant[net.names.index("Witebsk")] and net.pop[net.names.index("Witebsk")] == 0
    assert not any(net.dormant[u] or net.dormant[v] for u, v in zip(net.eu, net.ev))


def test_wakar_poland_belarus_setup():
    from plsim.model import Simulation
    from plsim.params import load_scenario
    sim = Simulation(load_scenario("wakar_poland_belarus"))
    by = [c for c in sim.codes if c.startswith("BY_")]
    assert len(by) == 12 and "BY_MIN.minsk" in by
    assert not any(c.startswith("LT") for c in sim.codes) and "WIL.wilno" not in sim.codes
    i = sim.codes.index("BY_HOM.homel")
    assert sim.dominant[i] == "be" and set(sim.official[i]) == {"pl", "be"}
    m = sim.net.names.index("Mińsk")
    assert not sim.net.foreign[m]
    edges = {frozenset((sim.net.names[u], sim.net.names[v])) for u, v in zip(sim.net.eu, sim.net.ev)}
    assert frozenset(("Mińsk", "Borysów")) in edges and frozenset(("Łuniniec", "Żytkowicze")) in edges


def _straight_best(x, y, poles, people):
    """Benchmark: the best straight line (half-plane) of the right size."""
    target, best = poles.sum(), 0.0
    for th in np.radians(np.arange(0, 360, 1.0)):
        o = np.argsort(x * np.cos(th) + y * np.sin(th))
        cp = np.cumsum(people[o])
        k = int(np.searchsorted(cp, target))
        if k < len(o):
            pa = (np.cumsum(poles[o])[k - 1] if k else 0) + (target - (cp[k - 1] if k else 0)) / people[o[k]] * poles[o[k]]
            best = max(best, pa)
    return best


def test_curzon_line_equal_exchange_and_optimality():
    """Non-Poles on the Polish side = Poles on the other side; both sides are in
    one piece; the free line keeps at least as many Poles as any straight one."""
    from scipy import ndimage

    from plsim.data.geography import BBOX
    rng = np.random.default_rng(3)
    R, C = 30, 40
    rows, cols = np.mgrid[0:R, 0:C]
    lat = BBOX[1] + (rows.ravel() + 0.5) * 0.1
    lon = BBOX[0] + (cols.ravel() + 0.5) * 0.1
    people = rng.uniform(50, 150, R * C)
    frac = np.clip(1.2 - cols.ravel() / C + 0.25 * np.sin(rows.ravel() / 4) + rng.normal(0, 0.1, R * C), 0, 1)
    poles = people * frac
    s = split(lat, lon, poles, people, 0.1, 0.1)
    assert s["west_others"] == pytest.approx(s["east_poles"], rel=1e-9)
    assert s["west"] == pytest.approx(poles.sum(), rel=1e-9)
    side = np.zeros((R, C), int)
    side[rows.ravel(), cols.ravel()] = np.where(s["polish_side"], 1, 2)
    assert ndimage.label(side == 1)[1] == 1 and ndimage.label(side == 2)[1] == 1
    assert len(s["lines"]) == 1                                         # one continuous line
    x, y = lon * 68.5, lat * 111.2
    assert s["west_poles"] >= _straight_best(x, y, poles, people) - 1e-6 * poles.sum()


def test_curzon_counts_leave_out_jews_germans_kashubians():
    from types import SimpleNamespace

    from plsim.curzon import excluded_share
    from plsim.data.languages import GROUP_INDEX, NG
    P = np.zeros((1, 2, NG, 2, 2, 3))
    P[0, 0, GROUP_INDEX[("RC", "pl")], 0, 0, 0] = 80
    P[0, 1, GROUP_INDEX[("JW", "pl")], 0, 0, 0] = 20
    P[0, 1, GROUP_INDEX[("JW", "yi")], 0, 0, 0] = 50
    P[0, 0, GROUP_INDEX[("RC", "csb")], 0, 0, 0] = 10
    P[0, 0, GROUP_INDEX[("OR", "uk")], 0, 0, 0] = 30
    f = excluded_share(SimpleNamespace(years=[1932], pop=[P]), 1932)[0]
    assert f[LANG_INDEX["pl"]] == pytest.approx(0.2) and f[LANG_INDEX["uk"]] == 0
    assert f[LANG_INDEX["yi"]] == f[LANG_INDEX["csb"]] == f[LANG_INDEX["de"]] == 1
