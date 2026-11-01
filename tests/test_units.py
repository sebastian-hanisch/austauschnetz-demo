"""Einheiten an den Mini-Netzen aus conftest.py, Erwartungswerte von Hand gerechnet (DEMO-PLAYBOOK §1b)."""

from fractions import Fraction as Fr

import numpy as np
import pytest

import aun_balanced as B
import aun_exact as X
import aun_game as G
import aun_matching as MT
import aun_multi as MU
import aun_net as N
import aun_principle as P
import aun_stable as S


# --- Netze -----------------------------------------------------------------------------------------------------------------------------------------
def test_make_net_normalises_and_rejects_bad_edges():
    net = N.make_net(3, [(2, 1), (0, 1)], [4, 2])
    assert net.edges == ((0, 1, 2), (1, 2, 4))
    for bad in ([(0, 0)], [(0, 1), (1, 0)], [(0, 5)]):
        with pytest.raises(ValueError):
            N.make_net(3, bad)
    with pytest.raises(ValueError):
        N.make_net(2, [(0, 1)], [0])


def test_hand_nets_have_the_documented_shape(path4, cycle4, star3, k23):
    assert path4.edges == ((0, 1, 1), (1, 2, 1), (2, 3, 1))
    assert len(cycle4.edges) == 4 and N.degrees(cycle4) == [2, 2, 2, 2]
    assert N.degrees(star3) == [3, 1, 1, 1]
    assert len(k23.edges) == 6 and k23.sides == (0, 0, 1, 1, 1)


def test_spider_has_three_legs_and_n_minus_one_edges():
    for n in (4, 7, 10, 13):
        s = N.spider(n)
        assert s.n == n and len(s.edges) == n - 1 and N.is_connected(s) and N.degrees(s)[0] == 3


def test_parse_edges_reads_weights_and_reports_errors():
    net, err = N.parse_edges("0-1, 1-2:3\n2-3")
    assert err is None and net.edges == ((0, 1, 1), (1, 2, 3), (2, 3, 1)) and net.labels == ("0", "1", "2", "3")
    for bad in ("", "0-1, abc", "0-0", "0-1, 1-0", "0-1:0"):
        assert N.parse_edges(bad)[0] is None
    assert N.parse_edges("5-9")[0].edges == ((0, 1, 1),)                      # Knotennamen werden neu nummeriert
    many = ", ".join(f"{i}-{i + 1}" for i in range(N.MAX_CUSTOM_NODES + 1))
    assert N.parse_edges(many)[0] is None


def test_betweenness_by_hand(path4, star3):
    # Weg 4: Knoten 1 liegt auf den Wegen 0-2 und 0-3, Knoten 2 auf 1-3 und 0-3; Stern: die Mitte auf allen C(3,2) = 3 Blattpaaren
    assert N.betweenness(path4) == [0, 2, 2, 0]
    assert N.betweenness(star3) == [3, 0, 0, 0]


def test_pearson_is_none_for_constant_series():
    assert N.pearson([1, 2, 3], [2, 4, 6]) == pytest.approx(1.0)
    assert N.pearson([1, 1, 1], [1, 2, 3]) is None


def test_random_generators_are_deterministic_and_respect_the_minimum():
    a = N.random_bipartite(8, 8, 0.3, N.stream(35, 1))
    b = N.random_bipartite(8, 8, 0.3, N.stream(35, 1))
    assert a == b and a != N.random_bipartite(8, 8, 0.3, N.stream(36, 1))
    sparse = N.random_bipartite(2, 2, 0.0, N.stream(1, 1))
    assert len(sparse.edges) == 4                                                # Auffüllen bis MIN_EDGES (2 x 2 = 4 mögliche Kanten)
    assert len(N.random_general(5, 0.0, N.stream(1, 1)).edges) == N.MIN_EDGES
    g = N.random_general(12, 0.4, N.stream(2, 1))
    assert all(d > 0 for d in N.degrees(g))                                      # Knoten ohne Kante entfallen


def test_random_tree_is_a_tree_and_all_labelled_trees_of_four_nodes_occur():
    seen = set()
    for s in range(400):
        t = N.random_tree(4, N.stream(s, 1))
        assert len(t.edges) == 3 and N.is_connected(t)
        seen.add(t.edges)
    assert len(seen) == 16                                                       # Cayley: 4^2 = 16 nummerierte Bäume
    assert len(N.random_tree(2, N.stream(1, 1)).edges) == 1


def test_bipartite_sides_are_consistent():
    net = N.random_bipartite(6, 6, 0.4, N.stream(7, 1))
    assert all(net.sides[u] != net.sides[v] for u, v, _ in net.edges)
    assert N.two_colouring(N.cycle(5)) is None and N.two_colouring(N.cycle(6)) is not None


def test_subnet_relabel_scaled_and_leaf(path4):
    sub = N.subnet(path4, [1, 2, 3])
    assert sub.edges == ((0, 1, 1), (1, 2, 1))
    assert N.scaled(path4, 3).edges == ((0, 1, 3), (1, 2, 3), (2, 3, 3))
    leaf = N.with_leaf(path4, 1)
    assert leaf.n == 5 and (1, 4, 1) in leaf.edges
    assert N.relabel(path4, [3, 2, 1, 0]).edges == path4.edges                  # Spiegeln des Wegs ändert nichts
    assert N.relabel(path4, [1, 0, 2, 3]).edges == ((0, 1, 1), (0, 2, 1), (2, 3, 1))


# --- Matchings und stabile Ergebnisse ----------------------------------------------------------------------------------------------------------------
def test_max_matching_weight_by_hand(path3, path4, triangle, literature):
    assert [MT.max_matching_weight(n) for n in (path3, path4, triangle, literature)] == [1, 2, 1, 10]


def test_matching_by_milp_equals_the_subset_recursion(path4, tail, literature):
    for net in (path4, tail, literature):
        assert MT.max_weight_matching(net)[0] == MT.coalition_matching_values(net)[(1 << net.n) - 1]


def test_lp_gap_of_odd_cycles(triangle):
    lp, ip = S.lp_gap(triangle)
    assert (lp, ip) == (pytest.approx(1.5), 1)                                   # jede Kante 1/2
    lp5, ip5 = S.lp_gap(N.cycle(5))
    assert (lp5, ip5) == (pytest.approx(2.5), 2)
    assert not S.stable_exists(triangle) and S.stable_exists(N.cycle(4))


def test_stable_range_by_hand(path3, path4, path5, triangle):
    lo, hi = S.stable_range(path3)
    assert lo == pytest.approx([0, 1, 0]) and hi == pytest.approx([0, 1, 0])
    lo, hi = S.stable_range(path4)
    assert lo == pytest.approx([0, 0, 0, 0]) and hi == pytest.approx([1, 1, 1, 1])
    lo, hi = S.stable_range(path5)
    assert lo == pytest.approx([0, 1, 0, 1, 0]) and hi == pytest.approx(lo)
    assert S.stable_range(triangle) is None


def test_fixed_nodes_of_path5_and_path4(path4, path5):
    assert S.fixed_nodes(*S.stable_range(path5)) == pytest.approx({0: 0, 1: 1, 2: 0, 3: 1, 4: 0})
    assert S.fixed_nodes(*S.stable_range(path4)) == {}


def test_is_stable_accepts_and_rejects(path4):
    m = ((0, 1, 1), (2, 3, 1))
    assert S.is_stable(path4, m, [Fr(1, 3), Fr(2, 3), Fr(2, 3), Fr(1, 3)], 0)
    assert S.is_stable(path4, m, [0, 1, 0, 1], 0)
    assert not S.is_stable(path4, m, [Fr(1, 2), Fr(1, 2), Fr(1, 4), Fr(3, 4)], 0)       # 1/2 + 1/4 < 1: Kante 12 blockiert
    assert not S.is_stable(path4, m, [Fr(1, 3), Fr(1, 3), Fr(2, 3), Fr(1, 3)], 0)       # Summe auf 01 ist nicht 1
    assert not S.is_stable(path4, ((0, 1, 1),), [Fr(1, 2), Fr(1, 2), 0, 0], 0)            # Kante 23 blockiert (0 + 0 < 1)
    assert not S.is_stable(path4, ((0, 1, 1), (1, 2, 1)), [0, 1, 0, 1], 0)                # Matching teilt einen Knoten


# --- Ausgewogen ----------------------------------------------------------------------------------------------------------------------------------
def test_outside_option_by_hand(path4):
    adj = N.adjacency(path4)
    y = [Fr(1, 3), Fr(2, 3), Fr(2, 3), Fr(1, 3)]
    assert B.outside_option(adj, y, 1, 0) == Fr(1, 3)        # Knoten 1 gegenüber 0: Nachbar 2 liefert 1 - 2/3
    assert B.outside_option(adj, y, 0, 1) == 0                 # Knoten 0 hat keinen anderen Nachbarn
    assert B.outside_option(adj, y, 2, 3) == Fr(1, 3)


def test_is_balanced_accepts_the_hand_result_and_rejects_neighbours(path4, literature):
    m = ((0, 1, 1), (2, 3, 1))
    assert B.is_balanced(path4, m, [Fr(1, 3), Fr(2, 3), Fr(2, 3), Fr(1, 3)], 0)
    assert not B.is_balanced(path4, m, [Fr(1, 2)] * 4, 0)                      # stabil, aber Kante 01: 1/2 - 0 gegen 1/2 - 1/2
    assert not B.is_balanced(path4, m, [Fr(1, 4), Fr(3, 4), Fr(3, 4), Fr(1, 4)], 0)
    lm = ((0, 1, 8), (2, 3, 2))
    assert B.is_balanced(literature, lm, [Fr(3, 2), Fr(13, 2), Fr(1), Fr(1)], 0)
    assert not B.is_balanced(literature, lm, [Fr(4), Fr(4), Fr(1), Fr(1)], 0)


def test_edge_offers_by_hand():
    st = B.dyn_structure(N.path(2))
    a = np.zeros(2)
    assert B.edge_offers(st.w, a, st.rev) == pytest.approx([0.5, 0.5])         # (1 - 0) - 1/2 (1 - 0 - 0) = 1/2
    assert B.edge_offers(st.w, np.array([0.5, 0.0]), st.rev)[0] == pytest.approx(0.25)     # a_{0} = 1/2: (1 - 1/2) - 1/2 (1 - 1/2 - 0) = 1/4
    assert B.edge_offers(st.w, np.array([1.5, 0.0]), st.rev)[0] == pytest.approx(0.0)       # w - a < 0: kein Angebot (Nichttausch)


def test_balancing_step_on_path3_by_hand():
    """Gerichtete Kanten: 0:(0,1), 1:(1,2), 2:(1,0), 3:(2,1). Nach einem Schritt mit kappa = 1 aus Null: a_{1\\2} = m_{0->1} = 1/2 und a_{1\\0} = m_{2->1} = 1/2, die anderen 0.
    Danach m_{1->0} = (1 - 1/2) - 1/2 (1 - 1/2 - 0) = 1/4 und m_{0->1} = 1 - 1/2 (1 - 0 - 1/2) = 3/4: Auszahlungen (1/4, 3/4, 1/4)."""
    st = B.dyn_structure(N.path(3))
    a1 = B.balancing_step(st, np.zeros(4), 1.0)
    assert a1 == pytest.approx([0, 0.5, 0.5, 0])
    assert B.payoffs(st, a1) == pytest.approx([0.25, 0.75, 0.25])
    half = B.balancing_step(st, np.zeros(4), 0.5)                                # gedämpft: (1 - 1/2) 0 + 1/2 (1/2)
    assert half == pytest.approx([0, 0.25, 0.25, 0])


def test_dynamics_reaches_the_fixed_point_and_reports_non_convergence(path3):
    st = B.dyn_structure(path3)
    res = B.run_dynamics(st, 1.0)
    assert res.converged and res.y == pytest.approx([0, 1, 0])
    cut = B.run_dynamics(st, 0.25, max_iter=3)
    assert not cut.converged and cut.iterations == 3
    assert B.run_dynamics(B.dyn_structure(N.make_net(3, [])), 0.5).converged


def test_dynamics_trace_has_one_row_per_step(path3):
    res = B.run_dynamics(B.dyn_structure(path3), 1.0, trace_steps=3)
    assert res.trace.shape == (4, 3)
    assert res.trace[0] == pytest.approx([0.5, 0.5, 0.5])
    assert res.trace[1] == pytest.approx([0.25, 0.75, 0.25])


@pytest.mark.parametrize("fixture, expected", [
    ("path3", [0, 1, 0]), ("path4", [Fr(1, 3), Fr(2, 3), Fr(2, 3), Fr(1, 3)]), ("path5", [0, 1, 0, 1, 0]),
    ("star3", [1, 0, 0, 0]), ("literature", [Fr(3, 2), Fr(13, 2), 1, 1]), ("tail", [Fr(3, 4), Fr(1, 2), Fr(1, 2), Fr(1, 4)]), ("k23", [1, 1, 0, 0, 0]),
])
def test_balanced_outcome_by_hand_in_fractions(request, fixture, expected):
    net = request.getfixturevalue(fixture)
    out = B.balanced_outcome(net)
    assert out.status == "ok"
    exact = X.exact_balanced(net, out.matching, out.y)
    assert exact == [Fr(e) for e in expected]


def test_balanced_outcome_of_the_unique_even_path_six():
    out = B.balanced_outcome(N.path(6))
    assert X.exact_balanced(N.path(6), out.matching, out.y) == [Fr(1, 4), Fr(3, 4), Fr(1, 2), Fr(1, 2), Fr(3, 4), Fr(1, 4)]


def test_triangle_and_pentagon_have_no_outcome_and_say_so(triangle):
    for net in (triangle, N.cycle(5)):
        out = B.balanced_outcome(net)
        assert out.status == "no_stable" and out.y is None and "kein stabiles" in out.note


def test_dynamics_from_zero_fails_on_k23_and_the_reduction_repairs_it(k23):
    st = B.dyn_structure(k23)
    res = B.run_dynamics(st, 0.5)
    assert res.converged and res.y == pytest.approx([0.5] * 5)                   # Summe 2,5 > 2: keine Auszahlung eines Matchings
    assert B.by_dynamics(k23, st)[0] is None
    out = B.balanced_outcome(k23)
    assert out.method == "Reduktion" and not out.d0_found
    assert out.y == pytest.approx((1, 1, 0, 0, 0))


def test_reduction_refuses_when_a_fixed_node_gives_a_free_node_an_option():
    """Ein fester Knoten (hier künstlich: Knoten 1 bei 0,2) mit freien Nachbarn und w - f = 0,8 > 0 bietet ihnen eine Außenoption: die Reduktion lehnt ab."""
    net = N.path(3)
    y, m, why = B.by_reduction(net, ([0, 0.2, 0], [1, 0.2, 1]), 0.5)  # Knoten 1 fest bei 0,2, die Ränder frei: w - f = 0,8 > 0
    assert y is None and "Außenoption" in why


def test_balanced_matching_needs_a_covering_matching():
    net = N.complete_bipartite(2, 3)
    assert B.balanced_matching(net, np.array([0.5] * 5)) is None


def test_candidate_matchings_cover_all_positive_nodes(path4):
    y = np.array([1 / 3, 2 / 3, 2 / 3, 1 / 3])
    ms = B.candidate_matchings(path4, y)
    assert ms == [((0, 1, 1), (2, 3, 1))]


def test_no_edges_means_no_trade():
    out = B.balanced_outcome(N.make_net(3, []))
    assert out.status == "ok" and out.y == (0.0, 0.0, 0.0) and out.matching == ()


# --- Exakt ----------------------------------------------------------------------------------------------------------------------------------------
def test_solve_linear_exact_and_singular():
    a = [[Fr(2), Fr(1)], [Fr(1), Fr(-1)]]
    assert X.solve_linear(a, [Fr(5), Fr(1)]) == [Fr(2), Fr(1)]
    assert X.solve_linear([[Fr(1), Fr(1)], [Fr(2), Fr(2)]], [Fr(1), Fr(2)]) is None
    assert X.fraction_text(Fr(6, 3)) == "2" and X.fraction_text(Fr(-3, 6)) == "-1/2"


def test_exact_balanced_on_the_cycle_family_falls_back_to_rounding(cycle4):
    out = B.balanced_outcome(cycle4)
    assert X.exact_balanced(cycle4, out.matching, out.y) == [Fr(1, 2)] * 4


def test_exact_balanced_returns_none_if_the_matching_admits_no_balanced_outcome(path4):
    assert X.exact_balanced(path4, ((1, 2, 1),), [0.0, 0.5, 0.5, 0.0]) is None      # nur die Mittelkante: 0 und 3 bleiben ungepaart, die Kanten 01 und 23 blockieren


# --- Mehrere Ergebnisse -------------------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("a", [Fr(0), Fr(1, 5), Fr(1, 3), Fr(1, 2), Fr(4, 5), Fr(1)])
def test_cycle4_family_is_balanced_for_every_a(a):
    net, m, y = MU.cycle4_family_member(a)
    assert B.is_balanced(net, m, y, 0)


def test_cycle4_family_rejects_the_asymmetric_pair():
    net, m, _ = MU.cycle4_family_member(Fr(1, 2))
    assert not B.is_balanced(net, m, [Fr(1, 5), Fr(4, 5), Fr(1, 2), Fr(1, 2)], 0)
    assert not B.is_balanced(net, m, [Fr(1, 5), Fr(4, 5), Fr(3, 5), Fr(2, 5)], 0)


def test_distinct_outcomes_find_several_on_cycle4_and_one_on_a_tree(cycle4, path5):
    assert len(MU.distinct_outcomes(cycle4, 35)) >= 3
    assert len(MU.distinct_outcomes(N.path(6), 35)) == 1
    assert MU.max_deviation(MU.distinct_outcomes(cycle4, 35)) > 0.1
    assert MU.distinct_outcomes(N.cycle(3), 35) == []


# --- Spiel ---------------------------------------------------------------------------------------------------------------------------------------
def test_coalition_values_by_hand(path4):
    v = G.coalition_values(path4)
    assert v[0b1111] == 2 and v[0b0110] == 1 and v[0b0101] == 0 and v[0b0111] == 1 and v[0b0001] == 0


def test_shapley_of_path3_by_hand(path3):
    """Von Hand über die sechs Reihenfolgen: Knoten 1 trägt in 4 von 6 Reihenfolgen 1 bei (2/3), jeder Rand in einer (1/6)."""
    assert G.shapley(G.coalition_values(path3), 3) == [Fr(1, 6), Fr(2, 3), Fr(1, 6)]


def test_core_check_and_nucleolus_of_path3(path3):
    v = G.coalition_values(path3)
    assert G.in_core([0, 1, 0], v, 3) and not G.in_core([Fr(1, 6), Fr(2, 3), Fr(1, 6)], v, 3)
    x, levels = G.nucleolus(v, 3)
    assert x == pytest.approx([0, 1, 0]) and levels


def test_nucleolus_of_the_triangle_is_the_equal_split(triangle):
    """Der Kern des Dreiecks ist leer; der Nukleolus teilt gleich (1/3 je Knoten, größter Überschuss 1/3)."""
    v = G.coalition_values(triangle)
    x, _ = G.nucleolus(v, 3)
    assert x == pytest.approx([1 / 3] * 3) and not G.in_core(x, v, 3)


def test_nucleolus_of_path4_equals_the_balanced_outcome(path4):
    x, _ = G.nucleolus(G.coalition_values(path4), 4)
    assert x == pytest.approx([1 / 3, 2 / 3, 2 / 3, 1 / 3])


# --- Ausstiegsprinzip -----------------------------------------------------------------------------------------------------------------------------
def test_splits_by_hand():
    assert P.nash_split(1, 0, Fr(1, 3)) == Fr(2, 3) and P.exit_split(1, 0, Fr(1, 3)) == Fr(1, 2)
    assert P.nash_split(1, 0, Fr(3, 5)) == Fr(4, 5) and P.exit_split(1, 0, Fr(3, 5)) == Fr(3, 5)
    assert P.nash_split(1, Fr(1, 5), Fr(3, 5)) == Fr(7, 10) and P.exit_split(1, Fr(1, 5), Fr(3, 5)) == Fr(3, 5)
    assert P.nash_split(1, Fr(1, 4), Fr(1, 4)) == P.exit_split(1, Fr(1, 4), Fr(1, 4)) == Fr(1, 2)      # gleiche Optionen unter 1/2: gleich
    assert P.nash_split(1, Fr(3, 5), Fr(2, 5) + Fr(1, 10)) is None and P.exit_split(1, Fr(3, 5), Fr(1, 2)) is None


def test_principle_on_path4_gives_everybody_one_half(path4):
    y, m, source = P.principle_outcome(path4, 35)
    assert y == pytest.approx((0.5, 0.5, 0.5, 0.5))
    assert P.is_principle(path4, m, y)
    assert not B.is_balanced(path4, m, y)                                                     # Nash und Prinzip unterscheiden sich auf Weg 4


def test_principle_agrees_with_nash_on_path3(path3):
    y, m, _ = P.principle_outcome(path3, 35)
    assert y == pytest.approx((0, 1, 0)) and B.is_balanced(path3, m, y)


def test_principle_gives_nothing_without_a_stable_outcome(triangle):
    assert P.principle_outcome(triangle, 35) is None
