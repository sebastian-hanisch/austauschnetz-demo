"""Texte der App: Einleitung, Erklärtexte, Annahmen und Formeln. Befundzahlen stehen hier nicht (sie kommen aus der Rechnung oder stehen in tests/test_claims.py)."""

INTRO = """
**Stück der Linie „Regeln setzen, verhandeln, kontrollieren“.** Verlader und Spediteure bilden ein **Netz**: eine Kante ist eine mögliche Tour mit einem Überschuss von 1 Euro (Einheitswert, im Modell normiert),
jeder Betrieb hat Kapazität für **eine** Tour. Wer tauscht mit wem, und wie teilen die beiden den Überschuss? Hier gibt es **keine Regeln und keine private Information** und keinen Ablauf: die Aufteilung
folgt allein aus der **Struktur**, weil die Alternative eines Betriebs davon abhängt, was sein Nachbar woanders bekommt. Die Demo rechnet, **wer im Netz Verhandlungsmacht hat**, was ein **ausgewogenes Ergebnis** ist
(jedes Paar teilt den Überschuss über den Alternativen gleich), wann es keines gibt, warum es **mehrere** geben kann und wie sich dieses Ergebnis zu Kern, Shapley-Wert und Nukleolus verhält.
`verhandlung-demo` hat zwei Betriebe und eine **gegebene** Außenoption; hier entsteht sie aus dem Netz und wirkt zurück.
Alle Zahlen sind **Modellannahmen**, keine Aussagen über echte Betriebe. Unten stehen die Erklärtabelle, die Annahmen („🚧 Wo die Annahmen enden“) und die Formeln („📐“).
"""

EXPLAINER = """
1. Das Netz: Betriebe als Knoten, mögliche Touren als Kanten mit Überschuss *w* (hier 1 Euro, im Literaturbeispiel und in Reiter 7 auch andere Werte). Jeder Betrieb tauscht **höchstens einmal**.
2. Ein **Ergebnis** besteht aus einem **Matching** (wer tauscht mit wem) und einer **Auszahlung** *y* je Betrieb: auf jedem Tauschpaar summieren sich die Auszahlungen zu *w*, Ungepaarte bekommen 0.
3. **Stabil** heißt: kein Paar auf einer Kante könnte sich gemeinsam besserstellen (*yᵤ* + *yᵥ* ≥ *w* auf jeder Kante). Die **stabile Spanne** eines Betriebs ist der Bereich seiner Auszahlung über alle stabilen Ergebnisse.
4. Die **Außenoption** von *u* gegenüber seinem Partner *v* ist das Beste, was *u* bei einem anderen Nachbarn *k* bekäme: *w*ᵤₖ − *y*ₖ (nie unter 0). Dabei bleibt die Auszahlung des Nachbarn fest.
5. **Ausgewogen** heißt: stabil, und auf jedem Tauschpaar teilen beide den Überschuss über ihren Außenoptionen gleich (Nash-Lösung mit Drohpunkt).
6. Gesucht wird so: der **Kantenausgleich** (eine lokale Dynamik) lässt Angebote und Außenoptionen hin- und herlaufen, bis nichts mehr ändert. Liefert die Dynamik von Null keine Auszahlung eines Matchings,
   hilft die **Reduktion**: Betriebe, deren Auszahlung schon die stabile Spanne festlegt, werden entfernt und die Dynamik läuft auf dem Rest. Ein **Prüfer** bestätigt jedes Ergebnis nach der Definition.

Das gezeigte Ergebnis ist das zuerst gefundene (Dynamik von Null, sonst Reduktion). Wo es mehrere ausgewogene Ergebnisse gibt (Reiter 4), ist das eine Auswahlregel dieser Demo.
"""

CONTROLS_TABLE = """
| Begriff / Regler | Bedeutung |
|---|---|
| **Netz** | Wahl der Struktur. Weg, Kreis, Stern, Spinne, vollständig zweiseitig und die Zufallsnetze nehmen die Zahl der Betriebe aus dem Regler; das Literaturbeispiel und die eigene Kantenliste haben ihre eigene Größe. |
| **Stabil** | Kein blockierendes Paar: auf jeder Kante ist *yᵤ* + *yᵥ* ≥ *w*. Existiert genau dann, wenn die LP-Relaxation des Matchings ganzzahlig ist. |
| **Stabile Spanne** | Kleinste und größte Auszahlung eines Betriebs über alle stabilen Ergebnisse (lineare Programme). Eine leere Spanne heißt: **festgelegt**; sonst **offen**. |
| **Außenoption** | Was ein Betrieb bei seinem besten anderen Nachbarn bekäme, wenn dessen Auszahlung gleich bliebe. |
| **Ausgewogen** | Stabil, und auf jedem Tauschpaar sind die Überschüsse über den Außenoptionen gleich. |
| **Kantenausgleich** | Die Dynamik, die Angebote und Außenoptionen auf jeder Kante aktualisiert; der Fixpunkt ist ein Kandidat für ein ausgewogenes Ergebnis. |
| **Dämpfung κ** | Wie stark ein Schritt den alten Wert durch den neuen ersetzt (1: ganz). Ändert die Zahl der Schritte; in den gemessenen Netzen blieb der Fixpunkt gleich (Reiter 3 zeigt es für das gewählte Netz). |
| **Reduktion** | Festgelegte Betriebe entfernen, die Dynamik nur auf den offenen laufen lassen, am ganzen Netz prüfen. |
| **Nukleolus, Shapley-Wert, Kern** | Lösungskonzepte des kooperativen Spiels „Wert einer Koalition = größtes Matching in ihrem Teilnetz“ (Reiter 6, höchstens 8 Betriebe). |
| **Ausstiegsprinzip** | Eigene Variante dieser Demo ohne Quelle: der Betrieb bekommt die Hälfte, mindestens seine Außenoption (Reiter 5). |
| **Zufalls-Seed** | Legt die Zufallsnetze der Netzwahl und die Zufallsstarts der Reiter 4 und 5 fest. |
"""

ASSUMPTIONS_MARKDOWN = """
**Annahmen**
- Einheitswert: jede mögliche Tour hat denselben Überschuss, außer im Literaturbeispiel, in eigenen Kantenlisten mit Werten und in Reiter 7.
- Jeder Betrieb tauscht höchstens einmal (Kapazität für eine Tour); der Überschuss einer Tour ist festgelegt, nur seine Aufteilung ist offen.
- Vollständige Information: alle kennen das Netz und alle Werte. Kein Ablauf, keine Geduld, keine Angebotsrunden: die Alternativen sind Gleichgewichtsbedingungen, kein Spiel mit Zügen (→ `verhandlung-demo`).
- Das ausgewogene Ergebnis ist eine **Gleichgewichtsauswahl**: Nash-Lösung mit Drohpunkt auf jeder Kante. Das Ausstiegsprinzip in Reiter 5 ist eine andere, eigene Auswahl.
- Kantenwerte sind ganze Zahlen; Euro je Tour und die Rollen Verlader und Spediteur sind Einkleidung. Das Modell kennt auch Netze ohne Rollen (allgemeine Zufallsnetze mit ungeraden Kreisen).
- Keine Daten echter Betriebe, keine Aussage über tatsächliche Verhandlungsmacht von Spediteuren oder Verladern.

**Grenzen**
- Ergebnisse in Reihen und in der App gelten für die gemessenen Netzklassen und für die Auswahlregel „Dynamik von Null, sonst Reduktion“, nicht für alle Netze.
- Live rechnet die Demo bis 60 Betriebe (zweiseitig 30 + 30); Kern, Shapley-Wert und Nukleolus nur bis 8 Betriebe (2⁸ Koalitionen).
- Mehrere Ergebnisse werden durch Suche gefunden (Dynamik von Null, Reduktion, Zufallsstarts): gefunden heißt „mindestens so viele“, nicht „genau so viele“.
- Das Ausstiegsprinzip hat im Netz weder Literaturgrundlage noch Eindeutigkeitsaussage; „kein Fixpunkt gefunden“ heißt nicht „keiner vorhanden“.
- Die Suche ist unvollständig: die Reduktion lehnt ab, wenn ein festgelegter Betrieb einem freien eine Außenoption bietet (bei einzelnen gewichteten Netzen und bei einem Teil der allgemeinen Zufallsnetze); dann bleibt es bei der Dynamik von Null oder bei „nicht gefunden“, auch wo ein stabiles Ergebnis existiert.
- Keine Spiele auf Netzen mit Aktionen (Netzwerkspiel, öffentliche Güter), keine Netzbildung, keine Mehrparteien-Koalitionsverhandlung: jede Einigung ist zweiseitig.

**Bekannte Probleme und Unsicherheiten**
- Die Quellen (Kleinberg und Tardos 2008; Bayati u. a.; Azar u. a.; Cook u. a. 1983) sind nur nach Abstract, Suchauszug und Teilen von Bayati u. a. eingeordnet, nicht im Volltext geprüft; die Zahlen der Demo sind eigene Messungen.
- Die Sätze „stabil existiert genau dann, wenn die LP-Lücke null ist“ und „zu jedem Netz mit stabilem Ergebnis gibt es ein ausgewogenes“ sind hier nicht bewiesen, sondern an Zufallsnetzen und dem Atlas aller kleinen zusammenhängenden Graphen geprüft.
- Die vorgerechneten Reihen sind Zählungen über vier Zufalls-Seeds und hängen vom Netz-Erzeuger ab; andere Erzeuger geben andere Anteile.
- Die Oberfläche ist im Browser nur stichprobenartig geprüft (Rechner und Telefonbreite).
"""

MATH_MARKDOWN = r"""
**Lesehilfe.** Gegeben: ein Graph mit Knoten (Betriebe) und Kanten $(u,v)$ mit Wert $w_{uv} > 0$. Gesucht: ein Matching $M$ und eine Auszahlung $y \ge 0$, die stabil und ausgewogen sind.

| Symbol | Bedeutung |
|---|---|
| $w_{uv}$ | Überschuss der Tour zwischen $u$ und $v$ |
| $M$ | Matching: Tauschpaare ohne gemeinsamen Betrieb |
| $y_u$ | Auszahlung von Betrieb $u$ (0 für Ungepaarte) |
| $a_{u\setminus v}$ | Außenoption von $u$ gegenüber seinem Partner $v$ |
| $\kappa$ | Dämpfung des Kantenausgleichs |
| $m_{i\to j}$ | Angebot von $i$ an $j$ in der Dynamik |

**Ergebnis und Stabilität.** Auf jedem Tauschpaar $(u,v)\in M$ gilt
$$y_u + y_v = w_{uv}.$$
Stabil heißt: auf jeder Kante $(u,v)$ des Netzes (auch außerhalb von $M$)
$$y_u + y_v \ge w_{uv}.$$

**Existenz stabiler Ergebnisse.** Das lineare Programm $\max \sum_e w_e x_e$ unter $\sum_{e \ni u} x_e \le 1$, $x \ge 0$ ist eine obere Schranke für das größte Matching $\nu$. Stabile Ergebnisse gibt es genau dann, wenn beide gleich sind (Sotomayor, laut Bayati u. a.); die stabilen Auszahlungen sind die optimalen Lösungen des dualen Programms
$$\min \sum_u y_u \quad \text{unter} \quad y_u + y_v \ge w_{uv}\ \text{für jede Kante},\ y \ge 0 .$$
Die **stabile Spanne** von $u$ ist $[\min y_u, \max y_u]$ über allen $y$ mit diesen Nebenbedingungen und $\sum_u y_u = \nu$.

**Außenoption und ausgewogen.**
$$a_{u\setminus v} = \max\Bigl(0,\ \max_{k \ne v}\ \bigl(w_{uk} - y_k\bigr)\Bigr).$$
Ein stabiles Ergebnis ist ausgewogen, wenn auf jedem Paar $(u,v)\in M$
$$y_u - a_{u\setminus v} = y_v - a_{v\setminus u}.$$

**Kantenausgleich** (Dynamik nach Bayati u. a.). Angebote auf jeder gerichteten Kante und Update der Außenoptionen:
$$m_{i\to j} = (w_{ij} - a_{i\setminus j})^+ - \tfrac12\,(w_{ij} - a_{i\setminus j} - a_{j\setminus i})^+,$$
$$a_{i\setminus j} \leftarrow (1-\kappa)\,a_{i\setminus j} + \kappa \max_{k \ne j} m_{k\to i},\qquad y_i = \max_k m_{k\to i}.$$

**Kooperatives Spiel.** Der Wert einer Koalition $S$ ist das größte Matching im Teilnetz auf $S$, geschrieben $v(S)$. Der Kern besteht aus allen $x$ mit
$$x(N) = v(N),\qquad x(S) \ge v(S)\ \text{für jede Koalition } S,$$
und fällt mit den stabilen Auszahlungen zusammen. Der Shapley-Wert ist
$$\varphi_i = \sum_{S \not\ni i} \frac{|S|!\,(n-|S|-1)!}{n!}\,\bigl(v(S \cup \{i\}) - v(S)\bigr).$$
Der Nukleolus minimiert lexikografisch die der Größe nach geordneten Überschüsse $v(S) - x(S)$.

**Zwei Lesarten einer Kante** (Wert $w$, Außenoptionen $a_u, a_v$ mit $a_u + a_v \le w$). Anteil von $v$: Nash mit Drohpunkt und das Ausstiegsprinzip (eigene Variante):
$$y_v^{\text{Nash}} = a_v + \tfrac12\,(w - a_u - a_v),\qquad y_v^{\text{Ausstieg}} = \min\bigl(\max(w/2,\ a_v),\ w - a_u\bigr).$$

**Quellen** (nach Abstract oder Auszug eingeordnet, nicht im Volltext geprüft): Kleinberg und Tardos, „Balanced Outcomes in Social Exchange Networks“, STOC 2008; Bayati, Borgs, Chayes, Kanoria, Montanari, „Bargaining dynamics in exchange networks“ (arXiv 1004.2079; Definitionen, Dynamik und Beispiel aus der ar5iv-Fassung, erste 100 000 von 215 260 Zeichen gelesen); Azar, Birnbaum, Celis, Devanur, Peres, „Convergence of Local Dynamics to Balanced Outcomes in Exchange Networks“ (arXiv 0907.4356, nur Abstract); Cook, Emerson, Gillmore, Yamagishi, „The Distribution of Power in Exchange Networks“, American Journal of Sociology 89 (1983).
"""
