"""Ausgewogene Ergebnisse: auf jeder Tauschkante teilen die beiden den Überschuss über ihren Außenoptionen gleich (Nash-Lösung mit Drohpunkt).

Außenoption von u gegenüber seinem Partner v: a_u = max(0, max über Nachbarn k != v von (w_uk - y_k)), die Auszahlung des Nachbarn bleibt fest.
Ausgewogen: stabil, und y_u - a_u = y_v - a_v auf jeder Matching-Kante. Verfahren: Kantenausgleich (Dynamik nach Bayati u. a.) mit Prüfer; wo die Dynamik von
Null keine Auszahlung eines Matchings liefert, die Reduktion (Knoten mit leerer stabiler Spanne entfernen, Dynamik auf dem Rest)."""

from dataclasses import dataclass

import numpy as np

from aun_matching import max_weight_matching
from aun_net import Net, adjacency, subnet
from aun_stable import TOL, fixed_nodes, is_stable, lp_gap, stable_range

MAX_ITER = 100000            # Obergrenze der Schritte; die Dynamik bricht ab, wenn die größte Änderung unter DYN_TOL liegt
DYN_TOL = 1e-13
CANDIDATE_LIMIT = 500        # so viele Matchings aus straffen Kanten werden höchstens durchprobiert
CANDIDATE_BUDGET = 50000     # und so viele Aufzählungsschritte höchstens


# --- Prüfer ------------------------------------------------------------------------------------------------------------------------------------------
def outside_option(adj, y, u, partner):
    """Außenoption von u gegenüber `partner`: der beste Nachbar außer dem Partner, dessen Auszahlung fest bleibt; nie unter 0 (Nichttausch)."""
    best = 0
    for k, w in adj[u].items():
        if k != partner and w - y[k] > best:
            best = w - y[k]
    return best


def is_balanced(net: Net, matching, y, tol=TOL) -> bool:
    """Prüfer in der Definition. Mit Brüchen und tol = 0 exakt."""
    if not is_stable(net, matching, y, tol):
        return False
    adj = adjacency(net)
    for u, v, _ in matching:
        if abs((y[u] - outside_option(adj, y, u, v)) - (y[v] - outside_option(adj, y, v, u))) > tol:
            return False
    return True


# --- Kantenausgleich ---------------------------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Structure:
    """Gerichtete Kanten e = (i -> j) in der Reihenfolge: erst alle (u, v), dann alle (v, u). Index E ist die Nullstelle (kein Angebot)."""
    n: int
    E: int
    w: np.ndarray            # Kantenwert je gerichtete Kante
    rev: np.ndarray          # Index der Gegenkante
    cand: np.ndarray         # cand[e = (i -> j)]: Angebote AN i von allen Nachbarn außer j (Indizes gerichteter Kanten)
    cand_all: np.ndarray     # cand_all[i]: Angebote an i von allen Nachbarn


def dyn_structure(net: Net, weights=None) -> Structure:
    """Gerichtete Kanten und Nachbarschaftstabellen; `weights` (je Kante der Liste net.edges) ersetzt die Kantenwerte (gestörte Werte, siehe aun_principle)."""
    m = len(net.edges)
    de = [(u, v) for u, v, _ in net.edges] + [(v, u) for u, v, _ in net.edges]
    ix = {e: k for k, e in enumerate(de)}
    E = 2 * m
    w = np.array(([wt for _, _, wt in net.edges] if weights is None else list(weights)) * 2, dtype=float)
    rev = np.array([ix[(v, u)] for u, v in de], dtype=int) if m else np.zeros(0, dtype=int)
    adj = adjacency(net)
    maxdeg = max((len(a) for a in adj), default=1)
    cand = np.full((E, max(maxdeg - 1, 1)), E, dtype=int)
    for k, (i, j) in enumerate(de):
        c = [ix[(kk, i)] for kk in adj[i] if kk != j]
        cand[k, :len(c)] = c
    cand_all = np.full((net.n, max(maxdeg, 1)), E, dtype=int)
    for i in range(net.n):
        c = [ix[(kk, i)] for kk in adj[i]]
        cand_all[i, :len(c)] = c
    return Structure(net.n, E, w, rev, cand, cand_all)


def edge_offers(w, a, rev, rule="nash"):
    """Angebot m_{i->j} an j auf der gerichteten Kante e = (i -> j): a[e] = a_{i\\j}, a[rev[e]] = a_{j\\i}.
    Nash mit Drohpunkt (Bayati u. a.): (w - a_i)^+ - 1/2 (w - a_i - a_j)^+.
    Ausstiegsprinzip (eigene Variante ohne Quelle): j bekommt min(max(w/2, a_j), w - a_i), wenn der Überschuss nicht negativ ist."""
    ai, aj = a, a[rev]
    if rule == "nash":
        return np.maximum(w - ai, 0) - 0.5 * np.maximum(w - ai - aj, 0)
    s = w - ai - aj
    clip = np.minimum(np.maximum(w / 2, aj), w - ai)
    return np.where(s >= 0, clip, np.maximum(w - ai, 0))


def balancing_step(st: Structure, a, kappa, rule="nash"):
    """Ein Schritt des Kantenausgleichs: a_{i\\j} <- (1 - kappa) a_{i\\j} + kappa max_{k != j} m_{k->i}."""
    m = edge_offers(st.w, a, st.rev, rule)
    mx = np.concatenate([m, np.zeros(1)])
    return (1 - kappa) * a + kappa * mx[st.cand].max(axis=1)


def payoffs(st: Structure, a, rule="nash"):
    """Auszahlung y_i = größtes Angebot an i."""
    m = edge_offers(st.w, a, st.rev, rule)
    mx = np.concatenate([m, np.zeros(1)])
    return mx[st.cand_all].max(axis=1)


@dataclass(frozen=True)
class DynResult:
    y: np.ndarray
    a: np.ndarray
    iterations: int
    converged: bool
    trace: np.ndarray | None = None      # Auszahlungen nach 0, 1, 2, ... Schritten (nur wenn verlangt)


def run_dynamics(st: Structure, kappa=0.5, a0=None, rule="nash", tol=DYN_TOL, max_iter=MAX_ITER, trace_steps=0) -> DynResult:
    """Kantenausgleich bis die größte Änderung unter `tol` liegt (oder max_iter Schritte). `trace_steps` > 0 hält die Auszahlungen der ersten Schritte fest."""
    a = np.zeros(st.E) if a0 is None else np.array(a0, dtype=float)
    rows = [payoffs(st, a, rule)] if trace_steps else None
    converged = st.E == 0
    it = 0
    while not converged and it < max_iter:
        new = balancing_step(st, a, kappa, rule)
        it += 1
        converged = float(np.max(np.abs(new - a))) < tol
        a = new
        if rows is not None and it <= trace_steps:
            rows.append(payoffs(st, a, rule))
    y = payoffs(st, a, rule)
    y = np.where(np.abs(y) < 1e-10, 0.0, y)
    return DynResult(y, a, it, converged, None if rows is None else np.array(rows))


# --- Matching zur Auszahlung ---------------------------------------------------------------------------------------------------------------------------
def tight_edges(net: Net, y, tol=1e-6):
    return tuple(e for e in net.edges if abs(y[e[0]] + y[e[1]] - e[2]) <= tol)


def candidate_matchings(net: Net, y, tol=1e-6, limit=CANDIDATE_LIMIT):
    """Matchings aus straffen Kanten (y_u + y_v = w), die alle Knoten mit y > 0 überdecken (Aufzählung, höchstens `limit`)."""
    pos = [i for i in range(net.n) if y[i] > tol]
    tight = [[] for _ in range(net.n)]
    for u, v, w in tight_edges(net, y, tol):
        tight[u].append((v, w))
        tight[v].append((u, w))
    out = []
    budget = [CANDIDATE_BUDGET]

    def rec(used, chosen):
        budget[0] -= 1
        if len(out) >= limit or budget[0] < 0:
            return
        todo = [i for i in pos if i not in used]
        if not todo:
            out.append(tuple(chosen))
            return
        i = todo[0]
        for k, w in tight[i]:
            if k not in used:
                rec(used | {i, k}, chosen + [(min(i, k), max(i, k), w)])

    rec(frozenset(), [])
    return out


def balanced_matching(net: Net, y, tol=1e-6, check_tol=TOL, check=None):
    """Ein Matching, das mit y ein ausgewogenes Ergebnis bildet (Prüfer `check`, Standard `is_balanced`), oder None. Zuerst das größte Matching aus den straffen Kanten (ein ganzzahliges Programm),
    dann die Aufzählung aller überdeckenden Matchings."""
    check = is_balanced if check is None else check
    tight = tight_edges(net, y, tol)
    weight, chosen = max_weight_matching(net, tight)
    covered = {x for u, v, _ in chosen for x in (u, v)}
    if not all(y[i] <= tol or i in covered for i in range(net.n)):
        return None          # das größte Matching aus straffen Kanten überdeckt nicht alle Knoten mit y > 0: dann tut es keines
    if check(net, chosen, y, check_tol):
        return chosen
    for m in candidate_matchings(net, y, tol):
        if check(net, m, y, check_tol):
            return m
    return None


# --- Ergebnis suchen -------------------------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Outcome:
    """status: "ok" (ausgewogenes Ergebnis vom Prüfer bestätigt), "no_stable" (kein stabiles, damit nach Kleinberg/Tardos auch kein ausgewogenes Ergebnis),
    "not_found" (stabil existiert, die Verfahren fanden nichts)."""
    status: str
    y: tuple | None
    matching: tuple
    method: str
    iterations: int
    converged: bool
    d0_found: bool
    note: str = ""


def by_dynamics(net: Net, st: Structure, kappa=0.5, a0=None, max_iter=MAX_ITER):
    """Dynamik (von Null oder von a0) plus Prüfer. Rückgabe (y, Matching, Schritte, konvergiert); y und Matching sind None, wenn nichts Ausgewogenes herauskommt."""
    res = run_dynamics(st, kappa, a0, max_iter=max_iter)
    if not res.converged:
        return None, None, res.iterations, False
    m = balanced_matching(net, res.y)
    if m is None:
        return None, None, res.iterations, True
    return res.y, m, res.iterations, True


def by_reduction(net: Net, rg, kappa=0.5, max_iter=MAX_ITER):
    """Reduktion: Knoten mit festgelegter Auszahlung entfernen, Dynamik nur auf dem freien Teilnetz, Prüfer am ganzen Netz. Rückgabe (y, Matching, Grund):
    Grund ist "" bei Erfolg, sonst warum nichts herauskam. Zulässig nur, wenn kein fester Knoten einem freien eine Außenoption bietet (w - Auszahlung > 0)."""
    lo, hi = rg
    fixed = fixed_nodes(lo, hi)
    for u, v, w in net.edges:
        if (u in fixed) != (v in fixed):
            k = u if u in fixed else v
            if w - fixed[k] > TOL:
                return None, None, "ein fester Knoten bietet einem freien eine Außenoption"
    y = np.array([fixed.get(i, 0.0) for i in range(net.n)])
    free = [i for i in range(net.n) if i not in fixed]
    if free:
        sub = subnet(net, free)
        res = run_dynamics(dyn_structure(sub), kappa, max_iter=max_iter)
        if not res.converged:
            return None, None, "Dynamik auf dem freien Teilnetz konvergiert nicht"
        for pos, i in enumerate(free):
            y[i] = res.y[pos]
    m = balanced_matching(net, y)
    if m is None:
        return None, None, "kein Matching passt zur Auszahlung"
    return y, m, ""


def balanced_outcome(net: Net, kappa=0.5, rg=None, max_iter=MAX_ITER) -> Outcome:
    """Das zuerst gefundene ausgewogene Ergebnis: Dynamik von Null, sonst Reduktion. Bei Mehrdeutigkeit ist das eine Auswahlregel, nicht das Ergebnis."""
    if not net.edges:
        return Outcome("ok", (0.0,) * net.n, (), "kein Tausch möglich", 0, True, True)
    lp, ip = lp_gap(net)
    if lp - ip >= TOL:
        return Outcome("no_stable", None, (), "", 0, True, False, f"Das LP-Matching ({lp:.4g}) ist größer als das ganzzahlige ({ip}): kein stabiles Ergebnis.")
    st = dyn_structure(net)
    y, m, it, conv = by_dynamics(net, st, kappa, max_iter=max_iter)
    if y is not None:
        return Outcome("ok", tuple(float(x) for x in y), m, "Dynamik von Null", it, conv, True)
    if rg is None:
        rg = stable_range(net, ip)
    y, m, why = by_reduction(net, rg, kappa, max_iter)
    if y is not None:
        return Outcome("ok", tuple(float(x) for x in y), m, "Reduktion", it, conv, False)
    return Outcome("not_found", None, (), "", it, conv, False, why)
