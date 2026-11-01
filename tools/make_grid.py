"""Rechnet die Messreihen (Existenz stabiler und ausgewogener Ergebnisse, Macht gegen Grad, Dynamik, Mehrdeutigkeit, Atlas, Kern/Shapley/Nukleolus, Ausstiegsprinzip,
Eigenschaften) neu und schreibt data/tables.json samt Erzeuger-Hash.

Aufruf (im Demo-Ordner, mit dem Test-venv):  python tools/make_grid.py [--workers 4]
Ändert sich eine Quelldatei aus aun_experiments.TABLE_SOURCES, stimmt der Hash nicht mehr (tests/test_measurements.py schlägt an, die App zeigt die Reihen dann nicht);
danach diesen Aufruf wiederholen. Die Zufallsströme hängen nur an (Zufalls-Seed, Zelle): die Reihen sind bei gleichem Code Zahl für Zahl dieselben, auch bei anderer Zahl von Prozessen."""

import argparse
import pickle
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import aun_experiments as XP  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--cache", default=None, help="Ordner für Zwischenergebnisse (Pickle je Auftrag und Code-Hash): ein abgebrochener Lauf rechnet nur den Rest")
    args = ap.parse_args()
    start = time.time()
    jobs = XP.jobs()
    results = {}
    cache = Path(args.cache) if args.cache else None
    if cache:
        cache.mkdir(parents=True, exist_ok=True)
        h = XP.tables_hash()
        for job in jobs:
            f = cache / f"{h}_{'_'.join(map(str, job))}.pkl"
            if f.exists():
                results[job] = pickle.loads(f.read_bytes())
    todo = [j for j in jobs if j not in results]
    with ProcessPoolExecutor(max_workers=min(args.workers, 4)) as ex:
        for job, res in ex.map(XP.run_job, todo, chunksize=1):
            results[job] = res
            if cache:
                (cache / f"{XP.tables_hash()}_{'_'.join(map(str, job))}.pkl").write_bytes(pickle.dumps(res))
            print(f"  fertig: {job} ({time.time() - start:.0f} s)", flush=True)
    XP.write_json(XP.TABLES_FILE, XP.assemble_payload(results))
    print(f"geschrieben: {XP.TABLES_FILE}  ({time.time() - start:.0f} s, Hash {XP.tables_hash()}, {len(jobs)} Aufträge)")


if __name__ == "__main__":
    main()
