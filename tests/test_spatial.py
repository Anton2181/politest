"""Spatial layer: grid, downscaling consistency and the neighbourhood shift rule."""
import numpy as np
import pytest
from scipy import sparse

from plsim.data.geography import build_grid
from plsim.data.languages import LANG_INDEX, NL
from plsim.data.regions import REGIONS
from plsim.spatial import Downscaler, _indicator, ipf, lang_totals


@pytest.fixture(scope="module")
def spatial(short_run):
    ds = Downscaler(short_run)
    return ds, ds.run()


def test_grid_areas_match_regions():
    codes = [r.code for r in REGIONS]
    g = build_grid(codes)
    area = np.bincount(g.region, weights=g.cell_km2, minlength=len(codes))
    for r, reg in enumerate(REGIONS):
        if reg.area_km2 > 1000:
            assert 0.85 < area[r] / reg.area_km2 < 1.15, reg.code


def test_ipf_matches_both_margins():
    rng = np.random.default_rng(0)
    seed = rng.random((50, 4)) + 0.01
    key = np.repeat([0, 1], 25)
    rows = rng.random(50) * 100
    cols = np.zeros((2, 4))
    for k in (0, 1):
        w = rng.random(4)
        cols[k] = w / w.sum() * rows[key == k].sum()
    X = ipf(seed, rows, _indicator(key, 2), key, cols, n_iter=200)
    assert np.allclose(X.sum(axis=1), rows, rtol=1e-6)
    assert np.allclose(_indicator(key, 2) @ X, cols, rtol=1e-4)


def test_cells_add_up_to_regions(spatial, short_run):
    ds, sr = spatial
    pops = [short_run.pop0] + list(short_run.pop)
    for j, y in enumerate(sr.years):
        tot = np.zeros((len(sr.region_codes), NL))
        np.add.at(tot, sr.grid.region, sr.cells[j])
        np.add.at(tot, sr.town_region, sr.towns[j])
        target = lang_totals(np.asarray(pops[j], float)).sum(axis=1)
        assert np.abs(tot - target).sum() / target.sum() < 1e-4, y


def test_no_negative_cells(spatial):
    _, sr = spatial
    assert sr.cells.min() >= -1e-6 and sr.towns.min() >= -1e-6


def test_shift_lands_at_contact_zones(spatial):
    """With the neighbourhood rule, a loser shifts more where the gainer is near."""
    ds, _ = spatial
    n = 2
    C = np.array([[90.0, 10.0], [10.0, 90.0]])
    S = np.zeros((n, NL))
    S[:, LANG_INDEX["uk"]] = C[:, 0]
    S[:, LANG_INDEX["pl"]] = C[:, 1]
    K = S / S.sum(axis=1, keepdims=True)
    delta = np.zeros((1, NL))
    delta[0, LANG_INDEX["uk"]] = -10.0
    delta[0, LANG_INDEX["pl"]] = 10.0
    sub = Downscaler.__new__(Downscaler)
    sub.p = dict(ds.p)
    sub.key = np.zeros(n, dtype=int)
    sub.A = sparse.csr_matrix(np.ones((1, n)))
    out = sub._shift(S, K, delta)
    loss = S[:, LANG_INDEX["uk"]] - out[:, LANG_INDEX["uk"]]
    assert np.isclose(loss.sum(), 10.0)
    per_capita = loss / S[:, LANG_INDEX["uk"]]
    assert per_capita[1] > 3 * per_capita[0]
    assert np.allclose(out.sum(axis=1), S.sum(axis=1))
