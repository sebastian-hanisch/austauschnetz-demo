"""Vorgerechnete Reihen: Erzeuger-Hash stimmt, Struktur vollständig, kleine Aufträge werden neu gerechnet und gleichen den gespeicherten (data/tables.json), Messdisziplin der Zählungen."""

import json

import pytest

import aun_constants as C
import aun_experiments as XP


@pytest.fixture(scope="module")
def tables():
    t = XP.load_tables()
    assert t is not None, "data/tables.json fehlt oder gehört zu einem anderen Rechencode: python tools/make_grid.py"
    return t


def test_generator_hash_matches_the_sources(tables):
    assert tables["generator_hash"] == XP.tables_hash()
    assert tables["seeds"] == list(C.TABLE_SEEDS) and len(C.TABLE_SEEDS) == 4


def test_a_changed_hash_makes_the_loader_refuse_the_file(tmp_path, monkeypatch):
    bad = tmp_path / "tables.json"
    bad.write_text(json.dumps({"generator_hash": "0000"}), encoding="utf-8")
    monkeypatch.setattr(XP, "TABLES_FILE", bad)
    assert XP.load_tables() is None
    monkeypatch.setattr(XP, "TABLES_FILE", tmp_path / "fehlt.json")
    assert XP.load_tables() is None


def test_structure_is_complete(tables):
    assert set(tables["classes"]) == set(XP.CLASSES)
    assert set(tables["share"]) == {f"{n}:{p}" for n in XP.SHARE_NS for p in XP.SHARE_PS}
    assert set(tables["dynamics"]["kappas"]) == {str(k) for k in C.KAPPAS}
    assert set(tables["growth"]) == {str(s) for s in XP.GROWTH_SIDES}
    assert set(tables["game"]) == set(XP.GAME_KINDS)
    assert tables["atlas"]["graphs"] == 142


def test_every_class_counts_four_seeds_of_sixty_nets(tables):
    for key, c in tables["classes"].items():
        assert c["nets"] == 4 * XP.PER_JOB, key
        assert len(c["stable_per_seed"]) == 4 and sum(c["stable_per_seed"]) == c["stable"], key
        assert c["either"] + c["none"] == c["stable"], key


def test_balanced_counts_are_consistent(tables):
    for key, c in tables["classes"].items():
        assert c["d0"] <= c["either"] <= c["stable"] and c["red"] <= c["either"], key
        assert c["fixed0"] + c["fixed1"] + c["fixed_other"] + c["open"] == c["nodes"], key
        assert c["open_half"] + c["open_less"] + c["open_more"] == c["open"], key
        assert c["lower"] + c["same"] <= c["unequal"], key


def same(a, b, path="probe"):
    """Gleich bis auf Rundung der Gleitkommazahlen (Windows und Linux dürfen in der 12. Stelle abweichen); Zählungen und Texte exakt."""
    if isinstance(b, dict):
        assert isinstance(a, dict) and set(a) == set(b), path
        for k in b:
            same(a[k], b[k], f"{path}/{k}")
    elif isinstance(b, list):
        assert isinstance(a, list) and len(a) == len(b), path
        for i, (x, y) in enumerate(zip(a, b)):
            same(x, y, f"{path}[{i}]")
    elif isinstance(b, float):
        assert a == pytest.approx(b, abs=1e-8), path
    else:
        assert a == b, path


@pytest.mark.parametrize("job", XP.PROBES, ids=lambda j: "|".join(map(str, j)))
def test_probe_job_recomputes_to_the_stored_result(tables, job):
    _, res = XP.run_job(job)
    again = json.loads(json.dumps(res, default=XP._json_default))
    same(again, tables["probes"]["|".join(map(str, job))])


def test_pooled_correlation_from_sums_equals_numpy():
    import numpy as np
    x = [1, 2, 3, 4, 5, 9]
    y = [2, 1, 4, 3, 7, 8]
    assert XP.pooled_correlation(XP.sums(x, y)) == pytest.approx(float(np.corrcoef(x, y)[0, 1]))
    assert XP.pooled_correlation(XP.sums([1, 1, 1], [1, 2, 3])) is None


def test_merge_adds_counts_concatenates_lists_and_keeps_maxima():
    a = {"n": 2, "xs": [1.0], "scale_dev": 0.1, "deg_sums": [1.0, 2.0], "sub": {"k": 1}}
    b = {"n": 3, "xs": [2.0], "scale_dev": 0.3, "deg_sums": [3.0, 4.0], "sub": {"k": 4}}
    assert XP._merge([a, b]) == {"n": 5, "xs": [1.0, 2.0], "scale_dev": 0.3, "deg_sums": [4.0, 6.0], "sub": {"k": 5}}


def test_job_list_has_one_entry_per_cell():
    jobs = XP.jobs()
    assert len(jobs) == len(set(jobs)) == 6 * 4 + 2 * 7 * 4 + 4 + 4 + 2 * 4 + 4 + 4 + 1


def test_streams_of_different_cells_do_not_collide():
    """Zelle und Zufalls-Seed gehen in einen Strom ein; verschiedene (Seed, Zelle)-Paare der Reihen ergeben verschiedene Zustände."""
    from aun_net import stream
    cells = {XP.class_cell(k) + i for k in XP.CLASSES for i in range(XP.PER_JOB)}
    cells |= {100000 + 10000 * n + 100 * p + i for n in XP.SHARE_NS for p in XP.SHARE_PS for i in range(XP.SHARE_PER_JOB)}
    cells |= {90000 + i for i in range(XP.DYN_PER_JOB)} | {60000 + i for i in range(XP.PROP_PER_JOB)}
    states = {stream(seed, cell).state for seed in C.TABLE_SEEDS for cell in cells}
    assert len(states) == len(C.TABLE_SEEDS) * len(cells)
