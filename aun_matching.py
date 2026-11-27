"""Matchings: das größte Gewicht eines Matchings (ganzzahlig), seine LP-Relaxation und die Werte aller Koalitionen.

scipy (HiGHS) wird erst in der Funktion geladen, die es braucht."""

import numpy as np

from aun_net import Net, adjacency

DP_LIMIT = 12          # bis zu so vielen Knoten rechnet `max_matching_weight` über Teilmengen (exakt, ohne scipy), darüber das ganzzahlige Programm


def coalition_matching_values(net: Net) -> list:
    """best[S] = größtes Gewicht eines Matchings im Teilnetz auf der Knotenmenge S (Bitmaske), für alle 2^n Mengen; Rekursion: der niedrigste Knoten bleibt
    allein oder wird mit einem Nachbarn in S gepaart. Das ist die Wertefunktion des Zuordnungsspiels."""
    n = net.n
    adj = adjacency(net)
    best = [0] * (1 << n)
    for mask in range(1, 1 << n):
        low = (mask & -mask).bit_length() - 1
        rest = mask & (mask - 1)
        b = best[rest]
        for j, w in adj[low].items():
            if rest >> j & 1:
                c = w + best[rest & ~(1 << j)]
                if c > b:
                    b = c
        best[mask] = b
    return best


def max_weight_matching(net: Net, edges=None):
    """Ein Matching größten Gewichts als (Gewicht, Kanten) über das ganzzahlige Programm; `edges` schränkt auf eine Teilmenge der Kanten ein."""
    from scipy.optimize import Bounds, LinearConstraint, milp

    es = tuple(net.edges if edges is None else edges)
    if not es:
        return 0, ()
    m = len(es)
    a = np.zeros((net.n, m))
    c = np.zeros(m)
    for k, (u, v, w) in enumerate(es):
        a[u, k] = 1
        a[v, k] = 1
        c[k] = -w
    res = milp(c, constraints=LinearConstraint(a, -np.inf, 1), integrality=np.ones(m), bounds=Bounds(0, 1), options={"mip_rel_gap": 0.0})
    if res.status != 0:
        raise RuntimeError(f"Matching-MILP nicht gelöst: {res.message}")
    chosen = tuple(es[k] for k in range(m) if res.x[k] > 0.5)
    return sum(w for _, _, w in chosen), chosen


def max_matching_weight(net: Net) -> int:
    """Größtes Gewicht eines Matchings."""
    if not net.edges:
        return 0
    if net.n <= DP_LIMIT:
        return coalition_matching_values(net)[(1 << net.n) - 1]
    return max_weight_matching(net)[0]


def lp_matching_value(net: Net) -> float:
    """Wert der LP-Relaxation (Knotensumme höchstens 1, Kantenvariablen ab 0): Obergrenze für das ganzzahlige Matching."""
    from scipy.optimize import linprog

    if not net.edges:
        return 0.0
    m = len(net.edges)
    a = np.zeros((net.n, m))
    c = np.zeros(m)
    for k, (u, v, w) in enumerate(net.edges):
        a[u, k] = 1
        a[v, k] = 1
        c[k] = -w
    res = linprog(c, A_ub=a, b_ub=np.ones(net.n), bounds=(0, None), method="highs")
    return float(-res.fun)
