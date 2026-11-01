"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jeder Zweig der Art steht hier."""

from fractions import Fraction as Fr

import pytest

import aun_evaluation as ev
import aun_multi as MU
from aun_scenario import Settings


def view(net="path", n=4, **kw):
    return ev.analyse(Settings(net=net, n=n, **kw))


def test_main_verdict_on_path4_names_the_counts_and_the_extremes():
    kind, text = ev.verdict_main(view())
    assert kind == "success"
    assert "Dynamik von Null" in text and "in Brüchen exakt" in text
    assert "0 von 4 Betrieben sind schon durch die stabile Spanne festgelegt, 4 sind offen" in text
    assert "höchste Auszahlung hat S1 (2/3)" in text and "niedrigste S3 (1/3)" in text
    assert "Auf 0 von 2 Tauschkanten mit ungleichem Grad bekommt der Betrieb mit dem höheren Grad weniger" in text


def test_main_verdict_on_path5_has_every_node_fixed():
    kind, text = ev.verdict_main(view(n=5))
    assert kind == "success" and "5 von 5 Betrieben sind schon durch die stabile Spanne festgelegt, 0 sind offen" in text
    assert "höchste Auszahlung hat S1 (1)" in text


def test_main_verdict_warns_without_a_stable_outcome_and_gives_both_numbers():
    kind, text = ev.verdict_main(view(net="cycle", n=3))
    assert kind == "warning" and "Kein stabiles Ergebnis" in text
    assert "1,50 Euro groß, das ganzzahlige nur 1" in text and "per Definition stabil" in text


def test_main_verdict_reports_a_bad_edge_list_as_error():
    v = view(net="custom", edges="0-0")
    kind, text = ev.verdict_main(v)
    assert v.net is None and kind == "error" and "Schleife am Knoten 0" in text


def test_main_verdict_counts_degree_reversals():
    """Netz mit einem Betrieb höheren Grades, der weniger bekommt: Weg 5, Kante 1-2 ist nicht im Matching; Spinne mit Mitte und drei Beinen der Länge 2 (n = 7)."""
    v = view(net="spider", n=7)
    kind, text = ev.verdict_main(v)
    assert kind == "success"
    unequal, lower, same = ev.reversal_counts(v)
    assert f"Auf {lower} von {unequal} Tauschkanten" in text
    assert unequal == 3 and lower == 0 and same == 0                        # die Mitte (Grad 3) bekommt 0 oder alles


def test_reversal_counts_on_path5_and_on_a_net_with_a_weaker_hub():
    v = view(n=5)
    assert ev.reversal_counts(v) == (2, 0, 0)           # Matching 01 und 34: je Grad 1 gegen 2, der Betrieb mit Grad 2 bekommt 1 gegen 0
    k23 = view(net="bipartite", n=5)
    assert ev.reversal_counts(k23)[0] == 2              # (1, 1, 0, 0, 0): Matching zwischen Grad 3 und Grad 2


def test_pattern_verdict_counts_even_and_odd_paths():
    rows = [{"n": 2, "y": (Fr(1, 2), Fr(1, 2)), "edge": Fr(1, 2), "second": Fr(1, 2)}, {"n": 3, "y": (Fr(0), Fr(1), Fr(0)), "edge": Fr(0), "second": Fr(1)},
            {"n": 4, "y": (Fr(1, 3), Fr(2, 3), Fr(2, 3), Fr(1, 3)), "edge": Fr(1, 3), "second": Fr(2, 3)}, {"n": 5, "y": (Fr(0), Fr(1), Fr(0), Fr(1), Fr(0)), "edge": Fr(0), "second": Fr(1)}]
    assert ev.pattern_matches(rows) == (2, 2, 2, 2)
    kind, text = ev.verdict_pattern(rows)
    assert kind == "info" and "2 bis 5 Knoten" in text and "in 2 von 2 Wegen" in text and "zeigen 2 von 2 Wegen" in text
    wrong = rows[:2] + [{"n": 4, "y": (Fr(1, 2),) * 4, "edge": Fr(1, 2), "second": Fr(1, 2)}]
    assert ev.pattern_matches(wrong)[0] == 1


def test_real_pattern_rows_follow_the_formula_for_every_even_path():
    ok_even, n_even, ok_odd, n_odd = ev.pattern_matches(ev.path_pattern_rows(10))
    assert (ok_even, n_even, ok_odd, n_odd) == (5, 5, 4, 4)


def test_power_verdict_names_correlations_or_says_undefined():
    kind, text = ev.verdict_power(view(n=6))
    assert kind == "info" and "Korrelation der Auszahlung mit dem Grad" in text and "6 Betriebe" in text
    _, text2 = ev.verdict_power(view(net="cycle", n=4))
    assert "nicht definiert" in text2                                        # Kreis: alle Grade gleich
    assert ev.verdict_power(view(net="cycle", n=3))[1].startswith("Ohne ausgewogenes Ergebnis")


def test_existence_verdict_branches():
    kind, text = ev.verdict_existence(view(net="cycle", n=3))
    assert kind == "warning" and "1,50" in text and "ganzzahligen Wert 1" in text
    kind, text = ev.verdict_existence(view(n=5))
    assert kind == "success" and "gleich" in text and "5 von 5" in text and "übrigen 0" in text
    kind, text = ev.verdict_existence(view(net="custom", edges="x"))
    assert kind == "error"


def test_dynamics_verdict_for_a_net_where_the_fixpoint_is_not_a_balanced_outcome():
    v = view(net="bipartite", n=5)
    dv = ev.dynamics_view(v.settings, v)
    kind, text = ev.verdict_dynamics(dv)
    assert kind == "warning" and "kein** ausgewogenes Ergebnis" in text and "2,500" in text and "Gewicht 2" in text
    assert [r[3] for r in dv.rows] == [False] * 4 and all(r[2] for r in dv.rows)


def test_dynamics_verdict_for_a_net_where_it_works():
    v = view(n=4)
    dv = ev.dynamics_view(v.settings, v)
    kind, text = ev.verdict_dynamics(dv)
    assert kind == "success" and "ausgewogenes Ergebnis (Prüfer bestätigt)" in text and "1,00:" in text
    assert dv.max_difference < 1e-9 and dv.trace.shape[1] == 4
    assert ev.verdict_dynamics(None)[1] == "Das Netz hat keine Kanten."


def test_k23_example_numbers():
    k = ev.k23_example()
    assert k["d0"] == pytest.approx((0.5,) * 5) and k["d0_sum"] == pytest.approx(2.5) and k["ip"] == 2 and k["method"] == "Reduktion"


def test_multi_verdict_branches():
    v4 = view(net="cycle", n=4)
    found = ev.multi_view(v4.settings, v4)
    kind, text = ev.verdict_multi(found, v4)
    assert kind == "warning" and f"{len(found)} verschiedene ausgewogene Ergebnisse" in text and len(found) >= 3
    vp = view(n=6)
    kind, text = ev.verdict_multi(ev.multi_view(vp.settings, vp), vp)
    assert kind == "info" and "denselben Auszahlungsvektor" in text and "beweist keine Eindeutigkeit" in text
    tri = view(net="cycle", n=3)
    assert ev.verdict_multi([], tri)[0] == "warning" and "Ohne stabiles Ergebnis" in ev.verdict_multi([], tri)[1]
    assert "Keiner der Wege" in ev.verdict_multi([], vp)[1]


def test_family_rows_say_yes_for_symmetric_members_and_no_for_the_asymmetric_pair():
    rows = ev.family_rows()
    assert [r["ausgewogen (Brüche)"] for r in rows] == ["ja"] * 6 + ["nein"]
    assert rows[0]["Ergebnis"] == "0, 1, 0, 1" and rows[3]["Ergebnis"] == "1/2, 1/2, 1/2, 1/2"


def test_split_rows_by_hand():
    rows = ev.split_rows()
    assert (rows[1]["Nash mit Drohpunkt"], rows[1]["Ausstiegsprinzip"], rows[1]["gleich"]) == ("2/3", "1/2", "nein")
    assert (rows[0]["Nash mit Drohpunkt"], rows[0]["gleich"]) == ("1/2", "ja")
    assert (rows[3]["Nash mit Drohpunkt"], rows[3]["Ausstiegsprinzip"]) == ("7/10", "3/5")
    assert rows[4]["gleich"] == "ja" and rows[5]["gleich"] == "ja"


def test_reading_verdict_branches():
    v4 = view(n=4)
    rv = ev.reading_view(v4.settings, v4)
    kind, text = ev.verdict_reading(rv, v4)
    assert kind == "warning" and "4 von 4 Betrieben" in text and "0,167" in text and "eigene Konstruktion" in text
    v3 = view(n=3)
    kind, text = ev.verdict_reading(ev.reading_view(v3.settings, v3), v3)
    assert kind == "info" and "dieselben Auszahlungen" in text
    assert "nichts zu vergleichen" in ev.verdict_reading(None, v3)[1]
    kind, text = ev.verdict_reading(((0.0, 1.0, 0.0), None, None), v3)
    assert kind == "warning" and "keine der Suchen" in text


def test_game_verdict_on_path4_and_on_the_triangle_and_on_a_big_net():
    v = view(n=4)
    gv = ev.game_view(v)
    kind, text = ev.verdict_game(gv, v)
    assert kind == "success" and "Kern nicht leer" in text and "Shapley-Wert im Kern" in text
    assert "vom Prüfer als ausgewogenes Ergebnis bestätigt" in text and "gleich dem Nukleolus: ja; gleich dem Shapley-Wert: nein" in text
    assert gv.shapley == (Fr(5, 12), Fr(7, 12), Fr(7, 12), Fr(5, 12))
    v5 = view(n=5)
    gv5 = ev.game_view(v5)
    assert not gv5.shapley_in_core and gv5.nucleolus == pytest.approx((0, 1, 0, 1, 0))
    t = view(net="cycle", n=3)
    kind, text = ev.verdict_game(ev.game_view(t), t)
    assert kind == "warning" and "Kern leer" in text
    big = view(net="path", n=9)
    assert ev.game_view(big) is None and "höchstens 8 Betriebe" in ev.verdict_game(None, big)[1] and "dieses Netz hat 9" in ev.verdict_game(None, big)[1]


def test_property_verdict_counts_leaf_effects():
    v = view(n=4)
    pv = ev.property_view(v.settings, v)
    kind, text = ev.verdict_properties(pv)
    assert kind == "info" and pv.scale_ok and pv.relabel_ok and len(pv.leaf_rows) == 4
    assert "mit 3 malgenommen" in text and "an einem der 4 ersten Betriebe" in text
    down = sum(1 for _, a, b in pv.leaf_rows if b < a - 1e-6)
    assert f"sinkt in {down}," in text
    assert ev.verdict_properties(None)[1].startswith("Ohne ausgewogenes")


def test_val_text_and_de():
    assert ev.de(0.5) == "0,50" and ev.de(1234.5678, 1) == "1234,6"
    assert ev.val_text(0.3333, Fr(1, 3)) == "1/3" and ev.val_text(0.3333) == "0,333"


def test_distinct_outcomes_helper_matches_the_verdict_count():
    found = MU.distinct_outcomes(view(net="cycle", n=4).net, 35)
    assert len(found) >= 3
