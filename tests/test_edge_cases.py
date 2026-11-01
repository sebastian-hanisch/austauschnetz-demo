"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12): n = 2, ein einziger Tausch, Gleichstände, Netze ohne Kante, Schleifen, Grenzen inklusive."""

from fractions import Fraction as Fr

import pytest

import aun_balanced as B
import aun_exact as X
import aun_game as G
import aun_matching as MT
import aun_multi as MU
import aun_net as N
import aun_stable as S


def test_exactly_two_nodes_split_the_surplus_in_half():
    """n = 2: eine einzige Tour, keine Alternative: beide bekommen die Hälfte (Außenoption 0 auf beiden Seiten)."""
    net = N.path(2)
    out = B.balanced_outcome(net)
    assert out.status == "ok" and X.exact_balanced(net, out.matching, out.y) == [Fr(1, 2), Fr(1, 2)]
    lo, hi = S.stable_range(net)
    assert lo == pytest.approx([0, 0]) and hi == pytest.approx([1, 1])


def test_two_nodes_with_a_weight_split_that_weight():
    net = N.make_net(2, [(0, 1)], [7])
    out = B.balanced_outcome(net)
    assert X.exact_balanced(net, out.matching, out.y) == [Fr(7, 2), Fr(7, 2)]


def test_a_single_trade_among_three_nodes_leaves_the_third_with_nothing():
    net = N.path(3)
    assert B.balanced_outcome(net).y == pytest.approx((0, 1, 0))


def test_net_without_edges_has_a_trivial_outcome_and_no_dynamics_step():
    net = N.make_net(4, [])
    assert MT.max_matching_weight(net) == 0 and S.lp_gap(net) == (0.0, 0)
    assert S.stable_range(net) == ([0.0] * 4, [0.0] * 4)
    assert MU.distinct_outcomes(net, 1) == []
    assert G.coalition_values(net) == [0] * 16


def test_isolated_node_next_to_an_edge_gets_zero():
    net = N.make_net(3, [(0, 1)])
    out = B.balanced_outcome(net)
    assert out.status == "ok" and out.y == pytest.approx((0.5, 0.5, 0))
    assert S.fixed_nodes(*S.stable_range(net)) == pytest.approx({2: 0})


def test_ties_between_equal_maximum_matchings_do_not_change_the_payout():
    """Weg mit 6 Betrieben: mehrere größte Matchings mit gleichem Gewicht; die Auszahlung ist unabhängig davon, welche Dämpfung das Verfahren nimmt (eindeutiges Ergebnis)."""
    net = N.path(6)
    a = B.balanced_outcome(net, 0.25)
    b = B.balanced_outcome(net, 1.0)
    assert a.y == pytest.approx(b.y)


def test_bounds_are_inclusive_for_kappa_one_and_tiny_steps():
    net = N.path(4)
    assert B.balanced_outcome(net, 1.0).y == pytest.approx((1 / 3, 2 / 3, 2 / 3, 1 / 3))
    res = B.run_dynamics(B.dyn_structure(net), 0.25, max_iter=1)
    assert res.iterations == 1 and not res.converged


def test_self_loops_and_duplicates_are_rejected_not_silently_dropped():
    for bad in ("1-1", "0-1, 1-0", "0-1:-2"):
        assert N.parse_edges(bad)[0] is None


def test_weights_larger_than_one_do_not_break_the_reduction():
    """Gewichtete Kanten: das Verfahren liefert ein vom Prüfer bestätigtes Ergebnis oder eine ehrliche Meldung, nie eine falsche Zahl."""
    net = N.make_net(5, [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)], [3, 1, 2, 1, 3])
    out = B.balanced_outcome(net)
    assert out.status in ("ok", "not_found", "no_stable")
    if out.status == "ok":
        assert B.is_balanced(net, out.matching, out.y, 1e-7)


def test_complete_graph_of_four_has_the_single_symmetric_outcome():
    net = N.make_net(4, [(i, j) for i in range(4) for j in range(i + 1, 4)])
    assert B.balanced_outcome(net).y == pytest.approx((0.5, 0.5, 0.5, 0.5))
    assert len(MU.distinct_outcomes(net, 3)) == 1


def test_game_with_one_player_and_two_players():
    net = N.path(2)
    v = G.coalition_values(net)
    assert G.shapley(v, 2) == [Fr(1, 2), Fr(1, 2)]
    x, _ = G.nucleolus(v, 2)
    assert x == pytest.approx([0.5, 0.5])
    assert G.nucleolus([0, 0], 1)[0] == pytest.approx([0.0])


def test_known_limit_of_the_search_a_weighted_net_with_stable_outcome_but_no_result():
    """Gefundene Grenze (Scratch-Lauf des Baus, Netz 241 aus Seed 9001): zweiseitig, Kantenwerte 1 und 2, stabil existiert, aber die Dynamik von Null liefert keine Auszahlung eines
    Matchings und die Reduktion lehnt ab (ein festgelegter Betrieb bietet einem freien eine Außenoption). Die App meldet dann „nicht gefunden“ statt einer Zahl. Wird die Suche
    erweitert, soll dieser Test bewusst geändert werden."""
    edges = [(0, 5, 2), (0, 6, 2), (0, 7, 2), (0, 8, 2), (1, 4, 2), (1, 6, 2), (1, 7, 2), (2, 4, 1), (2, 5, 1), (2, 7, 2), (2, 8, 1), (3, 5, 1), (3, 6, 1), (3, 8, 1)]
    net = N.make_net(9, [(u, v) for u, v, _ in edges], [w for _, _, w in edges], sides=[0, 0, 0, 0, 1, 1, 1, 1, 1])
    assert S.stable_exists(net)
    out = B.balanced_outcome(net)
    assert out.status == "not_found" and out.y is None and "Außenoption" in out.note and not out.d0_found
