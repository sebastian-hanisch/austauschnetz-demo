"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets.

Rechenaufwand am Slider-Maximum (60 Knoten, zweiseitig 30 + 30, bis zu 855 Kanten bei p = 95 %): zwei lineare Programme je Knoten für die stabile Spanne
(120 Programme mit n = 60 Variablen und einer Nebenbedingung je Kante), ein ganzzahliges Programm für das größte Matching, die Dynamik mit E = 2 · Kanten
gerichteten Kanten und einer Matrix E × (größter Grad - 1), je Schritt O(E · Grad). Die Reduktion braucht dieselben Programme noch einmal nur dann, wenn die Dynamik von Null
kein Ergebnis liefert. Kern, Shapley und Nukleolus (Reiter 6) nur bis GAME_MAX_N = 8 Knoten: 2^8 - 2 = 254 Koalitionen, die Programme des Nukleolus kosten einige Zehntelsekunden."""

N_MIN, N_MAX, DEFAULT_N = 3, 60, 4
P_MIN, P_MAX, DEFAULT_P = 5, 95, 30             # Kantenwahrscheinlichkeit der Zufallsnetze in Prozent
KAPPAS = (0.25, 0.5, 0.75, 1.0)                  # Dämpfung des Kantenausgleichs
DEFAULT_KAPPA = 0.5
SEED_MAX, DEFAULT_SEED = 999999, 35
DEFAULT_EDGES = "0-1, 1-2, 2-3"
EDGES_MAX_CHARS = 600

NETS = {
    "path": "Weg",
    "cycle": "Kreis",
    "star": "Stern",
    "spider": "Spinne (Mitte mit drei Beinen)",
    "bipartite": "Vollständig zweiseitig (Verlader und Spediteure)",
    "rand_bip": "Zufall: zweiseitig",
    "rand_tree": "Zufall: Baum",
    "rand_gen": "Zufall: allgemein (auch ungerade Kreise)",
    "literature": "Literaturbeispiel (Weg mit Werten 8, 6, 2)",
    "custom": "Eigene Kantenliste",
}
DEFAULT_NET = "path"

# Messreihen (tools/make_grid.py): vier Zufalls-Seeds je Zelle, nie ein einzelner Seed als Befund
TABLE_SEEDS = (11, 22, 33, 44)
SWEEP_SEEDS = TABLE_SEEDS

COLOR_LOW = "#4c78a8"          # Spediteur / niedrige Auszahlung
COLOR_HIGH = "#2F6B65"
COLOR_LOADER = "#e8a838"
COLOR_EDGE = "rgba(150,150,150,0.55)"
COLOR_MATCH = "#2F6B65"
COLOR_WARN = "#d62728"
COLOR_RANGE = "rgba(76,120,168,0.35)"

PRESETS = {
    "Weg mit 4 Betrieben (Voreinstellung)": {},
    "Weg mit 5: die Mitte bekommt nichts": {"net": "path", "n": 5},
    "Weg mit 6": {"net": "path", "n": 6},
    "Kreis mit 4: viele Ergebnisse": {"net": "cycle", "n": 4},
    "Dreieck: kein stabiles Ergebnis": {"net": "cycle", "n": 3},
    "Stern: die Mitte bekommt alles": {"net": "star", "n": 4},
    "Literaturbeispiel 8-6-2": {"net": "literature"},
    "Zweiseitig 2 + 3: Dynamik braucht Reduktion": {"net": "bipartite", "n": 5},
    "Dreieck mit Anhang": {"net": "custom", "edges": "0-1, 1-2, 0-2, 0-3"},
    "Zufallsnetz zweiseitig 8 + 8": {"net": "rand_bip", "n": 16},
    "Größtes Netz (30 + 30, κ = 0,25)": {"net": "rand_bip", "n": 60, "kappa": 0.25},
}
PRESET_HELP = {
    "Weg mit 4 Betrieben (Voreinstellung)": "Vier Betriebe in einer Kette, jede Nachbarschaft eine mögliche Tour mit Überschuss 1. Ausgewogen bekommen die Mitte 2/3 und die Ränder 1/3.",
    "Weg mit 5: die Mitte bekommt nichts": "Fünf Betriebe in einer Kette: der mittlere Betrieb hat zwei Nachbarn und bekommt trotzdem 0, seine Nachbarn bekommen alles.",
    "Weg mit 6": "Sechs Betriebe in einer Kette: die Ränder bekommen 1/4, ihre Nachbarn 3/4, die beiden mittleren je 1/2.",
    "Kreis mit 4: viele Ergebnisse": "Vier Betriebe im Kreis: (a, 1-a, a, 1-a) ist für jedes a zwischen 0 und 1 ausgewogen. Das Ergebnis ist hier eine Menge, die Anzeige nennt eine Auswahl.",
    "Dreieck: kein stabiles Ergebnis": "Drei Betriebe, jeder mit jedem, aber nur ein Paar kann tauschen: zu jeder Aufteilung gibt es ein blockierendes Paar. Das Programm meldet das, statt eine Zahl zu erfinden.",
    "Stern: die Mitte bekommt alles": "Ein Betrieb mit drei Nachbarn, die nur ihn haben: er bekommt den ganzen Überschuss der einen Tour, die zustande kommt.",
    "Literaturbeispiel 8-6-2": "Weg mit den Kantenwerten 8, 6 und 2, das Beispiel aus der Literatur (Bayati u. a.): ausgewogen sind 3/2, 13/2, 1 und 1.",
    "Zweiseitig 2 + 3: Dynamik braucht Reduktion": "Zwei Verlader, drei Spediteure, jeder mit jedem. Die Dynamik von Null liefert 1/2 für alle fünf, das ist kein Ergebnis eines Matchings; die Reduktion findet (1, 1, 0, 0, 0).",
    "Dreieck mit Anhang": "Dreieck 0-1-2 mit einem Anhang 3 an Betrieb 0: ausgewogen sind 3/4, 1/2, 1/2 und 1/4.",
    "Zufallsnetz zweiseitig 8 + 8": "Bis zu acht Verlader und acht Spediteure, jede Verbindung mit Wahrscheinlichkeit 30 Prozent; Betriebe ohne Verbindung entfallen. Der Zufalls-Seed legt das Netz fest.",
    "Größtes Netz (30 + 30, κ = 0,25)": "Bis zu 30 Verlader und 30 Spediteure mit langsamer Dämpfung: der Rechenaufwand liegt am Maximum der Demo.",
}
