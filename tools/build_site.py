"""Build site/data/validation.js and site/data/timeline.js from logs, specs, tests and git history."""
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "site" / "data"


def jsonl(name):
    p = ROOT / "logs" / name
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


def write_js(name, var, obj):
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / name).write_text(f"window.{var} = " + json.dumps(obj) + ";\n", encoding="utf-8")


def test_sources():
    """Map 'file::function' -> source code so reviewers can read each test next to its result."""
    out = {}
    for f in sorted((ROOT / "tests").glob("test_*.py")):
        src = f.read_text(encoding="utf-8")
        for m in re.finditer(r"^((?:@[^\n]*\n)*)def (test_\w+)\(.*?(?=^@|^def |\Z)", src, re.S | re.M):
            out[f"tests/{f.name}::{m.group(2)}"] = m.group(0).rstrip()
    return out


def acceptance_criteria():
    """Every '- **AC-x.y**' line in specs/*.md."""
    out = []
    for f in sorted((ROOT / "specs").glob("*.md")):
        for m in re.finditer(r"^- \*\*(AC-[\d.]+)\*\*\s*(.+)$", f.read_text(encoding="utf-8"), re.M):
            out.append({"id": m.group(1), "text": m.group(2).strip(), "spec": f.name})
    return out


def git_log():
    try:
        out = subprocess.run(["git", "log", "--pretty=format:%h\x1f%aI\x1f%an\x1f%s\x1f%b\x1e"],
                             capture_output=True, text=True, cwd=ROOT, encoding="utf-8").stdout
    except OSError:
        return []
    commits = []
    for rec in out.split("\x1e"):
        parts = rec.strip().split("\x1f")
        if len(parts) >= 4:
            commits.append({"hash": parts[0], "ts": parts[1], "author": parts[2], "subject": parts[3],
                            "claude_coauthor": "Co-Authored-By: Claude" in (parts[4] if len(parts) > 4 else "")})
    return commits


def main():
    results = jsonl("validation.jsonl")
    write_js("validation.js", "VALIDATION", {
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "results": results, "adhoc": jsonl("adhoc_checks.jsonl"),
        "sources": test_sources(), "criteria": acceptance_criteria()})
    write_js("timeline.js", "TIMELINE", {
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "events": jsonl("timeline.jsonl"), "commits": git_log(), "sessions": jsonl("sessions.jsonl")})
    print(f"site data: {len(results)} test results, {len(jsonl('timeline.jsonl'))} timeline events")


if __name__ == "__main__":
    main()
