# CLAUDE.md — Project 2: GenAI Policy in CS Education

Agentic, spec-driven project. The human supervises; Claude writes the code. Read this file, then
`STATE.md`, then the spec for the current phase before doing anything.

## Source of truth
- `specs/00-overview.md` — goals, deliverables, architecture, phase list. Change only with human approval.
- `specs/NN-*.md` — one spec per phase, with acceptance criteria. Work is "done" only when every
  criterion has a passing test or a recorded human check.
- `STATE.md` — current phase, what's done, what's next, open questions. **Always kept current.**

## Logging rules (required for deliverables #3 and #4)
Every working session, append to these files (JSON Lines, one object per line, ISO-8601 timestamps
with offset, e.g. `2026-11-10T12:45:37-05:00` — get it from `date -Iseconds`, never guess):

- `logs/timeline.jsonl` — `{ts, actor: "human"|"claude", kind, phase, summary, detail?}`
  - `kind` ∈ `question` (human prompt, paraphrased faithfully), `response` (Claude's answer, summarized),
    `decision`, `milestone`, `review` (human reviewed code/output), `correction` (human corrected Claude).
  - Log every human request and Claude's response. Attribute work honestly: who decided, who wrote it.
- `logs/sessions.jsonl` — `{ts, session_id, phase, practice: "fresh"|"clear"|"compact"|"continue", activity, notes}`
  - `activity` ∈ `planning`, `data-gathering`, `data-processing`, `coding`, `validation`, `docs`.
  - Session id = the transcript filename in `~/.claude/projects/d--SpecialTopics-Project2/`.
    Exact token counts are parsed from those transcripts by `tools/token_usage.py` (Phase 5);
    this file supplies the labels that the transcripts lack.
- `logs/validation.jsonl` — written automatically by the pytest hook in `tests/conftest.py`;
  ad-hoc checks Claude runs outside pytest are appended by hand as `{ts, phase, check, command, result, evidence}`.

## "Prepare to clear" protocol
When the human says **"Prepare to clear"** (or "prepare to compact"):
1. Update `STATE.md` (done / in progress / next step / open questions / gotchas learned).
2. Append timeline + sessions entries for this session, including the upcoming `clear`/`compact`.
3. Make sure tests pass or failures are recorded in `STATE.md`.
4. Commit with a descriptive message.
5. Reply with a ≤5-line summary and "Ready to clear."

## Conventions
- Python 3.10, standard library + `requests`, `beautifulsoup4`, `pytest` (see `requirements.txt`).
- Web UIs are static HTML/JS in `site/` (no build step) so they publish on GitHub Pages.
  Each reads JSON from `site/data/` that a Python script generates — never hand-edit generated data.
- Raw downloaded pages go in `data/raw/` (untracked). Every coded data point must cite its source URL
  and retrieval date. Never invent a policy or quote; mark unknowns as `null` / "not found".
- Run tests with `python -m pytest`. Don't claim something works without running it.
