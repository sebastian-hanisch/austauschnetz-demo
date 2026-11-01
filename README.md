# Wer hat im Netz Verhandlungsmacht? Das Austauschnetz – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-austauschnetz-demo.streamlit.app/)** -->

Stück der Linie **regeln-verhandeln** (Arbeitsname; Name, Bereich und Themenfeld werden erst bei der Einbindung in die Website festgelegt) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Der rote Faden der Linie: wer sich zuerst festlegt, lenkt. Dieses Stück ist der Gegenpol: **festgelegt wird nichts, die Struktur legt fest.** **Verlader und Spediteure** bilden ein **Netz**, eine Kante ist eine mögliche Tour mit einem Überschuss von 1 Euro (Einheitswert, im Modell normiert), jeder Betrieb hat Kapazität für **eine** Tour. Jede Einigung ist zweiseitig, es gibt keine Koalition, keine Regeln, keine private Information und keinen Ablauf: die vielen Beteiligten wirken nur über **Alternativen**, denn was ein Betrieb bei seinem Partner bekommt, hängt davon ab, was der Partner woanders bekäme. Die Demo rechnet, **wer im Netz Verhandlungsmacht hat**, was ein **stabiles** und was ein **ausgewogenes** Ergebnis ist (jedes Tauschpaar teilt den Überschuss über den Alternativen gleich: Nash-Lösung mit Drohpunkt), wann es keines gibt, warum es oft **mehrere** gibt, was der **Kantenausgleich** (eine lokale Dynamik) findet und was nicht, und wie sich das ausgewogene Ergebnis zu Kern, Shapley-Wert und Nukleolus verhält. **Netze, Überschüsse und Auszahlungen sind Modellannahmen, keine Aussagen über echte Betriebe.**

Abgrenzung: [`verhandlung-demo`](https://github.com/sebastian-hanisch/verhandlung-demo) rechnet zwei Betriebe mit Geduld, Angebot und Gegenangebot und einer **gegebenen** Außenoption (Zahl *o*); hier ist die Außenoption **endogen**: sie ist, was der Nachbar im Rest des Netzes bekommt, und wirkt zurück. [`kern-demo`](https://github.com/sebastian-hanisch/kern-demo) und [`shapley-demo`](https://github.com/sebastian-hanisch/shapley-demo) teilen einen Gewinn ohne Netz und ohne Ablauf (Vehikel dort: Spediteurs-Touren); das Austauschnetz ist als Zuordnungsspiel ein solches Spiel, und Reiter 6 rechnet dort Kern, Shapley-Wert und Nukleolus nach (Verweis, kein Doppel). `hungarian-demo` und `gale-shapley-demo` fragen, **welche Paarung** entsteht (Preise als Dualvariablen, Vorlieben ohne Geld); hier steht die Paarung fast fest, offen ist, **wie die Paare den Überschuss teilen**. `netzwerkspiel-demo` (Spiele auf Netzen) und die Nachbarstücke der Reihe „Märkte und Anreize“ haben Aktionen, die Nachbarn beeinflussen; hier gibt es keine Aktionen, nur die Aufteilung eines festen Überschusses. `einzelgut-auktion-demo` und `myerson-satterthwaite-demo` haben Regeln und private Werte; hier gibt es keines von beidem.

## Kernfrage

*Wer in einem Netz von Tauschmöglichkeiten hat Verhandlungsmacht, und was ist ein ausgewogenes Ergebnis?* Die Antwort hat fünf Teile. (1) **Macht folgt der Struktur, nicht der Zahl der Nachbarn.** Auf einem Weg mit 5 Betrieben bekommt die Mitte trotz zweier Nachbarn 0, ihre Nachbarn bekommen alles (exakt); in zweiseitigen Zufallsnetzen (8 + 8, p = 0,3) hängen Auszahlung und Grad zwar zusammen (Korrelation 0,46, Bäume 0,69), aber auf 117 von 1323 Tauschkanten mit ungleichem Grad bekommt der Betrieb mit dem höheren Grad weniger. (2) **Stabil und ausgewogen:** stabile Ergebnisse gibt es genau dann, wenn die LP-Relaxation des Matchings ganzzahlig ist; zweiseitige Netze und Bäume haben immer eines (720 von 720 Netze), Dreiecke und ungerade Kreise keines. In allen 1352 Zufallsnetzen mit stabilem Ergebnis fand die Demo ein vom Prüfer bestätigtes ausgewogenes. (3) **Das ausgewogene Ergebnis ist oft nicht eindeutig:** schon der Kreis mit 4 Betrieben hat die Familie (*a*, 1−*a*, *a*, 1−*a*) für jedes *a* in [0, 1]; in 91 von 240 zweiseitigen 8 + 8-Netzen fanden die Wege mindestens zwei, in Bäumen 0 von 240. „Das“ Ergebnis der Anzeige ist deshalb eine Auswahlregel. (4) **Der Kantenausgleich ist ein Kandidat, kein Beweis:** sein Fixpunkt von Null ist in 165 von 200 zweiseitigen Netzen ein ausgewogenes Ergebnis (nicht abhängig von der Dämpfung), in den übrigen gehört er zu keinem Matching; die Reduktion (festgelegte Betriebe entfernen) behebt das. (5) **Der Nukleolus wählt aus den ausgewogenen Ergebnissen eines:** in 76 von 76 Netzen mit nicht leerem Kern war er selbst ausgewogen; der Shapley-Wert lag in 10 von 96 Netzen im Kern und war in 0 von 76 gleich dem ausgewogenen Ergebnis. Alle Zahlen sind eigene Messungen mit den Voraussetzungen der jeweiligen Zeile (Netzklasse, Auswahlregel, Zufalls-Seeds).

## Befunde und Korrekturen gegenüber dem Plan

Der Einzelplan (Vormessung vom 2026-11-01, Wegwerfskripte mit numpy- und networkx-Strömen) wurde nicht blind übernommen; jede Zahl ist im Bau neu gemessen, mit SplitMix64-Strömen. Abweichungen und neue Funde:

- **Die „46 von 300“ der Märkte-Vorstufe sind kein Beleg für Nichtexistenz.** Die Märkte-Vorstufe (Stück 1 der Märkte-Linie) meldete bei 46 von 300 zweiseitigen 8 + 8-Netzen (p = 0,3) kein ausgewogenes Ergebnis. Die Vormessung des Plans fand in allen 46 ein stabiles Ergebnis (LP-Kriterium) und führte den Fehlschlag auf das Verfahren zurück; **die 46 Netze selbst sind hier nicht neu erzeugt** (anderer Zufallsstrom, das Verfahren der Vorstufe ist nicht nachgebaut), diese Zahl bleibt eine Angabe der Vormessung. Hier gemessen, mit eigenem Strom: in 240 von 240 zweiseitigen 8 + 8-Netzen (p = 0,3) existiert ein stabiles Ergebnis, die Dynamik von Null allein lieferte in 36 von 240 (15,0 %) kein Ergebnis eines Matchings, die Reduktion fand es in 240 von 240. Die Größenordnung (46 von 300 sind 15,3 %) passt zu einem Verfahrensmangel; dass es derselbe Mangel war, ist nicht nachgewiesen.
- **„Ausgewogen, aber nicht stabil“ kann es nach der Definition nicht geben** (ausgewogen ist stabil plus gleiche Aufteilung). Die Zeile des Plans „kein Netz hat ein ausgewogenes ohne stabiles“ war deshalb keine Messung und steht hier nicht als Befund. Gemessen ist die andere Richtung: zu jedem der 1352 Zufallsnetze mit stabilem Ergebnis und zu 126 von 126 stabilen Graphen des Atlas fand die Demo ein ausgewogenes Ergebnis (H5).
- **Zahlen weichen von der Vormessung ab, die Richtung bleibt** (SplitMix64 statt numpy, Auffüllen auf mindestens vier Kanten statt Neuziehen): mehrere ausgewogene Ergebnisse in 91 von 240 zweiseitigen 8 + 8-Netzen (Plan 100 von 240), 46 von 200 allgemeinen (Plan 51 von 206), 0 von 240 Bäumen (Plan 0 von 240); Fixpunkt von Null ausgewogen in 165 von 200 (Plan 168 von 200); Nukleolus ausgewogen in 76 von 76 (Plan 78 von 78); Shapley-Wert im Kern in 10 von 96 (Plan 11 von 96); Korrelation Auszahlung–Grad 0,46 (Plan 0,44); zusätzliche Kante senkt die Auszahlung eines Endbetriebs in 2 von 320 Beobachtungen (Plan 7 von 320). Der Atlas stimmt überein: 126 von 142 Graphen mit stabilem Ergebnis, 43 mit mehreren ausgewogenen, davon 7 zweiseitig.
- **Reduktion verallgemeinert.** Der Plan ließ die Reduktion nur zu, wenn alle festen Werte 0 oder 1 sind. Hier gilt die weichere Bedingung „kein fester Betrieb bietet einem freien eine Außenoption (Kantenwert minus fester Auszahlung ist nicht positiv)“, die für Einheitswerte die alte einschließt und auch gewichtete Netze trägt; jedes Ergebnis prüft der Prüfer am ganzen Netz. Abgelehnt wurde die Reduktion in 5 / 21 / 45 Netzen der allgemeinen Klassen (Plan mit der engen Bedingung: 10 / 126 / 89); die Dynamik von Null fand dort das Ergebnis.
- **Neue Klasse zweiseitig 6 + 6 (p = 0,5):** in 183 von 240 Netzen mehrere ausgewogene Ergebnisse (Untergrenze), also deutlich häufiger als bei 8 + 8 mit p = 0,3 (91 von 240). **Gegenprobe zu den Zufallsstarts:** mit 20 statt fünf Zufallsstarts finden die Wege in den 240 8 + 8-Netzen 91 statt 91 mit mehreren Ergebnissen; die Zahl blieb in diesen Netzen gleich, bleibt aber eine Untergrenze.
- **Gefundene Grenze der Suche bei gewichteten Netzen:** in Reiter 7 fand das Verfahren nach dem Anfügen eines Blattknotens in 1 von 160 Netzen kein ausgewogenes Ergebnis, obwohl in zweiseitigen Netzen ein stabiles existiert (die Reduktion lehnt ab, weil ein festgelegter Betrieb einem freien eine Außenoption bietet). Ein weiteres Beispiel (zweiseitig, 9 Betriebe, Kantenwerte 1 und 2) steht als Test `test_known_limit_of_the_search_a_weighted_net_with_stable_outcome_but_no_result`; in den Reihen mit Einheitswerten kam das nicht vor. Die App meldet „nicht gefunden“ statt einer Zahl. Eine Erweiterung der Reduktion um die Außenoptionen der festgelegten Betriebe ist nicht gebaut.
- **Festgelegt auf 0 und auf 1 in gleicher Zahl bei den offenen Betrieben ist keine Messung:** „offen, weniger“ und „offen, mehr“ sind in jeder Klasse gleich, weil auf jedem Tauschpaar die Auszahlungen zu 1 summieren und beide Partner offen oder beide festgelegt sind. Der Plan hatte die Verteilung als Befund geführt.
- **Gewichtete Netze nur mit ganzzahligen Werten:** Skalierfaktoren 2, 3 und 7 statt 0,1; 2,5; 7,0. Kantenwerte stehen im Literaturbeispiel, in eigenen Kantenlisten und in Reiter 7.
- **Ausstiegsprinzip als Reiter aufgenommen, ausdrücklich als eigene Variante ohne Quelle.** Die Suche braucht außer der Dynamik von Null Starts beim ausgewogenen Ergebnis und bei stabilen Zufallsauszahlungen: auf Weg 3 liefert die Dynamik von Null allein 1/2 für alle drei Betriebe, das gehört zu keinem Matching.
- **Sieben Reiter statt sechs:** „Stabil und ausgewogen“ (Existenz, Verfahren) und „Eigenschaften“ sind eigene Reiter. Reiter 4 (Suche nach mehreren Ergebnissen) rechnet bei mehr als 24 Betrieben und Reiter 7 bei mehr als 16 Betrieben erst auf Klick.
- **scipy ist Laufzeitbibliothek** (LP für die stabile Spanne, ganzzahliges Programm für das Matching, Nukleolus), wie im Plan vorgesehen; im Kern steht kein eigener Simplex. networkx wird nur in den Tests und im Erzeuger des Atlas gebraucht.
- **Port 9230** statt 9228 (9228 war im Plan nur ein Vorschlag, andere Stücke belegten Nachbarports).

## Modell

Ein Graph, Kante (*u*, *v*) mit Überschuss *w* > 0 (ganze Zahl, meist 1). Ein **Ergebnis** besteht aus einem Matching *M* und einer Auszahlung *y* ≥ 0 mit *yᵤ* + *yᵥ* = *w* auf jedem Paar von *M* und *y* = 0 für Ungepaarte. **Stabil:** *yᵤ* + *yᵥ* ≥ *w* auf **jeder** Kante (kein blockierendes Paar). Die **Außenoption** von *u* gegenüber dem Partner *v* ist *a*ᵤ = max(0, max über Nachbarn *k* ≠ *v* von (*w*ᵤₖ − *y*ₖ)): die Auszahlung des Nachbarn bleibt fest. **Ausgewogen:** stabil, und auf jedem Paar gilt *yᵤ* − *a*ᵤ = *yᵥ* − *a*ᵥ, der Überschuss über den Außenoptionen wird gleich geteilt (Nash-Lösung mit Drohpunkt). Stabile Ergebnisse gibt es genau dann, wenn die LP-Relaxation des Matchings ganzzahlig ist (Sotomayor, laut Bayati u. a.); ausgewogene gibt es laut Kleinberg und Tardos dann stets (laut Bayati u. a., Volltext nicht gelesen): hier gemessen, nicht bewiesen. Die **stabile Spanne** eines Betriebs sind kleinste und größte Auszahlung über alle stabilen Ergebnisse (zwei lineare Programme je Betrieb); ist sie leer, ist der Betrieb **festgelegt**. Alle Formeln stehen im 📐-Expander der App (je Display-Gleichung ein `$$`-Block).

## Methodik

- **Kern in kleinen Einheiten** (DEMO-PLAYBOOK §1b), je eine Regel als Funktion: `max_matching_weight`, `lp_matching_value`, `stable_range`, `fixed_nodes`, `is_stable`, `outside_option`, `is_balanced` (mit Brüchen und Toleranz 0 exakt), `edge_offers`, `balancing_step`, `run_dynamics`, `balanced_matching`, `by_reduction`, `balanced_outcome`, `exact_balanced`, `coalition_matching_values`, `shapley`, `nucleolus`, `is_principle`. Jede Einheit ist an von Hand gerechneten Mini-Netzen geprüft (`tests/conftest.py`).
- **Kantenausgleich** (`aun_balanced.py`): Dynamik nach Bayati u. a. auf den gerichteten Kanten, vektorisiert (Matrix der Angebote an einen Betrieb); Abbruch, wenn die größte Änderung unter 10⁻¹³ liegt. Danach sucht das größte Matching aus den straffen Kanten (ganzzahliges Programm) ein Matching, das zu den Auszahlungen passt, und der Prüfer bestätigt es nach der Definition. Schlägt das fehl, kommt die **Reduktion**: festgelegte Betriebe entfernen, Dynamik auf dem freien Teilnetz, Prüfer am ganzen Netz.
- **Exakte Bestätigung** (`aun_exact.py`): aus Matching und der Wahl der Außenoptionen ein lineares System in Brüchen aufstellen (Gauß), lösen, mit dem Prüfer (Toleranz 0) bestätigen; bei einer Familie von Ergebnissen (Kreis 4) ist das System singulär, dann bleibt das Runden. Bis 24 Betriebe wird das Ergebnis so zusätzlich bestätigt, wo das System eindeutig lösbar ist oder die gerundete Zahl exakt besteht; die App zeigt es dann als Bruch.
- **Mehrere Ergebnisse** (`aun_multi.py`): Dynamik von Null, Reduktion und Zufallsstarts (gleichverteilte Außenoptionen); zwei Ergebnisse gelten als verschieden, wenn ein Betrieb um mehr als 10⁻⁶ abweicht. Das Ergebnis ist eine **Untergrenze** der Zahl ausgewogener Ergebnisse.
- **Spiel** (`aun_game.py`): Wert einer Koalition = größtes Matching im Teilnetz (alle 2ⁿ Mengen), Shapley-Wert in Brüchen, Kern über alle Koalitionsungleichungen, Nukleolus als Folge linearer Programme (Maschler, Peleg, Shapley) mit linear unabhängigen Fesseln; höchstens 8 Betriebe.
- **Ausstiegsprinzip** (`aun_principle.py`, eigene Variante ohne Quelle): Anteil *y*ᵥ = min(max(*w*/2, *a*ᵥ), *w* − *a*ᵤ); Fixpunkt per Dynamik mit dieser Regel von Null, vom ausgewogenen Ergebnis und von stabilen Zufallsauszahlungen, Prüfer `is_principle`.
- **Vorgerechnete Reihen** (`tools/make_grid.py` → `data/tables.json`, Erzeuger-Hash, vier Zufalls-Seeds 11 / 22 / 33 / 44, Netze aus SplitMix64 ohne Python-`hash`): Existenz und Verfahren, Macht gegen Grad, Anteil stabil, Schritte der Dynamik, Mehrdeutigkeit, Ausstiegsprinzip, Kern/Shapley/Nukleolus, Eigenschaften; dazu der Atlas aller 142 zusammenhängenden Graphen mit 2 bis 6 Knoten (`tools/make_atlas.py`, networkx nur im Erzeuger; Datei `data/atlas_graphs.json`). Je Klasse und Seed 60 Netze; Zählungen über alle vier Seeds, Mittel ± Standardabweichung über die Seeds, wo angegeben.
- **Rechenzeit am Maximum** (60 Betriebe, einmal gemessen auf Windows mit Python 3.14, keine Testbedingung): die Hauptansicht (LP-Lücke, stabile Spanne, Kantenausgleich, Prüfer, exakte Bestätigung) braucht bei zweiseitigen Zufallsnetzen mit 60 Betrieben bei p = 5 % bis 95 % 0,25 bis 0,7 s, beim allgemeinen Zufallsnetz mit p = 95 % (1 688 Kanten) 1,3 s; die Suche nach mehreren Ergebnissen (Reiter 4) bis 2,9 s (Weg mit 60 Betrieben), Reiter 7 bis 6,8 s (Kreis mit 60 Betrieben); darum rechnen Reiter 4 und 7 bei großen Netzen erst auf Klick. Davon entfallen 0,23 bis 0,54 s auf die zwei linearen Programme je Betrieb für die stabile Spanne (30 + 30 Betriebe, p = 5 % bis 95 %).
- **Orakel:** Aufzählung aller isolierten ausgewogenen Ergebnisse in Brüchen (lineare Systeme je Wahl der Außenoptionen), Zulässigkeits-Programm je größtem Matching, alle Koalitionsungleichungen (Kern) mit scipy, Schleifenfassung des Kantenausgleichs, networkx (Matching, Zwischenzentralität), Shapley als Mittel über alle Reihenfolgen, Kohlberg-Kriterium für den Nukleolus (Abschnitt „Tests“).

## Befunde (gemessen, keine Behauptungen)

Hypothesen des Einzelplans und Stand nach dem Bau. „Teilweise“ heißt: gilt unter den genannten Bedingungen, nicht allgemein. Zufallsnetze: Zählungen über vier Zufalls-Seeds, ausgewogenes Ergebnis = das zuerst gefundene (Dynamik von Null, sonst Reduktion), Mehrdeutigkeit = Untergrenze.

| Nr. | Hypothese | Stand und Beleg |
|---|---|---|
| H1 | Weg 3: die Mitte bekommt alles; Weg 5: die Mitte bekommt 0; Weg 4: 1/3 und 2/3 | **Ja**, exakt (Brüche, vom Prüfer bestätigt; Weg 3, Weg 4 und das Literaturbeispiel zusätzlich von der Aufzählung): Weg 3 (0, 1, 0), Weg 4 (1/3, 2/3, 2/3, 1/3), Weg 5 (0, 1, 0, 1, 0); Literaturbeispiel mit den Werten 8, 6, 2: (3/2, 13/2, 1, 1), gleich dem Beispiel bei Bayati u. a. (1,5; 6,5; 1; 1; ar5iv-Text, nicht PDF) |
| H2 | Der Randknoten eines Wegs mit 2*k* Knoten bekommt 1/(*k* + 1) | **Ja** für *k* = 1 bis 7 (Wege mit 2 bis 14 Knoten, exakt), 4 Knoten: 1/3, 8: 1/5, 12: 1/7; Wege mit ungerader Knotenzahl 3 bis 13 zeigen abwechselnd 0 und 1; die Formel steht aus den Zeilen, nicht bewiesen |
| H3 | Kreis 4: alle 1/2 (Märkte-Vorstufe) | **Teilweise**: 1/2 ist ein Element der Familie (*a*, 1−*a*, *a*, 1−*a*), in Brüchen bestätigt für *a* = 0; 1/5; 1/3; 1/2; 4/5; 1; das Paar (1/5, 4/5, 1/2, 1/2) ist nicht ausgewogen; Kreis 6 mit *a* = 1/5 ebenfalls |
| H4 | Stabil existiert genau dann, wenn die LP-Relaxation ganzzahlig ist; zweiseitig und Bäume immer | **Ja** an 142 Atlas-Graphen und Zufallsnetzen (drei Wege: LP-Lücke, Zulässigkeits-Programm je größtem Matching, Koalitionsungleichungen; Orakel-Test); zweiseitig und Bäume 720 von 720 stabil; allgemein 200 von 240 / 224 von 240 / 208 von 240 |
| H5 | Zu jedem Netz mit stabilem Ergebnis gibt es ein ausgewogenes | **Gestützt, nicht bewiesen:** in 1352 von 1352 Zufallsnetzen und 126 von 126 Atlas-Graphen gefunden; nur die Dynamik von Null fand es in 1285 der 1352. Die Gegenrichtung gilt nach der Definition |
| H6 | „46 von 300 ohne ausgewogenes Ergebnis“ (Märkte-Vorstufe) ist Nichtexistenz | **Nein**: Verfahrensmangel laut Vormessung des Plans (46 von 46 stabil, hier nicht neu erzeugt); gemessen hier: Dynamik von Null ohne Ergebnis in 36 von 240 8 + 8-Netzen, Reduktion 240 von 240 |
| H7 | Der Fixpunkt des Kantenausgleichs von Null ist ein ausgewogenes Ergebnis | **Nein**: 165 von 200 (gleich für alle vier Dämpfungen); K2,3: Fixpunkt 1/2 für alle fünf (Summe 2,5 über dem größten Matching 2), richtig ist (1, 1, 0, 0, 0). Mit Reduktion 1352 von 1352 |
| H8 | Das ausgewogene Ergebnis ist eindeutig | **Nein**: zweiseitig 8 + 8 in 91 von 240 Netzen mehrere gefunden (Untergrenze; mit 20 Zufallsstarts 91 von 240), Bäume 0 von 240, allgemein 8 Knoten 46 von 200; Atlas 43 von 126 stabilen Graphen |
| H9 | Macht ist nicht Zentralität | **Teilweise**: Korrelation Auszahlung–Grad 0,46 (zweiseitig 8 + 8; je Seed 0,44 bis 0,48), 0,58 (allgemein), 0,69 (Bäume); der höhere Grad bekommt weniger auf 117 von 1323 / 11 von 532 / 10 von 874 Tauschkanten mit ungleichem Grad; die Mitte von Weg 5 (Auszahlung 0 trotz zweier Nachbarn) ist ein Handbeispiel; wie oft der höhere Grad in Zufallsnetzen weniger bekommt, zählen die Zahlen davor |
| H10 | Der Nukleolus ist ausgewogen, der Shapley-Wert nicht | **Ja als Messung**: Nukleolus ausgewogen in 76 von 76 Netzen mit nicht leerem Kern, ausgewogenes Ergebnis im Kern in 76 von 76; Shapley-Wert im Kern in 10 von 96, gleich dem ausgewogenen Ergebnis in 0 von 76; als Satz nicht belegt; Handnetze: Weg 4 Shapley (5/12, 7/12, 7/12, 5/12), Weg 5 Shapley nicht im Kern |
| H11 | Nash mit Drohpunkt und Ausstiegsprinzip teilen im Netz verschieden | **Ja** (Ausstiegsprinzip ist eine eigene Variante ohne Quelle): Weg 4 (1/3, 2/3, 2/3, 1/3) gegen (1/2, 1/2, 1/2, 1/2); gleiche Auszahlungen nur in 108 von 240 / 130 von 240 / 90 von 200 Netzen (zweiseitig / Baum / allgemein) |
| H12 | Eine Alternative mehr senkt die Auszahlung nie | **Teilweise**: neuer Blattknoten senkt die Auszahlung seines Betriebs in 0 von 159 Fällen (steigt in 84); eine neue Kante zwischen zwei Betrieben senkt die Auszahlung eines Endbetriebs in 2 von 320 Beobachtungen; beide nicht schlechter in 158 von 160 Netzen (gewichtete zweiseitige 8 + 8-Netze; bei Mehrdeutigkeit kann ein Teil Auswahl sein); nach dem Anfügen eines Blattknotens fand das Verfahren in 1 von 160 Netzen kein Ergebnis (die Reduktion lehnte ab), obwohl in zweiseitigen Netzen ein stabiles existiert |

**Handnetze** (Einheitswert, Knoten 0, 1, 2, ... in der Reihenfolge der Kanten; exakt in Brüchen):

| Netz | Betriebe | Auszahlungen (Betrieb 0, 1, ...) | Verfahren | mehrere ausgewogene gefunden |
|---|---|---|---|---|
| Weg mit 3 Betrieben | 3 | 0, 1, 0 | Dynamik von Null | nein |
| Weg mit 4 Betrieben | 4 | 1/3, 2/3, 2/3, 1/3 | Dynamik von Null | nein |
| Weg mit 5 Betrieben | 5 | 0, 1, 0, 1, 0 | Dynamik von Null | nein |
| Weg mit 6 Betrieben | 6 | 1/4, 3/4, 1/2, 1/2, 3/4, 1/4 | Dynamik von Null | nein |
| Weg mit 7 Betrieben | 7 | 0, 1, 0, 1, 0, 1, 0 | Dynamik von Null | nein |
| Stern mit 3 Blättern | 4 | 1, 0, 0, 0 | Dynamik von Null | nein |
| Spinne mit drei Beinen der Länge 2 | 7 | 0, 1, 0, 1, 0, 1, 0 | Dynamik von Null | nein |
| Kreis mit 4 Betrieben | 4 | 1/2, 1/2, 1/2, 1/2 | Dynamik von Null | ja |
| Vollständiges Netz mit 4 Betrieben | 4 | 1/2, 1/2, 1/2, 1/2 | Dynamik von Null | nein |
| Dreieck mit Anhang | 4 | 3/4, 1/2, 1/2, 1/4 | Dynamik von Null | nein |
| Weg mit den Werten 8, 6, 2 | 4 | 3/2, 13/2, 1, 1 | Dynamik von Null | nein |
| Zweiseitig 2 + 3 | 5 | 1, 1, 0, 0, 0 | Reduktion | nein |
| Dreieck | 3 | kein stabiles Ergebnis | – | – |
| Kreis mit 5 Betrieben | 5 | kein stabiles Ergebnis | – | – |

**Wege mit 2 bis 14 Betrieben** (ausgewogene Auszahlungen, exakt):

| Betriebe | Auszahlungen (exakt) |
|---|---|
| 2 | 1/2, 1/2 |
| 3 | 0, 1, 0 |
| 4 | 1/3, 2/3, 2/3, 1/3 |
| 5 | 0, 1, 0, 1, 0 |
| 6 | 1/4, 3/4, 1/2, 1/2, 3/4, 1/4 |
| 7 | 0, 1, 0, 1, 0, 1, 0 |
| 8 | 1/5, 4/5, 2/5, 3/5, 3/5, 2/5, 4/5, 1/5 |
| 9 | 0, 1, 0, 1, 0, 1, 0, 1, 0 |
| 10 | 1/6, 5/6, 1/3, 2/3, 1/2, 1/2, 2/3, 1/3, 5/6, 1/6 |
| 11 | 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0 |
| 12 | 1/7, 6/7, 2/7, 5/7, 3/7, 4/7, 4/7, 3/7, 5/7, 2/7, 6/7, 1/7 |
| 13 | 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0 |
| 14 | 1/8, 7/8, 1/4, 3/4, 3/8, 5/8, 1/2, 1/2, 5/8, 3/8, 3/4, 1/4, 7/8, 1/8 |

**Kreis mit 4 Betrieben: die Familie** (Matching 0-1 und 2-3, vom Prüfer in Brüchen bestätigt):

| a | Ergebnis | ausgewogen (Brüche) |
|---|---|---|
| 0 | 0, 1, 0, 1 | ja |
| 1/5 | 1/5, 4/5, 1/5, 4/5 | ja |
| 1/3 | 1/3, 2/3, 1/3, 2/3 | ja |
| 1/2 | 1/2, 1/2, 1/2, 1/2 | ja |
| 4/5 | 4/5, 1/5, 4/5, 1/5 | ja |
| 1 | 1, 0, 1, 0 | ja |
| 1/5 und 1/2 (nicht symmetrisch) | 1/5, 4/5, 1/2, 1/2 | nein |

**Eine Kante, Wert 1: Anteil von v** (Nash mit Drohpunkt gegen Ausstiegsprinzip, eigene Variante ohne Quelle):

| (a_u; a_v) | Nash mit Drohpunkt | Ausstiegsprinzip | gleich |
|---|---|---|---|
| (0; 0) | 1/2 | 1/2 | ja |
| (0; 1/3) | 2/3 | 1/2 | nein |
| (0; 3/5) | 4/5 | 3/5 | nein |
| (1/5; 3/5) | 7/10 | 3/5 | nein |
| (1/4; 1/4) | 1/2 | 1/2 | ja |
| (2/5; 2/5) | 1/2 | 1/2 | ja |

**Kleine Netze, LP-Wert gegen ganzzahliges Matching:**

| Netz | Knoten | LP-Wert | ganzzahlig | stabil |
|---|---|---|---|---|
| Weg mit 4 Knoten | 4 | 2,00 | 2 | ja |
| Kreis mit 4 Knoten | 4 | 2,00 | 2 | ja |
| Kreis mit 6 Knoten | 6 | 3,00 | 3 | ja |
| Dreieck | 3 | 1,50 | 1 | nein |
| Kreis mit 5 Knoten | 5 | 2,50 | 2 | nein |
| Kreis mit 7 Knoten | 7 | 3,50 | 3 | nein |
| Vollständiges Netz mit 4 Knoten | 4 | 2,00 | 2 | ja |
| Vollständiges Netz mit 5 Knoten | 5 | 2,50 | 2 | nein |
| Zweiseitig 2 + 3 | 5 | 2,00 | 2 | ja |
| Dreieck mit Anhang | 4 | 2,00 | 2 | ja |

**Existenz und Verfahren** (60 Netze je Klasse und Zufalls-Seed, vier Zufalls-Seeds):

| Netzklasse | Netze | stabil | Dynamik von Null | Reduktion | Reduktion abgelehnt (fester Knoten bietet Option) | eines von beiden | von keinem | Dynamik von Null ohne Matching-Ergebnis |
|---|---|---|---|---|---|---|---|---|
| zweiseitig 8 + 8, p = 0,3 | 240 | 240 | 204 | 240 | 0 | 240 | 0 | 36 |
| zweiseitig 6 + 6, p = 0,5 | 240 | 240 | 217 | 240 | 0 | 240 | 0 | 23 |
| Baum mit 10 Knoten | 240 | 240 | 240 | 240 | 0 | 240 | 0 | 0 |
| allgemein, 8 Knoten, p = 0,3 | 240 | 200 | 196 | 195 | 5 | 200 | 0 | 4 |
| allgemein, 8 Knoten, p = 0,5 | 240 | 224 | 223 | 203 | 21 | 224 | 0 | 1 |
| allgemein, 12 Knoten, p = 0,3 | 240 | 208 | 205 | 163 | 45 | 208 | 0 | 3 |

Anteil der allgemeinen Zufallsnetze mit stabilem Ergebnis (100 Netze je Zelle und Seed; Mittel ± Standardabweichung über vier Seeds):

| Kantenwahrscheinlichkeit p | 8 Knoten | 12 Knoten |
|---|---|---|
| 15 % | 95,0 ± 2,2 % | 89,5 ± 1,3 % |
| 20 % | 91,5 ± 1,7 % | 84,0 ± 1,4 % |
| 30 % | 85,5 ± 4,5 % | 82,8 ± 6,2 % |
| 40 % | 86,5 ± 1,9 % | 94,2 ± 2,6 % |
| 50 % | 95,5 ± 1,7 % | 99,5 ± 0,6 % |
| 60 % | 98,0 ± 1,2 % | 100,0 ± 0,0 % |
| 80 % | 100,0 ± 0,0 % | 100,0 ± 0,0 % |

Nicht monoton in *p*: bei 8 Knoten fällt der Anteil von 95,0 ± 2,2 % (p = 15 %) auf 85,5 ± 4,5 % (p = 30 %) und steigt dann auf 100,0 ± 0,0 %; bei 12 Knoten von 89,5 ± 1,3 % auf 82,8 ± 6,2 % und 100,0 ± 0,0 %. Die Streuung über die Seeds ist bei p = 30 % am größten (bis 6,2 Prozentpunkte).

**Macht gegen Grad** (Betriebe mit stabilem Ergebnis):

| Netzklasse | Netze mit stabilem Ergebnis | Betriebe | Korrelation mit Grad | Korrelation mit Zwischenzentralität | Tauschkanten mit ungleichem Grad | davon: höherer Grad bekommt weniger | davon: gleich viel |
|---|---|---|---|---|---|---|---|
| zweiseitig 8 + 8, p = 0,3 | 240 | 3594 | 0,46 | 0,39 | 1323 | 117 | 361 |
| zweiseitig 6 + 6, p = 0,5 | 240 | 2849 | 0,38 | 0,39 | 1152 | 39 | 735 |
| Baum mit 10 Knoten | 240 | 2400 | 0,69 | 0,54 | 874 | 10 | 104 |
| allgemein, 8 Knoten, p = 0,3 | 200 | 1489 | 0,58 | 0,51 | 532 | 11 | 144 |
| allgemein, 8 Knoten, p = 0,5 | 224 | 1787 | 0,41 | 0,49 | 719 | 1 | 573 |
| allgemein, 12 Knoten, p = 0,3 | 208 | 2466 | 0,44 | 0,45 | 1016 | 13 | 672 |

**Festgelegte und offene Betriebe:**

| Netzklasse | Betriebe | festgelegt auf 0 | festgelegt auf 1 | festgelegt auf anderen Wert | offen | offen, genau 1/2 | offen, weniger | offen, mehr |
|---|---|---|---|---|---|---|---|---|
| zweiseitig 8 + 8, p = 0,3 | 3594 | 937 | 697 | 0 | 1960 | 1066 | 447 | 447 |
| zweiseitig 6 + 6, p = 0,5 | 2849 | 228 | 175 | 0 | 2446 | 1856 | 295 | 295 |
| Baum mit 10 Knoten | 2400 | 830 | 460 | 0 | 1110 | 300 | 405 | 405 |
| allgemein, 8 Knoten, p = 0,3 | 1489 | 305 | 180 | 92 | 912 | 396 | 258 | 258 |
| allgemein, 8 Knoten, p = 0,5 | 1787 | 32 | 19 | 956 | 780 | 508 | 136 | 136 |
| allgemein, 12 Knoten, p = 0,3 | 2466 | 182 | 130 | 1164 | 990 | 514 | 238 | 238 |

**Schritte der Dynamik von Null** (200 zweiseitige 8 + 8-Netze, p = 0,3; die Fixpunkte weichen über die Dämpfungen höchstens um 2,1·10⁻¹¹ ab):

| κ | Schritte, Median | Schritte, 90-%-Quantil | konvergiert | Fixpunkt ausgewogen |
|---|---|---|---|---|
| 0,25 | 485 | 2258 | 200 von 200 | 165 von 200 |
| 0,50 | 243 | 1154 | 200 von 200 | 165 von 200 |
| 0,75 | 160 | 778 | 200 von 200 | 165 von 200 |
| 1,00 | 128 | 587 | 200 von 200 | 165 von 200 |

**Schritte über der Netzgröße** (zweiseitig n + n, mittlerer Grad 3, κ = 0,5, Dynamik von Null):

| Betriebe (n + n) | Netze | Schritte, Median | Schritte, Maximum | konvergiert | Fixpunkt ausgewogen |
|---|---|---|---|---|---|
| 8 + 8 | 20 | 52 | 1470 | 20 von 20 | 15 von 20 |
| 16 + 16 | 20 | 213 | 2644 | 20 von 20 | 13 von 20 |
| 32 + 32 | 20 | 321 | 3602 | 20 von 20 | 7 von 20 |
| 64 + 64 | 20 | 927 | 10450 | 20 von 20 | 6 von 20 |
| 128 + 128 | 20 | 1213 | 24280 | 20 von 20 | 6 von 20 |

**Mehrere ausgewogene Ergebnisse** (Netze mit stabilem Ergebnis; gefunden von Dynamik von Null, Reduktion und fünf Zufallsstarts):

| Netzklasse | Netze mit stabilem Ergebnis | mit mindestens zwei ausgewogenen Ergebnissen | je Zufalls-Seed | größte Abweichung eines Betriebs, Median | Maximum |
|---|---|---|---|---|---|
| zweiseitig 8 + 8, p = 0,3 | 240 | 91 | 16 / 27 / 25 / 23 | 0,140 | 0,301 |
| zweiseitig 6 + 6, p = 0,5 | 240 | 183 | 41 / 50 / 50 / 42 | 0,146 | 0,301 |
| Baum mit 10 Knoten | 240 | 0 | 0 / 0 / 0 / 0 | – | – |
| allgemein, 8 Knoten, p = 0,3 | 200 | 46 | 11 / 10 / 11 / 14 | 0,141 | 0,331 |
| allgemein, 8 Knoten, p = 0,5 | 224 | 71 | 18 / 20 / 14 / 19 | 0,127 | 0,241 |
| allgemein, 12 Knoten, p = 0,3 | 208 | 55 | 12 / 12 / 17 / 14 | 0,116 | 0,229 |

**Atlas** aller zusammenhängenden Graphen mit 2 bis 6 Knoten (Einheitswert; zwölf Wege je Graph):

| Knoten | Graphen | mit stabilem Ergebnis | mit mindestens zwei ausgewogenen |
|---|---|---|---|
| 2 | 1 | 1 | 0 |
| 3 | 2 | 1 | 0 |
| 4 | 6 | 6 | 2 |
| 5 | 21 | 9 | 0 |
| 6 | 112 | 109 | 41 |
| alle | 142 | 126 | 43 |

**Zwei Lesarten** (Netze mit stabilem Ergebnis):

| Netzklasse | Netze mit stabilem Ergebnis | Ausstiegsprinzip: Fixpunkt gefunden | kein Fixpunkt gefunden | gleiche Auszahlungen | je Zufalls-Seed | größte Abweichung eines Betriebs, Mittel | Maximum |
|---|---|---|---|---|---|---|---|
| zweiseitig 8 + 8, p = 0,3 | 240 | 240 | 0 | 108 von 240 | 33 / 21 / 23 / 31 | 0,152 | 0,400 |
| Baum mit 10 Knoten | 240 | 240 | 0 | 130 von 240 | 31 / 29 / 37 / 33 | 0,106 | 0,333 |
| allgemein, 8 Knoten, p = 0,3 | 200 | 200 | 0 | 90 von 200 | 25 / 22 / 21 / 22 | 0,146 | 0,375 |

**Kern, Shapley-Wert, Nukleolus** (Zufallsnetze mit höchstens 8 Betrieben; je 12 Netze und Seed, vier Seeds):

| Netzklasse | Netze | Kern nicht leer | ausgewogenes Ergebnis im Kern | Shapley-Wert im Kern | Shapley-Wert gleich ausgewogen | Nukleolus ausgewogen | Nukleolus gleich Dynamik-Ergebnis | Abweichung Shapley gegen ausgewogen, Median / Maximum |
|---|---|---|---|---|---|---|---|---|
| zweiseitig 4 + 4, p = 0,5 | 48 | 48 | 48 von 48 | 9 von 48 | 0 von 48 | 48 von 48 | 37 von 48 | 0,168 / 0,462 |
| allgemein, 7 Knoten, p = 0,4 | 48 | 28 | 28 von 28 | 1 von 48 | 0 von 28 | 28 von 28 | 26 von 28 | 0,330 / 0,436 |

**Eigenschaften** (gewichtete zweiseitige 8 + 8-Netze, Werte 1 bis 5, 40 Netze je Seed):

| Operation | Netze | Ergebnis |
|---|---|---|
| alle Kantenwerte mit 2, 3 und 7 malnehmen | 160 | Auszahlungen skalieren mit: 160 von 160, 160 von 160, 160 von 160; größte Abweichung 6,5·10⁻¹² |
| Knoten umnummerieren | 160 | gleiche Auszahlungen in 160 von 160; größte Abweichung 0 |
| neuer Blattknoten an einem zufälligen Betrieb u | 159 | Auszahlung von u sinkt in 0, steigt in 84, bleibt gleich in 75 |
| (dasselbe) übrige Betriebe | 2236 | sinkt in 220, steigt in 165, bleibt gleich in 1851 Beobachtungen |
| neue Kante zwischen zwei Betrieben auf verschiedenen Seiten | 160 | Endbetrieb: sinkt in 2, steigt in 54, bleibt gleich in 264 von 320 Beobachtungen; beide nicht schlechter in 158 von 160 Netzen |

## Ehrliche Grenzen

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

## Literatur

Kleinberg und Tardos, „Balanced Outcomes in Social Exchange Networks“, STOC 2008: **Abruf des PDF scheiterte** (Zertifikat), Inhalt nur über Suchauszüge und über Bayati u. a. eingeordnet, Volltext nicht gelesen. Bayati, Borgs, Chayes, Kanoria, Montanari, „Bargaining dynamics in exchange networks“ ([arXiv 1004.2079](https://arxiv.org/abs/1004.2079)): Definitionen, Dynamik und das Beispiel mit den Werten 8, 6, 2 aus der ar5iv-Fassung, **erste 100 000 von 215 260 Zeichen gelesen**. Azar, Birnbaum, Celis, Devanur, Peres, „Convergence of Local Dynamics to Balanced Outcomes in Exchange Networks“ ([arXiv 0907.4356](https://arxiv.org/abs/0907.4356)): nur Abstract (Kantenausgleich konvergiert gegen ein ausgewogenes Ergebnis, wo eines existiert). Cook, Emerson, Gillmore, Yamagishi, „The Distribution of Power in Exchange Networks“, American Journal of Sociology 89 (1983): nach Suchauszug (Zentralitätsmaße sagen die Machtverteilung nicht voraus), Seitenzahlen nicht geprüft. Cook und Emerson 1978 und Shapley und Shubik 1971 (Zuordnungsspiel): aus dem Gedächtnis genannt, nicht geprüft. [arXiv 2601.09198](https://arxiv.org/pdf/2601.09198) („Credible Nash Bargaining Solution for Bilateral Trading Networks“): nur Suchauszug (Vier-Knoten-Beispiel). **Zahlenangaben aus diesen Arbeiten werden nicht übernommen, nur selbst gemessene.**

## Tests

**229 Tests**, Laufzeit rund 2,5 Minuten seriell auf Windows mit Python 3.14 (den größten Teil brauchen die AppTest-Dateien; die Zahl steht in der Suite fest, die Laufzeit ist einmal gemessen). Linux-CI (Python 3.12) ist noch nicht gelaufen. Zusammensetzung:

- **Orakel (`tests/test_oracle_austauschnetz.py`):** größtes Matching gegen networkx und die Teilmengen-Rekursion; jede Koalitionswert gegen networkx auf dem Teilnetz; drei Wege zur Existenz stabiler Ergebnisse (LP-Lücke, Zulässigkeits-Programm je größtem Matching, alle Koalitionsungleichungen) auf Zufallsnetzen und dem ganzen Atlas; stabile Spanne gegen die Spanne über alle Koalitionsungleichungen; vektorisierter Schritt des Kantenausgleichs gegen eine Fassung mit Schleifen und Wörterbüchern, Fixpunkt als Fixpunkt der Schleifenfassung; Löser gegen die Aufzählung aller isolierten ausgewogenen Ergebnisse in Brüchen auf dem Atlas (Löser findet ein Ergebnis genau dann, wenn die LP-Lücke null ist); Shapley-Wert als Mittel über alle Reihenfolgen; Nukleolus gegen das Kohlberg-Kriterium, Nukleolus als ausgewogenes Ergebnis; Zwischenzentralität gegen networkx. Die Aufzählung nimmt höchstens 150 Wahlen je Matching (Laufzeit); der große Lauf im Scratch-Ordner nahm 1500 und mehr Zufallsnetze (siehe Bericht des Baus, nicht im Repo).
- **Einheiten an von Hand gerechneten Mini-Netzen (`test_units.py`):** Weg 3, 4, 5, Kreis 4, Dreieck, Stern, K2,3, Literaturbeispiel, Dreieck mit Anhang; Matching, LP-Lücke, stabile Spanne, festgelegte Betriebe, Angebote, ein Schritt des Kantenausgleichs, Prüfer, exakte Bestätigung, Familie des Kreises, Spiel, Ausstiegsprinzip.
- **Eigenschaftstests (`test_eigenschaften_austauschnetz.py`):** Auszahlungen summieren auf jeder Tauschkante zum Kantenwert und insgesamt zum größten Matching, ausgewogen liegt in der stabilen Spanne, festgelegte Betriebe, Skalieren, Umnummerieren (bei eindeutigem Ergebnis), zweiseitig und Bäume immer stabil und ausgewogen, kein stabiles Ergebnis heißt kein Ergebnis des Lösers, Ergebnis unabhängig vom Hash-Seed des Prozesses.
- **Randfälle und Zweige (`test_edge_cases.py`):** zwei Betriebe, Gewicht, Netz ohne Kante, isolierter Betrieb, Gleichstände, Schleifen und doppelte Kanten, vollständiges Netz, Spiel mit einem und zwei Spielern. Zweige (Nullspalten-Regel): Dynamik von Null gegen Reduktion weichen auf K2,3 ab, Nash gegen Ausstiegsprinzip auf Weg 4, nicht auf Weg 3; das Dreieck liefert „kein Ergebnis“; Kreis 4 meldet Mehrdeutigkeit, ein Baum nie.
- **Verdikte und Presets (`test_verdicts.py`, `test_presets.py`):** Zweige und jede Zahl im Text an Handnetzen; jedes Preset baut sein Netz.
- **Messreihen (`test_measurements.py`):** Erzeuger-Hash, Summen in sich stimmig, vier kleine Aufträge neu gerechnet und mit den gespeicherten gleich.
- **Claims (`test_claims.py`):** jede Zahl der README; die Tabellen werden mit denselben Zeilenbauern der App erzeugt und als Text in der README gesucht; Hypothesenzeilen H1 bis H12.
- **Literatur (`test_literatur_austauschnetz.py`):** das Beispiel mit den Werten 8, 6, 2 aus Bayati u. a. (ar5iv-Text, nicht PDF); das Vier-Knoten-Beispiel aus arXiv 2601.09198 (nur Suchauszug) und Kleinberg und Tardos sind offen und nicht getestet.
- **Atlas (`test_atlas.py`):** 142 Graphen, paarweise verschieden (eigener Kanonisierungscode), Zahl nach OEIS A001349.
- **Worst-Case (`test_worst_case.py`):** jedes Netz am Maximum (60 Betriebe) mit Prüfer; keine Zeit-Assertion.
- **App (`test_app.py`, `test_layout.py`, `test_footer.py`, `test_runtime_imports.py`, `test_copies.py`):** jeder Knopf (auch beide ▶️-Knöpfe), jeder Regler an beiden Rändern, jede Netzart an beiden Rändern der Größe, jedes Preset, ungültige Kantenliste, Permalink mit unsinnigen Werten, PDF, Hervorhebung des aktiven Presets, Footer, Laufzeit-Importe, Kopietest des Zufallsgenerators.

Ein Mutationstest läuft für diese Demo nicht (Entscheidung des Betreibers, 2026-10-28).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Hauptansicht und sieben Reiter |
| `aun_net.py` | Netze, Handnetze, Zufallsnetze (SplitMix64), eigene Kantenlisten, Zentralität |
| `aun_matching.py` | größtes Matching (Teilmengen und ganzzahliges Programm), LP-Relaxation, Werte aller Koalitionen |
| `aun_stable.py` | LP-Lücke, stabile Spanne, festgelegte Betriebe, Prüfer für stabile Ergebnisse |
| `aun_balanced.py` | Außenoption, Prüfer, Kantenausgleich, Matching zur Auszahlung, Reduktion, `balanced_outcome` |
| `aun_exact.py` | Gauß in Brüchen, exakte Bestätigung |
| `aun_multi.py` | mehrere ausgewogene Ergebnisse, Familie des Kreises mit 4 Betrieben |
| `aun_game.py` | Kern, Shapley-Wert, Nukleolus |
| `aun_principle.py` | Ausstiegsprinzip (eigene Variante ohne Quelle) |
| `aun_atlas.py` | liest den Atlas aller kleinen zusammenhängenden Graphen |
| `aun_rng.py` | SplitMix64, wörtliche Kopie aus `ab-test-demo/abt_rng.py` (Kopietest) |
| `aun_constants.py` | Regler-Grenzen, Netzarten, Farben, Presets |
| `aun_scenario.py` | Einstellungen und das daraus gebaute Netz |
| `aun_evaluation.py` | Ansichten, Kennzahlen, Verdikte als reine Funktionen |
| `aun_tablerows.py` | Zeilen und Verdikte der vorgerechneten Reihen |
| `aun_experiments.py` | Aufträge der Messreihen, Erzeuger-Hash, Laden und Prüfen von `data/tables.json` |
| `aun_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `aun_texts.py` | Einleitung, Erklärtexte, Annahmen, Formeln |
| `aun_layout.py`, `aun_presets.py`, `aun_pdf_export.py` | fester Kopf, Permalink und Presets, PDF-Export |
| `data/tables.json`, `data/atlas_graphs.json` | vorgerechnete Reihen mit Erzeuger-Hash; Atlas der Graphen bis 6 Knoten |
| `tools/make_grid.py`, `tools/make_atlas.py` | erzeugen die beiden Dateien in `data/` |
| `requirements.txt`, `requirements-dev.txt` | Laufzeit-Bibliotheken (ungepinnt); dev: pytest und networkx für die Orakel |
| `tests/` | Mini-Netze von Hand, Orakel, Einheiten, Eigenschaften, Randfälle, Verdikte, Presets, Messreihen, Claims, Atlas, Worst-Case, App, Layout, Footer, Laufzeit-Importe, Kopietest |

## Bewusst nicht umgesetzt

- **Spiele auf Netzen mit Aktionen** (Netzwerkspiel, öffentliche Güter) und **Netzbildung**: eigene Stücke, hier gibt es keine Aktionen.
- **Mehrparteien-Koalitionsverhandlung** (Baron–Ferejohn): jede Einigung ist zweiseitig, die Vielen wirken nur über Alternativen.
- **Geduld, Angebotsrunden, Information:** `verhandlung-demo` (Geduld), private Information in den Nachbarstücken der Linie.
- **Kombinatorische Bestimmung der festgelegten Betriebe** (Dulmage–Mendelsohn) statt linearer Programme: nicht gemessen; die LPs begrenzen die Live-Größe (Messung unten).
- **Beweise** der Sätze (Existenz, Eindeutigkeit der Fälle, Wegeformel): nur gemessen und an kleinen Netzen aufgezählt.
- **Kantenwerte mit Nachkommastellen** und gewichtete Zufallsnetze außerhalb von Reiter 7; **Daten echter Betriebe.**

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Die Streamlit-Cloud braucht dieselben Pakete wie `requirements.txt` (scipy gehört dazu); die in der Cloud eingestellte Python-Version ist beim Deploy zu notieren.

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Messreihen neu rechnen: `python tools/make_grid.py` (rund drei Minuten mit vier Prozessen); Atlas neu schreiben: `python tools/make_atlas.py`.

Gebaut mit Streamlit, Plotly, NumPy, SciPy und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
