"""Netze: Knoten sind Betriebe (Verlader und Spediteure), eine Kante ist eine mögliche Tour mit einem Überschuss w (ganze Zahl, Einheitswert 1).

Zufall nur über SplitMix64 (`stream(seed, zelle)`), kein Python-`hash`. Alle Erzeuger sind reine Funktionen von (Parametern, Strom)."""

from collections import deque
from dataclasses import dataclass

import numpy as np

from aun_rng import SplitMix64

SIDE_LOADER, SIDE_CARRIER = 0, 1          # Seite 0: Verlader, Seite 1: Spediteur (nur bei zweiseitigen Netzen)
MIN_EDGES = 4                              # Zufallsnetze haben mindestens so viele Kanten (sonst gibt es nichts zu verteilen)


@dataclass(frozen=True)
class Net:
    """Knoten 0 .. n-1, Kanten (u, v, w) mit u < v und w >= 1, sortiert. `sides` nur bei zweiseitigen Netzen; `labels` nur bei eigenen Kantenlisten."""
    n: int
    edges: tuple
    sides: tuple | None = None
    labels: tuple | None = None

    def label(self, i: int) -> str:
        if self.labels is not None:
            return self.labels[i]
        if self.sides is not None:
            return ("V" if self.sides[i] == SIDE_LOADER else "S") + str(i)
        return str(i)

    def role(self, i: int) -> str:
        if self.sides is None:
            return "Betrieb"
        return "Verlader" if self.sides[i] == SIDE_LOADER else "Spediteur"

    def weight(self, u: int, v: int) -> int:
        for a, b, w in self.edges:
            if (a, b) == (min(u, v), max(u, v)):
                return w
        return 0


def make_net(n: int, pairs, weights=None, sides=None, labels=None) -> Net:
    """Kanten normalisieren (u < v, sortiert); Schleifen, doppelte Kanten und Gewichte unter 1 sind Fehler."""
    seen = {}
    for k, (u, v) in enumerate(pairs):
        u, v = int(u), int(v)
        w = 1 if weights is None else int(weights[k])
        if u == v:
            raise ValueError(f"Schleife am Knoten {u}")
        if not (0 <= u < n and 0 <= v < n):
            raise ValueError(f"Kante ({u}, {v}) außerhalb von 0 bis {n - 1}")
        if w < 1:
            raise ValueError("Kantenwerte müssen ganze Zahlen ab 1 sein")
        key = (min(u, v), max(u, v))
        if key in seen:
            raise ValueError(f"Kante {key} doppelt")
        seen[key] = w
    edges = tuple((u, v, w) for (u, v), w in sorted(seen.items()))
    return Net(n, edges, None if sides is None else tuple(sides), None if labels is None else tuple(labels))


def adjacency(net: Net) -> list:
    """Liste von Wörterbüchern: adj[u][k] = Kantenwert."""
    adj = [dict() for _ in range(net.n)]
    for u, v, w in net.edges:
        adj[u][v] = w
        adj[v][u] = w
    return adj


def degrees(net: Net) -> list:
    d = [0] * net.n
    for u, v, _ in net.edges:
        d[u] += 1
        d[v] += 1
    return d


def two_colouring(net: Net):
    """Seiten 0/1, falls das Netz zweiseitig ist, sonst None (Breitensuche je Komponente)."""
    adj = adjacency(net)
    colour = [-1] * net.n
    for s in range(net.n):
        if colour[s] >= 0:
            continue
        colour[s] = 0
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for k in adj[u]:
                if colour[k] < 0:
                    colour[k] = 1 - colour[u]
                    queue.append(k)
                elif colour[k] == colour[u]:
                    return None
    return tuple(colour)


def is_connected(net: Net) -> bool:
    if net.n == 0:
        return True
    adj = adjacency(net)
    seen = {0}
    queue = deque([0])
    while queue:
        u = queue.popleft()
        for k in adj[u]:
            if k not in seen:
                seen.add(k)
                queue.append(k)
    return len(seen) == net.n


def subnet(net: Net, keep) -> Net:
    """Teilnetz auf den Knoten `keep` (aufsteigend neu nummeriert)."""
    keep = sorted(keep)
    idx = {v: i for i, v in enumerate(keep)}
    pairs = [(idx[u], idx[v]) for u, v, _ in net.edges if u in idx and v in idx]
    ws = [w for u, v, w in net.edges if u in idx and v in idx]
    sides = None if net.sides is None else [net.sides[v] for v in keep]
    labels = None if net.labels is None else [net.labels[v] for v in keep]
    return make_net(len(keep), pairs, ws, sides, labels)


def relabel(net: Net, perm) -> Net:
    """Knoten i bekommt die Nummer perm[i] (Umnummerieren, gleiche Struktur)."""
    pairs = [(perm[u], perm[v]) for u, v, _ in net.edges]
    ws = [w for _, _, w in net.edges]
    sides = None if net.sides is None else [net.sides[perm.index(j)] for j in range(net.n)]
    return make_net(net.n, pairs, ws, sides)


def scaled(net: Net, factor: int) -> Net:
    return make_net(net.n, [(u, v) for u, v, _ in net.edges], [w * factor for _, _, w in net.edges], net.sides, net.labels)


def with_leaf(net: Net, u: int) -> Net:
    """Ein neuer Blattknoten an u mit Kantenwert 1 (eine Alternative mehr für u); bei zweiseitigen Netzen auf der Gegenseite."""
    pairs = [(a, b) for a, b, _ in net.edges] + [(u, net.n)]
    ws = [w for _, _, w in net.edges] + [1]
    sides = None if net.sides is None else list(net.sides) + [1 - net.sides[u]]
    return make_net(net.n + 1, pairs, ws, sides)


# --- Handnetze ---------------------------------------------------------------------------------------------------------------------------------------
def path(n: int) -> Net:
    return make_net(n, [(i, i + 1) for i in range(n - 1)], sides=[i % 2 for i in range(n)])


def cycle(n: int) -> Net:
    sides = [i % 2 for i in range(n)] if n % 2 == 0 else None
    return make_net(n, [(i, (i + 1) % n) for i in range(n)], sides=sides)


def star(leaves: int) -> Net:
    return make_net(leaves + 1, [(0, i) for i in range(1, leaves + 1)], sides=[0] + [1] * leaves)


def spider(n: int) -> Net:
    """Mitte 0 und drei Beine, die zusammen n - 1 Knoten haben und sich um höchstens einen Knoten in der Länge unterscheiden (n >= 4)."""
    rest = n - 1
    lens = [rest // 3 + (1 if i < rest % 3 else 0) for i in range(3)]
    pairs, node = [], 1
    for ln in lens:
        prev = 0
        for _ in range(ln):
            pairs.append((prev, node))
            prev = node
            node += 1
    return make_net(n, pairs)


def complete_bipartite(a: int, b: int) -> Net:
    """a Verlader (Knoten 0 .. a-1) und b Spediteure (Knoten a .. a+b-1), jeder mit jedem."""
    pairs = [(i, a + j) for i in range(a) for j in range(b)]
    return make_net(a + b, pairs, sides=[0] * a + [1] * b)


def literature_example() -> Net:
    """Weg mit den Kantenwerten 8, 6, 2 (Beispiel aus der Literatur, Bayati u. a.): ausgewogen (3/2, 13/2, 1, 1)."""
    return make_net(4, [(0, 1), (1, 2), (2, 3)], [8, 6, 2], sides=[0, 1, 0, 1])


def triangle_with_tail() -> Net:
    """Dreieck 0-1-2 mit Anhang 3 an Knoten 0; ausgewogen (3/4, 1/2, 1/2, 1/4)."""
    return make_net(4, [(0, 1), (1, 2), (0, 2), (0, 3)])


# --- Zufall ------------------------------------------------------------------------------------------------------------------------------------------
def stream(seed: int, cell: int) -> SplitMix64:
    """Eigener Zufallsstrom je (Zufalls-Seed, Zelle). Reine Ganzzahl-Arithmetik, auf jeder Plattform gleich."""
    return SplitMix64(int(seed) * 1_000_003 + int(cell))


def rand_below(rng: SplitMix64, k: int) -> int:
    return int(rng.uniform() * k)


def _compress(n, pairs, weights, sides):
    """Knoten ohne Kante entfernen und neu nummerieren."""
    used = sorted({x for p in pairs for x in p})
    idx = {v: i for i, v in enumerate(used)}
    return make_net(len(used), [(idx[u], idx[v]) for u, v in pairs], weights, None if sides is None else [sides[v] for v in used])


def _top_up(candidates, chosen, rng, minimum):
    """Fehlen Kanten (weniger als `minimum`), kommen zufällige noch nicht gewählte Paare dazu."""
    pool = [c for c in candidates if c not in set(chosen)]
    while len(chosen) < min(minimum, len(chosen) + len(pool)):
        chosen.append(pool.pop(rand_below(rng, len(pool))))
    return chosen


def random_bipartite(a: int, b: int, p: float, rng: SplitMix64, max_weight: int = 1) -> Net:
    """a Verlader, b Spediteure; jede der a·b Kanten mit Wahrscheinlichkeit p; Knoten ohne Kante entfallen; mindestens MIN_EDGES Kanten."""
    cand = [(i, a + j) for i in range(a) for j in range(b)]
    chosen = [c for c in cand if rng.uniform() < p]
    chosen = _top_up(cand, chosen, rng, MIN_EDGES)
    chosen.sort()
    weights = [1 + rand_below(rng, max_weight) for _ in chosen] if max_weight > 1 else None
    return _compress(a + b, chosen, weights, [0] * a + [1] * b)


def random_general(n: int, p: float, rng: SplitMix64) -> Net:
    """Jede der n(n-1)/2 Kanten mit Wahrscheinlichkeit p; Knoten ohne Kante entfallen; mindestens MIN_EDGES Kanten."""
    cand = [(i, j) for i in range(n) for j in range(i + 1, n)]
    chosen = [c for c in cand if rng.uniform() < p]
    chosen = _top_up(cand, chosen, rng, MIN_EDGES)
    chosen.sort()
    return _compress(n, chosen, None, None)


def random_tree(n: int, rng: SplitMix64) -> Net:
    """Gleichverteilter Baum auf n nummerierten Knoten (Prüfer-Folge)."""
    if n == 2:
        return make_net(2, [(0, 1)])
    seq = [rand_below(rng, n) for _ in range(n - 2)]
    degree = [1] * n
    for x in seq:
        degree[x] += 1
    pairs = []
    for x in seq:
        leaf = min(i for i in range(n) if degree[i] == 1)
        pairs.append((leaf, x))
        degree[leaf] -= 1
        degree[x] -= 1
    last = [i for i in range(n) if degree[i] == 1]
    pairs.append((last[0], last[1]))
    return make_net(n, pairs, sides=two_colouring(make_net(n, pairs)))


# --- Eigene Kantenlisten -----------------------------------------------------------------------------------------------------------------------------
MAX_CUSTOM_NODES = 60


def parse_edges(text: str):
    """Kantenliste wie "0-1, 1-2:3, 2-3" (Wert nach dem Doppelpunkt, sonst 1). Rückgabe (Netz, None) oder (None, Fehlermeldung). Knotennamen sind ganze Zahlen."""
    tokens = [t.strip() for t in text.replace(";", ",").replace("\n", ",").split(",") if t.strip()]
    if not tokens:
        return None, "Die Kantenliste ist leer."
    pairs, weights = [], []
    for t in tokens:
        body, _, wtxt = t.partition(":")
        a, sep, b = body.partition("-")
        try:
            if not sep:
                raise ValueError
            u, v = int(a), int(b)
            w = int(wtxt) if wtxt.strip() else 1
        except ValueError:
            return None, f"„{t}“ ist keine Kante der Form 0-1 oder 0-1:3."
        pairs.append((u, v))
        weights.append(w)
    names = sorted({x for p in pairs for x in p})
    if len(names) > MAX_CUSTOM_NODES:
        return None, f"Höchstens {MAX_CUSTOM_NODES} Knoten."
    idx = {v: i for i, v in enumerate(names)}
    try:
        net = make_net(len(names), [(idx[u], idx[v]) for u, v in pairs], weights, labels=[str(v) for v in names])
    except ValueError as e:
        return None, str(e)
    col = two_colouring(net)
    if col is not None:
        net = Net(net.n, net.edges, col, net.labels)
    return net, None


# --- Zentralität -------------------------------------------------------------------------------------------------------------------------------------
def betweenness(net: Net) -> list:
    """Zwischenzentralität (Brandes), ungewichtet, nicht normiert: Summe über Knotenpaare des Anteils kürzester Wege durch den Knoten."""
    adj = adjacency(net)
    n = net.n
    cb = [0.0] * n
    for s in range(n):
        stack, pred = [], [[] for _ in range(n)]
        sigma = [0] * n
        sigma[s] = 1
        dist = [-1] * n
        dist[s] = 0
        queue = deque([s])
        while queue:
            u = queue.popleft()
            stack.append(u)
            for k in adj[u]:
                if dist[k] < 0:
                    dist[k] = dist[u] + 1
                    queue.append(k)
                if dist[k] == dist[u] + 1:
                    sigma[k] += sigma[u]
                    pred[k].append(u)
        delta = [0.0] * n
        while stack:
            k = stack.pop()
            for u in pred[k]:
                delta[u] += sigma[u] / sigma[k] * (1 + delta[k])
            if k != s:
                cb[k] += delta[k]
    return [c / 2 for c in cb]


def pearson(x, y):
    """Korrelation nach Pearson; None, wenn eine Reihe konstant ist."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(x) < 2 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])
