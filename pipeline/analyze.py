"""Phase 2b: aggregate coded documents into findings for the dashboard (Spec 02/03).
Output: site/data/findings.js (window.FINDINGS = {...})
"""
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, median

from pipeline.code import STANCE_LABELS

ROOT = Path(__file__).resolve().parent.parent
TOOLS = {"ChatGPT": r"chatgpt", "Copilot": r"copilot", "Claude": r"\bclaude\b", "Gemini": r"\bgemini\b",
         "Cursor": r"\bcursor\b", "Codex": r"\bcodex\b"}
COURSE_CATS = {"course", "se_course"}


def mid(vals):
    vals = [v for v in vals if v is not None]
    return round(median(vals)) if vals else None


def avg(vals):
    vals = [v for v in vals if v is not None]
    return round(mean(vals), 3) if vals else None


def cohen_kappa(a, b):
    """Cohen's kappa for two equal-length label lists."""
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(a) | set(b)) / (n * n)
    return round((po - pe) / (1 - pe), 3) if pe < 1 else 1.0


def gold_accuracy(coded):
    by_url = {d["url"]: d for d in coded}
    rows = []
    with open(ROOT / "data" / "gold_stance.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = by_url.get(r["url"])
            ok_set = {int(x) for x in r["acceptable_stances"].split("|")}
            got = d["stance"] if d else None
            rows.append({"url": r["url"], "expected": sorted(ok_set), "got": got,
                         "match": got in ok_set, "basis": r["basis"]})
    return {"n": len(rows), "correct": sum(r["match"] for r in rows), "rows": rows}


def human_review(coded):
    """Kappa between Claude's coder and the human's labels in data/review_sample.csv, if filled in."""
    path = ROOT / "data" / "review_sample.csv"
    if not path.exists():
        return None
    by_url = {d["url"]: d for d in coded}
    pairs = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            h = (r.get("human_stance") or "").strip()
            if h and r["url"] in by_url:
                pairs.append((str(by_url[r["url"]]["stance"]), "None" if h.lower() == "none" else h))
    if not pairs:
        return {"n": 0, "kappa": None}
    return {"n": len(pairs), "kappa": cohen_kappa([p[0] for p in pairs], [p[1] for p in pairs]),
            "agreement": round(sum(a == b for a, b in pairs) / len(pairs), 3)}


def build(coded, schools):
    schools_out = []
    by_school = defaultdict(list)
    for d in coded:
        by_school[d["domain"]].append(d)
    for s in schools:
        docs = by_school.get(s["domain"], [])
        course = [d for d in docs if d["category"] in COURSE_CATS]
        st = mid(d["stance"] for d in course)
        schools_out.append({
            **s, "n_docs": len(docs),
            "course_stance": st, "course_stance_label": STANCE_LABELS.get(st, "No data"),
            "guidance_stance": mid(d["stance"] for d in docs if d["category"] == "policy"),
            "dept_sentiment": avg(d["sentiment"] for d in docs if d["category"] in ("department", "policy")),
            "sentiment": avg(d["sentiment"] for d in docs),
            "collaboration": any(d["collaboration_any"] for d in docs),
            "disclosure": any(d["disclosure_required"] for d in docs),
            "se_docs": sum(d["category"] == "se_course" for d in docs),
            "se_ai_subject": any(d["se_ai_subject"] for d in docs),
        })

    def group(key):
        out = {}
        for val in sorted({s[key] for s in schools_out}):
            g = [s for s in schools_out if s[key] == val]
            out[val] = {"n": len(g), "mean_course_stance": avg(s["course_stance"] for s in g),
                        "mean_sentiment": avg(s["sentiment"] for s in g),
                        "pct_collaboration": round(100 * sum(s["collaboration"] for s in g) / len(g)),
                        "pct_disclosure": round(100 * sum(s["disclosure"] for s in g) / len(g))}
        return out

    course_docs = [d for d in coded if d["category"] in COURSE_CATS]
    se_docs = [d for d in coded if d["category"] == "se_course"]
    cats = sorted({d["category"] for d in coded})
    tool_counts = Counter()
    for d in coded:
        blob = " ".join(sum(d["evidence"].values(), []))
        for name, rx in TOOLS.items():
            if re.search(rx, blob, re.I):
                tool_counts[name] += 1
    return {
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "stance_labels": STANCE_LABELS,
        "totals": {"schools": len(schools), "documents": len(coded),
                   "schools_with_docs": sum(s["n_docs"] > 0 for s in schools_out),
                   "course_docs": len(course_docs), "se_docs": len(se_docs)},
        "course_stance_dist": dict(Counter(str(d["stance"]) for d in course_docs)),
        "school_stance_dist": dict(Counter(str(s["course_stance"]) for s in schools_out)),
        "se_stance_dist": dict(Counter(str(d["stance"]) for d in se_docs)),
        "se_ai_subject": {"docs": sum(d["se_ai_subject"] for d in se_docs), "of": len(se_docs),
                          "schools": sum(s["se_ai_subject"] for s in schools_out)},
        "sentiment_by_category": {c: {"mean": avg(d["sentiment"] for d in coded if d["category"] == c),
                                      "n": sum(d["category"] == c for d in coded),
                                      "positive": sum((d["sentiment"] or 0) > 0.2 for d in coded if d["category"] == c),
                                      "negative": sum((d["sentiment"] or 0) < -0.2 for d in coded if d["category"] == c)}
                                  for c in cats},
        "collaboration": {"docs_any": sum(d["collaboration_any"] for d in coded),
                          **{k: sum(d["collaboration"][k] for d in coded) for k in ("collaborator", "tutor", "assistant")}},
        "disclosure_docs": sum(d["disclosure_required"] for d in coded),
        "tools_mentioned": dict(tool_counts.most_common()),
        "by_tier": group("tier"), "by_control": group("control"), "by_region": group("region"),
        "gold": gold_accuracy(coded),
        "human_review": human_review(coded),
        "schools": schools_out,
        "documents": coded,
    }


def main():
    coded = json.loads((ROOT / "data" / "coded.json").read_text(encoding="utf-8"))
    with open(ROOT / "data" / "schools.csv", newline="", encoding="utf-8") as f:
        schools = list(csv.DictReader(f))
    out = build(coded, schools)
    (ROOT / "site" / "data").mkdir(parents=True, exist_ok=True)
    (ROOT / "site" / "data" / "findings.js").write_text(
        "window.FINDINGS = " + json.dumps(out) + ";\n", encoding="utf-8")
    g = out["gold"]
    print(f"findings: {out['totals']}  gold accuracy {g['correct']}/{g['n']}")


if __name__ == "__main__":
    main()
