"""Write data/review_sample.csv: a stratified random 25% of coded documents for independent human coding.

The human opens each URL, decides the stance (1-5 or None) WITHOUT looking at Claude's code, and fills
in `human_stance`. `python project2.py analyze` then reports Cohen's kappa on the dashboard.
Existing human answers are preserved if the file already exists.
"""
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "review_sample.csv"
FRACTION = 0.25


def sample(coded, fraction=FRACTION, seed=2026):
    rng = random.Random(seed)
    by_cat = defaultdict(list)
    for d in coded:
        by_cat[d["category"]].append(d)
    picked = []
    for cat in sorted(by_cat):
        docs = sorted(by_cat[cat], key=lambda d: d["url"])
        picked += rng.sample(docs, max(1, round(len(docs) * fraction)))
    return picked


def main():
    coded = json.loads((ROOT / "data" / "coded.json").read_text(encoding="utf-8"))
    existing = {}
    if OUT.exists():
        with open(OUT, newline="", encoding="utf-8") as f:
            existing = {r["url"]: r for r in csv.DictReader(f)}
    rows = sample(coded)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["school", "category", "url", "human_stance", "human_notes"])
        for d in rows:
            old = existing.get(d["url"], {})
            w.writerow([d["school"], d["category"], d["url"], old.get("human_stance", ""), old.get("human_notes", "")])
    print(f"review sample: {len(rows)}/{len(coded)} documents -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
