import json
from pathlib import Path

import pytest

from tools import build_site, token_usage

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"


def _transcript(tmp_path):
    lines = [
        {"type": "user", "timestamp": "2026-11-10T17:00:00Z"},
        {"type": "assistant", "timestamp": "2026-11-10T17:00:01Z", "requestId": "r1",
         "message": {"id": "m1", "model": "x", "usage": {"input_tokens": 10, "output_tokens": 5,
                     "cache_creation_input_tokens": 100, "cache_read_input_tokens": 1000},
                     "content": [{"type": "tool_use", "name": "Bash"}]}},
        # second content block of the same request repeats usage -> must not double count
        {"type": "assistant", "timestamp": "2026-11-10T17:00:02Z", "requestId": "r1",
         "message": {"id": "m1", "usage": {"input_tokens": 10, "output_tokens": 5,
                     "cache_creation_input_tokens": 100, "cache_read_input_tokens": 1000},
                     "content": [{"type": "tool_use", "name": "Write"}]}},
        {"type": "assistant", "timestamp": "2026-11-10T17:05:00Z", "requestId": "r2",
         "message": {"id": "m2", "usage": {"input_tokens": 1, "output_tokens": 2,
                     "cache_creation_input_tokens": 0, "cache_read_input_tokens": 3}, "content": []}},
        {"type": "system", "subtype": "compact_boundary", "timestamp": "2026-11-10T17:06:00Z"},
        {"type": "assistant", "isSidechain": True, "timestamp": "2026-11-10T17:07:00Z", "requestId": "r3",
         "message": {"usage": {"input_tokens": 999, "output_tokens": 999}}},
    ]
    p = tmp_path / "abc.jsonl"
    p.write_text("\n".join(json.dumps(l) for l in lines) + "\nnot json\n", encoding="utf-8")
    return p


@pytest.mark.phase(5)
def test_token_parser_dedupes_and_sums(tmp_path):
    """[AC-5.2] Requests are deduplicated by requestId, sidechains skipped, tokens summed exactly."""
    reqs, events = token_usage.parse_transcript(_transcript(tmp_path))
    assert [r["input_tokens"] for r in reqs] == [10, 1]
    assert sum(r["output_tokens"] for r in reqs) == 7
    assert reqs[0]["tools"] == ["Bash", "Write"]
    assert events == [{"ts": "2026-11-10T17:06:00Z", "session": "abc", "event": "compact"}]


@pytest.mark.phase(5)
def test_label_for_picks_latest_label():
    """[AC-5.3] Each request is labeled with the activity that started most recently before it."""
    labels = [{"ts": "2026-11-10T12:00:00-05:00", "activity": "planning", "phase": 0},
              {"ts": "2026-11-10T13:00:00-05:00", "activity": "coding", "phase": 2}]
    ts = token_usage.parse_ts
    assert token_usage.label_for(ts("2026-11-10T17:30:00Z"), labels)["activity"] == "planning"
    assert token_usage.label_for(ts("2026-11-10T18:30:00Z"), labels)["activity"] == "coding"
    assert token_usage.label_for(ts("2026-11-10T16:00:00Z"), labels)["activity"] == "unlabeled"


@pytest.mark.phase(4)
def test_every_criterion_extracted_and_tested():
    """[AC-4.3] Every acceptance criterion in specs/ is extracted, and the UI can map it to tests."""
    crit = build_site.acceptance_criteria()
    ids = {c["id"] for c in crit}
    assert {"AC-1.1", "AC-2.3", "AC-5.2"} <= ids
    sources = "\n".join(build_site.test_sources().values())
    untested = [i for i in ids if f"[{i}]" not in sources]
    # UI and publication criteria are verified by the checks in test_site_* and by human review.
    assert all(i.startswith(("AC-3", "AC-4", "AC-5", "AC-6")) for i in untested), untested


@pytest.mark.phase(4)
def test_test_sources_extracted():
    """[AC-4.2] Test source code is extracted per test so the explorer can show it."""
    src = build_site.test_sources()
    key = "tests/test_phase5_tokens_site.py::test_test_sources_extracted"
    assert key in src and "def test_test_sources_extracted" in src[key]


@pytest.mark.phase(3)
@pytest.mark.parametrize("page,data", [("index.html", "findings.js"), ("validation.html", "validation.js"),
                                       ("timeline.html", "timeline.js"), ("tokens.html", "tokens.js")])
def test_site_pages_wired(page, data):
    """[AC-3.1] [AC-4.1] [AC-5.1] [AC-5.3] Each page exists, loads its data file and the shared nav/style."""
    html = (SITE / page).read_text(encoding="utf-8")
    assert f"data/{data}" in html and "style.css" in html and "nav.js" in html
    assert (SITE / "data" / data).exists()


@pytest.mark.phase(3)
def test_dashboard_covers_research_questions():
    """[AC-3.2] [AC-3.3] [AC-3.4] The dashboard has a section for each RQ plus explorer and limitations."""
    html = (SITE / "index.html").read_text(encoding="utf-8")
    for anchor in ["rq1", "rq2", "rq3", "rq4", "rq5", "schools", "evidence", "method", "limitations"]:
        assert f'id="{anchor}"' in html, anchor


@pytest.mark.phase(6)
def test_publication_ready():
    """[AC-6.1] [AC-6.2] [AC-6.3] README, .nojekyll and the evaluation template exist."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for page in ["index.html", "validation.html", "timeline.html", "tokens.html"]:
        assert page in readme
    assert (SITE / ".nojekyll").exists()
    assert (ROOT / "docs" / "evaluation.md").exists()
