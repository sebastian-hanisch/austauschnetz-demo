"""Atlas: 142 zusammenhängende Graphen mit 2 bis 6 Knoten, paarweise verschieden (eigener Kanonisierungscode), Zahl nach OEIS A001349 (1, 2, 6, 21, 112 für n = 2 bis 6)."""

import itertools
from collections import Counter

import aun_atlas as A
import aun_net as N


def canonical(net):
    """Kleinste Kantenliste über alle Umnummerierungen (n <= 6: höchstens 720)."""
    pairs = {(u, v) for u, v, _ in net.edges}
    best = None
    for perm in itertools.permutations(range(net.n)):
        mask = tuple(sorted((min(perm[u], perm[v]), max(perm[u], perm[v])) for u, v in pairs))
        if best is None or mask < best:
            best = mask
    return best


def test_atlas_has_the_known_counts_and_only_connected_graphs():
    nets = A.load_atlas()
    assert Counter(n.n for n in nets) == {2: 1, 3: 2, 4: 6, 5: 21, 6: 112}
    assert len(nets) == 142 and all(N.is_connected(n) for n in nets)


def test_atlas_graphs_are_pairwise_non_isomorphic():
    forms = {(n.n, canonical(n)) for n in A.load_atlas()}
    assert len(forms) == 142


def test_atlas_marks_exactly_the_bipartite_graphs():
    for net in A.load_atlas():
        assert (net.sides is not None) == (N.two_colouring(net) is not None)
