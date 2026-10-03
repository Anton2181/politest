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


def test_atlas_cell_regions_survive_county_runs():
    """County runs have more than 255 regions: the atlas must not wrap them."""
    import base64
    from types import SimpleNamespace

    from plsim.data.subregions import county_seats
    from plsim.webmap import full_grid, geometry_payload
    codes = []
    for r in REGIONS:
        seats = county_seats(r.code)
        codes += [c[0] for c in seats] if len(seats) > 1 else [r.code]
    assert len(codes) > 255
    grid = build_grid(codes)
    res = SimpleNamespace(region_codes=codes, region_names=codes, members=["PL"] * len(codes), dominant=[])
    full = full_grid()
    reg = np.frombuffer(base64.b64decode(geometry_payload(res, SimpleNamespace(grid=grid), full)["cellreg"]), "<u2")
    inside = reg[reg != 65535]
    assert inside.max() == grid.region.max() > 255
    lt = [i for i, c in enumerate(codes) if c.startswith("LT_")]
    assert np.isin(inside, lt).sum() == np.isin(grid.region, lt).sum()


def test_state_borders_1932():
    """Territory comes from the CShapes 1932 borders (``data/borders_1932.json``),
    with Soviet Belarus (the BSSR of 1926) as an optional third state."""
    from plsim.data.geography import state_of
    from plsim.data.regions import state_of_code
    places = {"Wilno": (54.68, 25.28, "PL"), "Kaunas": (54.90, 23.90, "LT"), "Klaipėda": (55.71, 21.13, "LT"),
              "Gdańsk (Free City)": (54.35, 18.65, ""), "Hel": (54.61, 18.80, "PL"), "Stołpce": (53.48, 26.73, "PL"),
              "Mińsk": (53.90, 27.56, "BY"), "Homel": (52.44, 30.98, "BY"), "Smolensk": (54.78, 32.05, ""),
              "Daugavpils": (55.87, 26.53, ""), "Królewiec": (54.71, 20.51, ""),
              "Zbaraż": (49.66, 25.78, "PL"), "Kamieniec Podolski": (48.68, 26.58, ""), "Cieszyn": (49.75, 18.63, "PL")}
    got = state_of([v[0] for v in places.values()], [v[1] for v in places.values()])
    assert {k: g for k, g in zip(places, got)} == {k: v[2] for k, v in places.items()}
    g = build_grid([r.code for r in REGIONS])
    st = np.array([state_of_code(g.region_codes[k]) for k in g.region])
    assert (state_of(g.lat, g.lon) == st).all()
    for s, official in (("PL", 388_600), ("LT", 55_750), ("BY", 126_792), ("XK", 31_627)):
        assert g.cell_km2[st == s].sum() == pytest.approx(official, rel=0.03), s   # 1931; BSSR 1926; XK 1897 GIS
    # the map grid of Poland and Lithuania does not change when the optional lands are available
    pl_lt = build_grid([r.code for r in REGIONS if r.country not in ("BY", "XK")])
    assert len(pl_lt.lat) == 37532 and (~np.isin(st, ["BY", "XK"])).sum() == 37532
