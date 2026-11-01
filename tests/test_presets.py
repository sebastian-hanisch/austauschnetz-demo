"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen; jedes Preset baut ein Netz."""

import aun_constants as C
import aun_net as N
import aun_presets as P
import aun_scenario as S


def _settings(preset):
    d = {state_key: P.SETTING_SPECS[state_key].default for state_key in P.SETTING_SPECS}
    for key, state_key in P.PRESET_KEYS.items():
        if key in preset:
            d[state_key] = preset[key]
    return S.Settings(net=d["net_select"], n=d["n_slider"], p=d["p_slider"], kappa=d["kappa_slider"], seed=d["seed_input"], edges=d["edges_input"])


def test_every_preset_has_help_and_only_known_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) <= set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds_and_choices():
    for name, preset in C.PRESETS.items():
        s = _settings(preset)
        assert s.net in C.NETS and C.N_MIN <= s.n <= C.N_MAX and C.P_MIN <= s.p <= C.P_MAX and s.kappa in C.KAPPAS and 0 <= s.seed <= C.SEED_MAX, name
        assert len(s.edges) <= C.EDGES_MAX_CHARS


def test_default_preset_equals_the_default_settings():
    assert _settings(C.PRESETS[next(iter(C.PRESETS))]) == S.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_every_preset_builds_a_valid_net():
    for name, preset in C.PRESETS.items():
        net, err = S.build_net(_settings(preset))
        assert net is not None and err is None, name
        assert net.edges


def test_named_presets_have_the_documented_shape():
    by_name = {name: S.build_net(_settings(p))[0] for name, p in C.PRESETS.items()}
    assert by_name["Weg mit 5: die Mitte bekommt nichts"] == N.path(5)
    assert by_name["Kreis mit 4: viele Ergebnisse"] == N.cycle(4)
    assert by_name["Dreieck: kein stabiles Ergebnis"] == N.cycle(3)
    assert by_name["Stern: die Mitte bekommt alles"] == N.star(3)
    assert by_name["Literaturbeispiel 8-6-2"] == N.literature_example()
    assert by_name["Zweiseitig 2 + 3: Dynamik braucht Reduktion"] == N.complete_bipartite(2, 3)
    assert by_name["Dreieck mit Anhang"].edges == N.triangle_with_tail().edges
    assert by_name["Zufallsnetz zweiseitig 8 + 8"].n <= 16 and by_name["Zufallsnetz zweiseitig 8 + 8"].sides is not None
    assert by_name["Größtes Netz (30 + 30, κ = 0,25)"].n <= 60


def test_net_builder_covers_every_net_kind_and_is_deterministic():
    for kind in C.NETS:
        s = S.Settings(net=kind, n=11, p=40, seed=7, edges="0-1, 1-2")
        a, ea = S.build_net(s)
        b, _ = S.build_net(s)
        assert a is not None and a == b and ea is None, kind
