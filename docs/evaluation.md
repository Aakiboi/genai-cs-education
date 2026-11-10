# Evaluation & Reflection (to be completed by the human)

> Claude prepared this template and the data pointers. The judgments below are yours to write.

## 1. Independent check of the coding (do this first, ~30 min)
1. Open `data/review_sample.csv` (24 stratified documents).
2. For each URL, read the page and enter `human_stance` (1 Prohibited, 2 Restricted, 3 Conditional/mixed,
   4 Permitted, 5 Encouraged, or `None`). **Don't look at Claude's code for that document first.**
3. Run `python project2.py analyze`. Cohen's κ and % agreement then appear on the dashboard (Method section).
   Rough guide: κ > 0.6 is substantial agreement, 0.4–0.6 moderate, < 0.4 weak.

## 2. Did the project meet its goals?
| Goal (from the brief) | Where to look | Met? / Evidence / Gaps |
|---|---|---|
| How students may use genAI in CS courses | Dashboard RQ1, evidence explorer | |
| How departments talk about AI; positive? | Dashboard RQ2 | |
| Collaboration with AI discussed? | Dashboard RQ3 | |
| Software-engineering courses | Dashboard RQ4 | |
| An approach to analyze the data | `specs/02-coding-analysis.md` | |
| Dashboard communicates findings | `site/index.html` | |
| Spec-driven agentic development | `CLAUDE.md`, `specs/`, `STATE.md` | |
| Validation evidence a skeptic accepts | `site/validation.html` | |
| Contributions documented with timestamps | `site/timeline.html`, `logs/timeline.jsonl` | |
| Token usage + effect of clear/compact | `site/tokens.html` | |
| Published on GitHub and the web | repo URL + Pages URL | |

Questions worth answering:
- Is a 30-school purposive sample enough? Which kinds of schools are missing (community colleges, HBCUs, …)?
- Where did the rule-based coder disagree with you? Are the errors systematic (e.g., teaching-center templates coded as "mixed")?
- Would asking Claude to read and code each document have been more accurate, and worth the extra tokens?

## 3. Token-usage observations
Use `site/tokens.html`. Note how context per request grew within the first long session, and what changed after
`/clear` or `/compact`. Which activity used the most tokens (web searches for data gathering vs. coding)?

## 4. Reflection: agentic vs. AI-assisted development
Prompts to consider:
- How much code did you read directly? Where did you rely on tests or specs instead?
- When did you have to step in? (See `kind: decision/correction/review` in the timeline.)
- What did the agent get wrong without noticing, and what caught it? (Tests caught two coder bugs; a safety guardrail
  stopped a scraping approach.)
- Did the specs really let you `/clear` and resume without losing work?
- Compared with AI-assisted coding (you write, the AI suggests), what did you gain in speed, and what did you lose
  in understanding or control?

*Your reflection here.*
