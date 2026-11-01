"""Exakte Brüche: aus einem Gleitkomma-Ergebnis (Matching und Auszahlung) das lineare System der Ausgewogenheit aufstellen und in Brüchen lösen.

Auf jeder Matching-Kante (u, v, w) gilt y_u + y_v = w und y_u - a_u = y_v - a_v. Wählt man für jede Außenoption den besten Nachbarn k (dessen Auszahlung eingeht)
oder keinen (Außenoption 0), sind beide Gleichungen linear. Das System hat genau dann eine eindeutige Lösung, wenn das ausgewogene Ergebnis zu dieser Wahl isoliert ist;
bei einer Familie (Kreis 4) ist es singulär, dann bleibt nur das Runden der Gleitkommazahl."""

from fractions import Fraction

from aun_balanced import is_balanced
from aun_net import Net, adjacency

MAX_DENOMINATOR = 10000


def solve_linear(a, b):
    """Gauß in Brüchen. Rückgabe die eindeutige Lösung oder None (singulär oder widersprüchlich)."""
    n = len(a)
    m = [list(row) + [bb] for row, bb in zip(a, b)]
    for col in range(n):
        piv = next((r for r in range(col, n) if m[r][col] != 0), None)
        if piv is None:
            return None
        m[col], m[piv] = m[piv], m[col]
        pv = m[col][col]
        m[col] = [x / pv for x in m[col]]
        for r in range(n):
            if r != col and m[r][col] != 0:
                f = m[r][col]
                m[r] = [x - f * y for x, y in zip(m[r], m[col])]
    return [m[i][n] for i in range(n)]


def best_neighbours(net: Net, matching, y, tol=1e-7):
    """Für jeden Gepaarten: der Nachbar (außer dem Partner), der die Außenoption liefert, oder None, wenn sie 0 ist."""
    adj = adjacency(net)
    partner = {}
    for u, v, _ in matching:
        partner[u], partner[v] = v, u
    choice = {}
    for u, v in partner.items():
        best, arg = tol, None
        for k, w in adj[u].items():
            if k != v and w - y[k] > best:
                best, arg = w - y[k], k
        choice[u] = arg
    return choice, adj


def exact_balanced(net: Net, matching, y):
    """Das ausgewogene Ergebnis in Brüchen (Liste) mit dem Matching und den Wahlen der Außenoptionen aus dem Gleitkomma-Ergebnis `y`,
    vom exakten Prüfer bestätigt; sonst die auf MAX_DENOMINATOR gerundete Zahl, wenn auch sie exakt besteht; sonst None."""
    mnodes = sorted({x for u, v, _ in matching for x in (u, v)})
    pos = {v: i for i, v in enumerate(mnodes)}
    if not mnodes:
        return [Fraction(0)] * net.n
    choice, adj = best_neighbours(net, matching, y)
    size = len(mnodes)
    rows, rhs = [], []
    for u, v, w in matching:
        r1 = [Fraction(0)] * size
        r1[pos[u]] += 1
        r1[pos[v]] += 1
        rows.append(r1)
        rhs.append(Fraction(w))
        r2 = [Fraction(0)] * size
        r2[pos[u]] += 1
        r2[pos[v]] -= 1
        c = Fraction(0)
        for node, sign in ((u, 1), (v, -1)):
            k = choice[node]
            if k is not None:                     # y_node - a_node = y_node - w_nk + y_k
                c += sign * adj[node][k]
                if k in pos:
                    r2[pos[k]] += sign
        rows.append(r2)
        rhs.append(c)
    sol = solve_linear(rows, rhs)
    if sol is not None:
        yq = [Fraction(0)] * net.n
        for v in mnodes:
            yq[v] = sol[pos[v]]
        if is_balanced(net, matching, yq, 0):
            return yq
    yr = [Fraction(float(x)).limit_denominator(MAX_DENOMINATOR) for x in y]
    return yr if is_balanced(net, matching, yr, 0) else None


def fraction_text(x) -> str:
    """Bruch als Text: ganze Zahlen ohne Nenner, sonst „3/4“."""
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
