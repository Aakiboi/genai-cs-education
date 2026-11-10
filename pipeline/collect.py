"""Phase 1: fetch public genAI documents for each school (Spec 01).

Source URLs come from data/seed_urls.csv. They were found with Claude Code's WebSearch tool, one
site-restricted query per school ("computer science generative AI policy course software
engineering"). Scripted search-engine scraping was dropped: search engines block bots, and we
don't work around that. This script only downloads the schools' own public pages, extracts
text to data/raw/, and writes data/documents.json. URLs already fetched are skipped.
"""
import csv
import hashlib
import io
import json
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DOCS = ROOT / "data" / "documents.json"
UA = {"User-Agent": "Mozilla/5.0 (research crawler; CS education genAI policy study)"}
CATEGORIES = {"policy", "department", "course", "se_course"}


def load_csv(name):
    with open(ROOT / "data" / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def on_domain(url, domain):
    host = (urlparse(url).hostname or "").lower()
    return host == domain or host.endswith("." + domain)


def extract_text(content, content_type):
    if "pdf" in content_type or content[:5] == b"%PDF-":
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(content))
        return "\n".join((p.extract_text() or "") for p in reader.pages[:40])
    soup = BeautifulSoup(content, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "noscript", "svg"]):
        tag.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    lines = [ln.strip() for ln in soup.get_text("\n").splitlines()]
    return title + "\n" + "\n".join(ln for ln in lines if ln)


def fetch(url):
    r = requests.get(url, headers=UA, timeout=30)
    r.raise_for_status()
    return extract_text(r.content, r.headers.get("content-type", "").lower())


def main():
    schools = {s["domain"]: s for s in load_csv("schools.csv")}
    docs = json.loads(DOCS.read_text(encoding="utf-8")) if DOCS.exists() else []
    seen = {d["url"] for d in docs if d["status"] == "ok"}
    docs = [d for d in docs if d["url"] in seen]  # retry previous failures
    for row in load_csv("seed_urls.csv"):
        url, dom = row["url"], row["domain"]
        if url in seen:
            continue
        assert dom in schools and on_domain(url, dom) and row["category"] in CATEGORIES, row
        doc = {"school": schools[dom]["name"], "domain": dom, "category": row["category"],
               "url": url, "retrieved": datetime.now().astimezone().isoformat(timespec="seconds")}
        try:
            text = fetch(url)
            path = RAW / dom / f"{hashlib.sha1(url.encode()).hexdigest()[:12]}.txt"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            doc.update(status="ok", raw=path.relative_to(ROOT).as_posix(),
                       title=text.split("\n", 1)[0][:200], chars=len(text))
        except Exception as e:  # noqa: BLE001 - record the failure, keep going
            doc.update(status="error", error=str(e)[:200])
        docs.append(doc)
        print(f"{doc['status']:5} {dom:16} {url[:90]}")
        time.sleep(0.5)
    DOCS.write_text(json.dumps(docs, indent=1), encoding="utf-8")
    print(f"DONE: {sum(d['status'] == 'ok' for d in docs)}/{len(docs)} documents fetched")


if __name__ == "__main__":
    main()
