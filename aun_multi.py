"""Mehrere ausgewogene Ergebnisse: oft ist das ausgewogene Ergebnis nicht eindeutig (kleinster Fall: Kreis 4, (a, 1-a, a, 1-a) für jedes a in [0, 1]).

`distinct_outcomes` sammelt Ergebnisse aus mehreren Wegen (Dynamik von Null, Reduktion, Zufallsstarts); jedes vom Prüfer bestätigt. Zwei verschiedene belegen
Mehrdeutigkeit. Gefunden heißt nur: mindestens so viele; eine Obergrenze gibt dieses Suchen nicht."""

from dataclasses import dataclass
from fractions import Fraction

import numpy as np

import aun_balanced as B
from aun_net import Net, make_net, stream
from aun_stable import TOL, lp_gap, stable_range

DISTINCT = 1e-6          # zwei Auszahlungsvektoren gelten als verschieden, wenn sie in einem Knoten um mehr abweichen


@dataclass(frozen=True)
class Found:
    y: tuple
    matching: tuple
    sources: tuple         # Wege, die dieses Ergebnis lieferten


def random_start(st: B.Structure, net: Net, seed: int, cell: int):
    """Zufälliger Anfangswert der Außenoptionen: gleichverteilt zwischen 0 und dem größten Kantenwert."""
    rng = stream(seed, cell)
    top = max((w for _, _, w in net.edges), default=1)
    return np.array([rng.uniform() * top for _ in range(st.E)])


def distinct_outcomes(net: Net, seed: int, starts: int = 5, kappa: float = 0.5, rg=None, cell: int = 7000) -> list:
    """Alle verschiedenen ausgewogenen Ergebnisse, die Dynamik von Null, Reduktion und `starts` Zufallsstarts finden (Liste von Found, in der Reihenfolge des Findens)."""
    if not net.edges:
        return []
    lp, ip = lp_gap(net)
    if lp - ip >= TOL:
        return []
    st = B.dyn_structure(net)
    found = []

    def add(y, m, source):
        for f in found:
            if max(abs(a - b) for a, b in zip(f.y, y)) <= DISTINCT:
                found[found.index(f)] = Found(f.y, f.matching, f.sources + (source,))
                return
        found.append(Found(tuple(float(x) for x in y), m, (source,)))

    y, m, _, _ = B.by_dynamics(net, st, kappa)
    if y is not None:
        add(y, m, "Dynamik von Null")
    y, m, why = B.by_reduction(net, rg if rg is not None else stable_range(net, ip), kappa)
    if y is not None:
        add(y, m, "Reduktion")
    for i in range(starts):
        y, m, _, _ = B.by_dynamics(net, st, kappa, a0=random_start(st, net, seed, cell + i))
        if y is not None:
            add(y, m, f"Zufallsstart {i + 1}")
    return found


def max_deviation(found) -> float:
    """Größte Abweichung eines Knotens zwischen zwei gefundenen Ergebnissen (0 bei höchstens einem)."""
    best = 0.0
    for i in range(len(found)):
        for j in range(i + 1, len(found)):
            best = max(best, max(abs(a - b) for a, b in zip(found[i].y, found[j].y)))
    return best


def cycle4_family_member(a: Fraction):
    """Kreis 4 (Knoten 0-1-2-3-0, Wert 1) und das Ergebnis (a, 1-a, a, 1-a) mit dem Matching {01, 23}; für jedes a in [0, 1] ausgewogen."""
    net = make_net(4, [(0, 1), (1, 2), (2, 3), (0, 3)], sides=[0, 1, 0, 1])
    matching = ((0, 1, 1), (2, 3, 1))
    return net, matching, [a, 1 - a, a, 1 - a]
