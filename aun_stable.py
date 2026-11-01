"""Stabile Ergebnisse: kein blockierendes Paar. Ein Ergebnis ist (Matching M, Auszahlung y) mit y_u + y_v = w auf M und y = 0 für Ungepaarte;
es ist stabil, wenn y_u + y_v >= w auf JEDER Kante gilt. Stabile Ergebnisse gibt es genau dann, wenn die LP-Relaxation des Matchings
ganzzahlig ist (Sotomayor, laut Bayati u. a.); die Auszahlungen sind dann die optimalen Lösungen des dualen Programms (Knotenüberdeckung)."""

import numpy as np

from aun_matching import lp_matching_value, max_matching_weight
from aun_net import Net

TOL = 1e-7


def lp_gap(net: Net):
    """(LP-Wert, ganzzahliger Wert) des Matchings; stabil existiert genau dann, wenn beide gleich sind."""
    return lp_matching_value(net), max_matching_weight(net)


def stable_exists(net: Net) -> bool:
    lp, ip = lp_gap(net)
    return lp - ip < TOL


def stable_range(net: Net, ip=None):
    """Kleinste und größte Auszahlung jedes Knotens über ALLE stabilen Ergebnisse (alle Matchings): y >= 0, y_u + y_v >= w auf jeder Kante, Summe y = größtes
    Matching-Gewicht. Rückgabe (lo, hi) als Listen oder None, wenn es kein stabiles Ergebnis gibt. Zwei lineare Programme je Knoten."""
    from scipy.optimize import linprog

    if ip is None:
        ip = max_matching_weight(net)
    n = net.n
    if not net.edges:
        return [0.0] * n, [0.0] * n
    a_ub = np.zeros((len(net.edges), n))
    b_ub = np.zeros(len(net.edges))
    for k, (u, v, w) in enumerate(net.edges):
        a_ub[k, u] = -1
        a_ub[k, v] = -1
        b_ub[k] = -w
    a_eq, b_eq = np.ones((1, n)), [float(ip)]
    lo, hi = [], []
    for i in range(n):
        c = np.zeros(n)
        c[i] = 1
        r1 = linprog(c, A_ub=a_ub, b_ub=b_ub, A_eq=a_eq, b_eq=b_eq, bounds=(0, None), method="highs")
        if r1.status != 0:
            return None
        r2 = linprog(-c, A_ub=a_ub, b_ub=b_ub, A_eq=a_eq, b_eq=b_eq, bounds=(0, None), method="highs")
        lo.append(float(r1.fun))
        hi.append(float(-r2.fun))
    return lo, hi


def random_stable_vertex(net: Net, rng, ip=None):
    """Eine zufällige Ecke des stabilen Bereichs (lineares Programm mit zufälligem Ziel, Zufallsstrom `rng`); None, wenn es keine stabile Auszahlung gibt."""
    from scipy.optimize import linprog

    if ip is None:
        ip = max_matching_weight(net)
    n = net.n
    a_ub = np.zeros((len(net.edges), n))
    b_ub = np.zeros(len(net.edges))
    for k, (u, v, w) in enumerate(net.edges):
        a_ub[k, u] = -1
        a_ub[k, v] = -1
        b_ub[k] = -w
    cost = np.array([rng.uniform() - 0.5 for _ in range(n)])
    res = linprog(cost, A_ub=a_ub, b_ub=b_ub, A_eq=np.ones((1, n)), b_eq=[float(ip)], bounds=(0, None), method="highs")
    return None if res.status != 0 else [float(x) for x in res.x]


def fixed_nodes(lo, hi, tol=1e-7) -> dict:
    """Knoten mit leerer stabiler Spanne (lo = hi): ihre Auszahlung steht schon fest, bevor irgendetwas ausgehandelt wird. Rückgabe {Knoten: Wert}."""
    return {i: lo[i] for i in range(len(lo)) if hi[i] - lo[i] <= tol}


def is_stable(net: Net, matching, y, tol=TOL) -> bool:
    """Prüfer (Definition): y >= 0, Ungepaarte 0, Summe auf Matching-Kanten = w, y_u + y_v >= w auf jeder Kante, Matching ohne gemeinsamen Knoten.
    Mit Brüchen und tol = 0 exakt."""
    matched = []
    for u, v, w in matching:
        matched += [u, v]
        if abs(y[u] + y[v] - w) > tol:
            return False
    mset = set(matched)
    if len(mset) != len(matched):
        return False
    if any(yi < -tol for yi in y):
        return False
    if any(abs(y[i]) > tol for i in range(net.n) if i not in mset):
        return False
    return all(y[u] + y[v] >= w - tol for u, v, w in net.edges)
