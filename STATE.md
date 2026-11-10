# STATE — read me after /clear

**Current phase:** 6 — publication (all Claude-side work done)
**Last updated:** 2026-11-10 (see logs/timeline.jsonl for exact times)

## Done
- Phase 0: CLAUDE.md, specs, logging, pytest hook (logs every result to logs/validation.jsonl).
- Phase 1: 30 schools (data/schools.csv), 109 seed URLs from 30 WebSearch queries, 94 docs fetched (15 failed, mostly 403).
- Phase 2: rule-based codebook (pipeline/code.py), gold set 13/15, 25% review sample generated (data/review_sample.csv).
- Phases 3–5: site/index.html, validation.html, timeline.html, tokens.html; tools/token_usage.py parses transcripts.
- Phase 6: README, GitHub Pages workflow (.github/workflows/pages.yml), docs/evaluation.md template. 178 tests pass.

## Next (human)
1. DONE: published at https://github.com/Aakiboi/genai-cs-education, live at https://aakiboi.github.io/genai-cs-education/ (each push to main redeploys).
2. Fill `human_stance` in data/review_sample.csv, then run `python project2.py analyze` to get κ on the dashboard.
3. Write docs/evaluation.md (evaluation + reflection).
4. After any new session: log it in logs/sessions.jsonl (practice: clear/compact), then run `python project2.py build` and commit.

## Gotchas
- pytest 9.2.0 crashes on this machine; it's pinned to 8.3.5.
- Search engines block scripted queries; don't scrape them. Use the WebSearch tool, then `collect` fetches.
- When patching regexes from Python, use raw strings (a `\b` once became a backspace character).
- Transcripts: C:\Users\lithi\.claude\projects\d--SpecialTopics-Project2\*.jsonl (set CLAUDE_TRANSCRIPTS to override).
- The site loads data via `<script src="data/*.js">`, so it also works from file://.
