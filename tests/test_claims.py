"""Jede Zahl aus der README, nachgerechnet (DEMO-PLAYBOOK §4).

Drei Quellen, alle plattformsicher:
* die gespeicherten Messreihen (`data/tables.json`; Erzeuger-Hash geprüft in `test_measurements.py`): die README-Zahl ist der gespeicherte Wert, gerundet;
* exakte Rechnung (Brüche, Formeln, Identitäten): Gleitkommagleichheit nur mit `approx`;
* die Zeilenbauer der App (`aun_evaluation.*_rows`, `aun_tablerows.rows_*`): jede Zeile der README-Tabellen steht als Text in der README.
Keine Zeit-Assertion, keine exakten Zufallswerte einzelner Läufe. Zählungen über Netze stehen als Zählungen im Test, nicht als Urteilswort."""

import re
from fractions import Fraction as F
from pathlib import Path

import pytest

import aun_balanced as B
import aun_constants as C
import aun_evaluation as V
import aun_exact as X
import aun_experiments as XP
import aun_multi as MU
import aun_net as N
import aun_tablerows as R
import aun_texts as T

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")


def german(x, nd):
    """Eigene Fassung des deutschen Zahlenformats (unabhängig von V.de): Dezimalkomma."""
    return f"{x:.{nd}f}".replace(".", ",")


def row_of(label):
    """Die Tabellenzeile der Hypothese (eine Zeile der README, beginnt mit `| Hn |`)."""
    return next(line for line in README.splitlines() if line.startswith(f"| {label} |"))


def has(row, *needles):
    missing = [n for n in needles if n not in row]
    assert not missing, missing


def md_row(d):
    return "| " + " | ".join(str(v) for v in d.values()) + " |"


def kn(k, n):
    return f"{k} von {n}"


@pytest.fixture(scope="module")
def tables():
    t = XP.load_tables()
    assert t is not None
    return t


@pytest.fixture(scope="module")
def cl(tables):
    return tables["classes"]


# --- README und App: dieselben Texte, dieselben Tabellenzeilen ---------------------------------------------------------------------------------
def test_assumption_text_is_the_same_in_app_and_readme():
    assert T.ASSUMPTIONS_MARKDOWN.strip() in README


def test_readme_tables_are_built_by_the_same_row_builders(tables):
    builders = (V.hand_net_rows(), V.family_rows(), V.split_rows(), V.existence_examples(), R.rows_existence(tables), R.rows_share(tables), R.rows_power(tables), R.rows_open(tables),
                R.rows_dynamics(tables), R.rows_growth(tables), R.rows_ambiguity(tables), R.rows_atlas(tables), R.rows_reading(tables), R.rows_game(tables), R.rows_properties(tables),
                [{"Betriebe": r["n"], "Auszahlungen (exakt)": ", ".join(X.fraction_text(v) for v in r["y"])} for r in V.path_pattern_rows(14)])
    for rows in builders:
        assert rows
        for row in rows:
            assert md_row(row) in README, row


def test_hypothesis_table_has_h1_to_h12_with_a_clear_stand():
    rows = re.findall(r"^\| (H\d+) \|(?:\\\||[^|])*\|\s*\*\*([^*]+)\*\*", README, flags=re.M)
    assert [h for h, _ in rows] == [f"H{i}" for i in range(1, 13)]
    assert [a.split()[0].rstrip(",:") for _, a in rows] == ["Ja", "Ja", "Teilweise", "Ja", "Gestützt", "Nein", "Nein", "Nein", "Teilweise", "Ja", "Ja", "Teilweise"]


def test_math_blocks_are_display_equations_one_per_block():
    blocks = re.findall(r"^\$\$.*\$\$$", T.MATH_MARKDOWN, flags=re.M)
    assert len(blocks) >= 8 and T.MATH_MARKDOWN.count("$$") == 2 * len(blocks)


def test_app_and_readme_agree_on_the_limits_of_the_live_views():
    assert (V.MULTI_AUTO_MAX_N, V.PROPERTY_AUTO_MAX_N, V.PROPERTY_MAX_NODES, V.EXACT_MAX_N, C.N_MAX) == (24, 16, 8, 24, 60)
    has(README, "bei mehr als 24 Betrieben und Reiter 7 bei mehr als 16 Betrieben", "Bis 24 Betriebe", "bis 60 Betriebe (zweiseitig 30 + 30)", "höchstens 8 Betriebe")


# --- H1 bis H3: Handnetze exakt --------------------------------------------------------------------------------------------------------------------
def exact(net):
    out = B.balanced_outcome(net)
    assert out.status == "ok"
    return X.exact_balanced(net, out.matching, out.y)


def test_h1_hand_nets_exactly():
    assert exact(N.path(3)) == [0, 1, 0] and exact(N.path(5)) == [0, 1, 0, 1, 0]
    assert exact(N.path(4)) == [F(1, 3), F(2, 3), F(2, 3), F(1, 3)]
    assert exact(N.literature_example()) == [F(3, 2), F(13, 2), 1, 1]
    has(row_of("H1"), "Weg 3 (0, 1, 0)", "Weg 4 (1/3, 2/3, 2/3, 1/3)", "Weg 5 (0, 1, 0, 1, 0)", "(3/2, 13/2, 1, 1)", "(1,5; 6,5; 1; 1; ar5iv-Text, nicht PDF)")


def test_h2_even_paths_edge_node_is_one_over_k_plus_one():
    for n in range(2, 15, 2):
        y = exact(N.path(n))
        assert y[0] == F(1, n // 2 + 1) and y[-1] == y[0] and y[1] == F(n // 2, n // 2 + 1)
    for n in range(3, 14, 2):
        assert exact(N.path(n)) == [i % 2 for i in range(n)]
    has(row_of("H2"), "k* = 1 bis 7", "Wege mit 2 bis 14 Knoten", "4 Knoten: 1/3, 8: 1/5, 12: 1/7", "3 bis 13 zeigen abwechselnd 0 und 1")


def test_h3_cycle_family_exactly_and_cycle_six():
    for a in (F(0), F(1, 5), F(1, 3), F(1, 2), F(4, 5), F(1)):
        net, m, y = MU.cycle4_family_member(a)
        assert B.is_balanced(net, m, y, 0)
    net, m, _ = MU.cycle4_family_member(F(1, 2))
    assert not B.is_balanced(net, m, [F(1, 5), F(4, 5), F(1, 2), F(1, 2)], 0)
    c6 = N.cycle(6)
    a = F(1, 5)
    assert B.is_balanced(c6, ((0, 1, 1), (2, 3, 1), (4, 5, 1)), [a, 1 - a] * 3, 0)
    has(row_of("H3"), "für *a* = 0; 1/5; 1/3; 1/2; 4/5; 1", "(1/5, 4/5, 1/2, 1/2)", "Kreis 6 mit *a* = 1/5")


# --- H4 bis H8: Zufallsnetze -----------------------------------------------------------------------------------------------------------------
def test_h4_stable_exists_counts(cl, tables):
    bipartite = cl["bip88"]["stable"] + cl["bip66"]["stable"] + cl["tree10"]["stable"]
    nets = cl["bip88"]["nets"] + cl["bip66"]["nets"] + cl["tree10"]["nets"]
    assert bipartite == nets == 720
    assert (cl["gen8a"]["stable"], cl["gen8b"]["stable"], cl["gen12"]["stable"]) == (200, 224, 208)
    has(row_of("H4"), f"{kn(bipartite, nets)} stabil", f"allgemein {kn(cl['gen8a']['stable'], 240)} / {kn(cl['gen8b']['stable'], 240)} / {kn(cl['gen12']['stable'], 240)}", "142 Atlas-Graphen")
    assert tables["atlas"]["graphs"] == 142


def test_h5_balanced_found_in_every_stable_net(cl, tables):
    stable = sum(c["stable"] for c in cl.values())
    either = sum(c["either"] for c in cl.values())
    d0 = sum(c["d0"] for c in cl.values())
    atlas = tables["atlas"]
    assert either == stable and all(c["none"] == 0 for c in cl.values()) and atlas["none"] == 0
    has(row_of("H5"), f"{kn(either, stable)} Zufallsnetze", f"{atlas['stable']} von {atlas['stable']} Atlas-Graphen", f"{d0} der {stable}")
    assert stable == sum(c["stable"] for c in cl.values()) == 1352


def test_h6_dynamics_from_zero_misses_nets_that_the_reduction_solves(cl):
    b = cl["bip88"]
    assert (b["stable"], b["red"], b["stable"] - b["d0"], b["d0_not_matching"]) == (240, 240, 36, 36)
    has(row_of("H6"), f"{kn(b['d0_not_matching'], b['stable'])} 8 + 8-Netzen", f"Reduktion {kn(b['red'], b['stable'])}", "46 von 46 stabil")
    has(README, f"{german(100 * b['d0_not_matching'] / b['stable'], 1)} %", "46 von 300 sind 15,3 %")
    assert round(100 * 46 / 300, 1) == 15.3


def test_h7_fixpoint_from_zero_is_not_always_balanced(tables):
    d = tables["dynamics"]
    assert d["nets"] == 200 and all(c["converged"] == 200 and c["balanced"] == d["kappas"]["0.5"]["balanced"] for c in d["kappas"].values())
    assert d["max_fixpoint_difference"] < 1e-9
    has(row_of("H7"), f"{kn(d['kappas']['0.5']['balanced'], d['nets'])} (gleich für alle vier Dämpfungen)", "K2,3: Fixpunkt 1/2 für alle fünf (Summe 2,5 über dem größten Matching 2)", "richtig ist (1, 1, 0, 0, 0)")
    k = V.k23_example()
    assert k["d0"] == pytest.approx((0.5,) * 5) and k["ip"] == 2 and k["reduction"] == pytest.approx((1, 1, 0, 0, 0))


def test_h8_multiple_outcomes_counts(cl, tables):
    b, t, g, a, s = cl["bip88"], cl["tree10"], cl["gen8a"], tables["atlas"], tables["starts"]
    assert t["ambiguous"] == 0 and s["ambiguous_5"] == b["ambiguous"] and s["stable"] == b["stable"]
    row = row_of("H8")
    has(row, f"{kn(b['ambiguous'], b['stable'])} Netzen mehrere gefunden", f"mit {XP.MORE_STARTS} Zufallsstarts {s['ambiguous_more']} von {s['stable']}", f"Bäume {kn(t['ambiguous'], t['stable'])}",
        f"allgemein 8 Knoten {kn(g['ambiguous'], g['stable'])}", f"Atlas {a['ambiguous']} von {a['stable']}")
    assert (a["stable"], a["ambiguous"], a["ambiguous_bipartite"]) == (126, 43, 7)
    has(README, f"{kn(cl['bip66']['ambiguous'], cl['bip66']['stable'])} Netzen mehrere ausgewogene Ergebnisse (Untergrenze)")


def test_h9_power_and_degree(cl):
    b, g, t = cl["bip88"], cl["gen8a"], cl["tree10"]
    assert all(c["corr_deg"] > 0.3 for c in cl.values())
    row = row_of("H9")
    has(row, f"Korrelation Auszahlung–Grad {german(b['corr_deg'], 2)}", f"{german(g['corr_deg'], 2)} (allgemein)", f"{german(t['corr_deg'], 2)} (Bäume)",
        f"je Seed {german(min(b['corr_deg_per_seed']), 2)} bis {german(max(b['corr_deg_per_seed']), 2)}",
        f"{kn(b['lower'], b['unequal'])} / {kn(g['lower'], g['unequal'])} / {kn(t['lower'], t['unequal'])} Tauschkanten")
    assert b["lower"] + b["same"] <= b["unequal"]


def test_open_nodes_less_and_more_are_equal_by_construction(cl):
    """„offen, weniger“ gleich „offen, mehr“: auf jedem Paar summieren die Auszahlungen zu 1, beide Partner sind offen oder beide festgelegt (Einheitswert)."""
    for c in cl.values():
        assert c["open_less"] == c["open_more"]
    has(README, "keine Messung", "„offen, weniger“ und „offen, mehr“ sind in jeder Klasse gleich")


def test_h10_nucleolus_and_shapley(tables):
    g = tables["game"]
    core = sum(x["core"] for x in g.values())
    nb = sum(x["nucleolus_balanced"] for x in g.values())
    bic = sum(x["balanced_in_core"] for x in g.values())
    found = sum(x["balanced_found"] for x in g.values())
    shc = sum(x["shapley_in_core"] for x in g.values())
    nets = sum(x["nets"] for x in g.values())
    she = sum(x["shapley_equal"] for x in g.values())
    assert (core, nb, bic, found) == (76, 76, 76, 76) and she == 0 and nets == 96
    has(row_of("H10"), f"{kn(nb, core)} Netzen mit nicht leerem Kern", f"im Kern in {kn(bic, found)}", f"Shapley-Wert im Kern in {kn(shc, nets)}", f"in {kn(she, found)}",
        "Weg 4 Shapley (5/12, 7/12, 7/12, 5/12)", "Weg 5 Shapley nicht im Kern")
    from aun_game import coalition_values, in_core, shapley
    assert shapley(coalition_values(N.path(4)), 4) == [F(5, 12), F(7, 12), F(7, 12), F(5, 12)]
    v5 = coalition_values(N.path(5))
    assert not in_core(shapley(v5, 5), v5, 5)


def test_h11_the_two_readings_differ_on_path4_and_agree_on_path3(cl):
    import aun_principle as P
    y4 = P.principle_outcome(N.path(4), 35)[0]
    assert y4 == pytest.approx((0.5,) * 4) and exact(N.path(4)) != [F(1, 2)] * 4
    assert P.principle_outcome(N.path(3), 35)[0] == pytest.approx((0, 1, 0))
    b, t, g = cl["bip88"], cl["tree10"], cl["gen8a"]
    assert b["principle_none"] == t["principle_none"] == g["principle_none"] == 0
    has(row_of("H11"), "Weg 4 (1/3, 2/3, 2/3, 1/3) gegen (1/2, 1/2, 1/2, 1/2)", f"{kn(b['principle_same'], b['principle_both'])} / {kn(t['principle_same'], t['principle_both'])} / {kn(g['principle_same'], g['principle_both'])} Netzen")


def test_h12_properties(tables):
    p = tables["properties"]
    assert (p["nets"], p["found"], p["scale_dev"] < 1e-9, p["relabel_ok"]) == (160, 160, True, 160) and all(v == 160 for v in p["scale_ok"].values())
    assert p["leaf_down"] == 0 and p["leaf_up"] + p["leaf_same"] == p["leaf_nets"]
    assert p["edge_down"] + p["edge_up"] + p["edge_same"] == p["edge_obs"] == 2 * p["edge_nets"]
    has(row_of("H12"), f"senkt die Auszahlung seines Betriebs in {p['leaf_down']} von {p['leaf_nets']} Fällen (steigt in {p['leaf_up']})",
        f"senkt die Auszahlung eines Endbetriebs in {p['edge_down']} von {p['edge_obs']} Beobachtungen", f"beide nicht schlechter in {kn(p['edge_both_not_worse'], p['edge_nets'])} Netzen",
        f"in {p['found'] - p['leaf_nets']} von {p['found']} Netzen kein Ergebnis")


# --- Kernfrage und Korrekturen ---------------------------------------------------------------------------------------------------------------------
def test_known_limit_of_the_search_is_stated_with_its_count(tables):
    p = tables["properties"]
    assert p["found"] - p["leaf_nets"] == 1
    has(README, f"in {p['found'] - p['leaf_nets']} von {p['found']} Netzen kein ausgewogenes Ergebnis", "test_known_limit_of_the_search_a_weighted_net_with_stable_outcome_but_no_result")
    assert "def test_known_limit_of_the_search_a_weighted_net_with_stable_outcome_but_no_result" in (ROOT / "tests" / "test_edge_cases.py").read_text(encoding="utf-8")


def test_kernfrage_numbers(cl, tables):
    b, t = cl["bip88"], cl["tree10"]
    d = tables["dynamics"]
    g = tables["game"]
    core = sum(x["core"] for x in g.values())
    nb = sum(x["nucleolus_balanced"] for x in g.values())
    shc = sum(x["shapley_in_core"] for x in g.values())
    nets = sum(x["nets"] for x in g.values())
    stable = sum(c["stable"] for c in cl.values())
    has(README, f"Korrelation {german(b['corr_deg'], 2)}, Bäume {german(t['corr_deg'], 2)}", f"auf {kn(b['lower'], b['unequal'])} Tauschkanten mit ungleichem Grad bekommt der Betrieb mit dem höheren Grad weniger",
        f"In allen {stable} Zufallsnetzen mit stabilem Ergebnis", f"in {kn(b['ambiguous'], b['stable'])} zweiseitigen 8 + 8-Netzen fanden die Wege mindestens zwei, in Bäumen {kn(t['ambiguous'], t['stable'])}",
        f"in {kn(d['kappas']['0.5']['balanced'], d['nets'])} zweiseitigen Netzen ein ausgewogenes Ergebnis", f"in {kn(nb, core)} Netzen mit nicht leerem Kern", f"in {kn(shc, nets)} Netzen im Kern")


def test_plan_comparison_numbers_are_the_stored_ones(cl, tables):
    """Die Planwerte stehen als Zitat der Vormessung (nicht nachgerechnet); die Messwerte daneben sind die gespeicherten."""
    d, a, p = tables["dynamics"], tables["atlas"], tables["properties"]
    g8a = cl["gen8a"]
    has(README, "(Plan 100 von 240)", "(Plan 51 von 206)", "(Plan 0 von 240)", "(Plan 168 von 200)", "(Plan 78 von 78)", "(Plan 11 von 96)", "(Plan 0,44)", "(Plan 7 von 320)")
    has(README, f"{kn(g8a['ambiguous'], g8a['stable'])} allgemeinen", f"{kn(d['kappas']['0.5']['balanced'], d['nets'])} (Plan 168", f"{atlas_text(a)}")
    has(README, f"Abgelehnt wurde die Reduktion in {cl['gen8a']['red_refused']} / {cl['gen8b']['red_refused']} / {cl['gen12']['red_refused']} Netzen der allgemeinen Klassen (Plan mit der engen Bedingung: 10 / 126 / 89)")
    assert p["edge_obs"] == 320


def atlas_text(a):
    return f"{a['stable']} von {a['graphs']} Graphen mit stabilem Ergebnis, {a['ambiguous']} mit mehreren ausgewogenen, davon {a['ambiguous_bipartite']} zweiseitig"


def test_table_verdicts_say_what_the_stored_tables_say(tables):
    assert R.verdict_table_existence(tables)[0] == "success"
    kind, text = R.verdict_table_game(tables)
    assert "76 von 76 im Kern" in text and "10 von 96 Netzen im Kern" in text and "0 von 76 gleich" in text
    assert "nicht monoton" in R.verdict_table_share(tables)[1]
    assert "0 von 240" in R.verdict_table_ambiguity(tables)[1]
    assert "in 0 Netzen fand die Suche keinen Fixpunkt" in R.verdict_table_reading(tables)[1]
    assert "126 ein stabiles Ergebnis" in R.verdict_table_atlas(tables)[1] and "bei 43 davon" in R.verdict_table_atlas(tables)[1]
    assert "0 von 159 Fällen" in R.verdict_table_properties(tables)[1]
    assert "165 von 200" in R.verdict_table_dynamics(tables)[1]
    assert "0,46 (zweiseitig 8 + 8, p = 0,3)" in R.verdict_table_power(tables)[1]


def test_share_table_is_not_monotone_and_has_its_minimum_at_thirty_percent(tables):
    for n in XP.SHARE_NS:
        vals = [tables["share"][f"{n}:{p}"]["percent"]["mean"] for p in XP.SHARE_PS]
        assert vals.index(min(vals)) == XP.SHARE_PS.index(30) and vals[-1] == 100.0 and vals[0] > min(vals) < vals[3]
    has(README, "bei 8 Knoten fällt der Anteil von", "(p = 30 %) und steigt dann auf", "Die Streuung über die Seeds ist bei p = 30 % am größten")
    s30 = max(tables["share"]["8:30"]["percent"]["sd"], tables["share"]["12:30"]["percent"]["sd"])
    assert all(tables["share"][f"{n}:{p}"]["percent"]["sd"] <= s30 for n in XP.SHARE_NS for p in XP.SHARE_PS)
    has(README, f"(bis {german(s30, 1)} Prozentpunkte)")


def test_growth_and_dynamics_numbers_are_in_the_readme(tables):
    d = tables["dynamics"]
    mant, exp = f"{d['max_fixpoint_difference']:.1e}".split("e")
    sup = str(int(exp)).translate(str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"))
    has(README, f"{d['nets']} zweiseitige 8 + 8-Netze, p = 0,3; die Fixpunkte weichen über die Dämpfungen höchstens um {mant.replace('.', ',')}·10{sup} ab")
    assert all(c["converged"] == c["nets"] for c in tables["growth"].values())
    for k in C.KAPPAS:
        assert d["kappas"][str(k)]["median"] < d["kappas"][str(C.KAPPAS[0])]["median"] or k == C.KAPPAS[0]          # größere Dämpfung ist schneller


def test_weights_and_scaling_factors(tables):
    assert XP.PROP_FACTORS == (2, 3, 7)
    has(README, "Skalierfaktoren 2, 3 und 7 statt 0,1; 2,5; 7,0")


def test_every_readme_section_the_playbook_asks_for_exists():
    for heading in ("## Kernfrage", "## Befunde und Korrekturen gegenüber dem Plan", "## Modell", "## Methodik", "## Befunde (gemessen, keine Behauptungen)", "## Ehrliche Grenzen", "## Literatur", "## Tests",
                    "## Dateistruktur", "## Bewusst nicht umgesetzt", "## Lokal ausführen", "## Tests ausführen"):
        assert heading in README
    assert README.rstrip().endswith("[Regeln setzen, verhandeln, kontrollieren](https://sebastianhanisch.net/konzepte-verhandeln.html).")


def test_sources_are_marked_as_not_read_in_full():
    has(README, "Volltext nicht gelesen", "erste 100 000 von 215 260 Zeichen gelesen", "Abruf des PDF scheiterte", "nur Abstract", "aus dem Gedächtnis genannt, nicht geprüft")
