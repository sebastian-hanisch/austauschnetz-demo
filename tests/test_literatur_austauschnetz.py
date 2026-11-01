"""Literatur-Referenzwerte (ORACLE-PLAYBOOK §5.1).

* Bayati, Borgs, Chayes, Kanoria, Montanari, „Bargaining dynamics in exchange networks“ (arXiv 1004.2079), Beispiel eines Wegs mit den Kantenwerten 8, 6 und 2: das ausgewogene
  Ergebnis ist (1,5; 6,5; 1; 1). Stand der Einsicht: ar5iv-Fassung (https://ar5iv.arxiv.org/html/1004.2079), die ersten 100 000 von 215 260 Zeichen gelesen, nicht das PDF.
* Offen (kein Test): das Vier-Knoten-Beispiel (1/3, 2/3, 2/3, 1/3) aus arXiv 2601.09198 steht nur in einem Suchauszug; Kleinberg und Tardos (STOC 2008) war nicht abrufbar.
  Die Werte sind von Hand gerechnet (tests/conftest.py) und mit der Aufzählung geprüft, aber kein Literaturwert."""

from fractions import Fraction as Fr

import pytest

import aun_balanced as B
import aun_exact as X
import aun_net as N


def test_bayati_example_path_with_values_8_6_2():
    net = N.literature_example()
    assert net.edges == ((0, 1, 8), (1, 2, 6), (2, 3, 2))
    out = B.balanced_outcome(net)
    assert out.status == "ok"
    assert out.y == pytest.approx((1.5, 6.5, 1.0, 1.0))
    assert X.exact_balanced(net, out.matching, out.y) == [Fr(3, 2), Fr(13, 2), Fr(1), Fr(1)]
