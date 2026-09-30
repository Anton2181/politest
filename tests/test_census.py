import numpy as np
import pytest

from plsim.data.census1931 import build_initial_composition
from plsim.data.languages import GROUPS
from plsim.data.regions import REGIONS


def national_shares(variant):
    ic = build_initial_composition(REGIONS, variant, "census_1923")
    pl = np.array([r.country == "PL" for r in REGIONS])
    P = ic.pop[pl].sum(axis=(0, 1))
    tot = P.sum()
    lang, comm = {}, {}
    for g, (c, l) in enumerate(GROUPS):
        lang[l] = lang.get(l, 0) + P[g] / tot * 100
        comm[c] = comm.get(c, 0) + P[g] / tot * 100
    return tot, lang, comm


def test_total_matches_census():
    tot, _, _ = national_shares("official")
    assert abs(tot - 31_915_779) / 31_915_779 < 0.001


def test_official_reproduces_published_mother_tongue():
    _, lang, comm = national_shares("official")
    assert lang["pl"] + lang["csb"] + lang["wym"] + lang["rom"] == pytest.approx(68.9, abs=0.6)
    assert lang["uk"] + lang["rue"] == pytest.approx(13.9, abs=0.5)      # Ukrainian + 'Ruthenian'
    assert lang["yi"] == pytest.approx(8.6, abs=0.3)                    # Yiddish + Hebrew
    assert lang["be"] == pytest.approx(3.1, abs=0.2)
    assert lang["de"] == pytest.approx(2.3, abs=0.2)
    assert lang["pls"] == pytest.approx(2.2, abs=0.2)
    # religion
    assert comm["RC"] == pytest.approx(64.8, abs=0.7)
    assert comm["JW"] + comm["JH"] == pytest.approx(9.8, abs=0.3)
    assert comm["OR"] == pytest.approx(11.8, abs=0.7)


def test_religion_corrected_matches_tomaszewski():
    _, lang, comm = national_shares("religion_corrected")
    ethnic_poles = lang["pl"] + lang["csb"] + lang["wym"] + lang["rom"] - 1.3   # minus Polish-speaking Jews
    assert ethnic_poles == pytest.approx(64.7, abs=1.2)


def test_vernacular_has_more_minority_speech():
    _, off, _ = national_shares("official")
    _, ver, _ = national_shares("vernacular")
    assert ver["pl"] < off["pl"] - 3
    assert ver["be"] > off["be"] + 1.5


def test_lithuania_variants():
    lt = np.array([r.country == "LT" for r in REGIONS])
    out = {}
    for v in ["census_1923", "polish_claim_1923", "imperial_1897"]:
        ic = build_initial_composition(REGIONS, "official", v)
        P = ic.pop[lt].sum(axis=(0, 1))
        pol = sum(P[g] for g, (c, l) in enumerate(GROUPS) if l == "pl")
        out[v] = pol / P.sum()
    assert out["census_1923"] == pytest.approx(0.032, abs=0.006)
    assert out["polish_claim_1923"] > 0.065
    assert out["census_1923"] < out["imperial_1897"] < out["polish_claim_1923"]


def test_census_observation_model_consistency():
    from plsim.cli import census_consistency
    rows = {(r[0], r[1]): float(r[-1]) for r in census_consistency()}
    assert rows[("official", "latent")] < 1.0
    assert rows[("religion_corrected", "polish_1931")] < 3.5
    assert rows[("vernacular", "polish_1931")] < 3.5
