"""Das Austauschnetz als kooperatives Spiel (Zuordnungsspiel): v(S) = größtes Matching im Teilnetz auf S.

Der Kern sind die Auszahlungen x mit x(N) = v(N) und x(S) >= v(S) für jede Koalition S; er fällt mit den stabilen Auszahlungen zusammen. Hier: Shapley-Wert (exakt),
Kern-Prüfung über alle Koalitionen und Nukleolus (Folge linearer Programme, Maschler/Peleg/Shapley). Alles für höchstens GAME_MAX_N Knoten (2^n Koalitionen)."""

from fractions import Fraction
from math import factorial

import numpy as np

from aun_matching import coalition_matching_values
from aun_net import Net

GAME_MAX_N = 8
TOL = 1e-9


def coalition_values(net: Net) -> list:
    """v(S) für alle 2^n Koalitionen (Bitmaske S, Bit i = Knoten i)."""
    return coalition_matching_values(net)


def shapley(v, n: int) -> list:
    """Shapley-Wert in Brüchen: gewichteter Mittelwert der Beiträge v(S + i) - v(S) über alle Koalitionen S ohne i."""
    out = []
    for i in range(n):
        total = Fraction(0)
        for mask in range(1 << n):
            if mask >> i & 1:
                continue
            s = bin(mask).count("1")
            total += Fraction(factorial(s) * factorial(n - s - 1), factorial(n)) * (v[mask | (1 << i)] - v[mask])
        out.append(total)
    return out


def coalition_excess_violation(x, v, n: int) -> float:
    """Größte Verletzung des Kerns: max über Koalitionen von v(S) - x(S) (positiv = Koalition kann sich besserstellen), die große Koalition mit Betrag der Abweichung."""
    full = (1 << n) - 1
    worst = abs(sum(x) - v[full])
    for mask in range(1, full):
        worst = max(worst, v[mask] - sum(x[i] for i in range(n) if mask >> i & 1))
    return float(worst)


def in_core(x, v, n: int, tol=1e-7) -> bool:
    """Liegt x im Kern? Alle Koalitionsungleichungen, unabhängig von der Kantenprüfung."""
    return coalition_excess_violation(x, v, n) <= tol


def _coalition_matrix(n: int):
    masks = np.arange(1, (1 << n) - 1)
    return np.array([[(m >> i) & 1 for i in range(n)] for m in masks], dtype=float), masks


def nucleolus(v, n: int):
    """Nukleolus: minimiert lexikografisch die geordneten Überschüsse e(S, x) = v(S) - x(S). Rückgabe (x, Stufen) mit den Niveaus der fixierten Koalitionen.
    Nur linear unabhängige Fesseln kommen in die Gleichungen (redundante ließen HiGHS die Fläche als unzulässig melden)."""
    from scipy.optimize import linprog

    if n == 1:
        return np.array([float(v[1])]), []
    M, masks = _coalition_matrix(n)
    rhs = np.array([v[m] for m in masks], dtype=float)
    grand = float(v[(1 << n) - 1])
    remaining = np.ones(len(masks), dtype=bool)
    fixed_rows, fixed_vals, levels = [], [], []
    x = None
    for _ in range(len(masks) + 1):
        idx = np.flatnonzero(remaining)
        if len(idx) == 0:
            break
        a_eq = [np.append(np.ones(n), 0.0)] + [np.append(r, 0.0) for r in fixed_rows]
        b_eq = [grand] + list(fixed_vals)
        a_ub = np.hstack([-M[idx], -np.ones((len(idx), 1))])               # v(S) - x(S) <= eps
        res = linprog(np.append(np.zeros(n), 1.0), A_ub=a_ub, b_ub=-rhs[idx], A_eq=np.array(a_eq), b_eq=b_eq, bounds=[(None, None)] * (n + 1), method="highs")
        if not res.success:
            raise RuntimeError(res.message)
        eps, x = float(res.x[-1]), res.x[:n]
        excess = rhs[idx] - M[idx] @ x
        candidates = [k for k, e in zip(idx, excess) if e >= eps - TOL]
        face_a, face_b = -M[idx], -rhs[idx] + eps + TOL                     # Fläche der Lösungen mit Überschuss höchstens eps
        eq_a = np.array([np.ones(n)] + list(fixed_rows))
        eq_b = np.array([grand] + list(fixed_vals))
        newly = []
        for k in candidates:
            r = linprog(-M[k], A_ub=face_a, b_ub=face_b, A_eq=eq_a, b_eq=eq_b, bounds=[(None, None)] * n, method="highs")
            # kleinster Überschuss der Koalition auf der Fläche; fest, wenn er nicht unter eps sinken kann (Rundung: Spielraum von 10 TOL)
            if r.success and rhs[k] + r.fun >= eps - 10 * TOL:
                newly.append(k)
        if not newly:
            newly = candidates[:1]
        for k in newly:
            if np.linalg.matrix_rank(np.array([np.ones(n)] + fixed_rows + [M[k]]), tol=1e-9) > len(fixed_rows) + 1:
                fixed_rows.append(M[k])
                fixed_vals.append(rhs[k] - eps)
            remaining[k] = False
        levels.append(eps)
        if np.linalg.matrix_rank(np.array([np.ones(n)] + fixed_rows), tol=1e-9) >= n:
            x = np.linalg.lstsq(np.array([np.ones(n)] + fixed_rows), np.array([grand] + fixed_vals), rcond=None)[0]
            break
    return x, levels
