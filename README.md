# GenAI in CS Education — Project 2

How do US computer-science departments permit, encourage, or restrict student use of generative AI?
How do they talk about AI in official publications, do they frame it as a collaborator, and how do
software-engineering courses handle it? Built agentically with Claude Code, with a spec-driven workflow.

**Live site:** https://aakiboi.github.io/genai-cs-education/ · **Repo:** https://github.com/Aakiboi/genai-cs-education

## Web interfaces (`site/`, served by GitHub Pages)
| Page | What it shows |
|---|---|
| [`index.html`](site/index.html) | **Findings dashboard**: RQ1–RQ5 charts, school table, evidence explorer with source quotes, method, limitations |
| [`validation.html`](site/validation.html) | **Validation explorer**: every logged test run, searchable and filterable, with test source code, acceptance-criteria→test map, gold-set check, ad-hoc checks |
| [`timeline.html`](site/timeline.html) | **Timeline & contributions**: human vs. Claude questions, decisions, milestones and commits, with timestamps |
| [`tokens.html`](site/tokens.html) | **Token usage**: exact per-request tokens from Claude Code transcripts, by session, activity, phase and practice (clear/compact) |

Open `site/index.html` directly in a browser, or publish it (below).

## Headline findings (30 schools, 94 documents)
- Course policies lean **permissive but conditional**. The most common course-level code is "Permitted", almost always with
  **disclosure/citation** requirements. Outright bans cluster in introductory and systems courses.
- **Tone differs by publisher.** Department pages and news are strongly positive about AI. Course syllabi are cautious
  (integrity, over-reliance), and teaching-center guidance is balanced (a menu of options, instructor discretion).
- **Collaboration framing is uncommon.** Only a minority of documents describe AI as a collaborator, peer or tutor;
  "assistant/tool" framing is more common.
- **Software engineering is where AI becomes the subject**, through new courses on AI-assisted SE, coding agents and
  spec-driven development, alongside traditional SE courses that still forbid it.

Exact numbers are generated into the dashboard. Read the limitations there before citing them.

## Reproduce
```bash
pip install -r requirements.txt
python project2.py all      # collect -> code -> review sample -> analyze -> token + site data
python -m pytest            # every result is appended to logs/validation.jsonl
```
`python project2.py build` refreshes only the validation/timeline/token data.

## Repository map
```
CLAUDE.md, STATE.md     agent rules + current state (survive /clear)
specs/                  00 overview, 01 collection, 02 codebook/analysis, 03-06 interfaces/publish (acceptance criteria)
data/                   schools.csv, seed_urls.csv, documents.json, raw/ (page text), coded.json, gold_stance.csv, review_sample.csv
pipeline/               collect.py, code.py (codebook), analyze.py
tools/                  token_usage.py, build_site.py, review_sample.py
tests/                  pytest suites + conftest hook that logs every result
logs/                   timeline.jsonl, sessions.jsonl, validation.jsonl, adhoc_checks.jsonl
site/                   the four web interfaces + generated data/*.js
docs/evaluation.md      human evaluation + reflection (template)
```

## Publish to GitHub + the web
```bash
# 1. create an empty repo on github.com (e.g. genai-cs-education), then:
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
# 2. GitHub → Settings → Pages → Source: "GitHub Actions" (the included workflow deploys site/)
#    The site will be at https://<you>.github.io/<repo>/
```

## Spec-driven workflow
Say **"Prepare to clear"** → Claude updates `STATE.md`, appends to the logs, runs the tests, commits, and replies
"Ready to clear" → `/clear`. A new session reads `CLAUDE.md` → `STATE.md` → the current spec.
