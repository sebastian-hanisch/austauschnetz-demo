"""Das Ausstiegsprinzip: eine EIGENE Variante dieser Demo, ohne Quelle und ohne Eindeutigkeitsaussage.

Statt den Überschuss über den Außenoptionen gleich zu teilen (Nash mit Drohpunkt), bekommt v die Hälfte, mindestens aber seine Außenoption, höchstens aber das, was
nach der Außenoption von u übrig bleibt: y_v = min(max(w/2, a_v), w - a_u). Es ist ein Experiment, kein Satz: ob es im Netz ein Gleichgewicht dieser Art gibt, ist nicht
bekannt; die Suche (Dynamik mit dieser Regel von mehreren Starts, Prüfer) kann nichts finden, ohne dass es keines gäbe."""

from fractions import Fraction

import numpy as np

import aun_balanced as B
from aun_net import Net, adjacency, stream
from aun_stable import TOL, is_stable, lp_gap, random_stable_vertex

STARTS = 3                # zufällige stabile Anfangsauszahlungen
MAX_ITER = 20000          # Schritte je Lauf


def nash_split(w, a_u, a_v):
    """Anteil von v bei Nash mit Drohpunkt: a_v plus die Hälfte des Überschusses; None, wenn kein Überschuss (a_u + a_v > w)."""
    if a_u + a_v > w:
        return None
    return a_v + Fraction(w - a_u - a_v, 1) / 2


def exit_split(w, a_u, a_v):
    """Anteil von v beim Ausstiegsprinzip: die Hälfte, mindestens a_v, höchstens w - a_u; None, wenn kein Überschuss."""
    if a_u + a_v > w:
        return None
    return min(max(Fraction(w) / 2, Fraction(a_v)), Fraction(w) - a_u)


def is_principle(net: Net, matching, y, tol=TOL) -> bool:
    """Prüfer des Ausstiegsprinzips: stabil, und auf jeder Matching-Kante ist y_v = min(max(w/2, a_v), w - a_u) (und ebenso für u)."""
    if not is_stable(net, matching, y, tol):
        return False
    adj = adjacency(net)
    for u, v, w in matching:
        au, av = B.outside_option(adj, y, u, v), B.outside_option(adj, y, v, u)
        if au + av > w + tol:
            return False
        if abs(y[v] - min(max(w / 2, av), w - au)) > tol or abs(y[u] - min(max(w / 2, au), w - av)) > tol:
            return False
    return True


def a_from_y(net: Net, st: B.Structure, y):
    """Außenoptionen a_(i ohne j) (je gerichtete Kante der Dynamik) zu einer gegebenen Auszahlung: der beste Nachbar außer j, nie unter 0."""
    adj = adjacency(net)
    de = [(u, v) for u, v, _ in net.edges] + [(v, u) for u, v, _ in net.edges]
    return np.array([B.outside_option(adj, y, i, j) for i, j in de], dtype=float)


def principle_outcome(net: Net, seed: int, y_nash=None, random_starts: int = STARTS, kappa: float = 0.5, cell: int = 8000):
    """Ein Fixpunkt des Ausstiegsprinzips mit Matching oder None. Starts der Reihe nach: von Null; bei den Außenoptionen des ausgewogenen Ergebnisses (`y_nash`, wird sonst gesucht);
    von zufälligen stabilen Auszahlungen (Ecken des stabilen Bereichs). Rückgabe (y, Matching, Quelle) oder None. Bei Gleichständen (Einheitswerte) liefert die Dynamik von Null
    oft Auszahlungen, die zu keinem Matching gehören; ein Start bei einer stabilen Auszahlung umgeht das."""
    if not net.edges:
        return None
    lp, ip = lp_gap(net)
    if lp - ip >= TOL:
        return None
    st = B.dyn_structure(net)
    starts = [("Dynamik von Null", None)]
    if y_nash is None:
        out = B.balanced_outcome(net, kappa)
        y_nash = out.y
    if y_nash is not None:
        starts.append(("Start beim ausgewogenen Ergebnis", a_from_y(net, st, y_nash)))
    rng = stream(seed, cell)
    for i in range(random_starts):
        y0 = random_stable_vertex(net, rng, ip)
        if y0 is not None:
            starts.append((f"Start bei stabilem Zufallsergebnis {i + 1}", a_from_y(net, st, y0)))
    for source, a0 in starts:
        res = B.run_dynamics(st, kappa, a0, rule="exit", max_iter=MAX_ITER)
        if not res.converged:
            continue
        m = B.balanced_matching(net, res.y, check=is_principle)
        if m is not None:
            return tuple(float(x) for x in res.y), m, source
    return None
