"""Unabhängige Rechenwege für die Orakel-Tests: eigene Aufzählung und Schleifen, Bibliotheken nur hier (networkx, scipy), nie in der App.

- `all_max_matchings`: alle Matchings größten Gewichts durch Aufzählung der Kantenteilmengen.
- `enumerate_balanced`: alle ISOLIERTEN ausgewogenen Ergebnisse in Brüchen, durch Wahl des Maximierers je Außenoption (lineare Systeme, Gauß in Brüchen).
- `loop_step`: ein Schritt des Kantenausgleichs mit Wörterbüchern und Schleifen statt der vektorisierten Fassung.
- `coalition_core_lp`: Spanne jedes Knotens im Kern über ALLE Koalitionsungleichungen (anderes Programm als die Kantenungleichungen).
- `kohlberg_holds`: Kohlberg-Kriterium für den Nukleolus (ausgeglichene Koalitionsmengen).
"""

import itertools
from fractions import Fraction

import numpy as np

from aun_exact import solve_linear
from aun_net import Net, adjacency


def all_max_matchings(net: Net):
    """(Gewicht, Liste aller Matchings dieses Gewichts) durch Aufzählung."""
    edges = list(net.edges)
    best, found = -1, []

    def rec(i, used, wsum, chosen):
        nonlocal best, found
        if i == len(edges):
            if wsum > best:
                best, found = wsum, [tuple(chosen)]
            elif wsum == best:
                found.append(tuple(chosen))
            return
        rec(i + 1, used, wsum, chosen)
        u, v, w = edges[i]
        if u not in used and v not in used:
            rec(i + 1, used | {u, v}, wsum + w, chosen + [edges[i]])

    rec(0, frozenset(), 0, [])
    return best, found


def enumerate_balanced(net: Net, cap=60000):
    """Alle ausgewogenen Ergebnisse, die zu EINER Wahl der Außenoptionen gehören (eindeutig lösbares lineares System), als Liste von Bruchlisten.
    Rückgabe (Lösungen, Zahl singulärer Systeme) oder None, wenn mehr als `cap` Wahlen anfallen. Ausgewogenheit wird von der Definition geprüft (hier nachgebaut)."""
    adj = adjacency(net)
    _, matchings = all_max_matchings(net)
    solutions, singular = [], 0
    for matching in matchings:
        if not matching:
            solutions.append([Fraction(0)] * net.n)
            continue
        partner = {}
        for u, v, _ in matching:
            partner[u], partner[v] = v, u
        mnodes = sorted(partner)
        pos = {v: i for i, v in enumerate(mnodes)}
        options = [[k for k in adj[u] if k != partner[u]] + [None] for u in mnodes]
        total = 1
        for o in options:
            total *= len(o)
        if total > cap:
            return None
        for combo in itertools.product(*options):
            choice = dict(zip(mnodes, combo))
            rows, rhs = [], []
            for u, v, w in matching:
                r1 = [Fraction(0)] * len(mnodes)
                r1[pos[u]] += 1
                r1[pos[v]] += 1
                rows.append(r1)
                rhs.append(Fraction(w))
                r2 = [Fraction(0)] * len(mnodes)
                r2[pos[u]] += 1
                r2[pos[v]] -= 1
                c = Fraction(0)
                for node, sign in ((u, 1), (v, -1)):
                    k = choice[node]
                    if k is not None:
                        c += sign * adj[node][k]
                        if k in pos:
                            r2[pos[k]] += sign
                rows.append(r2)
                rhs.append(c)
            sol = solve_linear(rows, rhs)
            if sol is None:
                singular += 1
                continue
            y = [Fraction(0)] * net.n
            for v in mnodes:
                y[v] = sol[pos[v]]
            if _is_balanced_by_definition(net, adj, matching, y) and y not in solutions:
                solutions.append(y)
    return solutions, singular


def _is_balanced_by_definition(net, adj, matching, y):
    """Definition ohne Code der Demo: y >= 0, auf Matching-Kanten Summe w, überall y_u + y_v >= w, Ungepaarte 0, Überschüsse über den Außenoptionen gleich."""
    matched = {x for u, v, _ in matching for x in (u, v)}
    if any(val < 0 for val in y) or any(y[i] != 0 for i in range(net.n) if i not in matched):
        return False
    if any(y[u] + y[v] != w for u, v, w in matching) or any(y[u] + y[v] < w for u, v, w in net.edges):
        return False
    for u, v, _ in matching:
        au = max([Fraction(0)] + [w - y[k] for k, w in adj[u].items() if k != v])
        av = max([Fraction(0)] + [w - y[k] for k, w in adj[v].items() if k != u])
        if y[u] - au != y[v] - av:
            return False
    return True


def loop_step(net: Net, a: dict, kappa: float) -> dict:
    """Ein Schritt des Kantenausgleichs mit Schleifen; a[(i, j)] ist a_{i\\j}. Angebote m_{i->j} = (w - a_ij)^+ - 1/2 (w - a_ij - a_ji)^+."""
    adj = adjacency(net)

    def offer(i, j):
        w = adj[i][j]
        return max(w - a[(i, j)], 0) - 0.5 * max(w - a[(i, j)] - a[(j, i)], 0)

    new = {}
    for i in range(net.n):
        for j in adj[i]:
            best = max([offer(k, i) for k in adj[i] if k != j], default=0.0)
            new[(i, j)] = (1 - kappa) * a[(i, j)] + kappa * best
    return new


def loop_payoffs(net: Net, a: dict) -> list:
    adj = adjacency(net)
    out = []
    for i in range(net.n):
        best = 0.0
        for k in adj[i]:
            w = adj[k][i]
            best = max(best, max(w - a[(k, i)], 0) - 0.5 * max(w - a[(k, i)] - a[(i, k)], 0))
        out.append(best)
    return out


def coalition_core_lp(net: Net, values):
    """Kleinster und größter Wert jedes Knotens über alle x mit x(N) = v(N) und x(S) >= v(S) für alle Koalitionen S (scipy). None, wenn der Kern leer ist."""
    from scipy.optimize import linprog

    n = net.n
    full = (1 << n) - 1
    a_ub = np.array([[-(m >> i & 1) for i in range(n)] for m in range(1, full)], dtype=float)
    b_ub = np.array([-values[m] for m in range(1, full)], dtype=float)
    lo, hi = [], []
    for i in range(n):
        c = np.zeros(n)
        c[i] = 1
        kw = dict(A_ub=a_ub, b_ub=b_ub, A_eq=np.ones((1, n)), b_eq=[values[full]], bounds=(None, None), method="highs")
        r1 = linprog(c, **kw)
        if r1.status != 0:
            return None
        r2 = linprog(-c, **kw)
        lo.append(r1.fun)
        hi.append(-r2.fun)
    return lo, hi


def kohlberg_holds(x, values, n):
    """Kohlberg (1971), Gewinnspiel: x ist der Nukleolus genau dann, wenn für jedes Niveau alpha die Koalitionen mit Überschuss v(S) - x(S) >= alpha ausgeglichen sind
    (positive Gewichte mit Summe der Indikatoren = 1_N)."""
    from scipy.optimize import linprog

    full = (1 << n) - 1
    exc = {m: values[m] - sum(x[i] for i in range(n) if m >> i & 1) for m in range(1, full)}
    levels = []
    for e in sorted(exc.values(), reverse=True):
        if not levels or abs(e - levels[-1]) > 1e-6:
            levels.append(e)
    for alpha in levels:
        coal = [m for m, e in exc.items() if e >= alpha - 1e-6]
        k = len(coal)
        a = np.zeros((n, k + 1))
        for j, m in enumerate(coal):
            a[:, j] = [(m >> i) & 1 for i in range(n)]
        a_ub = np.hstack([-np.eye(k), np.ones((k, 1))])
        cost = np.zeros(k + 1)
        cost[-1] = -1.0
        res = linprog(cost, A_ub=a_ub, b_ub=np.zeros(k), A_eq=a, b_eq=np.ones(n), bounds=[(0, None)] * k + [(None, 1.0)], method="highs")
        if not (res.status == 0 and -res.fun > 1e-9):
            return False
    return True
