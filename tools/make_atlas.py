"""Schreibt data/atlas_graphs.json: alle zusammenhängenden Graphen mit 2 bis 6 Knoten (bis auf Umnummerieren), 142 Stück, aus dem Graphen-Atlas von networkx.

Aufruf (im Demo-Ordner, mit dem Test-venv, networkx nötig):  python tools/make_atlas.py
Die App selbst braucht networkx nicht: sie liest nur die Datei. tests/test_atlas.py prüft Zahl, Zusammenhang und Paarweise-Verschiedenheit mit eigenem Code."""

import json
from pathlib import Path

import networkx as nx

OUT = Path(__file__).resolve().parent.parent / "data" / "atlas_graphs.json"


def main():
    graphs = []
    for g in nx.graph_atlas_g():
        if 2 <= g.number_of_nodes() <= 6 and nx.is_connected(g):
            graphs.append({"n": g.number_of_nodes(), "edges": sorted([min(u, v), max(u, v)] for u, v in g.edges)})
    graphs.sort(key=lambda d: (d["n"], len(d["edges"]), d["edges"]))
    lines = ",\n".join(" " + json.dumps(g, separators=(",", ":")) for g in graphs)
    OUT.write_text('{"graphs": [\n' + lines + "\n]}\n", encoding="utf-8")
    print(f"geschrieben: {OUT} ({len(graphs)} Graphen)")


if __name__ == "__main__":
    main()
