import json
import re
from collections import Counter
from pathlib import Path

import pytest

from pipeline import analyze, code

ROOT = Path(__file__).resolve().parent.parent
CODED = json.loads((ROOT / "data" / "coded.json").read_text(encoding="utf-8"))
DOCS = {d["url"]: d for d in json.loads((ROOT / "data" / "documents.json").read_text(encoding="utf-8"))}
_js = (ROOT / "site" / "data" / "findings.js").read_text(encoding="utf-8")
FINDINGS = json.loads(_js[_js.index("{"):_js.rindex("}") + 1])


@pytest.mark.phase(2)
@pytest.mark.parametrize("sentence,expected", [
    ("The use of generative AI tools such as ChatGPT is prohibited on all assignments.", 1),
    ("Generative AI is not permitted in this course.", 1),
    ("You may not use AI tools; doing so is considered academic dishonesty.", 1),
    ("You may use ChatGPT to explain concepts, but AI may not be used to write code.", 3),
    ("You may use AI tools such as Copilot on projects if you cite them.", 4),
    ("We encourage you to use generative AI and welcome experimentation with coding agents.", 5),
    ("Generative AI is changing the field of computing.", None),
])
def test_stance_rules(sentence, expected):
    """[AC-2.1] Stance rules map hand-written policy sentences to the right ordinal level."""
    assert code.stance(code.ai_sentences(sentence)) == expected


@pytest.mark.phase(2)
def test_not_permitted_is_not_a_permission():
    """[AC-2.1] 'not permitted' / 'not allowed' never count as permissions."""
    s = "AI tools are not permitted and are not allowed on exams."
    assert code.PERMIT.findall(code.PROHIBIT.sub(" ", s)) == []


@pytest.mark.phase(2)
def test_heading_pulls_next_sentence():
    """[AC-2.1] A short AI heading includes the following rule sentence."""
    sents = code.ai_sentences("Use of Generative AI\nStudents must write all code themselves.")
    assert any("write all code" in s for s in sents)


@pytest.mark.phase(2)
def test_sentiment_lexicon():
    """[AC-2.1] Sentiment is positive for opportunity language and negative for risk/cheating language."""
    pos, _, _ = code.sentiment(["Generative AI offers an exciting opportunity to enhance learning."])
    neg, _, _ = code.sentiment(["Using ChatGPT is cheating and carries a risk of plagiarism."])
    assert pos > 0 > neg


@pytest.mark.phase(2)
def test_collaboration_framing():
    """[AC-2.1] 'use AI as a collaborator' is collaboration; a 'collaboration policy' heading is not."""
    yes = code.code_document("You may use generative AI tools as you would use a human collaborator.")
    no = code.code_document("Collaboration policy: AI tools are allowed for debugging.")
    assert yes["collaboration"]["collaborator"] and not no["collaboration"]["collaborator"]


@pytest.mark.phase(2)
@pytest.mark.skipif(not (ROOT / "data" / "raw").exists(), reason="raw pages not present")
def test_evidence_quotes_are_verbatim():
    """[AC-2.2] Every evidence quote occurs in the source document's raw text (no fabricated quotes)."""
    norm = lambda s: re.sub(r"\s+", " ", s)
    checked = 0
    for d in CODED:
        raw = norm((ROOT / DOCS[d["url"]]["raw"]).read_text(encoding="utf-8"))
        for quotes in d["evidence"].values():
            for q in quotes:
                # quotes may join lines that the extractor split; compare word sequences
                words = q[:120].split()
                assert re.search(r"\s*".join(map(re.escape, words)), raw), (d["url"], q[:80])
                checked += 1
    assert checked > 50


@pytest.mark.phase(2)
def test_gold_set_accuracy():
    """[AC-2.3] Stance agrees with independently described policies on >= 80% of the gold set."""
    g = analyze.gold_accuracy(CODED)
    misses = [(r["url"], r["got"], r["expected"]) for r in g["rows"] if not r["match"]]
    assert g["n"] >= 15
    assert g["correct"] / g["n"] >= 0.80, misses


@pytest.mark.phase(2)
def test_aggregates_match_recount():
    """[AC-2.4] Dashboard aggregates equal counts recomputed directly from coded.json."""
    course = [d for d in CODED if d["category"] in ("course", "se_course")]
    assert FINDINGS["totals"]["documents"] == len(CODED)
    assert FINDINGS["course_stance_dist"] == dict(Counter(str(d["stance"]) for d in course))
    assert FINDINGS["collaboration"]["docs_any"] == sum(d["collaboration_any"] for d in CODED)
    assert FINDINGS["disclosure_docs"] == sum(d["disclosure_required"] for d in CODED)
    assert sum(s["n_docs"] for s in FINDINGS["schools"]) == len(CODED)


@pytest.mark.phase(2)
def test_cohen_kappa_known_values():
    """[AC-2.5] Kappa = 1 for perfect agreement, 0 for chance-level, matches a textbook example."""
    assert analyze.cohen_kappa(list("aabb"), list("aabb")) == 1.0
    assert analyze.cohen_kappa(list("abab"), list("aabb")) == 0.0
    # Textbook 2x2: 20 yes/yes, 5 yes/no, 10 no/yes, 15 no/no -> kappa 0.4
    a = ["y"] * 25 + ["n"] * 25
    b = ["y"] * 20 + ["n"] * 5 + ["y"] * 10 + ["n"] * 15
    assert analyze.cohen_kappa(a, b) == 0.4


@pytest.mark.phase(2)
def test_review_sample_size():
    """[AC-2.6] The human review sample covers >= 20% of documents and every category."""
    from tools.review_sample import sample
    s = sample(CODED)
    assert len(s) >= 0.2 * len(CODED)
    assert {d["category"] for d in s} == {d["category"] for d in CODED}
