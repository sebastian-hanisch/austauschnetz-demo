"""Atlas aller zusammenhängenden Graphen mit 2 bis 6 Knoten (bis auf Umnummerieren) aus data/atlas_graphs.json, als Netze mit Einheitswert."""

import json
from pathlib import Path

from aun_net import Net, make_net, two_colouring

ATLAS_FILE = Path(__file__).resolve().parent / "data" / "atlas_graphs.json"


def load_atlas() -> list:
    """Alle Graphen der Datei als Netze (Einheitswert; zweiseitige mit Seiten)."""
    data = json.loads(ATLAS_FILE.read_text(encoding="utf-8"))
    nets = []
    for g in data["graphs"]:
        net = make_net(g["n"], [tuple(e) for e in g["edges"]])
        col = two_colouring(net)
        nets.append(net if col is None else Net(net.n, net.edges, col))
    return nets
