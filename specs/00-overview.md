# Spec 00 — Project Overview

## Goal
Find out how US computer-science departments permit, encourage, or restrict student use of
generative AI, how they talk about AI in official publications, and how software-engineering
courses handle it — then communicate the findings in a dashboard. Built agentically with Claude
Code; the process itself (validation, contributions, token usage) is documented in web interfaces.

## Research questions
- **RQ1** What do CS courses permit students to do with genAI? (prohibited → encouraged)
- **RQ2** How do departments talk about AI in official publications? Positive, neutral, cautious, negative?
- **RQ3** Do they frame AI as a *collaborator* (pair programmer, tutor) or only as a *tool/threat*?
- **RQ4** How do software-engineering courses specifically handle AI?
- **RQ5** Do patterns differ by institution type (R1 vs. other, public vs. private, region)?

## Analysis approach (summary — detail in Spec 02)
Qualitative content analysis with a fixed **codebook**. For each institution, collect public
documents (department AI statement, university policy, CS/SE syllabi). Each document is coded on:
policy stance (5-level ordinal), sentiment (−2..+2), collaboration framing (yes/no + type),
required disclosure/attribution, permitted uses, SE-course practice. Claude proposes codes with a
supporting quote; the human independently codes a random ~20% sample and we report agreement
(Cohen's κ). Results are aggregated into descriptive stats and cross-tabs for the dashboard.

## Deliverables → where they live
| # | Deliverable | Location |
|---|---|---|
| 1 | Findings dashboard | `site/index.html` |
| 2 | Validation explorer (search/filter tests, evidence) | `site/validation.html` |
| 3 | Contribution timeline (human vs. Claude, Q&A, timestamps) | `site/timeline.html` |
| 4 | Token usage explorer (by phase, activity, clear/compact) | `site/tokens.html` |
| — | Evaluation & reflection (written by the human) | `docs/evaluation.md` |
| — | Publication | GitHub repo + GitHub Pages serving `site/` |

## Architecture
```
data/sources.csv ──► collect.py ──► data/raw/ (html/pdf, untracked)
                                       │
                         extract + code (Claude-assisted, human-verified)
                                       ▼
                     data/coded.json ──► analyze.py ──► site/data/findings.json ──► index.html
tests/ + conftest hook ─────────────────────────────► logs/validation.jsonl ─┐
logs/timeline.jsonl ──────────────────────────────────────────────────────────┤ build_site.py
~/.claude/projects/.../*.jsonl + logs/sessions.jsonl ─► token_usage.py ───────┘ ──► site/data/*.json
```
`project2.py` is the CLI entry point: `python project2.py {collect|analyze|build|all}`.

## Phases
| Phase | Spec | Output | Main activity |
|---|---|---|---|
| 0 | this file | scaffolding, logging, test hook | planning |
| 1 | `01-data-collection.md` | institution list + source documents | data-gathering |
| 2 | `02-coding-analysis.md` | codebook, coded dataset, κ | data-processing |
| 3 | `03-dashboard.md` | findings dashboard | coding |
| 4 | `04-validation-ui.md` | validation explorer | coding/validation |
| 5 | `05-timeline-tokens.md` | timeline + token UIs | coding |
| 6 | `06-publish.md` | GitHub repo + Pages | docs |

Each phase spec is written and approved by the human *before* that phase starts.

## Constraints
- Claude Code Pro plan: web fetching is token-heavy. Batch fetches, store raw pages, don't re-fetch.
- Public sources only. Cite every claim. No fabricated quotes or policies.
- Static site, no backend, no build step.
