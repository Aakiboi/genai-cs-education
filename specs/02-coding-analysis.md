# Spec 02 — Codebook and analysis approach

## Approach
**Directed qualitative content analysis, automated with a transparent rule-based codebook**, validated three ways:
(1) unit tests on hand-written sentences, (2) a gold set of 15 course pages whose stance was independently
described by the WebSearch summaries (`data/gold_stance.csv`), (3) a human-coded random sample
(`data/review_sample.csv`), with Cohen's κ reported on the dashboard once the human fills it in.

Rule-based coding was chosen over having Claude read every document: it costs almost no tokens, is
deterministic, and every code can be audited against the exact sentence that triggered it.

## Unit of analysis
Sentences that mention AI (generative AI, ChatGPT, Copilot, LLM, Claude, Gemini, Cursor, "AI tools", …).
A short AI heading also includes the sentence that follows it.

## Codes (per document) — implemented in `pipeline/code.py`
| Code | Values | Rule summary |
|---|---|---|
| stance (RQ1) | 1 Prohibited · 2 Restricted · 3 Conditional/mixed · 4 Permitted · 5 Encouraged · none | counts of prohibit / permit / encourage phrases (prohibitions removed before counting permits) |
| sentiment (RQ2) | −1…+1 | (positive − negative)/(positive + negative) over a lexicon (opportunity, enhance… vs. risk, cheating…) |
| disclosure | yes/no | cite / acknowledge / disclose / attribution / usage statement |
| collaboration (RQ3) | collaborator, tutor (count as collaboration); assistant (tool framing, reported separately) | "as a collaborator/partner/peer", "collaborate with AI", pair programming; tutor / rubber duck / study aid |
| SE AI-as-subject (RQ4) | yes/no | AI-assisted software engineering, coding agents, code generation, prompt engineering, spec-driven |

School level: course stance = median of course + SE-course documents; department tone = mean sentiment of
department + policy documents. Group comparisons by tier, control and region (RQ5).

## Acceptance criteria
- **AC-2.1** Stance rules classify hand-written prohibit / restrict / conditional / permit / encourage sentences correctly, and "not permitted" is never counted as a permission.
- **AC-2.2** Every evidence quote appears verbatim (after whitespace normalization) in the document's raw text — no fabricated quotes.
- **AC-2.3** Gold-set accuracy is ≥ 80% (stance within the acceptable set).
- **AC-2.4** Aggregates in `findings.js` match counts recomputed directly from `coded.json`.
- **AC-2.5** Cohen's κ implementation matches known values.
- **AC-2.6** A stratified review sample of ≥ 20% of documents is generated for human coding.
