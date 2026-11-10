import csv
import json
from datetime import datetime
from pathlib import Path

import pytest

from pipeline import collect

ROOT = Path(__file__).resolve().parent.parent
DOCS = json.loads((ROOT / "data" / "documents.json").read_text(encoding="utf-8"))
SCHOOLS = list(csv.DictReader(open(ROOT / "data" / "schools.csv", encoding="utf-8")))
SEEDS = list(csv.DictReader(open(ROOT / "data" / "seed_urls.csv", encoding="utf-8")))
HAVE_RAW = (ROOT / "data" / "raw").exists()


@pytest.mark.phase(1)
@pytest.mark.parametrize("school", SCHOOLS, ids=lambda s: s["domain"])
def test_every_school_has_a_document(school):
    """[AC-1.1] Each sampled school has at least one successfully fetched document."""
    assert any(d["domain"] == school["domain"] and d["status"] == "ok" for d in DOCS)


@pytest.mark.phase(1)
def test_document_records_complete():
    """[AC-1.2] Every record has school, category, URL, ISO timestamp with offset, and status."""
    for d in DOCS:
        assert d["school"] and d["category"] in collect.CATEGORIES and d["url"].startswith("http")
        assert datetime.fromisoformat(d["retrieved"]).tzinfo is not None
        assert d["status"] in {"ok", "error"}


@pytest.mark.phase(1)
@pytest.mark.skipif(not HAVE_RAW, reason="raw pages are not committed; run `python project2.py collect`")
def test_ok_documents_have_raw_text():
    """[AC-1.2] Every 'ok' document points to an existing, non-empty raw text file."""
    for d in DOCS:
        if d["status"] == "ok":
            p = ROOT / d["raw"]
            assert p.exists() and p.stat().st_size > 0, d["url"]


@pytest.mark.phase(1)
@pytest.mark.parametrize("seed", SEEDS, ids=lambda s: s["url"][:60])
def test_seed_urls_on_school_domain(seed):
    """[AC-1.3] Seed URLs belong to their school's own domain and have a valid category."""
    assert seed["domain"] in {s["domain"] for s in SCHOOLS}
    assert collect.on_domain(seed["url"], seed["domain"])
    assert seed["category"] in collect.CATEGORIES


@pytest.mark.phase(1)
def test_on_domain_rejects_lookalikes():
    """[AC-1.3] Domain check accepts subdomains but rejects look-alike hosts."""
    assert collect.on_domain("https://cs.cmu.edu/x", "cmu.edu")
    assert collect.on_domain("https://cmu.edu/", "cmu.edu")
    assert not collect.on_domain("https://evilcmu.edu/", "cmu.edu")
    assert not collect.on_domain("https://cmu.edu.evil.com/", "cmu.edu")


@pytest.mark.phase(1)
def test_html_extraction_strips_scripts():
    """[AC-1.4] HTML extraction keeps title and visible text, drops script/style content."""
    html = b"<html><head><title>CS 101 Syllabus</title><style>p{}</style></head><body>" \
           b"<script>var x='secret';</script><p>Generative AI is not permitted.</p></body></html>"
    text = collect.extract_text(html, "text/html")
    assert text.startswith("CS 101 Syllabus")
    assert "Generative AI is not permitted." in text
    assert "secret" not in text and "p{}" not in text


@pytest.mark.phase(1)
def test_pdf_extraction():
    """[AC-1.4] PDF bytes are detected and parsed (via pypdf) without error."""
    from pypdf import PdfWriter
    import io
    buf = io.BytesIO()
    w = PdfWriter()
    w.add_blank_page(width=72, height=72)
    w.write(buf)
    assert isinstance(collect.extract_text(buf.getvalue(), "application/octet-stream"), str)


@pytest.mark.phase(1)
def test_failures_recorded_with_error():
    """[AC-1.5] Failed fetches stay in documents.json with an error message."""
    errors = [d for d in DOCS if d["status"] == "error"]
    assert all(d.get("error") for d in errors)
    assert len(DOCS) == len({d["url"] for d in DOCS}), "duplicate URLs"
