import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.phase(0)
@pytest.mark.parametrize("path", ["CLAUDE.md", "STATE.md", "specs/00-overview.md", "project2.py"])
def test_required_files_exist(path):
    """Spec 00: scaffolding files that let work survive /clear must exist and be non-empty."""
    p = ROOT / path
    assert p.exists() and p.stat().st_size > 0, f"{path} missing or empty"


@pytest.mark.phase(0)
@pytest.mark.parametrize("name", ["timeline.jsonl", "sessions.jsonl"])
def test_logs_are_valid_jsonl_with_timestamps(name):
    """CLAUDE.md logging rules: every log line is JSON with an ISO-8601 timestamp including offset."""
    from datetime import datetime
    lines = (ROOT / "logs" / name).read_text(encoding="utf-8").splitlines()
    assert lines, f"{name} is empty"
    for i, line in enumerate(lines, 1):
        obj = json.loads(line)
        ts = datetime.fromisoformat(obj["ts"])
        assert ts.tzinfo is not None, f"{name}:{i} timestamp has no UTC offset"


@pytest.mark.phase(0)
def test_timeline_actors_are_valid():
    """Timeline entries attribute every event to either the human or Claude."""
    for line in (ROOT / "logs" / "timeline.jsonl").read_text(encoding="utf-8").splitlines():
        assert json.loads(line)["actor"] in {"human", "claude"}
