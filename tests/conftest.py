"""Gemeinsame Fixtures: die Mini-Netze, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b). Alle Erwartungswerte sind von Hand gerechnet."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import aun_net as N  # noqa: E402


@pytest.fixture
def path3():
    """0 - 1 - 2, Einheitswert. Das größte Matching hat Gewicht 1; die Mitte ist Teil jedes Matchings, also bekommt sie alles: (0, 1, 0)."""
    return N.path(3)


@pytest.fixture
def path4():
    """0 - 1 - 2 - 3. Größtes Matching {01, 23} mit Gewicht 2. Stabile Spanne jedes Knotens [0, 1]; ausgewogen (1/3, 2/3, 2/3, 1/3):
    Kante 01: y0 - a0 = y1 - a1 mit a0 = 0, a1 = 1 - y2 = 1/3, also 1/3 - 0 = 2/3 - 1/3."""
    return N.path(4)


@pytest.fixture
def path5():
    """0 - 1 - 2 - 3 - 4. Größtes Matching hat Gewicht 2 und lässt immer 0, 2 oder 4 aus; stabil: y1 = y3 = 1, y0 = y2 = y4 = 0 (fest)."""
    return N.path(5)


@pytest.fixture
def cycle4():
    """Kreis 0-1-2-3-0. Größtes Matching Gewicht 2; (a, 1-a, a, 1-a) ist für jedes a in [0, 1] ausgewogen."""
    return N.cycle(4)


@pytest.fixture
def triangle():
    """Dreieck: das größte Matching hat Gewicht 1, die LP-Relaxation 3/2 (jede Kante 1/2): kein stabiles Ergebnis."""
    return N.cycle(3)


@pytest.fixture
def star3():
    """Mitte 0 und drei Blätter: Gewicht 1, die Mitte bekommt alles."""
    return N.star(3)


@pytest.fixture
def k23():
    """Zwei Verlader (0, 1) und drei Spediteure (2, 3, 4), jeder mit jedem: Matching-Gewicht 2, stabil nur (1, 1, 0, 0, 0)."""
    return N.complete_bipartite(2, 3)


@pytest.fixture
def literature():
    """Weg mit den Kantenwerten 8, 6, 2; ausgewogen (3/2, 13/2, 1, 1), von Hand: a1 = 6 - y2 = 5, also y0 = y1 - 5 und y0 + y1 = 8."""
    return N.literature_example()


@pytest.fixture
def tail():
    """Dreieck 0-1-2 mit Anhang 3 an Knoten 0; Matching {03, 12} mit Gewicht 2; ausgewogen (3/4, 1/2, 1/2, 1/4)."""
    return N.triangle_with_tail()
