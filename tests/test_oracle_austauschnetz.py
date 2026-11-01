"""Orakel-Tests (anderer Rechenweg als die Demo): Aufzählung, Schleifen, Koalitionsungleichungen, Kohlberg-Kriterium, networkx und exakte Brüche.

- Matching: networkx.max_weight_matching und die Teilmengen-Rekursion gegen das ganzzahlige Programm.
- Stabil: Zulässigkeits-Programm je größtem Matching und die Koalitionsungleichungen (Kern des Zuordnungsspiels) gegen das LP-Kriterium und die Kantenungleichungen.
- Ausgewogen: Aufzählung der Maximierer-Wahl in Brüchen (lineare Systeme) gegen Dynamik/Reduktion/Prüfer; „Löser findet ein Ergebnis“ genau dann, wenn LP-Lücke null (Atlas).
- Dynamik: vektorisierter Schritt gegen eine Fassung mit Schleifen und Wörterbüchern.
- Spiel: Shapley-Wert als Mittel über alle Reihenfolgen; Nukleolus gegen das Kohlberg-Kriterium; Nukleolus eines Netzes mit Kern ist ausgewogen.
Ausgewogen schließt stabil ein (Definition): „ausgewogen, aber nicht stabil“ kann es nicht geben; die messbare Richtung ist die andere."""

import itertools
import math
from fractions import Fraction as Fr

import numpy as np
import pytest

import aun_atlas as A
import aun_balanced as B
import aun_exact as X
import aun_game as G
import aun_matching as MT
import aun_net as N
import aun_stable as S
import oracles as O

ENUM_CAP = 150          # so viele Wahlen der Außenoptionen höchstens je Matching (der große Lauf im Scratch-Ordner nimmt 1500)
nx = pytest.importorskip("networkx")
linprog = pytest.importorskip("scipy.optimize").linprog


def to_nx(net):
    g = nx.Graph()
    g.add_nodes_from(range(net.n))
    for u, v, w in net.edges:
        g.add_edge(u, v, weight=w)
    return g


def random_nets(count, kind, seed, **kw):
    out = []
    for i in range(count):
        rng = N.stream(seed, i)
        if kind == "gen":
            out.append(N.random_general(kw["n"], kw["p"], rng))
        elif kind == "bip":
            out.append(N.random_bipartite(kw["a"], kw["b"], kw["p"], rng, kw.get("max_weight", 1)))
        else:
            out.append(N.random_tree(kw["n"], rng))
    return out


# --- Matching --------------------------------------------------------------------------------------------------------------------------------------
def test_matching_weight_equals_networkx_weighted_and_unit():
    nets = random_nets(30, "gen", 1, n=9, p=0.4) + random_nets(20, "bip", 2, a=5, b=6, p=0.4, max_weight=5)
    for net in nets:
        m = nx.max_weight_matching(to_nx(net), weight="weight")
        ref = sum(net.weight(u, v) for u, v in m)
        assert MT.max_matching_weight(net) == ref
        assert MT.max_weight_matching(net)[0] == ref
        if net.n <= 12:
            assert MT.coalition_matching_values(net)[(1 << net.n) - 1] == ref


def test_every_coalition_value_equals_networkx_on_the_induced_subnet():
    for net in random_nets(8, "gen", 3, n=7, p=0.5):
        v = MT.coalition_matching_values(net)
        for mask in range(1 << net.n):
            keep = [i for i in range(net.n) if mask >> i & 1]
            sub = to_nx(net).subgraph(keep)
            assert v[mask] == sum(net.weight(a, b) for a, b in nx.max_weight_matching(sub, weight="weight"))


def test_betweenness_equals_networkx():
    for net in random_nets(15, "gen", 4, n=10, p=0.3) + random_nets(5, "tree", 5, n=9):
        ref = nx.betweenness_centrality(to_nx(net), normalized=False)
        assert N.betweenness(net) == pytest.approx([ref[i] for i in range(net.n)])


# --- Stabil -----------------------------------------------------------------------------------------------------------------------------------------
def feasibility_with_matching(net, matching):
    """Zulässigkeits-Programm: y >= 0, y_u + y_v >= w überall, = w auf dem Matching, 0 für Ungepaarte."""
    n = net.n
    a_ub = np.zeros((len(net.edges), n))
    b_ub = np.zeros(len(net.edges))
    for k, (u, v, w) in enumerate(net.edges):
        a_ub[k, u] = a_ub[k, v] = -1
        b_ub[k] = -w
    a_eq, b_eq = [], []
    matched = set()
    for u, v, w in matching:
        row = np.zeros(n)
        row[u] = row[v] = 1
        a_eq.append(row)
        b_eq.append(w)
        matched |= {u, v}
    for i in range(n):
        if i not in matched:
            row = np.zeros(n)
            row[i] = 1
            a_eq.append(row)
            b_eq.append(0)
    res = linprog(np.zeros(n), A_ub=a_ub, b_ub=b_ub, A_eq=np.array(a_eq) if a_eq else None, b_eq=b_eq if b_eq else None, bounds=(0, None), method="highs")
    return res.status == 0


def core_nonempty_by_coalitions(net):
    return O.coalition_core_lp(net, MT.coalition_matching_values(net)) is not None


def test_lp_gap_criterion_equals_feasibility_with_some_maximum_matching_equals_coalition_core():
    """Drei Wege zur Frage „gibt es ein stabiles Ergebnis?“ auf Zufallsnetzen (Einheits- und ganzzahlige Werte) und dem ganzen Atlas."""
    nets = random_nets(25, "gen", 6, n=7, p=0.45) + random_nets(10, "bip", 7, a=4, b=4, p=0.5, max_weight=3) + A.load_atlas()
    stable_count = 0
    for net in nets:
        gap = S.stable_exists(net)
        _, matchings = O.all_max_matchings(net)
        feas = any(feasibility_with_matching(net, m) for m in matchings)
        assert gap == feas
        if net.n <= 8:
            assert gap == core_nonempty_by_coalitions(net)
        stable_count += gap
    assert 100 < stable_count < len(nets)                      # beide Arten kommen vor


def test_stable_range_equals_the_range_over_all_coalition_inequalities():
    checked = 0
    for net in random_nets(40, "gen", 8, n=7, p=0.45) + [N.path(4), N.path(5), N.cycle(4), N.complete_bipartite(2, 3), N.literature_example()]:
        rg = S.stable_range(net)
        ref = O.coalition_core_lp(net, MT.coalition_matching_values(net))
        assert (rg is None) == (ref is None)
        if rg is not None:
            assert rg[0] == pytest.approx(ref[0], abs=1e-7) and rg[1] == pytest.approx(ref[1], abs=1e-7)
            checked += 1
    assert checked >= 20


def test_bipartite_and_tree_nets_always_have_a_stable_outcome():
    for net in random_nets(40, "bip", 9, a=6, b=6, p=0.3, max_weight=4) + random_nets(20, "tree", 10, n=9):
        assert S.stable_exists(net)


# --- Dynamik --------------------------------------------------------------------------------------------------------------------------------------
def test_vectorised_step_equals_the_loop_version_on_random_nets_and_states():
    for i, net in enumerate(random_nets(12, "gen", 11, n=8, p=0.4) + random_nets(6, "bip", 12, a=4, b=4, p=0.5, max_weight=3)):
        st = B.dyn_structure(net)
        de = [(u, v) for u, v, _ in net.edges] + [(v, u) for u, v, _ in net.edges]
        rng = N.stream(13, i)
        a = np.array([rng.uniform() * 2 for _ in range(st.E)])
        for kappa in (0.25, 1.0):
            vec = B.balancing_step(st, a, kappa)
            loop = O.loop_step(net, {e: a[k] for k, e in enumerate(de)}, kappa)
            assert vec == pytest.approx([loop[e] for e in de], abs=1e-12)
        assert B.payoffs(st, a) == pytest.approx(O.loop_payoffs(net, {e: a[k] for k, e in enumerate(de)}), abs=1e-12)


def test_the_fixed_point_of_the_dynamics_is_a_fixed_point_of_the_loop_version():
    for net in [N.path(4), N.cycle(6), N.complete_bipartite(3, 3), N.literature_example()] + random_nets(5, "bip", 14, a=5, b=5, p=0.4):
        st = B.dyn_structure(net)
        res = B.run_dynamics(st, 0.5)
        assert res.converged
        de = [(u, v) for u, v, _ in net.edges] + [(v, u) for u, v, _ in net.edges]
        a = {e: res.a[k] for k, e in enumerate(de)}
        again = O.loop_step(net, a, 0.5)
        assert max(abs(again[e] - a[e]) for e in de) < 1e-10


# --- Ausgewogen ------------------------------------------------------------------------------------------------------------------------------------
def test_solver_agrees_with_the_enumeration_on_the_atlas():
    """Alle zusammenhängenden Graphen bis 6 Knoten: findet der Löser ein Ergebnis genau dann, wenn die LP-Lücke null ist, und liegt sein exaktes Ergebnis unter den
    aufgezählten isolierten Lösungen? Graphen mit zu vielen Wahlen der Außenoptionen werden übersprungen (Zähler unten)."""
    compared = skipped = families = stable = 0
    stable_total = 0
    for net in A.load_atlas():
        out = B.balanced_outcome(net)
        gap_zero = S.stable_exists(net)
        stable_total += gap_zero
        assert (out.status == "ok") == gap_zero, (net.n, net.edges)
        enum = O.enumerate_balanced(net, cap=ENUM_CAP)
        if enum is None:
            skipped += 1
            continue
        solutions, singular = enum
        if not gap_zero:
            assert solutions == []                         # nach Definition (stabil nötig) gibt es keines
            continue
        stable += 1
        assert solutions or singular, (net.n, net.edges)    # wenn stabil: isolierte Lösung oder eine Familie
        exact = X.exact_balanced(net, out.matching, out.y)
        assert exact is not None, (net.n, net.edges)
        assert O._is_balanced_by_definition(net, N.adjacency(net), out.matching, exact)
        if solutions and singular == 0:
            assert exact in solutions                      # kein Familienfall: die Lösung ist isoliert und aufgezählt
            compared += 1
        elif singular:
            families += 1
    assert stable_total == 126                                   # 126 der 142 zusammenhängenden Graphen mit 2 bis 6 Knoten haben ein stabiles Ergebnis
    assert compared >= 12 and stable >= 40, (compared, stable, skipped, families)


def test_solver_result_is_balanced_by_the_independent_definition_on_random_nets():
    found = 0
    for net in random_nets(30, "gen", 15, n=9, p=0.35) + random_nets(20, "bip", 16, a=6, b=6, p=0.35, max_weight=4) + random_nets(10, "tree", 17, n=12):
        out = B.balanced_outcome(net)
        assert (out.status == "ok") == S.stable_exists(net) or out.status == "not_found"
        if out.status == "ok":
            found += 1
            yq = [Fr(float(x)).limit_denominator(10000) for x in out.y]
            exact = X.exact_balanced(net, out.matching, out.y)
            assert exact is not None or max(abs(float(a) - b) for a, b in zip(yq, out.y)) > 1e-9
            assert B.is_balanced(net, out.matching, out.y, 1e-7)
    assert found >= 40


def test_not_found_never_happens_on_trees_and_bipartite_nets():
    for net in random_nets(40, "tree", 18, n=10) + random_nets(40, "bip", 19, a=8, b=8, p=0.3):
        assert B.balanced_outcome(net).status == "ok"


def test_literature_example_by_the_enumeration(literature):
    solutions, singular = O.enumerate_balanced(literature)
    assert solutions == [[Fr(3, 2), Fr(13, 2), Fr(1), Fr(1)]] and singular == 0


def test_enumeration_oracle_on_hand_nets(path3, path4, star3):
    assert O.enumerate_balanced(path3)[0] == [[Fr(0), Fr(1), Fr(0)]]
    assert O.enumerate_balanced(path4)[0] == [[Fr(1, 3), Fr(2, 3), Fr(2, 3), Fr(1, 3)]]
    assert [Fr(1), Fr(0), Fr(0), Fr(0)] in O.enumerate_balanced(star3)[0]


def test_enumeration_oracle_sees_the_cycle_family_as_singular(cycle4):
    solutions, singular = O.enumerate_balanced(cycle4)
    assert singular > 0                                      # die Familie (a, 1-a, a, 1-a) liefert singuläre Systeme
    assert all(O._is_balanced_by_definition(cycle4, N.adjacency(cycle4), m, s) for s in solutions for m in O.all_max_matchings(cycle4)[1] if any(s[u] + s[v] == w for u, v, w in m))


# --- Spiel ------------------------------------------------------------------------------------------------------------------------------------------
def test_shapley_equals_the_average_over_all_orders():
    for net in random_nets(6, "gen", 20, n=6, p=0.5):
        n = net.n
        v = G.coalition_values(net)
        total = [Fr(0)] * n
        for order in itertools.permutations(range(n)):
            mask = 0
            for i in order:
                total[i] += v[mask | (1 << i)] - v[mask]
                mask |= 1 << i
        assert G.shapley(v, n) == [t / math.factorial(n) for t in total]


def test_nucleolus_satisfies_kohlberg_on_random_nets_with_and_without_core():
    with_core = without = 0
    for net in random_nets(16, "gen", 21, n=6, p=0.5) + [N.cycle(3), N.cycle(5), N.cycle(7), N.path(4), N.path(5), N.star(3)]:
        v = G.coalition_values(net)
        x, _ = G.nucleolus(v, net.n)
        assert abs(sum(x) - v[(1 << net.n) - 1]) < 1e-7
        assert O.kohlberg_holds(x, v, net.n), (net.n, net.edges)
        if S.stable_exists(net):
            with_core += 1
        else:
            without += 1
    assert with_core >= 5 and without >= 3


def test_nucleolus_of_a_net_with_core_is_balanced_on_small_random_nets():
    checked = 0
    for net in random_nets(25, "gen", 22, n=6, p=0.5) + random_nets(10, "bip", 23, a=3, b=3, p=0.6):
        if not S.stable_exists(net):
            continue
        x, _ = G.nucleolus(G.coalition_values(net), net.n)
        assert G.in_core(x, G.coalition_values(net), net.n, 1e-6)
        assert any(B.is_balanced(net, m, list(x), 1e-6) for m in B.candidate_matchings(net, x, 1e-5)), (net.n, net.edges)
        checked += 1
    assert checked >= 15
