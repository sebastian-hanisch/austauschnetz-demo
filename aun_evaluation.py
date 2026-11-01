"""Kennzahlen, Ansichten und Verdikt-Logik. Jedes Verdikt ist eine reine Funktion `verdict_*(...) -> (Art, Text)`; die App ruft `getattr(st, Art)(Text)`.

Zahlen im Text kommen aus der Rechnung (f-Strings) oder aus den vorgerechneten Reihen (`data/tables.json`), nie hartcodiert."""

from dataclasses import dataclass
from fractions import Fraction

import numpy as np

import aun_balanced as B
import aun_constants as C
import aun_exact as X
import aun_game as G
import aun_multi as MU
import aun_net as N
import aun_principle as P
import aun_scenario as S
import aun_stable as ST
from aun_scenario import Settings

EXACT_MAX_N = 24            # bis zu so vielen Knoten wird das Ergebnis zusätzlich in Brüchen bestätigt
SAME = 1e-6
TABLE_NOTE = "Zählungen über vier Zufalls-Seeds"


def de(x, nd=2) -> str:
    """Zahl mit Dezimalkomma."""
    return f"{x:.{nd}f}".replace(".", ",")


_SUP = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def sci(x, nd=1) -> str:
    """Kleine Zahl in Zehnerpotenz-Schreibweise mit Dezimalkomma: 2,1·10⁻¹¹; null bleibt „0“."""
    if x == 0:
        return "0"
    mant, exp = f"{x:.{nd}e}".split("e")
    return f"{mant.replace('.', ',')}·10{str(int(exp)).translate(_SUP)}"


def val_text(x, exact=None) -> str:
    """Auszahlung als Bruch (wenn exakt bekannt), sonst als Dezimalzahl mit drei Stellen."""
    if exact is not None:
        return X.fraction_text(exact)
    return de(float(x), 3)


# --- Hauptansicht ------------------------------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class View:
    settings: Settings
    net: object
    error: str | None
    lp: float = 0.0
    ip: int = 0
    stable: bool = False
    lo: tuple = ()
    hi: tuple = ()
    fixed: tuple = ()               # Knoten mit leerer stabiler Spanne
    outcome: object = None
    exact: tuple | None = None      # Auszahlungen in Brüchen, wenn der exakte Prüfer bestanden hat
    partner: tuple = ()
    outside: tuple = ()             # Außenoption gegenüber dem Partner (bei Ungepaarten: beste Alternative überhaupt)
    deg: tuple = ()
    bet: tuple = ()

    @property
    def ok(self) -> bool:
        return self.outcome is not None and self.outcome.status == "ok"

    def y(self, i):
        return self.outcome.y[i]

    def yx(self, i):
        return None if self.exact is None else self.exact[i]


def analyse(settings: Settings) -> View:
    net, err = S.build_net(settings)
    if net is None:
        return View(settings, None, err)
    lp, ip = ST.lp_gap(net)
    stable = lp - ip < ST.TOL
    rg = ST.stable_range(net, ip) if stable else None
    out = B.balanced_outcome(net, settings.kappa, rg)
    lo, hi = (tuple(rg[0]), tuple(rg[1])) if rg else ((), ())
    fixed = tuple(sorted(ST.fixed_nodes(*rg))) if rg else ()
    exact = partner = outside = None
    adj = N.adjacency(net)
    if out.status == "ok":
        if net.n <= EXACT_MAX_N:
            ex = X.exact_balanced(net, out.matching, out.y)
            exact = None if ex is None else tuple(ex)
        pt = [-1] * net.n
        for u, v, _ in out.matching:
            pt[u], pt[v] = v, u
        partner = tuple(pt)
        outside = tuple(B.outside_option(adj, out.y, i, pt[i]) for i in range(net.n))
    return View(settings, net, None, lp, ip, stable, lo, hi, fixed, out, exact, partner or (), outside or (), tuple(N.degrees(net)), tuple(N.betweenness(net)))


def node_rows(view: View) -> list:
    rows = []
    for i in range(view.net.n):
        row = {"Knoten": view.net.label(i), "Rolle": view.net.role(i), "Grad": view.deg[i]}
        if view.stable:
            row["stabile Spanne"] = f"[{de(view.lo[i], 3)}; {de(view.hi[i], 3)}]"
            row["festgelegt"] = "ja" if i in view.fixed else "nein"
        if view.ok:
            row["Partner"] = view.net.label(view.partner[i]) if view.partner[i] >= 0 else "–"
            row["Auszahlung"] = val_text(view.y(i), view.yx(i))
            row["Auszahlung (dezimal)"] = de(view.y(i), 3)
            row["Außenoption"] = de(view.outside[i], 3)
        rows.append(row)
    return rows


def reversal_counts(view: View):
    """(Kanten mit ungleichem Grad, davon: der Betrieb mit dem höheren Grad bekommt weniger, bekommt gleich viel)."""
    deg = view.deg
    unequal = lower = same = 0
    for u, v, _ in view.outcome.matching:
        if deg[u] != deg[v]:
            unequal += 1
            hi, lo = (u, v) if deg[u] > deg[v] else (v, u)
            if view.y(hi) < view.y(lo) - SAME:
                lower += 1
            elif abs(view.y(hi) - view.y(lo)) <= SAME:
                same += 1
    return unequal, lower, same


def verdict_main(view: View):
    if view.error:
        return "error", f"Die Kantenliste ist ungültig: {view.error}"
    out = view.outcome
    if out.status == "no_stable":
        return "warning", (f"**Kein stabiles Ergebnis.** Das LP-Matching ist {de(view.lp, 2)} Euro groß, das ganzzahlige nur {view.ip}: wie auch verteilt wird, bleibt ein Paar, das lieber miteinander tauschte "
                           "(ein blockierendes Paar). Ein ausgewogenes Ergebnis ist per Definition stabil, also gibt es hier keines; die Demo zeigt keine Zahl, statt eine zu erfinden.")
    if out.status == "not_found":
        return "warning", (f"**Stabile Ergebnisse gibt es, aber weder die Dynamik von Null noch die Reduktion fand ein ausgewogenes Ergebnis** ({out.note or 'kein Grund gemeldet'}). "
                           "Das heißt nicht, dass keines existiert; die Suche ist unvollständig.")
    n = view.net.n
    nfix = len(view.fixed)
    order = sorted(range(n), key=lambda i: (-view.y(i), i))
    top, bottom = order[0], order[-1]
    text = (f"**Ausgewogenes Ergebnis** ({out.method}; vom Prüfer bestätigt{', in Brüchen exakt' if view.exact is not None else ''}). "
            f"{nfix} von {n} Betrieben sind schon durch die stabile Spanne festgelegt, {n - nfix} sind offen. "
            f"Die höchste Auszahlung hat {view.net.label(top)} ({val_text(view.y(top), view.yx(top))}), die niedrigste {view.net.label(bottom)} ({val_text(view.y(bottom), view.yx(bottom))}).")
    unequal, lower, _ = reversal_counts(view)
    if unequal:
        text += f" Auf {lower} von {unequal} Tauschkanten mit ungleichem Grad bekommt der Betrieb mit dem höheren Grad weniger."
    text += " Ob das Ergebnis die einzige Möglichkeit ist, zeigt Reiter 4."
    return "success", text


# --- Reiter 1: Wer hat Macht? ---------------------------------------------------------------------------------------------------------------------------------
def path_pattern_rows(max_nodes=14):
    """Wege mit 2 bis max_nodes Knoten, Einheitswert: ausgewogene Auszahlungen in Brüchen. Gerade Knotenzahl 2k: Randknoten 1/(k+1); ungerade: abwechselnd 0 und 1."""
    rows = []
    for n in range(2, max_nodes + 1):
        net = N.path(n)
        out = B.balanced_outcome(net)
        ex = X.exact_balanced(net, out.matching, out.y)
        rows.append({"n": n, "y": tuple(ex), "edge": ex[0], "second": ex[1]})
    return rows


def pattern_matches(rows) -> tuple:
    """(Wege mit gerader Knotenzahl 2k, deren Randknoten 1/(k+1) bekommt, Wege mit gerader Knotenzahl; Wege mit ungerader Knotenzahl, die abwechselnd 0 und 1 zeigen, Wege ungerader Zahl)."""
    even = [r for r in rows if r["n"] % 2 == 0]
    odd = [r for r in rows if r["n"] % 2 == 1]
    ok_even = sum(r["edge"] == Fraction(1, r["n"] // 2 + 1) and r["y"][-1] == r["edge"] for r in even)
    ok_odd = sum(all(r["y"][i] == (i % 2) for i in range(r["n"])) for r in odd)
    return ok_even, len(even), ok_odd, len(odd)


def verdict_pattern(rows):
    ok_even, n_even, ok_odd, n_odd = pattern_matches(rows)
    first, last = rows[0]["n"], rows[-1]["n"]
    return "info", (f"Wege mit {first} bis {last} Knoten (Einheitswert, exakt in Brüchen): bei gerader Knotenzahl 2k bekommt der Randknoten 1/(k+1) in {ok_even} von {n_even} Wegen, "
                    f"bei ungerader Knotenzahl zeigen {ok_odd} von {n_odd} Wegen abwechselnd 0 und 1, die Mitte eines Wegs mit 5 Knoten also 0. Das sind Zeilen aus der Rechnung, kein Beweis.")


def power_scatter_data(view: View):
    """(Grad, Zwischenzentralität, Auszahlung, Beschriftung) je Knoten und die Korrelationen der Auszahlung mit Grad und Zwischenzentralität."""
    y = [view.y(i) for i in range(view.net.n)]
    return {"deg": list(view.deg), "bet": list(view.bet), "y": y, "labels": [view.net.label(i) for i in range(view.net.n)],
            "corr_deg": N.pearson(view.deg, y), "corr_bet": N.pearson(view.bet, y)}


def verdict_power(view: View):
    if not view.ok:
        return "info", "Ohne ausgewogenes Ergebnis gibt es hier keine Auszahlung, die man mit dem Grad vergleichen könnte."
    d = power_scatter_data(view)
    unequal, lower, same = reversal_counts(view)
    rd = "nicht definiert (alle Grade gleich)" if d["corr_deg"] is None else de(d["corr_deg"], 2)
    rb = "nicht definiert (alle Werte gleich)" if d["corr_bet"] is None else de(d["corr_bet"], 2)
    text = f"In diesem Netz: Korrelation der Auszahlung mit dem Grad {rd}, mit der Zwischenzentralität {rb} ({view.net.n} Betriebe)."
    if unequal:
        text += f" Von {unequal} Tauschkanten mit ungleichem Grad bekommt der Betrieb mit dem höheren Grad auf {lower} weniger und auf {same} gleich viel."
    return "info", text


# --- Reiter 2: stabil und ausgewogen --------------------------------------------------------------------------------------------------------------------------
def existence_examples():
    """Kleine Netze: LP-Wert, ganzzahliger Wert, stabil?"""
    nets = [("Weg mit 4 Knoten", N.path(4)), ("Kreis mit 4 Knoten", N.cycle(4)), ("Kreis mit 6 Knoten", N.cycle(6)), ("Dreieck", N.cycle(3)), ("Kreis mit 5 Knoten", N.cycle(5)),
            ("Kreis mit 7 Knoten", N.cycle(7)), ("Vollständiges Netz mit 4 Knoten", N.make_net(4, [(i, j) for i in range(4) for j in range(i + 1, 4)])),
            ("Vollständiges Netz mit 5 Knoten", N.make_net(5, [(i, j) for i in range(5) for j in range(i + 1, 5)])), ("Zweiseitig 2 + 3", N.complete_bipartite(2, 3)),
            ("Dreieck mit Anhang", N.triangle_with_tail())]
    rows = []
    for name, net in nets:
        lp, ip = ST.lp_gap(net)
        rows.append({"Netz": name, "Knoten": net.n, "LP-Wert": de(lp, 2), "ganzzahlig": ip, "stabil": "ja" if lp - ip < ST.TOL else "nein"})
    return rows


def verdict_existence(view: View):
    if view.error:
        return "error", view.error
    if view.stable:
        word = "gleich" if abs(view.lp - view.ip) < ST.TOL else "ungleich"
        return "success", (f"LP-Wert {de(view.lp, 2)} und ganzzahliger Wert {view.ip} sind {word}: dieses Netz hat stabile Ergebnisse. Die stabile Spanne reicht für {len(view.fixed)} von {view.net.n} Betrieben "
                           f"auf einen einzigen Wert; die übrigen {view.net.n - len(view.fixed)} können je nach Auszahlung innerhalb der Spanne liegen.")
    return "warning", f"LP-Wert {de(view.lp, 2)} gegen ganzzahligen Wert {view.ip}: die LP-Relaxation ist größer, also gibt es kein stabiles und damit kein ausgewogenes Ergebnis."


# --- Reiter 3: Kantenausgleich ------------------------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class DynamicsView:
    rows: tuple                 # je κ: (κ, Schritte, konvergiert, Fixpunkt ist ausgewogen)
    max_difference: float       # größte Abweichung der Fixpunkte über die κ
    trace: object               # Auszahlungen der ersten Schritte für das κ der Seitenleiste
    kappa: float
    trace_steps: int
    d0_balanced: bool           # Fixpunkt von Null (κ der Seitenleiste) ist ein ausgewogenes Ergebnis
    d0_sum: float | None
    ip: int


TRACE_MAX = 120


def dynamics_view(settings: Settings, view: View) -> DynamicsView | None:
    net = view.net
    if net is None or not net.edges:
        return None
    st = B.dyn_structure(net)
    rows, ys = [], []
    for k in C.KAPPAS:
        res = B.run_dynamics(st, k)
        ys.append(res.y)
        rows.append((k, res.iterations, res.converged, bool(res.converged and B.balanced_matching(net, res.y) is not None)))
    res = B.run_dynamics(st, settings.kappa, trace_steps=TRACE_MAX)
    diff = float(max(np.max(np.abs(y - ys[0])) for y in ys))
    return DynamicsView(tuple(rows), diff, res.trace, settings.kappa, min(res.iterations, TRACE_MAX), bool(B.balanced_matching(net, res.y) is not None), float(np.sum(res.y)), view.ip)


def k23_example():
    """Zweiseitig 2 + 3: Dynamik von Null gegen Reduktion (Summe der Fixpunkt-Auszahlungen gegen das größte Matching)."""
    net = N.complete_bipartite(2, 3)
    st = B.dyn_structure(net)
    res = B.run_dynamics(st, 0.5)
    out = B.balanced_outcome(net)
    return {"net": net, "d0": tuple(float(x) for x in res.y), "d0_sum": float(np.sum(res.y)), "ip": ST.lp_gap(net)[1], "reduction": out.y, "method": out.method}


def verdict_dynamics(dv: DynamicsView):
    if dv is None:
        return "info", "Das Netz hat keine Kanten."
    conv = sum(1 for r in dv.rows if r[2])
    bal = sum(1 for r in dv.rows if r[3])
    kind = "success" if bal == len(dv.rows) else "warning"
    steps = ", ".join(f"{de(r[0], 2)}: {r[1]}" for r in dv.rows)
    text = (f"Schritte bis zur Änderung unter 10⁻¹³ (κ: Schritte): {steps}. Der Fixpunkt ist bei {conv} von {len(dv.rows)} Dämpfungen erreicht, "
            f"größte Abweichung der Fixpunkte über die Dämpfungen {sci(dv.max_difference)}. ")
    if bal == len(dv.rows):
        text += "Der Fixpunkt von Null ist hier ein ausgewogenes Ergebnis (Prüfer bestätigt)."
    else:
        text += (f"Der Fixpunkt von Null ist hier **kein** ausgewogenes Ergebnis: seine Auszahlungen summieren sich auf {de(dv.d0_sum, 3)}, das größte Matching hat Gewicht {dv.ip}, "
                 "also gehören sie zu keinem Matching. Die Reduktion (Reiter 3, Beispiel unten) umgeht das.")
    return kind, text


# --- Reiter 4: Mehrere Ergebnisse ---------------------------------------------------------------------------------------------------------------------------
def multi_view(settings: Settings, view: View):
    if not view.stable or view.net is None:
        return []
    return MU.distinct_outcomes(view.net, settings.seed, starts=5, kappa=settings.kappa, rg=(list(view.lo), list(view.hi)))


FAMILY_AS = (Fraction(0), Fraction(1, 5), Fraction(1, 3), Fraction(1, 2), Fraction(4, 5), Fraction(1))


def family_rows():
    """Kreis 4: (a, 1-a, a, 1-a) für sechs Werte von a, in Brüchen geprüft, dazu das Paar (a, 1-a, b, 1-b) mit a ungleich b."""
    rows = []
    for a in FAMILY_AS:
        net, m, y = MU.cycle4_family_member(a)
        rows.append({"a": X.fraction_text(a), "Ergebnis": ", ".join(X.fraction_text(v) for v in y), "ausgewogen (Brüche)": "ja" if B.is_balanced(net, m, y, 0) else "nein"})
    net, m, _ = MU.cycle4_family_member(Fraction(1, 5))
    y = [Fraction(1, 5), Fraction(4, 5), Fraction(1, 2), Fraction(1, 2)]
    rows.append({"a": "1/5 und 1/2 (nicht symmetrisch)", "Ergebnis": ", ".join(X.fraction_text(v) for v in y), "ausgewogen (Brüche)": "ja" if B.is_balanced(net, m, y, 0) else "nein"})
    return rows


def verdict_multi(found, view: View):
    if view.error:
        return "error", view.error
    if not view.stable:
        return "warning", "Ohne stabiles Ergebnis gibt es kein ausgewogenes und damit auch keine mehreren."
    if not found:
        return "warning", "Keiner der Wege (Dynamik von Null, Reduktion, fünf Zufallsstarts) fand ein ausgewogenes Ergebnis."
    if len(found) == 1:
        return "info", ("Alle Wege, die ein Ergebnis fanden (Dynamik von Null, Reduktion, fünf Zufallsstarts), lieferten denselben Auszahlungsvektor. Das beweist keine Eindeutigkeit; "
                        "gefunden heißt hier nur: mindestens so viele, eine Obergrenze gibt diese Suche nicht.")
    return "warning", (f"**{len(found)} verschiedene ausgewogene Ergebnisse** gefunden (Dynamik von Null, Reduktion, fünf Zufallsstarts; jedes vom Prüfer bestätigt); die größte Abweichung eines Betriebs zwischen zwei "
                       f"Ergebnissen ist {de(MU.max_deviation(found), 3)}. „Das“ ausgewogene Ergebnis der Anzeige ist eine Auswahlregel (Dynamik von Null, sonst Reduktion), nicht das Ergebnis.")


# --- Reiter 5: Zwei Lesarten --------------------------------------------------------------------------------------------------------------------------------
READING_PAIRS = ((Fraction(0), Fraction(0)), (Fraction(0), Fraction(1, 3)), (Fraction(0), Fraction(3, 5)), (Fraction(1, 5), Fraction(3, 5)), (Fraction(1, 4), Fraction(1, 4)), (Fraction(2, 5), Fraction(2, 5)))


def split_rows():
    """Eine Kante mit Wert 1 und Außenoptionen (a_u; a_v): Anteil von v bei Nash mit Drohpunkt und beim Ausstiegsprinzip (eigene Variante)."""
    rows = []
    for au, av in READING_PAIRS:
        nash, ex = P.nash_split(1, au, av), P.exit_split(1, au, av)
        rows.append({"(a_u; a_v)": f"({X.fraction_text(au)}; {X.fraction_text(av)})", "Nash mit Drohpunkt": X.fraction_text(nash), "Ausstiegsprinzip": X.fraction_text(ex),
                     "gleich": "ja" if nash == ex else "nein"})
    return rows


def reading_view(settings: Settings, view: View):
    """(y_nash, y_prinzip, Quelle) für das Netz der Seitenleiste; y_prinzip None, wenn keine Suche ein Ergebnis fand."""
    if not view.ok:
        return None
    pr = P.principle_outcome(view.net, settings.seed, y_nash=view.outcome.y, kappa=settings.kappa)
    return view.outcome.y, None if pr is None else pr[0], None if pr is None else pr[2]


def verdict_reading(rv, view: View):
    if rv is None:
        return "info", "Ohne ausgewogenes Ergebnis gibt es nichts zu vergleichen."
    yn, yp, source = rv
    if yp is None:
        return "warning", ("Für das Ausstiegsprinzip fand keine der Suchen (von Null, beim ausgewogenen Ergebnis, von drei zufälligen stabilen Auszahlungen) einen Fixpunkt. "
                           "Das heißt nicht, dass keiner existiert; für diese Variante gibt es weder Quelle noch Satz.")
    dev = max(abs(a - b) for a, b in zip(yn, yp))
    n_diff = sum(1 for a, b in zip(yn, yp) if abs(a - b) > SAME)
    if dev <= SAME:
        return "info", f"Beide Lesarten geben in diesem Netz dieselben Auszahlungen (Ausstiegsprinzip gefunden: {source}). Das passiert, wenn die Auszahlungen schon durch die stabile Spanne feststehen oder alle Außenoptionen klein sind."
    return "warning", (f"Die Lesarten unterscheiden sich in {n_diff} von {view.net.n} Betrieben, am stärksten um {de(dev, 3)} (Ausstiegsprinzip gefunden: {source}). "
                       "Die Variante ist eine eigene Konstruktion dieser Demo, ohne Quelle und ohne Aussage zur Eindeutigkeit.")


# --- Reiter 6: Kern, Shapley, Nukleolus ----------------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class GameView:
    values: tuple
    n: int
    core: bool
    shapley: tuple
    shapley_in_core: bool
    nucleolus: tuple
    levels: tuple
    nucleolus_in_core: bool
    nucleolus_balanced: bool | None
    balanced_in_core: bool | None
    balanced_equal_nucleolus: bool | None
    shapley_equal_balanced: bool | None


def game_view(view: View) -> GameView | None:
    if view.error or view.net is None or view.net.n > G.GAME_MAX_N:
        return None
    net = view.net
    n = net.n
    v = G.coalition_values(net)
    sh = G.shapley(v, n)
    x, levels = G.nucleolus(v, n)
    core = view.stable
    nb = bic = beq = seq = None
    if core:
        nb = any(B.is_balanced(net, m, list(x), 1e-6) for m in B.candidate_matchings(net, x, 1e-5))
    if view.ok:
        bic = G.in_core(list(view.outcome.y), v, n, 1e-6)
        beq = max(abs(a - b) for a, b in zip(view.outcome.y, x)) <= SAME
        seq = max(abs(a - float(b)) for a, b in zip(view.outcome.y, sh)) <= SAME
    return GameView(tuple(v), n, core, tuple(sh), G.in_core(sh, v, n), tuple(float(t) for t in x), tuple(levels), G.in_core(x, v, n, 1e-6) if core else False, nb, bic, beq, seq)


def verdict_game(gv: GameView | None, view: View):
    if gv is None:
        return "info", f"Der Reiter rechnet höchstens {G.GAME_MAX_N} Betriebe (2^{G.GAME_MAX_N} Koalitionen); dieses Netz hat {view.net.n if view.net else '–'}."
    parts = [f"Kern {'nicht leer' if gv.core else 'leer'}; Shapley-Wert {'im Kern' if gv.shapley_in_core else 'nicht im Kern'}"]
    if gv.core:
        parts.append(f"Nukleolus {'im Kern' if gv.nucleolus_in_core else 'nicht im Kern'}, vom Prüfer als ausgewogenes Ergebnis {'bestätigt' if gv.nucleolus_balanced else 'nicht bestätigt'}")
    if gv.balanced_in_core is not None:
        parts.append(f"das ausgewogene Ergebnis der Anzeige {'liegt im Kern' if gv.balanced_in_core else 'liegt nicht im Kern'}")
        parts.append(f"gleich dem Nukleolus: {'ja' if gv.balanced_equal_nucleolus else 'nein'}; gleich dem Shapley-Wert: {'ja' if gv.shapley_equal_balanced else 'nein'}")
    kind = "success" if gv.core and gv.nucleolus_balanced else "warning" if not gv.core else "info"
    return kind, "; ".join(parts) + "."


# --- Reiter 7: Eigenschaften -------------------------------------------------------------------------------------------------------------------------------
PROPERTY_FACTOR = 3
PROPERTY_MAX_NODES = 8
PROPERTY_AUTO_MAX_N = 16            # bis zu so vielen Betrieben rechnet Reiter 7 sofort, sonst erst auf Klick
MULTI_AUTO_MAX_N = 24               # ebenso für die Suche nach mehreren Ergebnissen in Reiter 4


@dataclass(frozen=True)
class PropertyView:
    scale_ok: bool
    scale_dev: float
    relabel_ok: bool
    relabel_dev: float
    leaf_rows: tuple            # je Knoten (höchstens PROPERTY_MAX_NODES): (Label, vorher, nachher)
    leaf_nodes_total: int


def property_view(settings: Settings, view: View) -> PropertyView | None:
    if not view.ok:
        return None
    net = view.net
    y = np.array(view.outcome.y)
    o = B.balanced_outcome(N.scaled(net, PROPERTY_FACTOR), settings.kappa)
    sd = float(np.max(np.abs(np.array(o.y) / PROPERTY_FACTOR - y))) if o.status == "ok" else float("inf")
    perm = list(reversed(range(net.n)))
    o2 = B.balanced_outcome(N.relabel(net, perm), settings.kappa)
    rd = float(max(abs(o2.y[perm[v]] - y[v]) for v in range(net.n))) if o2.status == "ok" else float("inf")
    rows = []
    for u in range(min(net.n, PROPERTY_MAX_NODES)):
        o3 = B.balanced_outcome(N.with_leaf(net, u), settings.kappa)
        rows.append((net.label(u), float(y[u]), None if o3.status != "ok" else float(o3.y[u])))
    return PropertyView(sd <= SAME, sd, rd <= SAME, rd, tuple(rows), net.n)


def verdict_properties(pv: PropertyView | None):
    if pv is None:
        return "info", "Ohne ausgewogenes Ergebnis gibt es nichts zu vergleichen."
    down = sum(1 for _, a, b in pv.leaf_rows if b is not None and b < a - SAME)
    up = sum(1 for _, a, b in pv.leaf_rows if b is not None and b > a + SAME)
    same = sum(1 for _, a, b in pv.leaf_rows if b is not None and abs(b - a) <= SAME)
    text = (f"Alle Kantenwerte mit {PROPERTY_FACTOR} malgenommen: größte Abweichung der durch {PROPERTY_FACTOR} geteilten Auszahlungen {sci(pv.scale_dev)}. "
            f"Knoten umgekehrt nummeriert: größte Abweichung {sci(pv.relabel_dev)}. "
            f"Ein neuer Blattknoten an einem der {len(pv.leaf_rows)} ersten Betriebe: dessen Auszahlung sinkt in {down}, steigt in {up}, bleibt gleich in {same} Fällen.")
    return "info", text + " Bei mehreren ausgewogenen Ergebnissen kann ein Teil der Änderungen die Auswahlregel sein."


# --- Handnetze im Überblick ------------------------------------------------------------------------------------------------------------------------------
def hand_nets():
    """Die von Hand gerechneten Netze (Einheitswert, außer dem Literaturbeispiel); Reihenfolge der Knoten 0, 1, 2, ..."""
    return [("Weg mit 3 Betrieben", N.path(3)), ("Weg mit 4 Betrieben", N.path(4)), ("Weg mit 5 Betrieben", N.path(5)), ("Weg mit 6 Betrieben", N.path(6)), ("Weg mit 7 Betrieben", N.path(7)),
            ("Stern mit 3 Blättern", N.star(3)), ("Spinne mit drei Beinen der Länge 2", N.spider(7)), ("Kreis mit 4 Betrieben", N.cycle(4)),
            ("Vollständiges Netz mit 4 Betrieben", N.make_net(4, [(i, j) for i in range(4) for j in range(i + 1, 4)])), ("Dreieck mit Anhang", N.triangle_with_tail()),
            ("Weg mit den Werten 8, 6, 2", N.literature_example()), ("Zweiseitig 2 + 3", N.complete_bipartite(2, 3)), ("Dreieck", N.cycle(3)), ("Kreis mit 5 Betrieben", N.cycle(5))]


def hand_net_rows():
    """Je Handnetz: stabil?, ausgewogene Auszahlungen in Brüchen (Knoten 0, 1, ...), Verfahren, mehrere ausgewogene Ergebnisse gefunden?"""
    rows = []
    for name, net in hand_nets():
        out = B.balanced_outcome(net)
        if out.status == "ok":
            ex = X.exact_balanced(net, out.matching, out.y)
            pay = ", ".join(X.fraction_text(v) for v in ex)
            multi = "ja" if len(MU.distinct_outcomes(net, 0)) >= 2 else "nein"
            method = out.method
        else:
            pay, multi, method = "kein stabiles Ergebnis", "–", "–"
        rows.append({"Netz": name, "Betriebe": net.n, "Auszahlungen (Betrieb 0, 1, ...)": pay, "Verfahren": method, "mehrere ausgewogene gefunden": multi})
    return rows
