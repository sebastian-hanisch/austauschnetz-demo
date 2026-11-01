"""Wer hat im Netz Verhandlungsmacht? Das Austauschnetz - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück der Linie „Regeln setzen, verhandeln, kontrollieren“. Verlader und Spediteure bilden ein Netz möglicher Touren mit Überschuss 1; jeder Betrieb tauscht höchstens einmal. Die Demo rechnet stabile und
ausgewogene Ergebnisse (Nash-Lösung mit Drohpunkt auf jeder Kante), die stabile Spanne, den Kantenausgleich, mehrere ausgewogene Ergebnisse, zwei Lesarten der Außenoption und das Verhältnis zu Kern,
Shapley-Wert und Nukleolus.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import aun_constants as C
import aun_evaluation as V
import aun_exact as X
import aun_experiments as XP
import aun_tablerows as R
import aun_texts as T
import aun_visualization as Z
from aun_layout import dunkles_design, kopf_css
from aun_presets import (
    SETTING_SPECS,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    settings_from_state,
    sidebar_presets,
    sync_query_params,
)

st.set_page_config(page_title="Austauschnetz – Sebastian Hanisch", layout="wide")


# --- Zwischenspeicher (Schlüssel = alle Eingaben inklusive Zufalls-Seed) --------------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def _tables():
    return XP.load_tables()


@st.cache_data(show_spinner=False)
def _view(settings):
    return V.analyse(settings)


@st.cache_data(show_spinner=False)
def _dynamics(settings):
    return V.dynamics_view(settings, V.analyse(settings))


@st.cache_data(show_spinner=False)
def _multi(settings):
    return V.multi_view(settings, V.analyse(settings))


@st.cache_data(show_spinner=False)
def _reading(settings):
    return V.reading_view(settings, V.analyse(settings))


@st.cache_data(show_spinner=False)
def _game(settings):
    return V.game_view(V.analyse(settings))


@st.cache_data(show_spinner=False)
def _properties(settings):
    return V.property_view(settings, V.analyse(settings))


@st.cache_data(show_spinner=False)
def _pattern():
    return V.path_pattern_rows()


@st.cache_data(show_spinner=False)
def _hand_nets():
    return V.hand_net_rows()


@st.cache_data(show_spinner=False)
def _existence_examples():
    return V.existence_examples()


@st.cache_data(show_spinner=False)
def _k23():
    return V.k23_example()


def show(verdict):
    kind, text = verdict
    getattr(st, kind)(text)


def table(rows):
    st.dataframe(rows, hide_index=True, width="stretch")


def on_demand(key, label, settings, compute, auto):
    """Teure Zusatzrechnung: bei kleinen Netzen sofort, sonst erst auf Klick (und nur für die Einstellungen, bei denen geklickt wurde)."""
    if auto:
        return compute(settings)
    if st.button(label, key=key):
        st.session_state[key + "_for"] = settings
    return compute(settings) if st.session_state.get(key + "_for") == settings else None


def footer():
    st.markdown("---")
    st.caption(
        "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
        "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
        "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
    )


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in aun_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🕸️ Wer hat im Netz Verhandlungsmacht? Das Austauschnetz")
st.markdown(T.INTRO)

with st.expander("So funktioniert das Austauschnetz", expanded=True):
    st.markdown(T.EXPLAINER)

with st.expander("Erklärtabelle: Begriffe und Regler"):
    st.markdown(T.CONTROLS_TABLE)

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("🕸️ Netz")
    st.selectbox("Netz", list(C.NETS), key="net_select", format_func=C.NETS.get,
                 help="Weg, Kreis, Stern, Spinne und vollständig zweiseitige Netze sind feste Strukturen; die Zufallsnetze nehmen den Zufalls-Seed unten.")
    st.slider("Betriebe", *bounds("n_slider"), key="n_slider", step=1,
              help="Zahl der Betriebe bei Weg, Kreis, Stern (Mitte plus Blätter), Spinne, Baum und allgemeinem Zufallsnetz; bei den zweiseitigen Netzen verteilen sie sich auf Verlader (halbe Zahl, abgerundet) und Spediteure. "
                   "Betriebe ohne Verbindung entfallen bei den Zufallsnetzen. Das Literaturbeispiel und die eigene Kantenliste haben ihre eigene Größe.")
    st.slider("Kantenwahrscheinlichkeit p (%)", *bounds("p_slider"), key="p_slider", step=5,
              help="Nur bei den Zufallsnetzen (zweiseitig und allgemein): jede mögliche Tour kommt mit dieser Wahrscheinlichkeit vor.")
    st.select_slider("Dämpfung κ des Kantenausgleichs", options=list(C.KAPPAS), key="kappa_slider", format_func=lambda k: V.de(k, 2),
                     help="Wie stark ein Schritt den alten Wert ersetzt (1: ganz). Ändert die Zahl der Schritte; in den gemessenen Netzen blieb der Fixpunkt gleich (Reiter 3).")
    st.header("✏️ Eigene Kantenliste")
    st.text_area("Kanten", key="edges_input", height=90, max_chars=C.EDGES_MAX_CHARS,
                 help="Gilt nur, wenn oben „Eigene Kantenliste“ gewählt ist. Format: 0-1, 1-2:3, 2-3 (Wert nach dem Doppelpunkt, sonst 1). Knotennamen sind ganze Zahlen, höchstens 60 Knoten.")
    st.header("🎲 Zufall")
    st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1, help="Legt die Zufallsnetze und die Zufallsstarts in den Reitern 4 und 5 fest.")
    st.button("🎲 Neuer Zufalls-Seed", width="stretch", on_click=randomize_seed)

settings = settings_from_state()
sync_query_params({k: st.session_state[k] for k in SETTING_SPECS})

verdicts = []      # Verdikte für den PDF-Export
tables = _tables()
if tables is None:
    st.warning("Die vorgerechneten Messreihen (data/tables.json) fehlen oder gehören zu einem anderen Rechencode: `python tools/make_grid.py` ausführen. Die Reiter zeigen dann keine Reihen.")

view = _view(settings)
if view.error:
    st.error(f"Die Kantenliste ist ungültig: {view.error}")
    footer()
    st.stop()

net = view.net

# --- Hauptansicht --------------------------------------------------------------------------------------------------------------------------------
st.markdown("## 🎯 Ergebnis: Wer bekommt wie viel im Netz?")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Betriebe / Touren", f"{net.n} / {len(net.edges)}", help="Knoten und mögliche Touren (Kanten) des Netzes.")
m2.metric("Größtes Matching", str(view.ip), help="Größtes Gewicht, das gleichzeitig getauscht werden kann; die LP-Relaxation liefert " + V.de(view.lp, 2) + ".")
m3.metric("Stabil", "ja" if view.stable else "nein", help="Gibt es ein Ergebnis ohne blockierendes Paar? Genau dann, wenn die LP-Relaxation des Matchings ganzzahlig ist.")
m4.metric("Festgelegt / offen", f"{len(view.fixed)} / {net.n - len(view.fixed)}" if view.stable else "–",
          help="Betriebe, deren Auszahlung in allen stabilen Ergebnissen gleich ist, gegen Betriebe mit einer Spanne.")
m5.metric("Verfahren", {"Dynamik von Null": "Dynamik", "Reduktion": "Reduktion"}.get(view.outcome.method, "–"), help="Wie das gezeigte ausgewogene Ergebnis gefunden wurde: Dynamik von Null oder Reduktion (das zuerst gefundene; bei mehreren Ergebnissen eine Auswahlregel).")
col_a, col_b = st.columns(2)
with col_a:
    st.plotly_chart(Z.build_network(view, settings.net), width="stretch", key="network_chart")
    st.caption("Dick und grün: die Tauschpaare, dünn grau: die übrigen möglichen Touren. Farbe und Zahl im Knoten: ausgewogene Auszahlung (Bruch, wenn exakt bestätigt). Bei Kantenwert ungleich 1 steht der Wert an der Kante.")
with col_b:
    if view.stable:
        st.plotly_chart(Z.build_ranges(view), width="stretch", key="range_chart")
        st.caption("Balken: stabile Spanne jedes Betriebs über alle stabilen Ergebnisse, Raute: ausgewogene Auszahlung. Wo die Raute den ganzen Balken füllt (Spanne leer), ist der Betrieb festgelegt.")
    else:
        st.info("Ohne stabiles Ergebnis gibt es keine stabile Spanne zu zeigen.")
with st.expander("Zahlen im Einzelnen: Spanne, Partner, Außenoption und Auszahlung je Betrieb"):
    table(V.node_rows(view))
st.markdown("#### ❓ Kernfrage: Wer hat im Netz Verhandlungsmacht, und was ist ein ausgewogenes Ergebnis?")
v_main = V.verdict_main(view)
show(v_main)
verdicts.append(v_main)

# --- Reiter --------------------------------------------------------------------------------------------------------------------------------------
tabs = st.tabs(["1 Wer hat Macht?", "2 Stabil und ausgewogen", "3 Kantenausgleich", "4 Mehrere Ergebnisse", "5 Zwei Lesarten", "6 Kern, Shapley, Nukleolus", "7 Eigenschaften"])

# --- Reiter 1 ------------------------------------------------------------------------------------------------------------------------------------
with tabs[0]:
    st.subheader("🔬 Experiment E1: Hat Macht mit der Zahl der Verbindungen zu tun?")
    st.caption("**Erwartung:** Wege zeigen, dass nicht die Zahl der Nachbarn zählt, sondern wer eine Alternative hat, die der Partner nicht hat: auf einem Weg mit 5 Betrieben bekommt die Mitte nichts, obwohl sie zwei Nachbarn hat. "
               "In Zufallsnetzen hängen Auszahlung und Grad dagegen positiv zusammen; die Reihen unten zählen, wie oft der höhere Grad trotzdem weniger bekommt. Live: das Netz der Seitenleiste und Wege mit 2 bis 14 Betrieben.")
    pattern = _pattern()
    table([{"Betriebe": r["n"], "Auszahlungen (exakt)": ", ".join(X.fraction_text(v) for v in r["y"])} for r in pattern])
    v_pat = V.verdict_pattern(pattern)
    show(v_pat)
    verdicts.append(v_pat)
    with st.expander("Handnetze im Überblick: von Hand gerechnet und in den Tests geprüft"):
        table(_hand_nets())
    st.markdown("**Das Netz der Seitenleiste:** Auszahlung gegen Grad und Zwischenzentralität")
    if view.ok:
        st.plotly_chart(Z.build_power(V.power_scatter_data(view)), width="stretch", key="power_chart")
        st.caption("Jeder Punkt ist ein Betrieb. Links der Grad (Zahl der möglichen Touren), rechts die Zwischenzentralität (Anteil kürzester Wege durch den Betrieb, ungewichtet).")
    v_pow = V.verdict_power(view)
    show(v_pow)
    verdicts.append(v_pow)
    if tables:
        st.markdown(f"**Vorgerechnet: Zufallsnetze, Macht gegen Grad** (Betriebe mit stabilem Ergebnis; {XP.PER_JOB} Netze je Klasse und Zufalls-Seed, vier Zufalls-Seeds)")
        table(R.rows_power(tables))
        st.markdown("**Vorgerechnet: festgelegte und offene Betriebe**")
        table(R.rows_open(tables))
        v_t1 = R.verdict_table_power(tables)
        show(v_t1)
        verdicts.append(v_t1)

# --- Reiter 2 ------------------------------------------------------------------------------------------------------------------------------------
with tabs[1]:
    st.subheader("🔬 Experiment E2: Wann gibt es ein stabiles und ein ausgewogenes Ergebnis?")
    st.caption("**Erwartung:** Ein stabiles Ergebnis gibt es genau dann, wenn die LP-Relaxation des Matchings nicht größer ist als das ganzzahlige Matching; zweiseitige Netze und Bäume haben immer eines, Dreiecke und ungerade Kreise nicht. "
               "Zu jedem Netz mit stabilem Ergebnis sollte es ein ausgewogenes geben (Satz von Kleinberg und Tardos, laut Bayati u. a.; hier gemessen, nicht bewiesen). Ausgewogen schließt stabil ein, die messbare Richtung ist also „stabil, dann ausgewogen“.")
    v_ex = V.verdict_existence(view)
    show(v_ex)
    verdicts.append(v_ex)
    st.markdown("**Kleine Netze, LP-Wert gegen ganzzahliges Matching**")
    table(_existence_examples())
    if tables:
        st.markdown(f"**Vorgerechnet: Zufallsnetze, Existenz und Verfahren** ({XP.PER_JOB} Netze je Klasse und Zufalls-Seed, vier Zufalls-Seeds)")
        table(R.rows_existence(tables))
        v_t2 = R.verdict_table_existence(tables)
        show(v_t2)
        verdicts.append(v_t2)
        st.markdown(f"**Vorgerechnet: Anteil der allgemeinen Zufallsnetze mit stabilem Ergebnis** (je {XP.SHARE_PER_JOB} Netze, vier Zufalls-Seeds; Mittel ± Standardabweichung in Prozent)")
        st.plotly_chart(Z.build_share(tables["share"], XP.SHARE_NS, XP.SHARE_PS), width="stretch", key="share_chart")
        table(R.rows_share(tables))
        v_t2b = R.verdict_table_share(tables)
        show(v_t2b)
        verdicts.append(v_t2b)

# --- Reiter 3 ------------------------------------------------------------------------------------------------------------------------------------
with tabs[2]:
    st.subheader("🔬 Experiment E3: Findet der Kantenausgleich das ausgewogene Ergebnis?")
    st.caption("**Erwartung:** Die Dynamik konvergiert und ihr Fixpunkt hängt nicht von der Dämpfung ab. Ob der Fixpunkt von Null aber ein ausgewogenes Ergebnis ist, ist eine andere Frage: bei vielen größten Matchings (Einheitswerte) "
               "kann er eine Auszahlung sein, die zu keinem Matching gehört. Die Reduktion soll das beheben. Live am Netz der Seitenleiste.")
    dv = _dynamics(settings)
    if dv is not None:
        table([{"κ": V.de(r[0], 2), "Schritte": r[1], "konvergiert": "ja" if r[2] else "nein", "Fixpunkt ausgewogen": "ja" if r[3] else "nein"} for r in dv.rows])
        st.plotly_chart(Z.build_trace(dv, [net.label(i) for i in range(net.n)]), width="stretch", key="trace_chart")
        st.caption(f"Auszahlungen der ersten {dv.trace_steps} Schritte bei κ = {V.de(dv.kappa, 2)} (bis zu zwölf Betriebe mit der größten Veränderung).")
    v_dyn = V.verdict_dynamics(dv)
    show(v_dyn)
    verdicts.append(v_dyn)
    st.markdown("**Wo die Dynamik von Null scheitert: zweiseitig 2 + 3**")
    k23 = _k23()
    table([{"Betriebe": ", ".join(k23["net"].label(i) for i in range(5)), "Fixpunkt von Null": ", ".join(V.de(x, 3) for x in k23["d0"]), "Summe": V.de(k23["d0_sum"], 3),
            "größtes Matching": k23["ip"], "Reduktion": ", ".join(V.de(x, 3) for x in k23["reduction"])}])
    st.caption("Die Summe der Auszahlungen im Fixpunkt von Null übersteigt das größte Matching: keine Auszahlung eines Matchings. Die Reduktion entfernt die festgelegten Betriebe und findet ein Ergebnis.")
    if tables:
        st.markdown(f"**Vorgerechnet: Schritte je Dämpfung** ({tables['dynamics']['nets']} zweiseitige 8 + 8-Netze, p = 0,3; Dynamik von Null)")
        table(R.rows_dynamics(tables))
        st.markdown("**Vorgerechnet: Schritte über der Netzgröße** (zweiseitig n + n, mittlerer Grad 3, κ = 0,5)")
        st.plotly_chart(Z.build_growth(tables["growth"], XP.GROWTH_SIDES), width="stretch", key="growth_chart")
        table(R.rows_growth(tables))
        v_t3 = R.verdict_table_dynamics(tables)
        show(v_t3)
        verdicts.append(v_t3)

# --- Reiter 4 ------------------------------------------------------------------------------------------------------------------------------------
with tabs[3]:
    st.subheader("🔬 Experiment E4: Ist das ausgewogene Ergebnis eindeutig?")
    st.caption("**Erwartung:** Nein. Schon der Kreis mit 4 Betrieben hat eine ganze Familie ausgewogener Ergebnisse. Das gezeigte Ergebnis ist darum eine Auswahlregel. In Zufallsnetzen kommt Mehrdeutigkeit vor; in Bäumen sollte sie nicht vorkommen (Reihen unten). Live: das Netz der Seitenleiste.")
    found = on_demand("multi_button", "▶️ Weitere Ergebnisse suchen (einige Sekunden)", settings, _multi, net.n <= V.MULTI_AUTO_MAX_N)
    if found is None:
        st.info(f"Bei mehr als {V.MULTI_AUTO_MAX_N} Betrieben läuft die Suche (Dynamik von Null, Reduktion, fünf Zufallsstarts) erst auf Klick.")
    elif found:
        table([{"Nr.": i + 1, "gefunden von": ", ".join(f.sources), **{net.label(v): V.de(f.y[v], 3) for v in range(net.n)}} for i, f in enumerate(found)] if net.n <= 20
              else [{"Nr.": i + 1, "gefunden von": ", ".join(f.sources), "größte Auszahlung": V.de(max(f.y), 3), "kleinste Auszahlung": V.de(min(f.y), 3)} for i, f in enumerate(found)])
    if found is not None:
        v_mul = V.verdict_multi(found, view)
        show(v_mul)
        verdicts.append(v_mul)
    st.markdown("**Der kleinste Fall: Kreis mit 4 Betrieben**")
    table(V.family_rows())
    st.caption("Exakt in Brüchen vom Prüfer bestätigt (Matching: 0-1 und 2-3). Das Paar mit ungleichem a bricht die Bedingung.")
    if tables:
        st.markdown("**Vorgerechnet: Mehrdeutigkeit in Zufallsnetzen** (Netze mit stabilem Ergebnis; gefunden von Dynamik von Null, Reduktion und fünf Zufallsstarts: Untergrenze)")
        table(R.rows_ambiguity(tables))
        v_t4 = R.verdict_table_ambiguity(tables)
        show(v_t4)
        verdicts.append(v_t4)
        st.markdown("**Vorgerechnet: Atlas aller zusammenhängenden Graphen mit 2 bis 6 Knoten** (Einheitswert; zwölf Wege je Graph)")
        table(R.rows_atlas(tables))
        v_t4b = R.verdict_table_atlas(tables)
        show(v_t4b)
        verdicts.append(v_t4b)

# --- Reiter 5 ------------------------------------------------------------------------------------------------------------------------------------
with tabs[4]:
    st.subheader("🔬 Experiment E5: Zwei Lesarten der Außenoption")
    st.caption("**Erwartung:** Nash mit Drohpunkt gibt dem Betrieb mit der besseren Alternative mehr als die Hälfte, das Ausstiegsprinzip (**eigene Variante dieser Demo, ohne Quelle**) nur seine Alternative, mindestens die Hälfte. "
               "Im Netz sind beide gleich, wo die Auszahlungen schon durch die stabile Spanne feststehen; sonst können sie sich unterscheiden (Reihen unten). `verhandlung-demo` rechnet dieselbe Frage für zwei Betriebe mit gegebener Außenoption.")
    st.markdown("**Eine Kante, Wert 1, Anteil von v bei Außenoptionen (a_u; a_v)**")
    table(V.split_rows())
    rv = _reading(settings)
    if rv is not None and rv[1] is not None and net.n <= 24:
        table([{"Betrieb": net.label(i), "ausgewogen (Nash)": V.de(rv[0][i], 3), "Ausstiegsprinzip": V.de(rv[1][i], 3)} for i in range(net.n)])
    v_rd = V.verdict_reading(rv, view)
    show(v_rd)
    verdicts.append(v_rd)
    if tables:
        st.markdown("**Vorgerechnet: Zufallsnetze, gleiche Auszahlungen?** (Netze mit stabilem Ergebnis; Fixpunkt des Ausstiegsprinzips gesucht von Null, vom ausgewogenen Ergebnis und von drei stabilen Zufallsauszahlungen)")
        table(R.rows_reading(tables))
        v_t5 = R.verdict_table_reading(tables)
        show(v_t5)
        verdicts.append(v_t5)

# --- Reiter 6 ------------------------------------------------------------------------------------------------------------------------------------
with tabs[5]:
    st.subheader("🔬 Experiment E6: Kern, Shapley-Wert und Nukleolus")
    st.caption("**Erwartung:** Das Austauschnetz mit Einheitswert ist ein Zuordnungsspiel (Wert einer Koalition = größtes Matching im Teilnetz). Seine stabilen Auszahlungen sind der Kern; das ausgewogene Ergebnis sollte darin liegen; "
               "ob der Shapley-Wert darin liegt, zählen die Reihen unten. Ob der Nukleolus selbst ausgewogen ist, ist ein Messbefund (Reihen unten), kein Satz. Höchstens 8 Betriebe. `kern-demo` und `shapley-demo` teilen einen Gewinn ohne Netz.")
    gv = _game(settings)
    if gv is not None:
        labels = [net.label(i) for i in range(net.n)]
        series = {"Nukleolus": gv.nucleolus, "Shapley-Wert": [float(s) for s in gv.shapley]}
        if view.ok:
            series["ausgewogen"] = view.outcome.y
        st.plotly_chart(Z.build_node_values(labels, series), width="stretch", key="game_chart")
        table([{"Betrieb": labels[i], "Shapley-Wert": X.fraction_text(gv.shapley[i]), "Nukleolus": V.de(gv.nucleolus[i], 3), "ausgewogen": V.de(view.y(i), 3) if view.ok else "–"} for i in range(net.n)])
    v_gm = V.verdict_game(gv, view)
    show(v_gm)
    verdicts.append(v_gm)
    if tables:
        st.markdown(f"**Vorgerechnet: Zufallsnetze mit höchstens 8 Betrieben** (je {XP.GAME_PER_JOB} Netze und Zufalls-Seed, vier Zufalls-Seeds)")
        table(R.rows_game(tables))
        v_t6 = R.verdict_table_game(tables)
        show(v_t6)
        verdicts.append(v_t6)

# --- Reiter 7 ------------------------------------------------------------------------------------------------------------------------------------
with tabs[6]:
    st.subheader("🔬 Experiment E7: Welche Eigenschaften hat das ausgewogene Ergebnis?")
    st.caption("**Erwartung:** Skalieren aller Kantenwerte skaliert die Auszahlungen, Umnummerieren ändert nichts. Eine zusätzliche Alternative (neuer Blattknoten) sollte dem Betrieb nie schaden; für eine zusätzliche Kante zwischen zwei "
               "Betrieben gilt das nicht ohne Weiteres. Beides ist hier gemessen, nicht bewiesen; bei mehreren ausgewogenen Ergebnissen kann ein Teil der Änderungen die Auswahlregel sein.")
    if view.ok:
        pv = on_demand("prop_button", "▶️ Eigenschaften für dieses Netz rechnen (einige Sekunden)", settings, _properties, net.n <= V.PROPERTY_AUTO_MAX_N)
    else:
        pv = None
    if view.ok and pv is None:
        st.info(f"Bei mehr als {V.PROPERTY_AUTO_MAX_N} Betrieben rechnet dieser Reiter erst auf Klick (je Betrieb ein weiteres Netz).")
    else:
        if pv is not None:
            table([{"Betrieb mit neuem Blattknoten": lab, "Auszahlung vorher": V.de(a, 3), "nachher": ("–" if b is None else V.de(b, 3))} for lab, a, b in pv.leaf_rows])
        v_pr = V.verdict_properties(pv)
        show(v_pr)
        verdicts.append(v_pr)
    if tables:
        st.markdown(f"**Vorgerechnet: gewichtete zweiseitige 8 + 8-Netze** (Kantenwerte 1 bis 5; {XP.PROP_PER_JOB} Netze je Zufalls-Seed, vier Zufalls-Seeds)")
        table(R.rows_properties(tables))
        v_t7 = R.verdict_table_properties(tables)
        show(v_t7)
        verdicts.append(v_t7)

# --- Grenzen, Formeln, Export ---------------------------------------------------------------------------------------------------------------------
st.markdown("---")
st.subheader("🔗 Verwandte Demos")
st.markdown(
    "- [`verhandlung-demo`](https://github.com/sebastian-hanisch/verhandlung-demo): zwei Betriebe, Geduld und eine **gegebene** Außenoption; hier entsteht sie aus dem Netz.\n"
    "- [`kern-demo`](https://github.com/sebastian-hanisch/kern-demo) und [`shapley-demo`](https://github.com/sebastian-hanisch/shapley-demo): Aufteilung eines Gewinns ohne Netz und ohne Ablauf; Reiter 6 nutzt dieselben Lösungskonzepte.\n"
    "- `hungarian-demo` und `gale-shapley-demo`: Matching mit Preisen bzw. Vorlieben; hier geht es nicht um die Paarung, sondern um die Aufteilung.\n"
    "- `netzwerkspiel-demo`: Spiele auf Netzen, in denen jeder eine Aktion wählt; hier gibt es keine Aktionen, nur die Aufteilung eines festen Überschusses."
)

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(T.ASSUMPTIONS_MARKDOWN)

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(T.MATH_MARKDOWN)

st.subheader("📄 Ergebnisse als PDF")
if st.button("PDF erstellen", key="pdf_button"):
    from aun_pdf_export import build_pdf
    st.session_state["pdf_bytes"] = build_pdf(settings, view, verdicts)
if st.session_state.get("pdf_bytes"):
    st.download_button("⬇️ PDF herunterladen", st.session_state["pdf_bytes"], file_name="austauschnetz.pdf", mime="application/pdf", key="pdf_download")

footer()
