"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben.
Kantenbeschriftungen sind Annotationen mit Hintergrund, keine Text-Spuren (DEMO-PLAYBOOK §3)."""

import math

import numpy as np
import plotly.graph_objects as go

import aun_constants as C
import aun_net as N

NETWORK_HEIGHT = 420
PATH_HEIGHT = 240           # Wege liegen auf einer Linie und brauchen wenig Höhe
LABEL_LIMIT = 36            # bis zu so vielen Betrieben werden Auszahlungen in die Knoten geschrieben


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def positions(net, kind):
    """Koordinaten je Knoten: Weg auf einer Linie, Bäume (Stern, Spinne, Zufallsbaum) strahlenförmig, zweiseitige Netze in zwei Spalten, sonst auf dem Kreis."""
    n = net.n
    if kind == "path":
        return [(float(i), 0.0) for i in range(n)]
    if kind in ("star", "spider", "rand_tree"):
        adj = N.adjacency(net)
        deg = N.degrees(net)
        root = max(range(n), key=lambda i: (deg[i], -i))
        depth, order, seen = {root: 0}, [root], {root}
        for u in order:
            for k in sorted(adj[u]):
                if k not in seen:
                    seen.add(k)
                    depth[k] = depth[u] + 1
                    order.append(k)
        for i in range(n):                          # nicht zusammenhängende Reste
            if i not in seen:
                depth[i] = 1
                order.append(i)
        pos = {root: (0.0, 0.0)}
        by_depth = {}
        for v in order:
            by_depth.setdefault(depth[v], []).append(v)
        for d, nodes in by_depth.items():
            if d == 0:
                continue
            for j, v in enumerate(nodes):
                ang = 2 * math.pi * (j + 0.5) / len(nodes)
                pos[v] = (d * math.cos(ang), d * math.sin(ang))
        return [pos[i] for i in range(n)]
    if kind not in ("cycle", "rand_gen") and net.sides is not None:
        cols = {0: [], 1: []}
        for i in range(n):
            cols[net.sides[i]].append(i)
        pos = {}
        for side, nodes in cols.items():
            for j, v in enumerate(nodes):
                pos[v] = (float(side), (len(nodes) - 1) / 2 - j)
        return [pos[i] for i in range(n)]
    return [(math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n)) for i in range(n)]


def build_network(view, kind):
    """Netz mit Tauschpaaren (dick) und den übrigen möglichen Touren (dünn); Farbe und Beschriftung der Knoten: ausgewogene Auszahlung."""
    net = view.net
    pos = positions(net, kind)
    matched = {(u, v) for u, v, _ in view.outcome.matching} if view.ok else set()
    fig = go.Figure()
    xs, ys = [], []
    mx, my = [], []
    for u, v, _ in net.edges:
        lx, ly = (mx, my) if (u, v) in matched else (xs, ys)
        lx.extend([pos[u][0], pos[v][0], None])
        ly.extend([pos[u][1], pos[v][1], None])
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_EDGE, width=1.5), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=mx, y=my, mode="lines", line=dict(color=C.COLOR_MATCH, width=5), hoverinfo="skip", name="Tauschpaar"))
    if any(w != 1 for _, _, w in net.edges) and len(net.edges) <= 60:
        for u, v, w in net.edges:
            fig.add_annotation(x=(pos[u][0] + pos[v][0]) / 2, y=(pos[u][1] + pos[v][1]) / 2, text=str(w), showarrow=False, bgcolor="rgba(255,255,255,0.88)", font=dict(size=11, color="#333"))
    top = max([w for _, _, w in net.edges] + [1])
    ids = list(range(net.n))
    if view.ok:
        yv = [view.y(i) for i in ids]
        text = [(_short(view.y(i), view.yx(i)) if net.n <= LABEL_LIMIT else "") for i in ids]
    else:
        yv = [0.0] * net.n
        text = [""] * net.n
    hover = []
    for i in ids:
        h = f"{net.label(i)} ({net.role(i)}), Grad {view.deg[i]}"
        if view.stable:
            h += f"<br>stabile Spanne [{view.lo[i]:.3f}; {view.hi[i]:.3f}]"
        if view.ok:
            h += f"<br>Auszahlung {view.y(i):.3f}, Außenoption {view.outside[i]:.3f}"
        hover.append(h)
    fig.add_trace(go.Scatter(x=[p[0] for p in pos], y=[p[1] for p in pos], mode="markers+text", text=text, textposition="middle center", hovertext=hover, hoverinfo="text", showlegend=False,
                             marker=dict(size=34 if net.n <= LABEL_LIMIT else 14, color=yv, cmin=0, cmax=top, colorscale="Teal", line=dict(color="#333", width=1),
                                         colorbar=dict(title="Auszahlung", thickness=12, len=0.8)),
                             textfont=dict(size=11, color="#111")))
    for i in ids:
        if net.n <= LABEL_LIMIT:
            fig.add_annotation(x=pos[i][0], y=pos[i][1], text=net.label(i), showarrow=False, yshift=-26, font=dict(size=10, color="#555"))
    fig.update_layout(height=PATH_HEIGHT if kind == "path" else NETWORK_HEIGHT, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
    fig.update_xaxes(visible=False, fixedrange=True, scaleanchor=None)
    fig.update_yaxes(visible=False, fixedrange=True)
    return fig


def _short(y, exact):
    if exact is not None:
        return str(exact.numerator) if exact.denominator == 1 else f"{exact.numerator}/{exact.denominator}"
    return f"{y:.2f}".replace(".", ",")


def build_ranges(view):
    """Stabile Spanne je Betrieb (Balken von lo bis hi) und die ausgewogene Auszahlung (Raute)."""
    net = view.net
    labels = [net.label(i) for i in range(net.n)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=[view.hi[i] - view.lo[i] for i in range(net.n)], base=list(view.lo), marker_color=C.COLOR_RANGE, name="stabile Spanne",
                         hovertext=[f"{labels[i]}: [{view.lo[i]:.3f}; {view.hi[i]:.3f}]" for i in range(net.n)], hoverinfo="text"))
    if view.ok:
        fig.add_trace(go.Scatter(x=labels, y=[view.y(i) for i in range(net.n)], mode="markers", marker=dict(symbol="diamond", size=11, color=C.COLOR_HIGH, line=dict(width=1, color="#222")),
                                 name="ausgewogen", hovertemplate="%{x}: %{y:.3f}<extra>ausgewogen</extra>"))
    top = max([w for _, _, w in net.edges] + [1])
    fig.update_yaxes(title_text="Auszahlung", range=[-0.05 * top, 1.05 * top])
    return _base(fig)


def build_trace(dv, labels):
    """Auszahlungen über den Schritten des Kantenausgleichs (die ersten Schritte; bis zu zwölf Betriebe als Linien)."""
    tr = dv.trace
    steps = list(range(len(tr)))
    n = tr.shape[1]
    cols = list(range(n)) if n <= 12 else sorted(range(n), key=lambda i: -float(np.ptp(tr[:, i])))[:12]
    fig = go.Figure()
    for i in sorted(cols):
        fig.add_trace(go.Scatter(x=steps, y=tr[:, i], mode="lines", name=labels[i], line=dict(width=2)))
    fig.update_xaxes(title_text="Schritt")
    fig.update_yaxes(title_text="Auszahlung nach t Schritten")
    return _base(fig)


def build_power(sc):
    """Auszahlung gegen Grad und gegen Zwischenzentralität je Betrieb."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sc["deg"], y=sc["y"], mode="markers", text=sc["labels"], marker=dict(size=10, color=C.COLOR_LOW), name="gegen Grad",
                             hovertemplate="%{text}: Grad %{x}, Auszahlung %{y:.3f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=sc["bet"], y=sc["y"], mode="markers", text=sc["labels"], marker=dict(size=10, symbol="diamond", color=C.COLOR_LOADER), name="gegen Zwischenzentralität", xaxis="x2",
                             hovertemplate="%{text}: Zwischenzentralität %{x:.2f}, Auszahlung %{y:.3f}<extra></extra>"))
    fig.update_layout(xaxis=dict(title="Grad", domain=[0, 0.47]), xaxis2=dict(title="Zwischenzentralität", domain=[0.53, 1.0], anchor="y", fixedrange=True))
    fig.update_yaxes(title_text="Auszahlung")
    return _base(fig)


def build_share(share_rows, ns, ps):
    """Anteil der Zufallsnetze mit stabilem Ergebnis über der Kantenwahrscheinlichkeit, Mittel ± Standardabweichung über vier Zufalls-Seeds."""
    fig = go.Figure()
    for n in ns:
        rows = [share_rows[f"{n}:{p}"] for p in ps]
        fig.add_trace(go.Scatter(x=list(ps), y=[r["percent"]["mean"] for r in rows], mode="lines+markers", name=f"{n} Knoten",
                                 error_y=dict(type="data", array=[r["percent"]["sd"] for r in rows], visible=True)))
    fig.update_xaxes(title_text="Kantenwahrscheinlichkeit p (%)")
    fig.update_yaxes(title_text="Anteil mit stabilem Ergebnis (%)", range=[60, 102])
    return _base(fig)


def build_growth(growth, sides):
    """Schritte der Dynamik von Null über der Netzgröße (Median und Maximum), beide Achsen logarithmisch."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[2 * s for s in sides], y=[growth[str(s)]["median"] for s in sides], mode="lines+markers", name="Median"))
    fig.add_trace(go.Scatter(x=[2 * s for s in sides], y=[growth[str(s)]["maximum"] for s in sides], mode="lines+markers", name="Maximum"))
    fig.update_xaxes(title_text="Betriebe (n + n)", type="log")
    fig.update_yaxes(title_text="Schritte", type="log")
    return _base(fig)


def build_node_values(labels, series: dict, ylabel="Auszahlung"):
    """Balken je Betrieb für mehrere Verfahren (Nukleolus, Shapley, ausgewogen)."""
    fig = go.Figure()
    colours = [C.COLOR_HIGH, C.COLOR_LOW, C.COLOR_LOADER, C.COLOR_WARN]
    for k, (name, vals) in enumerate(series.items()):
        fig.add_trace(go.Bar(x=labels, y=[None if v is None else float(v) for v in vals], name=name, marker_color=colours[k % len(colours)]))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text=ylabel)
    return _base(fig)
