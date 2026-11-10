# Spec 01 — Data collection

## Sample
30 US institutions in `data/schools.csv`, stratified: 22 R1 (10 private, 12 public) and 8 non-R1
(teaching-focused, liberal-arts, regional publics), across West / Midwest / Northeast / South.

## Method
1. **Find sources.** One Claude Code `WebSearch` per school, restricted to the school's domain, with the query
   `computer science generative AI policy course software engineering`. Claude picks relevant results
   (teaching-center guidance, CS department pages/news, course syllabi, software-engineering courses) and skips
   professional-education marketing. Results go in `data/seed_urls.csv` with a category:
   `policy` (institution/teaching-center guidance), `department` (CS department publications, news, catalogs),
   `course` (a CS course policy/syllabus), `se_course` (a software-engineering course or SE-with-AI course).
2. **Fetch.** `python project2.py collect` downloads each URL, extracts text (HTML or PDF) to `data/raw/`, and
   records metadata in `data/documents.json`.
   - Scripted search-engine scraping was tried first and dropped: engines return bot challenges, and the
     project does not circumvent them. Sites that answer 403 are recorded as failures, not retried with tricks.

## Acceptance criteria
- **AC-1.1** Every school in `schools.csv` has at least one successfully fetched document.
- **AC-1.2** Every document record has school, category, URL, ISO retrieval timestamp, and status; every `ok` record points to an existing, non-empty raw text file.
- **AC-1.3** Every seed URL is on its school's own domain and has a valid category.
- **AC-1.4** HTML and PDF text extraction work, and scripts/styles are stripped (unit test on fixtures).
- **AC-1.5** Fetch failures are recorded with an error message, not silently dropped.

## Known limitations
Search ranking decides what's found, so this is a purposive sample, not a census. JavaScript-only pages
yield little text. Some sites block automated clients (403).
