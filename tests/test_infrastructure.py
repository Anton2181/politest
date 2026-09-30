import numpy as np
from scipy.sparse.csgraph import shortest_path

from plsim.data.network import NODES
from plsim.infrastructure import Network
from plsim.params import load_scenario


def _net(federation=True):
    p = load_scenario("baseline")
    codes = [c for c in ["WAW", "WAR", "LOD", "KIE", "LUB", "BIA", "WIL", "NOW", "POL", "WOL", "POZ", "POM", "SLA",
                         "KRA", "LWO", "STA", "TAR", "LT_KAU", "LT_LAU", "LT_ZEM", "LT_SUV", "LT_NEA", "LT_KLA"]]
    if not federation:
        codes = codes[:17]
    return Network(p["infrastructure"], codes, federation, np.random.default_rng(0))


def test_no_foreign_to_foreign_edges():
    net = _net(False)
    for u, v in zip(net.eu, net.ev):
        assert not (net.foreign[u] and net.foreign[v])


def test_single_edge_update_is_exact():
    net = _net()
    net.travel_times(1950, 10.0)
    D = net.D.copy()
    np.fill_diagonal(D, 0.0)
    # take a road edge, make it much faster, compare formula vs full recomputation
    e = next(i for i in range(len(net.eu)) if net.emode[i] == 1 and net.eactive[i])
    a, b = net.eu[e], net.ev[e]
    w_new = 0.05
    via = np.minimum(D[:, a][:, None] + w_new + D[b, :][None, :], D[:, b][:, None] + w_new + D[a, :][None, :])
    est = np.minimum(D, via)
    adj, _ = net._adjacency(net._times)
    adj = adj.tolil()
    adj[a, b] = min(adj[a, b], w_new) if adj[a, b] else w_new
    adj[b, a] = adj[a, b]
    exact = shortest_path(adj.tocsr(), method="D", directed=False)
    exact[~np.isfinite(exact)] = 99.0
    mask = D < 98
    assert np.allclose(est[mask], exact[mask], atol=1e-6)


def test_dated_projects_and_federation_links():
    net = _net(True)
    n0 = len(net.eu)
    net.inject_dated_projects(1932, True, 0)
    names = {(net.names[u], net.names[v]) for u, v in zip(net.eu, net.ev)}
    assert ("Wilno", "Kaišiadorys") in names
    net2 = _net(False)
    net2.inject_dated_projects(1932, True, 0)
    names2 = {(net2.names[u], net2.names[v]) for u, v in zip(net2.eu, net2.ev)}
    assert ("Wilno", "Kaišiadorys") not in names2
    assert len(net.eu) > n0
