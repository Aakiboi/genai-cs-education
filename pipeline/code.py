"""Phase 2: apply the codebook (specs/02-coding-analysis.md) to every fetched document.

The coding is deterministic and rule-based, so anyone can audit and re-run it. Only sentences that
mention AI are coded. Every code keeps up to 2 verbatim evidence sentences from the raw text.
Output: data/coded.json
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

AI = re.compile(r"generative\s+ai|gen-?ai|chatgpt|copilot|\bllms?\b|large language models?|"
                r"ai[- ](?:tools?|assist\w*|generated|models?|systems?|agents?|use|usage|policy|coding)|"
                r"artificial intelligence|\bclaude\b|\bgemini\b|\bcursor\b|coding agents?|\bAI\b", re.I)
PROHIBIT = re.compile(r"not\s+(?:be\s+)?(?:permitted|allowed)|prohibit\w*|forbid\w*|forbidden|"
                      r"(?:may|must|should|can)\s*not\s+(?:be\s+used|use)|cannot\s+use|not\s+to\s+use|\bbann?ed\b|"
                      r"considered\s+(?:cheating|plagiarism|academic\s+(?:dishonesty|misconduct))|"
                      r"academic\s+(?:dishonesty|misconduct)|integrity\s+violation|violation\s+of\s+(?:the\s+)?academic|"
                      r"no\s+(?:generative\s+)?ai\s+use|not\s+allowed|\bdo\s+not\s+(?:use|copy|submit|have)", re.I)
ENCOURAGE = re.compile(r"encourag\w*|welcome\w*|embrac\w*|expected\s+to\s+use|required\s+to\s+use|"
                       r"(?:are|is)\s+free\s+to\s+use|for\s+any\s+work|leverag\w*|integrat\w*\s+(?:ai|generative)", re.I)
PERMIT = re.compile(r"\bmay\s+(?:\w+\s+)?use|\bcan\s+(?:\w+\s+)?use|may\s+be\s+(?:used|treated)|\ballowed\b|\bpermitted\b|\bpermissi\w*|is\s+fine|"
                    r"no\s+restrictions", re.I)
DISCLOSE = re.compile(r"\bcite\b|citation|acknowledg\w*|disclos\w*|attribut\w*|"
                      r"document\s+(?:your|their|how|the\s+use)|assist\s+statement|usage\s+statement|"
                      r"transparen\w*|describe\s+how", re.I)
POS = re.compile(r"opportunit\w*|benefi\w*|enhanc\w*|empower\w*|innovat\w*|powerful|valuable|useful|"
                 r"helpful|potential|transform\w*|excit\w*|creativ\w*|productiv\w*|effective\w*|"
                 r"fluency|literacy|explor\w*|support\w*\s+(?:learning|students)|accelerat\w*", re.I)
NEG = re.compile(r"\brisks?\b|concern\w*|misuse|cheat\w*|plagiar\w*|\bharm\w*|\bbias\w*|hallucinat\w*|"
                 r"inaccura\w*|threat\w*|dishonest\w*|violat\w*|misconduct|danger\w*|over-?relian\w*|"
                 r"fabricat\w*|privacy|copyright|undermin\w*|shortcut|penalt\w*|sanction\w*|errors?\b", re.I)
COLLAB = {
    "collaborator": re.compile(r"\b(?:collaborator|teammate)s?\b|(?:as|like)\s+(?:a|an|your|any)\s+(?:\w+\s+)?(?:partner|peer)s?\b|"
                               r"collaborat\w*\s+with\s+(?:an?\s+)?(?:ai|generative|llms?|chatgpt|the\s+ai|these\s+tools)|"
                               r"pair[- ]?program\w*|co-pilot|thinking\s+partner|human[- ]ai\s+collaborat\w*|"
                               r"work(?:ing)?\s+(?:alongside|together\s+with)", re.I),
    "tutor": re.compile(r"\btutor\w*|rubber[- ]?duck|study\s+aid|learning\s+aid|explain\w*\s+(?:concepts|errors?)", re.I),
    "assistant": re.compile(r"\bassistant\b|consult\w*|helper", re.I),
}
SE_SUBJECT = re.compile(r"ai[- ](?:assisted|enhanced|augmented|driven|enabled)\s+(?:software|development|engineering|design)|"
                        r"coding\s+agents?|agentic|code\s+generation|generate\s+code|prompt\s+engineering|"
                        r"spec-driven|software\s+development\s+(?:with|using)\s+(?:ai|generative)|"
                        r"(?:with|using)\s+(?:ai|llms?|generative\s+ai)\s+(?:tools\s+)?to\s+(?:write|build|develop)", re.I)

STANCE_LABELS = {1: "Prohibited", 2: "Restricted", 3: "Conditional / mixed", 4: "Permitted", 5: "Encouraged"}


def sentences(text):
    """Split into sentences. HTML extraction breaks lines at inline tags, so a line that doesn't end
    in punctuation is joined to the next one first. Whitespace is normalized."""
    merged, buf = [], ""
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        buf = f"{buf} {line}" if buf else line
        if re.search(r"[.!?:;]$", line) or len(buf) > 600:
            merged.append(buf)
            buf = ""
    if buf:
        merged.append(buf)
    out = []
    for para in merged:
        for s in re.split(r"(?<=[.!?])\s+", para):
            s = re.sub(r"\s+", " ", s).strip()
            if len(s) >= 15:
                out.append(s)
    return out


def ai_sentences(text):
    """Sentences that mention AI. A short AI sentence (a heading such as 'Use of Generative AI')
    also pulls in the sentence after it, which usually carries the actual rule."""
    sents, out = sentences(text), []
    for i, s in enumerate(sents):
        if AI.search(s):
            out.append(s)
            if len(s) < 60 and i + 1 < len(sents) and not AI.search(sents[i + 1]):
                out.append(sents[i + 1])
    return out


def stance(sents):
    """Ordinal stance 1..5 from AI sentences, or None if no policy language is present."""
    p = e = a = 0
    for s in sents:
        p += len(PROHIBIT.findall(s))
        rest = PROHIBIT.sub(" ", s)          # "not permitted" must not count as "permitted"
        e += len(ENCOURAGE.findall(rest))
        a += len(PERMIT.findall(rest))
    if p == e == a == 0:
        return None
    if e >= 2 and e > p:
        return 5
    if p and not (a or e):
        return 1
    if a + e > p:
        return 4
    if a + e > 0:
        return 3
    return 2


def sentiment(sents):
    pos = sum(len(POS.findall(s)) for s in sents)
    neg = sum(len(NEG.findall(s)) for s in sents)
    if pos + neg == 0:
        return None, pos, neg
    return round((pos - neg) / (pos + neg), 3), pos, neg


def evidence(sents, rx, k=2):
    return [s[:300] for s in sents if rx.search(s)][:k]


def code_document(text):
    sents = ai_sentences(text)
    st = stance(sents)
    score, pos, neg = sentiment(sents)
    collab = {name: bool(evidence(sents, rx, 1)) for name, rx in COLLAB.items()}
    stance_rx = re.compile(f"{PROHIBIT.pattern}|{ENCOURAGE.pattern}|{PERMIT.pattern}", re.I)
    return {
        "ai_sentences": len(sents),
        "stance": st,
        "stance_label": STANCE_LABELS.get(st, "No policy language"),
        "sentiment": score, "pos_terms": pos, "neg_terms": neg,
        "disclosure_required": bool(evidence(sents, DISCLOSE, 1)),
        "collaboration": collab,
        "collaboration_any": collab["collaborator"] or collab["tutor"],  # assistant = tool framing
        "se_ai_subject": bool(evidence(sents, SE_SUBJECT, 1)),
        "evidence": {
            "stance": evidence(sents, stance_rx),
            "sentiment_pos": evidence(sents, POS),
            "sentiment_neg": evidence(sents, NEG),
            "disclosure": evidence(sents, DISCLOSE),
            "collaboration": [s for name, rx in COLLAB.items() for s in evidence(sents, rx, 1)][:2],
            "se_ai_subject": evidence(sents, SE_SUBJECT),
        },
    }


def main():
    docs = json.loads((ROOT / "data" / "documents.json").read_text(encoding="utf-8"))
    coded = []
    for d in docs:
        if d["status"] != "ok":
            continue
        text = (ROOT / d["raw"]).read_text(encoding="utf-8")
        coded.append({**{k: d[k] for k in ("school", "domain", "category", "url", "retrieved", "title")},
                      **code_document(text)})
    (ROOT / "data" / "coded.json").write_text(json.dumps(coded, indent=1), encoding="utf-8")
    print(f"coded {len(coded)} documents")


if __name__ == "__main__":
    main()
