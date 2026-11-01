"""Zeilen und Verdikte der vorgerechneten Reihen (data/tables.json). Alle Zahlen im Text kommen aus den Tabellen (f-Strings); `tests/test_claims.py` hält dieselben Zahlen fest."""

import aun_constants as C
import aun_experiments as XP
from aun_evaluation import de, sci

ORDER_POWER = ("bip88", "tree10", "gen8a")


def pct(a, b, nd=1) -> str:
    return "–" if not b else de(100 * a / b, nd) + " %"


def kn(k, n) -> str:
    return f"{k} von {n}"


def corr(x) -> str:
    return "nicht definiert" if x is None else de(x, 2)


def seeds_text(values) -> str:
    return " / ".join(str(v) for v in values)


# --- Reiter 1 ----------------------------------------------------------------------------------------------------------------------------------------
def rows_power(t):
    rows = []
    for key in XP.CLASSES:
        c = t["classes"][key]
        rows.append({"Netzklasse": XP.CLASSES[key], "Netze mit stabilem Ergebnis": c["stable"], "Betriebe": c["nodes"], "Korrelation mit Grad": corr(c["corr_deg"]),
                     "Korrelation mit Zwischenzentralität": corr(c["corr_bet"]), "Tauschkanten mit ungleichem Grad": c["unequal"],
                     "davon: höherer Grad bekommt weniger": c["lower"], "davon: gleich viel": c["same"]})
    return rows


def rows_open(t):
    rows = []
    for key in XP.CLASSES:
        c = t["classes"][key]
        rows.append({"Netzklasse": XP.CLASSES[key], "Betriebe": c["nodes"], "festgelegt auf 0": c["fixed0"], "festgelegt auf 1": c["fixed1"], "festgelegt auf anderen Wert": c["fixed_other"],
                     "offen": c["open"], "offen, genau 1/2": c["open_half"], "offen, weniger": c["open_less"], "offen, mehr": c["open_more"]})
    return rows


def verdict_table_power(t):
    cs = {k: t["classes"][k] for k in ORDER_POWER}
    cors = [cs[k]["corr_deg"] for k in ORDER_POWER]
    text = ("Auszahlung und Grad: Korrelation " + ", ".join(f"{corr(cs[k]['corr_deg'])} ({XP.CLASSES[k]})" for k in ORDER_POWER) + ". "
            + "Der Betrieb mit dem höheren Grad bekommt trotzdem weniger auf "
            + ", ".join(f"{kn(cs[k]['lower'], cs[k]['unequal'])} Tauschkanten mit ungleichem Grad ({XP.CLASSES[k]})" for k in ORDER_POWER) + ". ")
    if all(c is not None and c > 0 for c in cors):
        text += "Grad und Auszahlung hängen in diesen drei Klassen positiv zusammen, aber nicht ausnahmslos. "
    return "info", text


# --- Reiter 2 ----------------------------------------------------------------------------------------------------------------------------------------
def rows_existence(t):
    rows = []
    for key in XP.CLASSES:
        c = t["classes"][key]
        rows.append({"Netzklasse": XP.CLASSES[key], "Netze": c["nets"], "stabil": c["stable"], "Dynamik von Null": c["d0"], "Reduktion": c["red"],
                     "Reduktion abgelehnt (fester Knoten bietet Option)": c["red_refused"], "eines von beiden": c["either"], "von keinem": c["none"],
                     "Dynamik von Null ohne Matching-Ergebnis": c["d0_not_matching"]})
    return rows


def existence_totals(t):
    stable = sum(t["classes"][k]["stable"] for k in XP.CLASSES)
    either = sum(t["classes"][k]["either"] for k in XP.CLASSES)
    d0 = sum(t["classes"][k]["d0"] for k in XP.CLASSES)
    return stable, either, d0


def verdict_table_existence(t):
    stable, either, d0 = existence_totals(t)
    bip = t["classes"]["bip88"]
    text = (f"In allen {len(XP.CLASSES)} Klassen zusammen haben {stable} Netze ein stabiles Ergebnis; Dynamik von Null oder Reduktion fand in {either} davon ein vom Prüfer bestätigtes ausgewogenes Ergebnis "
            f"({'in allen' if either == stable else 'nicht in allen'}). Die Dynamik von Null allein fand es in {d0}. ")
    text += (f"Zweiseitig 8 + 8 (p = 0,3): stabil in {kn(bip['stable'], bip['nets'])} Netzen, die Dynamik von Null allein lieferte kein Ergebnis in {kn(bip['stable'] - bip['d0'], bip['stable'])} davon, "
             f"die Reduktion fand es in {kn(bip['red'], bip['stable'])}.")
    return ("success" if either == stable else "warning"), text


def rows_share(t):
    rows = []
    for p in XP.SHARE_PS:
        row = {"Kantenwahrscheinlichkeit p": f"{p} %"}
        for n in XP.SHARE_NS:
            c = t["share"][f"{n}:{p}"]
            row[f"{n} Knoten"] = f"{de(c['percent']['mean'], 1)} ± {de(c['percent']['sd'], 1)} %"
        rows.append(row)
    return rows


def share_minimum(t, n):
    """(p des kleinsten Anteils, Anteil dort, Anteil bei größtem p, ob zwischen kleinstem und größtem p eine Steigung vorkommt)."""
    vals = [(t["share"][f"{n}:{p}"]["percent"]["mean"], p) for p in XP.SHARE_PS]
    lo = min(vals)
    return lo[1], lo[0], vals[-1][0], any(vals[i + 1][0] > vals[i][0] for i in range(len(vals) - 1)) and any(vals[i + 1][0] < vals[i][0] for i in range(len(vals) - 1))


def verdict_table_share(t):
    parts = []
    nonmono = True
    for n in XP.SHARE_NS:
        p, v, last, mono = share_minimum(t, n)
        nonmono &= mono
        parts.append(f"bei {n} Knoten am kleinsten bei p = {p} % ({de(v, 1)} %) und bei p = {XP.SHARE_PS[-1]} % {de(last, 1)} %")
    return "info", ("Der Anteil der Netze mit stabilem Ergebnis ist " + "; ".join(parts) + ". "
                    + ("Er ist nicht monoton in p: er fällt zunächst und steigt dann wieder." if nonmono else "Er ist in mindestens einer Zeile monoton in p.")
                    + "")


# --- Reiter 3 ----------------------------------------------------------------------------------------------------------------------------------------
def rows_dynamics(t):
    rows = []
    for k in C.KAPPAS:
        c = t["dynamics"]["kappas"][str(k)]
        rows.append({"κ": de(k, 2), "Schritte, Median": int(c["median"]), "Schritte, 90-%-Quantil": int(c["q90"]), "konvergiert": kn(c["converged"], c["nets"]), "Fixpunkt ausgewogen": kn(c["balanced"], c["nets"])})
    return rows


def rows_growth(t):
    rows = []
    for side in XP.GROWTH_SIDES:
        c = t["growth"][str(side)]
        rows.append({"Betriebe (n + n)": f"{side} + {side}", "Netze": c["nets"], "Schritte, Median": int(c["median"]), "Schritte, Maximum": int(c["maximum"]), "konvergiert": kn(c["converged"], c["nets"]),
                     "Fixpunkt ausgewogen": kn(c["balanced"], c["nets"])})
    return rows


def verdict_table_dynamics(t):
    d = t["dynamics"]
    ks = d["kappas"]
    allconv = all(c["converged"] == c["nets"] for c in ks.values())
    bal = {k: c["balanced"] for k, c in ks.items()}
    g = t["growth"]
    allg = all(c["converged"] == c["nets"] for c in g.values())
    text = (f"{d['nets']} zweiseitige 8 + 8-Netze: Die Dynamik von Null {'konvergiert für alle vier Dämpfungen in allen' if allconv else 'konvergiert nicht immer, in'} Netzen; "
            f"die Fixpunkte weichen über die Dämpfungen höchstens um {sci(d['max_fixpoint_difference'])} ab. Der Fixpunkt ist in {bal[str(C.DEFAULT_KAPPA)]} von {d['nets']} Netzen ein ausgewogenes Ergebnis "
            f"(die übrigen {d['nets'] - bal[str(C.DEFAULT_KAPPA)]} brauchen die Reduktion). Mit der Netzgröße wächst die Schrittzahl (Median {int(g[str(XP.GROWTH_SIDES[0])]['median'])} bei {XP.GROWTH_SIDES[0]} + {XP.GROWTH_SIDES[0]}, "
            f"{int(g[str(XP.GROWTH_SIDES[-1])]['median'])} bei {XP.GROWTH_SIDES[-1]} + {XP.GROWTH_SIDES[-1]}); {'alle Läufe konvergierten' if allg else 'nicht alle Läufe konvergierten'}.")
    return "info", text


# --- Reiter 4 ----------------------------------------------------------------------------------------------------------------------------------------
def rows_ambiguity(t):
    rows = []
    for key in XP.CLASSES:
        c = t["classes"][key]
        rows.append({"Netzklasse": XP.CLASSES[key], "Netze mit stabilem Ergebnis": c["stable"], "mit mindestens zwei ausgewogenen Ergebnissen": c["ambiguous"],
                     "je Zufalls-Seed": seeds_text(c["ambiguous_per_seed"]), "größte Abweichung eines Betriebs, Median": "–" if c["deviation_median"] is None else de(c["deviation_median"], 3),
                     "Maximum": "–" if c["deviation_max"] is None else de(c["deviation_max"], 3)})
    return rows


def rows_atlas(t):
    a = t["atlas"]
    rows = [{"Knoten": n, "Graphen": r["graphs"], "mit stabilem Ergebnis": r["stable"], "mit mindestens zwei ausgewogenen": r["ambiguous"]} for n, r in sorted(a["by_n"].items(), key=lambda kv: int(kv[0]))]
    rows.append({"Knoten": "alle", "Graphen": a["graphs"], "mit stabilem Ergebnis": a["stable"], "mit mindestens zwei ausgewogenen": a["ambiguous"]})
    return rows


def verdict_table_ambiguity(t):
    cs = t["classes"]
    trees = cs["tree10"]
    return "warning", (f"Zweiseitig 8 + 8: in {kn(cs['bip88']['ambiguous'], cs['bip88']['stable'])} Netzen fanden die Wege mindestens zwei verschiedene ausgewogene Ergebnisse; "
                       f"Bäume mit 10 Knoten: {kn(trees['ambiguous'], trees['stable'])}; allgemein mit 8 Knoten (p = 0,3): {kn(cs['gen8a']['ambiguous'], cs['gen8a']['stable'])}. "
                       "Das sind Untergrenzen (fünf Zufallsstarts, Dynamik von Null, Reduktion). In den Netzen mit Mehrdeutigkeit ist „das“ ausgewogene Ergebnis eine Auswahlregel.")


def verdict_table_atlas(t):
    a = t["atlas"]
    return "warning", (f"Von {a['graphs']} zusammenhängenden Graphen mit 2 bis 6 Knoten haben {a['stable']} ein stabiles Ergebnis, bei {a['ambiguous']} davon fanden zwölf Wege mindestens zwei verschiedene ausgewogene "
                       f"Ergebnisse ({a['ambiguous_bipartite']} der {a['bipartite_stable']} zweiseitigen mit stabilem Ergebnis); für {a['none']} stabile Graphen fand sich keines.")


# --- Reiter 5 ----------------------------------------------------------------------------------------------------------------------------------------
def rows_reading(t):
    rows = []
    for key in XP.PRINCIPLE_CLASSES:
        c = t["classes"][key]
        both = c["principle_both"]
        rows.append({"Netzklasse": XP.CLASSES[key], "Netze mit stabilem Ergebnis": c["stable"], "Ausstiegsprinzip: Fixpunkt gefunden": both, "kein Fixpunkt gefunden": c["principle_none"],
                     "gleiche Auszahlungen": kn(c["principle_same"], both), "je Zufalls-Seed": seeds_text(c["principle_same_per_seed"]),
                     "größte Abweichung eines Betriebs, Mittel": "–" if c["principle_dev_mean"] is None else de(c["principle_dev_mean"], 3),
                     "Maximum": "–" if c["principle_dev_max"] is None else de(c["principle_dev_max"], 3)})
    return rows


def verdict_table_reading(t):
    cs = [t["classes"][k] for k in XP.PRINCIPLE_CLASSES]
    return "info", ("Beide Lesarten geben dieselben Auszahlungen in "
                    + ", ".join(f"{kn(c['principle_same'], c['principle_both'])} Netzen ({XP.CLASSES[k]})" for k, c in zip(XP.PRINCIPLE_CLASSES, cs))
                    + f"; in {sum(c['principle_none'] for c in cs)} Netzen fand die Suche keinen Fixpunkt des Ausstiegsprinzips. Für das Ausstiegsprinzip im Netz gibt es keine Quelle; die Zahlen sind eine Messung dieser Suche, kein Satz.")


# --- Reiter 6 ----------------------------------------------------------------------------------------------------------------------------------------
def rows_game(t):
    rows = []
    for kind, label in XP.GAME_KINDS.items():
        g = t["game"][kind]
        rows.append({"Netzklasse": label, "Netze": g["nets"], "Kern nicht leer": g["core"], "ausgewogenes Ergebnis im Kern": kn(g["balanced_in_core"], g["balanced_found"]),
                     "Shapley-Wert im Kern": kn(g["shapley_in_core"], g["nets"]), "Shapley-Wert gleich ausgewogen": kn(g["shapley_equal"], g["balanced_found"]),
                     "Nukleolus ausgewogen": kn(g["nucleolus_balanced"], g["core"]), "Nukleolus gleich Dynamik-Ergebnis": kn(g["nucleolus_equal"], g["balanced_found"]),
                     "Abweichung Shapley gegen ausgewogen, Median / Maximum": f"{de(g['shapley_dev_median'], 3)} / {de(g['shapley_dev_max'], 3)}"})
    return rows


def verdict_table_game(t):
    g = t["game"]
    core = sum(x["core"] for x in g.values())
    nb = sum(x["nucleolus_balanced"] for x in g.values())
    bic = sum(x["balanced_in_core"] for x in g.values())
    found = sum(x["balanced_found"] for x in g.values())
    sh = sum(x["shapley_in_core"] for x in g.values())
    nets = sum(x["nets"] for x in g.values())
    she = sum(x["shapley_equal"] for x in g.values())
    return "info", (f"In {core} Netzen mit nicht leerem Kern liegt das ausgewogene Ergebnis in {kn(bic, found)} im Kern und der Nukleolus ist in {kn(nb, core)} selbst ein vom Prüfer bestätigtes ausgewogenes Ergebnis. "
                    f"Der Shapley-Wert liegt in {kn(sh, nets)} Netzen im Kern und ist in {kn(she, found)} gleich dem ausgewogenen Ergebnis. "
                    "Dass der Nukleolus ausgewogen ist, ist hier eine Messung an diesen Netzen, kein Satz.")


# --- Reiter 7 ----------------------------------------------------------------------------------------------------------------------------------------
def rows_properties(t):
    p = t["properties"]
    return [
        {"Operation": "alle Kantenwerte mit 2, 3 und 7 malnehmen", "Netze": p["found"], "Ergebnis": f"Auszahlungen skalieren mit: {', '.join(kn(p['scale_ok'][str(c)], p['found']) for c in XP.PROP_FACTORS)}; größte Abweichung {sci(p['scale_dev'])}"},
        {"Operation": "Knoten umnummerieren", "Netze": p["found"], "Ergebnis": f"gleiche Auszahlungen in {kn(p['relabel_ok'], p['found'])}; größte Abweichung {sci(p['relabel_dev'])}"},
        {"Operation": "neuer Blattknoten an einem zufälligen Betrieb u", "Netze": p["leaf_nets"], "Ergebnis": f"Auszahlung von u sinkt in {p['leaf_down']}, steigt in {p['leaf_up']}, bleibt gleich in {p['leaf_same']}"},
        {"Operation": "(dasselbe) übrige Betriebe", "Netze": p["leaf_others"], "Ergebnis": f"sinkt in {p['leaf_others_down']}, steigt in {p['leaf_others_up']}, bleibt gleich in {p['leaf_others_same']} Beobachtungen"},
        {"Operation": "neue Kante zwischen zwei Betrieben auf verschiedenen Seiten", "Netze": p["edge_nets"], "Ergebnis": f"Endbetrieb: sinkt in {p['edge_down']}, steigt in {p['edge_up']}, bleibt gleich in {p['edge_same']} von {p['edge_obs']} Beobachtungen; beide nicht schlechter in {kn(p['edge_both_not_worse'], p['edge_nets'])} Netzen"},
    ]


def verdict_table_properties(t):
    p = t["properties"]
    return "info", (f"Gewichtete zweiseitige 8 + 8-Netze ({p['found']} mit Ergebnis): Skalieren und Umnummerieren ändern bis auf Rundung nichts (größte Abweichung {sci(max(p['scale_dev'], p['relabel_dev']))}). "
                    f"Ein neuer Blattknoten senkt die Auszahlung seines Betriebs in {p['leaf_down']} von {p['leaf_nets']} Fällen, eine neue Kante senkt die Auszahlung eines Endbetriebs in {p['edge_down']} von {p['edge_obs']} Beobachtungen. "
                    "Beides bei dem zuerst gefundenen Ergebnis; wo es mehrere gibt, kann ein Teil der Änderungen die Auswahlregel sein.")
