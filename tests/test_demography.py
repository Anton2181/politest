import numpy as np
import pytest

from plsim.demography import (FertilitySchedule, MortalityModel, alkema_decrement, frontier_e0_female,
                              stable_age_distribution)


@pytest.fixture(scope="module")
def mort():
    return MortalityModel()


@pytest.mark.parametrize("e0", [35.0, 51.4, 70.0, 84.0])
def test_life_table_inversion(mort, e0):
    L = mort.person_years(np.array(e0), 1)
    assert L.sum() == pytest.approx(e0, abs=0.05)


def test_mortality_levels_1931(mort):
    # 1931-32: e0 f 51.4 -> infant mortality around 120-140 per 1000
    L0 = mort.birth_survival(np.array(51.4), 1)
    imr = 2 * (1 - L0)
    assert 0.09 < imr < 0.16
    s = mort.survival(np.array([51.4, 80.0]), 1)
    assert np.all((s > 0) & (s <= 1))
    assert np.all(s[1] >= s[0] - 1e-9)


def test_alkema_shape():
    f = np.linspace(1.0, 7.0, 200)
    d = alkema_decrement(f, U=np.full_like(f, 6.0), d=np.full_like(f, 0.8), D1=1.2, D3=1.2, D4=np.full_like(f, 1.75))
    assert np.all(d >= 0)
    assert d.max() <= 0.8 + 1e-9
    mid = d[(f > 3.2) & (f < 4.5)]
    assert mid.min() > 0.6          # near-maximal decline mid-transition
    assert d[f < 1.8].max() < 0.2   # slows near the end level
    assert d[f > 6.5].max() < 0.2   # slow start at pre-transition levels


def test_schedules_normalised():
    fs = FertilitySchedule()
    sch = fs.schedule(np.array([25.0, 29.0, 32.0]))
    assert np.allclose(sch.sum(axis=1), 1.0)
    ages = np.arange(15, 50) + 0.5
    assert np.all(np.diff((sch * ages).sum(axis=1)) > 0)


def test_stable_population(mort):
    d = stable_age_distribution(4.5, 50, 47, mort, "RU")
    assert d.sum() == pytest.approx(1.0)
    a = d.sum(axis=0)
    assert 0.30 < a[:15].sum() < 0.42
    # WW1 birth deficit visible at ages 13-15 in 1931
    assert a[14] < 0.75 * a[18]


def test_frontier():
    assert frontier_e0_female(1931) == pytest.approx(67.1)
    assert 83 < frontier_e0_female(2000) < 86   # record (Japan) 2000: 84.6
