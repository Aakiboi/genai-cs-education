"""Records every pytest result to logs/validation.jsonl for the validation explorer (Deliverable #2)."""
import json
import subprocess
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "logs" / "validation.jsonl"
RUN_ID = datetime.now().astimezone().isoformat(timespec="seconds")


def _git_commit():
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, cwd=ROOT)
        return out.stdout.strip() or None
    except OSError:
        return None


COMMIT = _git_commit()


def pytest_configure(config):
    config.addinivalue_line("markers", "phase(n): project phase this test validates")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    # Log the test body result, or a setup failure/skip (the body never ran then).
    if rep.when != "call" and not (rep.when == "setup" and rep.outcome != "passed"):
        return
    marker = item.get_closest_marker("phase")
    fn = getattr(item, "function", None)
    entry = {
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "run_id": RUN_ID,
        "commit": COMMIT,
        "test": rep.nodeid,
        "file": rep.location[0],
        "outcome": rep.outcome,
        "duration_s": round(rep.duration, 4),
        "phase": marker.args[0] if marker else None,
        "doc": ((fn.__doc__ or "").strip() or None) if fn else None,
        "message": str(rep.longrepr)[:2000] if rep.failed else None,
    }
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
