"""Calibration harness, diaspora term, identity layer, population exchange,
historical Curzon line, road density check and the county-polygon hook."""
import json

import numpy as np
import pytest

from plsim.data.languages import GROUP_INDEX, GROUPS, NG
from plsim.params import DEFAULTS


# ---------------------------------------------------------------- calibration
def test_defaults_are_not_ruled_out_by_history_matching():
    from plsim import calibration as cb
    sim = cb.simulate(cb.default_theta())
    imp = cb.implausibility(sim)
    worst = max(imp.values())
    assert worst <= 3.0, {k: round(v, 2) for k, v in imp.items()}


def test_nroy_rows_feed_the_ensemble():
    from plsim import calibration as cb
    from plsim.ensemble import draw_params
    rows = cb.load_nroy()
    assert len(rows) >= 20
    p = draw_params(DEFAULTS, np.random.default_rng(1), rows)
    lang = p["language"]
    # the drawn row's class anchors are applied ...
    assert any(abs(lang["sigma0"]["RC:be"] - r["sigma_vern"]) < 1e-9 for r in rows)
    # ... and the class members move with their anchor
    f = lang["sigma0"]["RC:be"] / DEFAULTS["language"]["sigma0"]["RC:be"]
    assert lang["sigma0"]["RC:csb"] == pytest.approx(DEFAULTS["language"]["sigma0"]["RC:csb"] * f)


def test_diaspora_floor_raises_shift_where_institutions_are_missing():
    from plsim import calibration as cb
    th = cb.default_theta()
    lo = cb.simulate(dict(th, sigma_diaspora=0.0))[("diaspora", 0)]
    hi = cb.simulate(dict(th, sigma_diaspora=0.6))[("diaspora", 0)]
    assert hi > lo + 0.1


# ---------------------------------------------------------------- identity
def test_identity_totals_track_population(short_run):
    I = np.asarray(short_run.identity[-1]).sum(axis=1)
    P = np.asarray(short_run.pop[-1]).sum(axis=(1, 2))
    assert np.allclose(I, P, rtol=1e-6)


def test_nationality_census_counts_identity_not_language(short_run):
    from plsim.language import CENSUS_CATEGORIES
    y = 1932
    nat = short_run.census[("polish_1921", y)].sum(axis=0)
    lang = short_run.census[("polish_1931", y)].sum(axis=0)
    assert nat.sum() == pytest.approx(lang.sum(), rel=1e-6)
    jw = CENSUS_CATEGORIES.index("jw")
    assert nat[jw] > 0 and lang[jw] == 0          # Jewish nationality vs Yiddish mother tongue
    # 1921-type shares near the 1921 census (Polish 69 %, Ukrainian 14 %, Jewish 8 %)
    pl = CENSUS_CATEGORIES.index("pl")
    assert 0.62 < nat[pl] / nat.sum() < 0.74


def test_state_pull_moves_identity_before_language():
    """'Lithuanisation': under the pull of the Lithuanian state, Polish
    speakers' identity drifts to Lithuanian while their language stays."""
    from plsim.identity import ID_INDEX, IdentityModel
    g = GROUP_INDEX[("RC", "pl")]
    pop = np.zeros((1, 2, NG))
    pop[0, :, g] = 1000.0
    im = IdentityModel(DEFAULTS["identity"], ["LT_X"], ["lt"], pop)
    lt0 = im.I[0, :, g, ID_INDEX["lt"]].sum()
    for _ in range(50):
        im.drift(np.array([[0.6, 0.8]]), np.array([1.0]))
    assert im.I[0, :, g, ID_INDEX["lt"]].sum() > lt0
    assert im.I.sum() == pytest.approx(2000.0)


# ---------------------------------------------------------------- exchange
def test_exchange_moves_people_and_conserves_them():
    from plsim.exchange import apply_exchange
    R = 2
    P = np.zeros((R, 2, NG, 2, 2, 101))
    pl, uk = GROUP_INDEX[("RC", "pl")], GROUP_INDEX[("GC", "uk")]
    P[0, :, pl, 1, :, 20:60] = 10.0          # west: Poles and some Ukrainians
    P[0, :, uk, 0, :, 20:60] = 2.0
    P[1, :, pl, 1, :, 20:60] = 3.0           # east: Ukrainians and some Poles
    P[1, :, uk, 0, :, 20:60] = 10.0
    tot = P.sum()
    plan = {"year": 1946, "east_poles": {"E": 1.0}, "west_others": {"W": {"uk": 1.0}}}
    info = apply_exchange(P, ["W", "E"], plan)
    assert P.sum() == pytest.approx(tot)
    assert P[1, :, pl].sum() == pytest.approx(0.0)
    assert P[0, :, uk].sum() == pytest.approx(0.0)
    assert info["to_polish_side"] == pytest.approx(3.0 * 2 * 2 * 40)


def test_exchange_scenario_runs_with_a_plan():
    from plsim.model import Simulation
    from plsim.params import load_scenario
    p = load_scenario("curzon_exchange")
    p["partition"] = []
    p["end_year"] = 1934
    p["population_exchange"] = {"year": 1933, "plan": {"year": 1933, "east_poles": {"WOL": 0.5},
                                                     "west_others": {"KRA": {"uk": 1.0}}}}
    res = Simulation(p).run()
    assert res.exchange["to_polish_side"] > 0 and res.exchange["to_other_side"] > 0
    assert np.allclose(np.asarray(res.identity[-1]).sum(axis=1), np.asarray(res.pop[-1]).sum(axis=(1, 2)), rtol=1e-6)


# ---------------------------------------------------------------- Curzon line of 1919-20
def test_historical_curzon_line_sides():
    from plsim.curzon import historical_side
    lat = [52.23, 53.13, 54.35, 53.68, 49.84, 52.10, 54.90]       # Warsaw, Białystok, Gdańsk area, Grodno, Lwów, Brest, Kaunas
    lon = [21.01, 23.16, 18.65, 23.84, 24.03, 23.70, 23.90]
    assert list(historical_side(lat, lon)) == [True, True, True, False, False, False, False]


# ---------------------------------------------------------------- roads
def test_road_density_check_is_reported():
    from plsim.validate import plausibility_checks

    class R:                       # a minimal stand-in for Results
        years = [2031, 2032]
        region_codes = ["WAR", "KRA"]
        km = [{"road_express": 0.0, "road_motorway": 0.0}, {"road_express": 600.0, "road_motorway": 400.0}]

        def arrays(self):
            return {"pop": np.zeros((2, 2, 2, len(GROUPS))), "tfr": np.zeros((2, 2)), "e0": np.zeros((2, 2, 2))}
    rows = [c for c in plausibility_checks(R()) if "Expressways" in c.name]
    assert rows and rows[0].value > 0


# ---------------------------------------------------------------- real county borders
def test_county_polygons_override_voronoi(tmp_path, monkeypatch):
    from plsim.data import subregions as sr
    lat, lon = 49.30, 25.00                       # Voronoi: Podhajce
    assert sr.assign("TAR", [lat], [lon])[0] == "TAR.podhajce"
    sq = [[lon - .05, lat - .05], [lon + .05, lat - .05], [lon + .05, lat + .05], [lon - .05, lat + .05], [lon - .05, lat - .05]]
    path = tmp_path / "powiaty_1931.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"plsim_code": "TAR.tarnopol"}, "geometry": {"type": "Polygon", "coordinates": [sq]}}]}))
    monkeypatch.setattr(sr, "POWIAT_FILE", str(path))
    monkeypatch.setattr(sr, "_POLYS", None)
    assert sr.assign("TAR", [lat, 49.55], [lon, 25.6]).tolist() == ["TAR.tarnopol", "TAR.tarnopol"]
    monkeypatch.setattr(sr, "_POLYS", None)
