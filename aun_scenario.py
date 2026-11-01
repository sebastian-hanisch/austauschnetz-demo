"""Szenario: Einstellungen der Seitenleiste und das daraus gebaute Netz (Verlader und Spediteure, eine Kante = eine mögliche Tour mit Überschuss w)."""

from dataclasses import dataclass

import aun_constants as C
import aun_net as N

CELL_NET = 1          # Zelle des Zufallsstroms für das Netz der Seitenleiste


@dataclass(frozen=True)
class Settings:
    net: str = C.DEFAULT_NET
    n: int = C.DEFAULT_N
    p: int = C.DEFAULT_P
    kappa: float = C.DEFAULT_KAPPA
    seed: int = C.DEFAULT_SEED
    edges: str = C.DEFAULT_EDGES


def build_net(s: Settings):
    """Das Netz der Einstellungen. Rückgabe (Netz, None) oder (None, Fehlermeldung) bei einer ungültigen eigenen Kantenliste."""
    kind, n = s.net, s.n
    if kind == "path":
        return N.path(n), None
    if kind == "cycle":
        return N.cycle(n), None
    if kind == "star":
        return N.star(n - 1), None
    if kind == "spider":
        return N.spider(n), None
    if kind == "bipartite":
        return N.complete_bipartite(n // 2, n - n // 2), None
    if kind == "rand_bip":
        return N.random_bipartite(n // 2, n - n // 2, s.p / 100, N.stream(s.seed, CELL_NET)), None
    if kind == "rand_tree":
        return N.random_tree(n, N.stream(s.seed, CELL_NET)), None
    if kind == "rand_gen":
        return N.random_general(n, s.p / 100, N.stream(s.seed, CELL_NET)), None
    if kind == "literature":
        return N.literature_example(), None
    return N.parse_edges(s.edges[: C.EDGES_MAX_CHARS])
