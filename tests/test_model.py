import numpy as np

from plsim.data.languages import GROUPS
from plsim.validate import historical_checks


def test_accounting_identity(short_run):
    A = short_run.arrays()
    tot = A["pop"].sum(axis=(1, 2, 3))
    for i in range(1, len(tot)):
        expected = tot[i - 1] + A["births"][i].sum() - A["deaths"][i].sum() - A["emig"][i].sum() + A["immig"][i].sum()
        assert abs(tot[i] - expected) / tot[i] < 1e-6


def test_no_negative_population(short_run):
    A = short_run.arrays()
    assert A["pop"].min() >= 0
    assert np.all(A["bil"] <= A["pop"] + 1e-6)


def test_dominant_language_groups_are_competent(short_run):
    A = short_run.arrays()
    codes = short_run.region_codes
    for r, c in enumerate(codes):
        dom = "lt" if c.startswith("LT") else "pl"
        for g, (cc, l) in enumerate(GROUPS):
            if l == dom:
                assert np.allclose(A["bil"][-1][r, :, g], A["pop"][-1][r, :, g], rtol=1e-6, atol=1e-3)


def test_back_validation_1932_1939(short_run):
    checks = historical_checks(short_run)
    failed = [c.row() for c in checks if not c.ok]
    assert not failed, "\n".join(failed)


def test_snapshots_and_census_views(short_run):
    assert 1932 in short_run.pyramids and 1939 in short_run.pyramids
    for (regime, year), tab in short_run.census.items():
        tot = tab.sum()
        pop = short_run.arrays()["pop"][short_run.years.index(year)].sum() if year in short_run.years else tot
        assert abs(tot - pop) / pop < 1e-6


def test_county_run_accounts_and_back_validates(county_run):
    """The default (county-level) baseline adds up and passes the 1932-39 checks."""
    A = county_run.arrays()
    assert len(county_run.region_codes) == 270
    tot = A["pop"].sum(axis=(1, 2, 3))
    for i in range(1, len(tot)):
        expected = tot[i - 1] + A["births"][i].sum() - A["deaths"][i].sum() - A["emig"][i].sum() + A["immig"][i].sum()
        assert abs(tot[i] - expected) / tot[i] < 1e-6
    failed = [c.row() for c in historical_checks(county_run) if not c.ok]
    assert not failed, "\n".join(failed)


def test_region_streams_do_not_depend_on_the_other_regions():
    """Each region draws its noise from its own stream, keyed by its code, so
    adding a region (or a state) to a run leaves the draws of the others as
    they were."""
    from plsim.model import keyed_rngs
    a = keyed_rngs(7, 1, ["PL_WAR", "PL_KRA"])
    b = keyed_rngs(7, 1, ["LT_KAU", "PL_KRA", "PL_WAR", "BY_MIN"])
    for k in ("PL_WAR", "PL_KRA"):
        assert np.array_equal(a[k].normal(size=5), b[k].normal(size=5))
    c = keyed_rngs(7, 2, ["PL_WAR"])
    d = keyed_rngs(8, 1, ["PL_WAR"])
    x = keyed_rngs(7, 1, ["PL_WAR"])["PL_WAR"].normal(size=5)
    assert not np.array_equal(x, c["PL_WAR"].normal(size=5))
    assert not np.array_equal(x, d["PL_WAR"].normal(size=5))
