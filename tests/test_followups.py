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


def test_unsupported_language_anchors_identity_less():
    """A home language without status or schools anchors its speakers'
    identity less: Ukrainian speakers in a Polish region keep a Ukrainian
    identity longer when Ukrainian has status than when it is stigmatised."""
    from plsim.identity import ID_INDEX, IdentityModel
    from plsim.data.languages import LANG_INDEX, LANGUAGES
    g = GROUP_INDEX[("GC", "uk")]
    pop = np.zeros((1, 2, NG))
    pop[0, :, g] = 1000.0
    kept = {}
    for st in (0.35, 0.05):
        im = IdentityModel(DEFAULTS["identity"], ["LUB"], ["pl"], pop)
        status = np.full((1, len(LANGUAGES)), 0.1)
        status[0, LANG_INDEX["pl"]], status[0, LANG_INDEX["uk"]] = 1.0, st
        for _ in range(30):
            im.drift(np.array([[0.6, 0.8]]), np.array([1.3]), status, np.zeros((1, NG)))
        kept[st] = im.I[0, :, g, ID_INDEX["uk"]].sum()
    assert kept[0.05] < kept[0.35] < 2000.0


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
    lat, lon = 49.27, 25.13                       # the seat of Podhajce: always in its own county
    assert sr.assign("TAR", [lat], [lon])[0] == "TAR.podhajce"
    sq = [[lon - .05, lat - .05], [lon + .05, lat - .05], [lon + .05, lat + .05], [lon - .05, lat + .05], [lon - .05, lat - .05]]
    path = tmp_path / "powiaty_1931.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"plsim_code": "TAR.tarnopol"}, "geometry": {"type": "Polygon", "coordinates": [sq]}}]}))
    monkeypatch.setattr(sr, "POWIAT_FILE", str(path))
    monkeypatch.setattr(sr, "_POLYS", None)
    assert sr.assign("TAR", [lat, 49.55], [lon, 25.6]).tolist() == ["TAR.tarnopol", "TAR.tarnopol"]
    monkeypatch.setattr(sr, "_POLYS", None)


# ---------------------------------------------------------------- county Curzon line, Belarus exclave, new states
def test_county_curzon_line_keeps_counties_whole():
    from plsim.curzon import BBOX, split
    d = 0.1
    rr, cc = np.meshgrid(np.arange(30), np.arange(30), indexing="ij")
    lat = BBOX[1] + d / 2 + rr.ravel() * d
    lon = BBOX[0] + d / 2 + cc.ravel() * d
    units = (rr // 5 * 6 + cc // 5).ravel()                     # 36 counties of 5 x 5 cells
    people = np.full(lat.size, 100.0)
    share = np.clip(1.1 - cc.ravel() / 25.0, 0, 1)              # Polish in the west, not in the east
    s = split(lat, lon, share * people, people, d, d, units=units)
    side = s["polish_side"]
    for u in np.unique(units):
        assert side[units == u].all() or not side[units == u].any()
    assert abs(s["residual"]) <= 2500                             # within one county
    assert len(s["lines"]) == 1


def test_belarus_has_no_exclave():
    from scipy import ndimage
    from plsim.data.geography import BBOX, build_grid
    from plsim.params import load_scenario
    from plsim.model import Simulation
    p = load_scenario("wakar_poland_belarus")
    p["end_year"] = p["start_year"]
    codes = Simulation(p).codes
    g = build_grid(codes)
    by = np.array([codes[k].startswith("BY_") for k in g.region])
    r = np.round((g.lat[by] - (BBOX[1] + g.dlat / 2)) / g.dlat).astype(int)
    c = np.round((g.lon[by] - (BBOX[0] + g.dlon / 2)) / g.dlon).astype(int)
    M = np.zeros((r.max() + 2, c.max() + 2), int)
    M[r, c] = 1
    _, n = ndimage.label(M, structure=np.ones((3, 3)))
    assert n == 1


@pytest.fixture(scope="module", params=["nw_krai", "lit_bel"])
def krai_sim(request):
    from plsim.model import Simulation
    from plsim.params import load_scenario
    p = load_scenario(request.param)
    p["end_year"] = p["start_year"]
    return request.param, Simulation(p)


def test_krai_follows_the_governorates(krai_sim):
    name, sim = krai_sim
    mem = dict(zip(sim.codes, sim.member))
    krai = "NWK" if name == "nw_krai" else "LB"
    for code in ["WIL.wilno", "NOW.lida", "BIA.grodno", "BIA.bialystok", "POL.pinsk", "LT_NEA.utena", "BY_MIN.minsk"]:
        assert mem[code] == krai, code
    for code in ["BIA.lomza", "BIA.wysokiemazowie", "WOL.luck", "LUB.wlodawa", "WAW"]:
        assert mem[code] == "PL", code
    # Kamień Koszyrski (1930) was carved from Pińsk (Minsk governorate) and Kowel (Volhynia) uezds: on
    # the county land fitted to the census areas its piece in the krai's governorates is a sliver, and
    # the county stays Polish whole
    kk = [c for c in sim.codes if c.startswith("POL.kamienkoszyrsk")]
    assert [mem[c] for c in kk] == ["PL"]
    assert not any(c.startswith("LT_KLA") for c in sim.codes)         # Prussian before 1920
    # the Suwałki governorate: Poland's in the krai scenario, Lit-Bel's in Lit-Bel
    suw = "PL" if name == "nw_krai" else krai
    for code in ["LT_SUV.marijampole", "LT_SUV.vilkaviskis", "BIA.suwalki", "BIA.augustow"]:
        assert mem[code] == suw, code
    assert sorted(sim.official[sim.codes.index("WIL.wilno")]) == ["be", "lt", "pl", "ru", "yi"]
    if name == "nw_krai":                    # Latgale and the Nevel lands join; the BSSR whole
        for code in ["LV_LAT.dyneburg", "RU_VIT.newel", "RU_MOH", "BY_WIT.witebsk", "BY_MOH.mohylew"]:
            assert mem[code] == krai, code
        assert sim.dominant[sim.codes.index("LV_LAT.rzezyca")] == "lv"
    else:                                    # the Mogilev and Vitebsk lands are left out
        for code in ["BY_WIT.witebsk", "BY_MOH.mohylew", "BY_HOM.homel"]:
            assert code not in sim.codes
        assert not any(c.startswith(("LV_", "RU_")) for c in sim.codes)


def test_cut_pieces_cover_their_county(krai_sim):
    """Pieces of a cut unit add up to its people, and the map grid gives each
    piece the land of its own governorates."""
    from plsim.data.geography import build_grid
    from plsim.data.governorates import letter, split_code
    name, sim = krai_sim
    pieces = [c for c in sim.codes if "~" in c]
    assert pieces
    g = build_grid(sim.codes)
    for c in pieces:
        r = sim.codes.index(c)
        m = g.region == r
        assert m.any(), c
        lets = split_code(c)[1]
        assert np.isin(letter(g.lat[m], g.lon[m]), list(lets)).all(), c
