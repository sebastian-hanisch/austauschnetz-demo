"""Vorgerechnete Messreihen (data/tables.json) mit Erzeuger-Hash und die Zählungen dahinter.

Jede Reihe ist über die Zufalls-Seeds `C.TABLE_SEEDS` (vier Stück) gemessen, die Netze kommen aus `aun_net` (SplitMix64, kein Python-hash).
Aufträge sind kleine, einzeln und in beliebiger Reihenfolge berechenbare Blöcke; `tools/make_grid.py` verteilt sie auf Prozesse und setzt sie zusammen.
Ändert sich eine der Quelldateien in TABLE_SOURCES, stimmt der Hash nicht mehr: die App zeigt die Reihen dann nicht, `tests/test_measurements.py` schlägt an.

Ausgewogenes Ergebnis eines Netzes in den Reihen = das zuerst gefundene (`aun_balanced.balanced_outcome`: Dynamik von Null mit κ = 0,5, sonst Reduktion). Bei Mehrdeutigkeit
ist das eine Auswahlregel; Aussagen über „das“ Ergebnis in den Reihen gelten für diese Regel."""

import hashlib
import json
import numbers
import statistics
from pathlib import Path

import numpy as np

import aun_atlas as AT
import aun_balanced as B
import aun_constants as C
import aun_game as G
import aun_multi as MU
import aun_net as N
import aun_principle as P
import aun_stable as S

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
TABLES_FILE = DATA / "tables.json"
TABLE_SOURCES = ("aun_net.py", "aun_matching.py", "aun_stable.py", "aun_balanced.py", "aun_exact.py", "aun_multi.py", "aun_game.py", "aun_principle.py", "aun_atlas.py",
                 "aun_rng.py", "aun_experiments.py", "data/atlas_graphs.json")

# --- Netzklassen der Reihen --------------------------------------------------------------------------------------------------------------------------------
CLASSES = {
    "bip88": "zweiseitig 8 + 8, p = 0,3",
    "bip66": "zweiseitig 6 + 6, p = 0,5",
    "tree10": "Baum mit 10 Knoten",
    "gen8a": "allgemein, 8 Knoten, p = 0,3",
    "gen8b": "allgemein, 8 Knoten, p = 0,5",
    "gen12": "allgemein, 12 Knoten, p = 0,3",
}
PER_JOB = 60                         # Netze je Klasse und Zufalls-Seed
PRINCIPLE_CLASSES = ("bip88", "tree10", "gen8a")
SHARE_NS = (8, 12)
SHARE_PS = (15, 20, 30, 40, 50, 60, 80)          # Prozent
SHARE_PER_JOB = 100
DYN_PER_JOB = 50
GROWTH_SIDES = (8, 16, 32, 64, 128)
GROWTH_PER_JOB = 5
GAME_PER_JOB = 12
GAME_KINDS = {"bip44": "zweiseitig 4 + 4, p = 0,5", "gen7": "allgemein, 7 Knoten, p = 0,4"}
PROP_PER_JOB = 40
PROP_FACTORS = (2, 3, 7)
ATLAS_STARTS = 10                    # Zufallsstarts je Atlas-Graph (dazu Dynamik von Null und Reduktion: zwölf Wege)
SAME = 1e-6                          # Auszahlungen gelten als gleich, wenn kein Knoten um mehr abweicht
MORE_STARTS = 20                     # Gegenprobe zur Mehrdeutigkeit: so viele Zufallsstarts statt fünf
PROBES = (("share", 8, 30, 11), ("dyn", 11), ("growth", 11), ("game", "bip44", 11))      # kleine Aufträge, die ein Test noch einmal rechnet und mit den gespeicherten Ergebnissen vergleicht


def tables_hash() -> str:
    h = hashlib.sha256()
    for name in TABLE_SOURCES:
        data = (ROOT / name).read_bytes().replace(b"\r\n", b"\n")
        h.update(name.encode() + b"\0" + data + b"\0")
    return h.hexdigest()[:16]


def load_tables():
    """Die vorgerechneten Reihen, oder None, wenn die Datei fehlt oder zu einem anderen Rechencode gehört."""
    if not TABLES_FILE.exists():
        return None
    try:
        payload = json.loads(TABLES_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return payload if payload.get("generator_hash") == tables_hash() else None


def _json_default(x):
    if isinstance(x, np.generic):
        return x.item()
    raise TypeError(f"nicht serialisierbar: {type(x)}")


def write_json(path: Path, payload: dict):
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True, default=_json_default) + "\n", encoding="utf-8")


def mean_sd(values) -> dict:
    v = [float(x) for x in values]
    return {"mean": statistics.fmean(v), "sd": statistics.stdev(v) if len(v) > 1 else 0.0, "values": v}


def median(values):
    return float(statistics.median(values)) if values else None


def quantile(values, q):
    return float(np.quantile(values, q)) if len(values) else None


# --- Netze der Klassen ---------------------------------------------------------------------------------------------------------------------------------------
def class_net(key: str, rng) -> N.Net:
    if key == "bip88":
        return N.random_bipartite(8, 8, 0.3, rng)
    if key == "bip66":
        return N.random_bipartite(6, 6, 0.5, rng)
    if key == "tree10":
        return N.random_tree(10, rng)
    if key == "gen8a":
        return N.random_general(8, 0.3, rng)
    if key == "gen8b":
        return N.random_general(8, 0.5, rng)
    return N.random_general(12, 0.3, rng)


def class_cell(key: str) -> int:
    return 100 * (list(CLASSES).index(key) + 1)


def max_dev(a, b) -> float:
    return float(max(abs(x - y) for x, y in zip(a, b)))


def edge_stats(net, y, matching):
    """Matching-Kanten mit ungleichem Grad: wie viele, in wie vielen bekommt der Knoten mit dem höheren Grad weniger / gleich viel."""
    deg = N.degrees(net)
    unequal = lower = same = 0
    for u, v, _ in matching:
        if deg[u] != deg[v]:
            unequal += 1
            hi, lo = (u, v) if deg[u] > deg[v] else (v, u)
            if y[hi] < y[lo] - SAME:
                lower += 1
            elif abs(y[hi] - y[lo]) <= SAME:
                same += 1
    return unequal, lower, same


def sums(x, y):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    return [float(len(x)), float(x.sum()), float(y.sum()), float((x * y).sum()), float((x * x).sum()), float((y * y).sum())]


def class_job(key: str, seed: int) -> dict:
    """60 Netze einer Klasse: Existenz stabiler Ergebnisse, Verfahren, festgelegte und offene Knoten, Macht gegen Grad, Mehrdeutigkeit, Ausstiegsprinzip."""
    base = class_cell(key)
    r = dict(nets=0, stable=0, d0=0, red=0, either=0, none=0, red_refused=0, nodes=0, fixed0=0, fixed1=0, fixed_other=0, open=0, open_half=0, open_less=0, open_more=0,
             deg_sums=[0.0] * 6, bet_sums=[0.0] * 6, deg_sums_matched=[0.0] * 6, unequal=0, lower=0, same=0, ambiguous=0, deviations=[], principle_both=0, principle_same=0,
             principle_none=0, principle_dev=[], d0_not_matching=0)
    deg_x, deg_y, bet_x, bet_y, dm_x, dm_y = [], [], [], [], [], []
    for i in range(PER_JOB):
        rng = N.stream(seed, base + i)
        net = class_net(key, rng)
        r["nets"] += 1
        lp, ip = S.lp_gap(net)
        if lp - ip >= S.TOL:
            continue
        r["stable"] += 1
        rg = S.stable_range(net, ip)
        fixed = S.fixed_nodes(*rg)
        st = B.dyn_structure(net)
        y0, m0, _, conv = B.by_dynamics(net, st, 0.5)
        yr, mr, why = B.by_reduction(net, rg, 0.5)
        r["d0"] += y0 is not None
        r["red"] += yr is not None
        r["red_refused"] += (yr is None and "Außenoption" in why)
        r["either"] += (y0 is not None or yr is not None)
        r["none"] += (y0 is None and yr is None)
        if y0 is None:
            r["d0_not_matching"] += 1
        y, m = (y0, m0) if y0 is not None else (yr, mr)
        if y is None:
            continue
        deg = N.degrees(net)
        bet = N.betweenness(net)
        matched = {x for u, v, _ in m for x in (u, v)}
        r["nodes"] += net.n
        for v in range(net.n):
            if v in fixed:
                if abs(fixed[v]) < 1e-7:
                    r["fixed0"] += 1
                elif abs(fixed[v] - 1) < 1e-7:
                    r["fixed1"] += 1
                else:
                    r["fixed_other"] += 1
            else:
                r["open"] += 1
                if abs(y[v] - 0.5) <= SAME:
                    r["open_half"] += 1
                elif y[v] < 0.5:
                    r["open_less"] += 1
                else:
                    r["open_more"] += 1
        deg_x += deg
        deg_y += list(y)
        bet_x += bet
        bet_y += list(y)
        dm_x += [deg[v] for v in matched]
        dm_y += [y[v] for v in matched]
        u_, l_, s_ = edge_stats(net, y, m)
        r["unequal"] += u_
        r["lower"] += l_
        r["same"] += s_
        found = MU.distinct_outcomes(net, seed, starts=5, rg=rg, cell=7000 + 10 * i)
        if len(found) >= 2:
            r["ambiguous"] += 1
            r["deviations"].append(MU.max_deviation(found))
        if key in PRINCIPLE_CLASSES:
            pr = P.principle_outcome(net, seed, y_nash=y, cell=8000 + 10 * i)
            if pr is None:
                r["principle_none"] += 1
            else:
                r["principle_both"] += 1
                d = max_dev(y, pr[0])
                r["principle_dev"].append(d)
                r["principle_same"] += d <= SAME
    r["deg_sums"], r["bet_sums"], r["deg_sums_matched"] = sums(deg_x, deg_y), sums(bet_x, bet_y), sums(dm_x, dm_y)
    return r


def starts_job(seed: int) -> dict:
    """Gegenprobe zu den Zufallsstarts: dieselben 60 zweiseitigen 8 + 8-Netze der Klasse bip88, Mehrdeutigkeit mit 5 und mit MORE_STARTS Zufallsstarts gefunden?"""
    base = class_cell("bip88")
    r = dict(nets=0, stable=0, ambiguous_5=0, ambiguous_more=0)
    for i in range(PER_JOB):
        net = class_net("bip88", N.stream(seed, base + i))
        r["nets"] += 1
        if not S.stable_exists(net):
            continue
        r["stable"] += 1
        found5 = MU.distinct_outcomes(net, seed, starts=5, cell=7000 + 10 * i)
        found_more = MU.distinct_outcomes(net, seed, starts=MORE_STARTS, cell=7000 + 10 * i)
        r["ambiguous_5"] += len(found5) >= 2
        r["ambiguous_more"] += len(found_more) >= 2
    return r


def share_job(n: int, p: int, seed: int) -> dict:
    stable = 0
    for i in range(SHARE_PER_JOB):
        net = N.random_general(n, p / 100, N.stream(seed, 100000 + 10000 * n + 100 * p + i))
        stable += S.stable_exists(net)
    return dict(n=n, p=p, seed=seed, nets=SHARE_PER_JOB, stable=stable)


def dyn_job(seed: int) -> dict:
    """50 zweiseitige 8 + 8-Netze (p = 0,3): Schritte der Dynamik von Null je Dämpfung, Fixpunkt ausgewogen?, Fixpunkt gleich über die Dämpfungen?"""
    out = {str(k): dict(steps=[], converged=0, balanced=0) for k in C.KAPPAS}
    out["max_fixpoint_difference"] = 0.0
    out["nets"] = 0
    for i in range(DYN_PER_JOB):
        net = N.random_bipartite(8, 8, 0.3, N.stream(seed, 90000 + i))
        st = B.dyn_structure(net)
        ys = []
        for k in C.KAPPAS:
            res = B.run_dynamics(st, k)
            row = out[str(k)]
            row["steps"].append(res.iterations)
            row["converged"] += res.converged
            row["balanced"] += (res.converged and B.balanced_matching(net, res.y) is not None)
            ys.append(res.y)
        out["nets"] += 1
        out["max_fixpoint_difference"] = max(out["max_fixpoint_difference"], max(float(np.max(np.abs(y - ys[0]))) for y in ys[1:]))
    return out


def growth_job(seed: int) -> dict:
    """Zweiseitige n + n-Netze mit mittlerem Grad 3 (p = 3/n): Schritte der Dynamik von Null (κ = 0,5), Fixpunkt ausgewogen?"""
    out = {}
    for side in GROWTH_SIDES:
        steps, conv, bal = [], 0, 0
        for i in range(GROWTH_PER_JOB):
            net = N.random_bipartite(side, side, 3 / side, N.stream(seed, 95000 + 10 * side + i))
            res = B.run_dynamics(B.dyn_structure(net), 0.5)
            steps.append(res.iterations)
            conv += res.converged
            bal += (res.converged and B.balanced_matching(net, res.y) is not None)
        out[str(side)] = dict(steps=steps, converged=conv, balanced=bal, nets=GROWTH_PER_JOB)
    return out


def game_job(kind: str, seed: int) -> dict:
    """Kern, Shapley und Nukleolus für kleine Netze (höchstens 8 Knoten)."""
    r = dict(nets=0, core=0, balanced_found=0, balanced_in_core=0, shapley_in_core=0, shapley_equal=0, shapley_dev=[], nucleolus_balanced=0, nucleolus_equal=0,
             nucleolus_dev=[], nucleolus_in_core=0)
    for i in range(GAME_PER_JOB):
        rng = N.stream(seed, 70000 + (0 if kind == "bip44" else 500) + i)
        net = N.random_bipartite(4, 4, 0.5, rng) if kind == "bip44" else N.random_general(7, 0.4, rng)
        n = net.n
        v = G.coalition_values(net)
        r["nets"] += 1
        sh = G.shapley(v, n)
        x, _ = G.nucleolus(v, n)
        has_core = S.stable_exists(net)
        r["core"] += has_core
        r["shapley_in_core"] += G.in_core(sh, v, n)
        if not has_core:
            continue
        r["nucleolus_in_core"] += G.in_core(x, v, n, 1e-6)
        r["nucleolus_balanced"] += any(B.is_balanced(net, m, list(x), 1e-6) for m in B.candidate_matchings(net, x, 1e-5))
        out = B.balanced_outcome(net)
        if out.status != "ok":
            continue
        r["balanced_found"] += 1
        r["balanced_in_core"] += G.in_core(list(out.y), v, n, 1e-6)
        d_sh = max_dev(out.y, [float(s) for s in sh])
        d_nu = max_dev(out.y, x)
        r["shapley_dev"].append(d_sh)
        r["nucleolus_dev"].append(d_nu)
        r["shapley_equal"] += d_sh <= SAME
        r["nucleolus_equal"] += d_nu <= SAME
    return r


def prop_job(seed: int) -> dict:
    """Gewichtete zweiseitige 8 + 8-Netze (Werte 1 bis 5): Skalieren, Umnummerieren, ein Blattknoten mehr, eine Kante mehr."""
    r = dict(nets=0, found=0, scale_ok={str(c): 0 for c in PROP_FACTORS}, scale_dev=0.0, relabel_ok=0, relabel_dev=0.0, leaf_nets=0, leaf_down=0, leaf_up=0, leaf_same=0,
             leaf_others=0, leaf_others_down=0, leaf_others_up=0, leaf_others_same=0, edge_nets=0, edge_obs=0, edge_down=0, edge_up=0, edge_same=0, edge_both_not_worse=0)
    for i in range(PROP_PER_JOB):
        rng = N.stream(seed, 60000 + i)
        net = N.random_bipartite(8, 8, 0.3, rng, max_weight=5)
        r["nets"] += 1
        base = B.balanced_outcome(net)
        if base.status != "ok":
            continue
        r["found"] += 1
        y = list(base.y)
        for c in PROP_FACTORS:
            o = B.balanced_outcome(N.scaled(net, c))
            if o.status == "ok":
                d = float(max(abs(o.y[v] / c - y[v]) for v in range(net.n)))
                r["scale_dev"] = max(r["scale_dev"], d)
                r["scale_ok"][str(c)] += d <= SAME
        perm = list(range(net.n))
        for k in range(net.n - 1, 0, -1):
            j = N.rand_below(rng, k + 1)
            perm[k], perm[j] = perm[j], perm[k]
        o = B.balanced_outcome(N.relabel(net, perm))
        if o.status == "ok":
            d = float(max(abs(o.y[perm[v]] - y[v]) for v in range(net.n)))
            r["relabel_dev"] = max(r["relabel_dev"], d)
            r["relabel_ok"] += d <= SAME
        u = N.rand_below(rng, net.n)
        o = B.balanced_outcome(N.with_leaf(net, u))
        if o.status == "ok":
            r["leaf_nets"] += 1
            diff = o.y[u] - y[u]
            if diff < -SAME:
                r["leaf_down"] += 1
            elif diff > SAME:
                r["leaf_up"] += 1
            else:
                r["leaf_same"] += 1
            for v in range(net.n):
                if v != u:
                    d = o.y[v] - y[v]
                    r["leaf_others"] += 1
                    r["leaf_others_down"] += d < -SAME
                    r["leaf_others_up"] += d > SAME
                    r["leaf_others_same"] += abs(d) <= SAME
        sides = net.sides
        present = {(a, b) for a, b, _ in net.edges}
        free = [(a, b) for a in range(net.n) for b in range(a + 1, net.n) if sides[a] != sides[b] and (a, b) not in present]
        if free:
            a, b = free[N.rand_below(rng, len(free))]
            o = B.balanced_outcome(N.make_net(net.n, [(x, z) for x, z, _ in net.edges] + [(a, b)], [w for _, _, w in net.edges] + [1], net.sides))
            if o.status == "ok":
                r["edge_nets"] += 1
                worse = 0
                for v in (a, b):
                    d = o.y[v] - y[v]
                    r["edge_obs"] += 1
                    r["edge_down"] += d < -SAME
                    r["edge_up"] += d > SAME
                    r["edge_same"] += abs(d) <= SAME
                    worse += d < -SAME
                r["edge_both_not_worse"] += (worse == 0)
    return r


def atlas_job() -> dict:
    """Alle 142 zusammenhängenden Graphen mit 2 bis 6 Knoten (Einheitswert): stabil? mehrere ausgewogene Ergebnisse (zwölf Wege)?"""
    r = dict(graphs=0, stable=0, ambiguous=0, ambiguous_bipartite=0, bipartite_stable=0, none=0, by_n={})
    for idx, net in enumerate(AT.load_atlas()):
        r["graphs"] += 1
        row = r["by_n"].setdefault(str(net.n), dict(graphs=0, stable=0, ambiguous=0))
        row["graphs"] += 1
        lp, ip = S.lp_gap(net)
        if lp - ip >= S.TOL:
            continue
        r["stable"] += 1
        row["stable"] += 1
        bip = net.sides is not None
        r["bipartite_stable"] += bip
        found = MU.distinct_outcomes(net, 0, starts=ATLAS_STARTS, cell=9000 + 100 * idx)
        if not found:
            r["none"] += 1
        if len(found) >= 2:
            r["ambiguous"] += 1
            row["ambiguous"] += 1
            r["ambiguous_bipartite"] += bip
    return r


# --- Aufträge ----------------------------------------------------------------------------------------------------------------------------------------
def jobs() -> list:
    out = [("cls", k, s) for k in CLASSES for s in C.TABLE_SEEDS]
    out += [("share", n, p, s) for n in SHARE_NS for p in SHARE_PS for s in C.TABLE_SEEDS]
    out += [("dyn", s) for s in C.TABLE_SEEDS] + [("growth", s) for s in C.TABLE_SEEDS]
    out += [("game", kind, s) for kind in GAME_KINDS for s in C.TABLE_SEEDS]
    out += [("prop", s) for s in C.TABLE_SEEDS] + [("starts", s) for s in C.TABLE_SEEDS] + [("atlas",)]
    return out


def run_job(job):
    kind = job[0]
    if kind == "cls":
        res = class_job(job[1], job[2])
    elif kind == "share":
        res = share_job(job[1], job[2], job[3])
    elif kind == "dyn":
        res = dyn_job(job[1])
    elif kind == "growth":
        res = growth_job(job[1])
    elif kind == "game":
        res = game_job(job[1], job[2])
    elif kind == "prop":
        res = prop_job(job[1])
    elif kind == "starts":
        res = starts_job(job[1])
    else:
        res = atlas_job()
    return job, res


def _merge(parts):
    """Zählungen und Listen mehrerer Aufträge zusammenfügen (Zahlen addieren, Listen anhängen, Dictionaries rekursiv; Maxima bei *_dev-Feldern über 'max')."""
    out = {}
    for p in parts:
        for k, v in p.items():
            if isinstance(v, dict):
                out[k] = _merge([out.get(k, {}), v]) if k in out else _merge([v])
            elif isinstance(v, list):
                if v and isinstance(v[0], float) and "_sums" in k:
                    out[k] = [a + b for a, b in zip(out.get(k, [0.0] * len(v)), v)]
                else:
                    out[k] = out.get(k, []) + v
            elif isinstance(v, numbers.Number) and k in ("scale_dev", "relabel_dev", "max_fixpoint_difference"):
                out[k] = max(out.get(k, 0.0), v)
            elif isinstance(v, numbers.Number):
                out[k] = out.get(k, 0) + v
    return out


def pooled_correlation(s):
    """Korrelation aus den Summen (n, Σx, Σy, Σxy, Σx², Σy²); None, wenn eine Reihe konstant ist."""
    n, sx, sy, sxy, sxx, syy = s
    if n < 2:
        return None
    cov = sxy - sx * sy / n
    vx, vy = sxx - sx * sx / n, syy - sy * sy / n
    if vx <= 1e-12 or vy <= 1e-12:
        return None
    return cov / (vx * vy) ** 0.5


def assemble_payload(results: dict) -> dict:
    """Aus den Ergebnissen aller Aufträge die Tabellen der App (JSON-fest)."""
    payload = {"generator_hash": tables_hash(), "seeds": list(C.TABLE_SEEDS)}
    cls = {}
    for key in CLASSES:
        per_seed = [results[("cls", key, s)] for s in C.TABLE_SEEDS]
        tot = _merge(per_seed)
        tot["corr_deg_per_seed"] = [pooled_correlation(p["deg_sums"]) for p in per_seed]
        tot["corr_bet_per_seed"] = [pooled_correlation(p["bet_sums"]) for p in per_seed]
        tot["corr_deg"] = pooled_correlation(tot["deg_sums"])
        tot["corr_bet"] = pooled_correlation(tot["bet_sums"])
        tot["corr_deg_matched"] = pooled_correlation(tot["deg_sums_matched"])
        tot["ambiguous_per_seed"] = [p["ambiguous"] for p in per_seed]
        tot["principle_same_per_seed"] = [p["principle_same"] for p in per_seed]
        tot["stable_per_seed"] = [p["stable"] for p in per_seed]
        tot["none_per_seed"] = [p["none"] for p in per_seed]
        tot["deviation_median"] = median(tot["deviations"])
        tot["deviation_max"] = max(tot["deviations"], default=None)
        tot["principle_dev_mean"] = float(np.mean(tot["principle_dev"])) if tot["principle_dev"] else None
        tot["principle_dev_max"] = max(tot["principle_dev"], default=None)
        for drop in ("deviations", "principle_dev"):
            tot.pop(drop)
        cls[key] = tot
    payload["classes"] = cls
    share = {}
    for n in SHARE_NS:
        for p in SHARE_PS:
            parts = [results[("share", n, p, s)] for s in C.TABLE_SEEDS]
            per = [100 * q["stable"] / q["nets"] for q in parts]
            share[f"{n}:{p}"] = dict(n=n, p=p, nets=sum(q["nets"] for q in parts), stable=sum(q["stable"] for q in parts), per_seed_percent=per, **{"percent": mean_sd(per)})
    payload["share"] = share
    dyn = {"nets": 0, "max_fixpoint_difference": 0.0, "kappas": {}}
    for k in C.KAPPAS:
        parts = [results[("dyn", s)][str(k)] for s in C.TABLE_SEEDS]
        steps = [x for p in parts for x in p["steps"]]
        dyn["kappas"][str(k)] = dict(median=median(steps), q90=quantile(steps, 0.9), converged=sum(p["converged"] for p in parts), balanced=sum(p["balanced"] for p in parts), nets=len(steps))
    dyn["nets"] = sum(results[("dyn", s)]["nets"] for s in C.TABLE_SEEDS)
    dyn["max_fixpoint_difference"] = max(results[("dyn", s)]["max_fixpoint_difference"] for s in C.TABLE_SEEDS)
    payload["dynamics"] = dyn
    growth = {}
    for side in GROWTH_SIDES:
        parts = [results[("growth", s)][str(side)] for s in C.TABLE_SEEDS]
        steps = [x for p in parts for x in p["steps"]]
        growth[str(side)] = dict(median=median(steps), maximum=max(steps), converged=sum(p["converged"] for p in parts), balanced=sum(p["balanced"] for p in parts), nets=len(steps))
    payload["growth"] = growth
    game = {}
    for kind in GAME_KINDS:
        tot = _merge([results[("game", kind, s)] for s in C.TABLE_SEEDS])
        tot["shapley_dev_median"] = median(tot["shapley_dev"])
        tot["shapley_dev_max"] = max(tot["shapley_dev"], default=None)
        tot["nucleolus_dev_max"] = max(tot["nucleolus_dev"], default=None)
        tot.pop("shapley_dev")
        tot.pop("nucleolus_dev")
        game[kind] = tot
    payload["game"] = game
    payload["properties"] = _merge([results[("prop", s)] for s in C.TABLE_SEEDS])
    payload["starts"] = _merge([results[("starts", s)] for s in C.TABLE_SEEDS])
    payload["probes"] = {"|".join(map(str, job)): results[job] for job in PROBES}
    payload["atlas"] = results[("atlas",)]
    return payload
