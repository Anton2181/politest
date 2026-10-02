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


def _counts(variant, lt_variant="census_1923"):
    ic = build_initial_composition(REGIONS, variant, lt_variant)
    out = {}
    for country in ("PL", "LT"):
        m = np.array([r.country == country for r in REGIONS])
        P = ic.pop[m].sum(axis=(0, 1))
        lang, comm = {}, {}
        for g, (c, l) in enumerate(GROUPS):
            lang[l] = lang.get(l, 0) + P[g]
            comm[c] = comm.get(c, 0) + P[g]
        jew_pl = sum(P[g] for g, (c, l) in enumerate(GROUPS) if l == "pl" and c in ("JW", "JH"))
        out[country] = (P.sum(), lang, comm, jew_pl, P)
    return out


def test_religion_corrected_matches_tomaszewski():
    """The baseline start reproduces Tomaszewski (1985): ethnic Poles 64.7 %,
    Ukrainians 5.11 M + Belarusians 1.95 M (West Polesian speakers counted
    with them), Germans 0.78 M, Jews 3.11 M (by religion)."""
    tot, lang, comm, jew_pl, _ = _counts("religion_corrected")["PL"]
    poles = lang["pl"] + lang["csb"] + lang["wym"] + lang["rom"] - jew_pl
    assert poles / tot * 100 == pytest.approx(64.7, abs=0.3)
    east = lang["uk"] + lang["rue"] + lang["be"] + lang["pls"]
    assert east == pytest.approx(5.113e6 + 1.954e6, rel=0.02)
    assert lang["de"] == pytest.approx(0.78e6, rel=0.03)
    assert comm["JW"] + comm["JH"] == pytest.approx(3.114e6, rel=0.01)


def test_vernacular_is_the_kubijovyc_upper_bound():
    """Upper bound: ~5.85 M Ukrainians (Kubijovyč 1983; West Polesian speakers
    split half and half), ~470 k Latin-rite Ukrainian speakers in Galicia."""
    tot, lang, _, _, P = _counts("vernacular")["PL"]
    assert lang["uk"] + lang["rue"] + lang["pls"] / 2 == pytest.approx(5.85e6, rel=0.02)
    latyn = sum(P[g] for g, (c, l) in enumerate(GROUPS) if c == "RC" and l == "uk")
    assert 0.45e6 < latyn < 0.56e6
    off = _counts("official")["PL"][1]
    assert lang["pl"] < off["pl"] - 1.5e6 and lang["be"] > off["be"] + 0.7e6


def test_lithuania_variants():
    pol = {}
    for v in ["census_1923", "research", "polish_claim_1923", "imperial_1897"]:
        tot, lang, _, _, _ = _counts("official", v)["LT"]
        pol[v] = lang["pl"]
    assert pol["census_1923"] / _counts("official")["LT"][0] == pytest.approx(0.036, abs=0.006)
    assert pol["research"] == pytest.approx(150e3, rel=0.05)          # historians' middle estimate
    assert pol["census_1923"] < pol["imperial_1897"] < pol["polish_claim_1923"]
    assert pol["census_1923"] < pol["research"] < pol["polish_claim_1923"]


def test_census_observation_model_consistency():
    from plsim.cli import census_consistency
    rows = {(r[0], r[1]): float(r[-1]) for r in census_consistency()}
    assert rows[("official", "latent")] < 1.0
    # the baseline population, recorded the way the 1931 census recorded it,
    # gives back the printed census (sum of absolute errors over 8 categories, points)
    assert rows[("religion_corrected", "polish_1931")] < 1.5
    assert rows[("vernacular", "polish_1931")] < 2.5
