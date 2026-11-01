"""Worst-Case am Regler-Maximum (DEMO-PLAYBOOK §1c): keine Zeit-Assertion, nur Ergebnis und Abschluss. Zeiten stehen in der README als einmalige Messung."""

import pytest

import aun_balanced as B
import aun_constants as C
import aun_evaluation as V
import aun_net as N
from aun_scenario import Settings


@pytest.mark.parametrize("net, p, kappa", [("rand_bip", 30, 0.25), ("rand_bip", 95, 0.25), ("rand_bip", 5, 1.0), ("rand_gen", 95, 0.25), ("rand_gen", 5, 0.5), ("rand_tree", 30, 0.25)])
def test_largest_random_nets_finish_with_a_verified_outcome_or_an_honest_message(net, p, kappa):
    view = V.analyse(Settings(net=net, n=C.N_MAX, p=p, kappa=kappa, seed=35))
    assert view.error is None and view.outcome.status in ("ok", "no_stable", "not_found")
    if view.outcome.status == "ok":
        assert B.is_balanced(view.net, view.outcome.matching, view.outcome.y, 1e-7)
    if net in ("rand_bip", "rand_tree"):
        assert view.outcome.status == "ok"


@pytest.mark.parametrize("net", ["path", "cycle", "star", "spider", "bipartite"])
def test_largest_structured_nets_finish(net):
    view = V.analyse(Settings(net=net, n=C.N_MAX, kappa=0.25))
    assert view.error is None
    assert view.outcome.status == ("ok" if (net != "cycle" or C.N_MAX % 2 == 0) else "no_stable")
    assert view.net.n == C.N_MAX


def test_dynamics_view_and_other_live_views_finish_on_the_largest_bipartite_net():
    s = Settings(net="rand_bip", n=C.N_MAX, p=30, kappa=0.25, seed=35)
    view = V.analyse(s)
    dv = V.dynamics_view(s, view)
    assert dv is not None and all(r[2] for r in dv.rows)
    assert V.multi_view(s, view) and V.reading_view(s, view) is not None
    assert V.game_view(view) is None                                   # mehr als 8 Betriebe: kein Spiel
    assert len(V.property_view(s, view).leaf_rows) == V.PROPERTY_MAX_NODES


def test_largest_custom_edge_list_is_accepted():
    text = ", ".join(f"{i}-{i + 1}" for i in range(N.MAX_CUSTOM_NODES - 1))
    net, err = N.parse_edges(text)
    assert err is None and net.n == N.MAX_CUSTOM_NODES
    assert B.balanced_outcome(net).status == "ok"
