"""Eigenschaftstests: Sätze und Invarianten, die für ALLE Zufallsnetze der Stichprobe gelten müssen (keine Messung der Demo, sondern Folgerungen aus der Definition)."""

import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

import aun_balanced as B
import aun_matching as MT
import aun_net as N
import aun_stable as S

ROOT = Path(__file__).resolve().parent.parent


def _nets():
    out = []
    for i in range(25):
        out.append(N.random_bipartite(5, 5, 0.4, N.stream(61, i), max_weight=4))
    for i in range(15):
        out.append(N.random_general(8, 0.35, N.stream(62, i)))
    for i in range(10):
        out.append(N.random_tree(9, N.stream(63, i)))
    return out


def test_balanced_outcome_is_stable_and_sums_to_the_edge_value_on_every_trade():
    checked = 0
    for net in _nets():
        out = B.balanced_outcome(net)
        if out.status != "ok":
            continue
        checked += 1
        y = out.y
        for u, v, w in out.matching:
            assert y[u] + y[v] == pytest.approx(w, abs=1e-8)
        assert all(y[u] + y[v] >= w - 1e-8 for u, v, w in net.edges)
        assert all(val >= -1e-9 for val in y)
        assert sum(y) == pytest.approx(MT.max_matching_weight(net), abs=1e-8)       # Summe der Auszahlungen = Gewicht des größten Matchings
    assert checked >= 35


def test_bipartite_nets_and_trees_always_have_a_stable_outcome_and_a_balanced_one():
    seen = 0
    for net in _nets():
        if net.sides is not None:
            seen += 1
            assert S.stable_exists(net)
            assert B.balanced_outcome(net).status == "ok"
    assert seen >= 30


def test_scaling_all_values_scales_the_payout():
    checked = 0
    for net in _nets()[:20]:
        base = B.balanced_outcome(net)
        for c in (2, 5):
            scaled = B.balanced_outcome(N.scaled(net, c))
            if base.status == "ok" and scaled.status == "ok":
                checked += 1
                assert np.array(scaled.y) / c == pytest.approx(np.array(base.y), abs=1e-8)
    assert checked >= 20


def test_a_balanced_outcome_is_invariant_under_renumbering_when_it_is_unique():
    """Bei Bäumen ist das Ergebnis eindeutig (gemessen in den Reihen); dann ändert Umnummerieren nichts."""
    for i in range(8):
        net = N.random_tree(9, N.stream(64, i))
        rng = N.stream(65, i)
        perm = list(range(net.n))
        for k in range(net.n - 1, 0, -1):
            j = N.rand_below(rng, k + 1)
            perm[k], perm[j] = perm[j], perm[k]
        a = B.balanced_outcome(net)
        b = B.balanced_outcome(N.relabel(net, perm))
        assert [b.y[perm[v]] for v in range(net.n)] == pytest.approx(list(a.y), abs=1e-8)


def test_fixed_nodes_have_the_same_payout_in_the_balanced_outcome():
    checked = 0
    for net in _nets()[:25]:
        out = B.balanced_outcome(net)
        rg = S.stable_range(net)
        if out.status != "ok" or rg is None:
            continue
        for i, val in S.fixed_nodes(*rg).items():
            checked += 1
            assert out.y[i] == pytest.approx(val, abs=1e-6)
    assert checked >= 20


def test_the_balanced_outcome_lies_inside_the_stable_range():
    for net in _nets()[:25]:
        out = B.balanced_outcome(net)
        rg = S.stable_range(net)
        if out.status == "ok":
            assert all(rg[0][i] - 1e-6 <= out.y[i] <= rg[1][i] + 1e-6 for i in range(net.n))


def test_no_stable_outcome_means_no_balanced_outcome_from_the_solver():
    complete5 = N.make_net(5, [(i, j) for i in range(5) for j in range(i + 1, 5)])
    for net in [N.cycle(3), N.cycle(5), N.cycle(7), complete5]:
        assert not S.stable_exists(net)
        assert B.balanced_outcome(net).status == "no_stable"


def test_same_result_under_two_hash_seeds_in_a_second_process():
    """Dasselbe Netz und Ergebnis unter zwei Hash-Seeds (set-/dict-Reihenfolge darf nichts ändern)."""
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import aun_net as N, aun_balanced as B; "
            "net = N.random_bipartite(6, 6, 0.4, N.stream(5, 1)); o = B.balanced_outcome(net); print(net.edges, [round(x, 9) for x in o.y], o.method)")
    outs = []
    for seed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=seed)
        r = subprocess.run([sys.executable, "-X", "utf8", "-c", code, str(ROOT)], capture_output=True, text=True, env=env)
        assert r.returncode == 0, r.stderr
        outs.append(r.stdout)
    assert outs[0] == outs[1] and outs[0].strip()


def test_cycle4_family_is_balanced_for_fifty_one_values_of_a():
    """Von Hand: y0 - a0 = a - (1 - y3) = 0 und y1 - a1 = (1 - a) - (1 - y2) = 0 für jedes a; stabil, weil auf jeder Kante a + (1 - a) = 1. Hier in Brüchen für a = k/50."""
    from fractions import Fraction

    import aun_multi as MU
    for k in range(51):
        net, m, y = MU.cycle4_family_member(Fraction(k, 50))
        assert B.is_balanced(net, m, y, 0), k
