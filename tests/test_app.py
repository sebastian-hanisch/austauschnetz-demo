"""End-to-end Smoke-Test via Streamlits AppTest: lädt app.py mit den Standardeinstellungen, klickt jeden Knopf, fährt jeden Regler an seine Grenzen, durchläuft jedes Preset und die Eckfälle
und prüft, dass kein Python-Fehler auftritt (insbesondere `StreamlitDuplicateElementId` bei Diagrammen mit gleichem Inhalt)."""

import os

import pytest
from streamlit.testing.v1 import AppTest

import aun_constants as C
import aun_presets as P

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last (parallele Läufe) reichen 180 s nicht immer; Umgebungsvariable zum Anpassen
AUTOPLAY_MARKER = "▶"  # Auto-Play-Buttons (Animation mit sleep) im Smoke-Test auslassen


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH, default_timeout=TIMEOUT)
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _set(at, **kw):
    """Regler der Seitenleiste nach Schlüssel setzen und einmal laufen lassen."""
    for key, value in kw.items():
        for art in ("selectbox", "slider", "select_slider", "number_input", "text_area"):
            try:
                getattr(at.sidebar, art)(key=key).set_value(value)
                break
            except KeyError:
                continue
        else:
            raise AssertionError(key)
    at.run()
    return at


def test_app_loads_without_exception():
    at = _fresh_app()
    assert len(at.tabs) == 7
    assert [m.label for m in at.metric][:3] == ["Betriebe / Touren", "Größtes Matching", "Stabil"]


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        if AUTOPLAY_MARKER in label:
            continue
        at = _fresh_app()
        at.button[index].click().run()
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_slider_at_its_min_and_max_does_not_raise():
    labels = [s.label for s in _fresh_app().sidebar.slider]
    assert labels, "keine Slider gefunden"
    for key in ("n_slider", "p_slider"):
        for edge in (P.SETTING_SPECS[key].lo, P.SETTING_SPECS[key].hi):
            at = _set(_fresh_app(), **{key: edge})
            assert not at.exception, (key, edge, [str(e) for e in at.exception])
    for k in C.KAPPAS:
        at = _set(_fresh_app(), kappa_slider=k)
        assert not at.exception, (k, [str(e) for e in at.exception])


@pytest.mark.parametrize("net", list(C.NETS))
def test_every_net_kind_at_both_ends_of_the_size_slider(net):
    for n in (C.N_MIN, C.N_MAX):
        at = _set(_fresh_app(), net_select=net, n_slider=n)
        assert not at.exception, (net, n, [str(e) for e in at.exception])


def test_every_preset_runs_and_shows_a_verdict():
    for name in C.PRESETS:
        at = _fresh_app()
        at.sidebar.button(key=f"preset_{name}").click().run()
        assert not at.exception, (name, [str(e) for e in at.exception])
        assert at.success or at.warning, name


def test_largest_net_at_slowest_damping_does_not_raise_or_hang():
    at = _set(_fresh_app(), net_select="rand_bip", n_slider=C.N_MAX, kappa_slider=0.25, p_slider=C.P_MAX)
    assert not at.exception, [str(e) for e in at.exception]


def test_invalid_custom_edge_list_shows_an_error_and_keeps_the_footer():
    at = _set(_fresh_app(), net_select="custom", edges_input="0-0, abc")
    assert not at.exception, [str(e) for e in at.exception]
    assert any("ungültig" in e.value for e in at.error)
    assert any("Diese Demo ist Teil des Portfolios" in c.value for c in at.caption)


def test_custom_edge_list_with_weights_is_used():
    at = _set(_fresh_app(), net_select="custom", edges_input="0-1:8, 1-2:6, 2-3:2")
    assert not at.exception
    assert any("13/2" in str(d.value) for d in at.dataframe)          # Auszahlung 13/2 des zweiten Betriebs, Literaturbeispiel


def test_permalink_is_clamped_to_the_slider_bounds():
    at = AppTest.from_file(APP_PATH, default_timeout=TIMEOUT)
    at.query_params["n"] = "100000"
    at.query_params["netz"] = "unbekannt"
    at.query_params["kappa"] = "0.3"
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    assert at.sidebar.slider(key="n_slider").value == C.N_MAX
    assert at.sidebar.selectbox(key="net_select").value == C.DEFAULT_NET
    assert at.sidebar.select_slider(key="kappa_slider").value == C.DEFAULT_KAPPA


def test_pdf_button_creates_a_download():
    at = _fresh_app()
    at.button(key="pdf_button").click().run()
    assert not at.exception, [str(e) for e in at.exception]
    assert at.session_state["pdf_bytes"][:5] == b"%PDF-"


def test_pdf_for_a_net_without_stable_outcome():
    at = _set(_fresh_app(), net_select="cycle", n_slider=3)
    at.button(key="pdf_button").click().run()
    assert not at.exception, [str(e) for e in at.exception]
    assert at.session_state["pdf_bytes"][:5] == b"%PDF-"


def test_on_demand_buttons_appear_only_for_large_nets_and_compute_on_click():
    at = _fresh_app()
    assert not [b for b in at.button if AUTOPLAY_MARKER in b.label]                   # kleines Netz: alles sofort
    at = _set(_fresh_app(), net_select="rand_bip", n_slider=40, p_slider=30)
    labels = [b.label for b in at.button if AUTOPLAY_MARKER in b.label]
    assert len(labels) == 2
    assert any("Weitere Ergebnisse suchen" in label for label in labels) and any("Eigenschaften" in label for label in labels)
    assert any("erst auf Klick" in i.value for i in at.info)
    at.button(key="multi_button").click().run()
    assert not at.exception, [str(e) for e in at.exception]
    assert any("verschiedene ausgewogene Ergebnisse" in w.value or "denselben Auszahlungsvektor" in i.value for w in at.warning for i in at.info)
    at.button(key="prop_button").click().run()
    assert not at.exception, [str(e) for e in at.exception]
    assert any("Blattknoten" in str(d.value.columns) for d in at.dataframe)
    # nach einer Änderung der Einstellungen ist das Ergebnis weg und der Knopf wieder nötig
    at = _set(at, seed_input=36)
    assert any("erst auf Klick" in i.value for i in at.info)
