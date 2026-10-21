# Chapter-writer subagent brief

The main agent fills the `{…}` fields from PLAN.md and spawns one `general-purpose` subagent per
chapter with this prompt. All chapters of a wave are spawned in **one message** (parallel).
Waves of ≤ 6 subagents keep the machine and the rate limits sane.

```
You write ONE chapter of a LaTeX study book on {subject}, in {language}.
Work in the book folder: {book_dir}. Python: {python}. Skill folder: {skill}.

YOUR CHAPTER
  file:    chapters/{NN}-{key}.tex          label prefix: {key}:
  title:   {title}
  ledger:  ledger/{NN}-{key}.json
  backbone section(s): {backbone_sections}   (in backbone.md — read only these)
  source pages: {source_pages}               (files source/<TAG>/pNNN.txt; image-only pages as .png:
                {image_pages} — read those with the Read tool, which displays images)
  figures available: {figures}               (names in figures/manifest.json; \includegraphics{name})
  lecturer questions to answer here: {lecturer_questions}   (label, question, TAG, page)
  depends on chapters: {deps}                (you may \cref{<depkey>:ch}; do not explain their content again)
  target length: {pages} pages; audience: {audience}; features OFF: {features_off}

READ FIRST
  1. {skill}/references/stage2-book-spec.md  §2–§6 and §10 (anatomy, boxes, tags, style, LaTeX rules, exemplar)
  2. glossary.md  — use its terms, symbols and units exactly
  3. your backbone section(s), then every one of your source pages

WRITE (with the Write tool only — never shell heredocs/echo/sed; they break backslashes)
  A. chapters/{NN}-{key}.tex following the chapter anatomy. Cover every point of your backbone
     section(s) and every source page listed; put a \src{TAG}{page} on every factual paragraph or
     bullet group. Content not in the sources goes in a beyondslides box or is left out.
  B. ledger/{NN}-{key}.json — a JSON list, one entry per number, threshold, formula constant, date,
     named value and key definition in your chapter:
       {"claim": "<short paraphrase>", "tokens": ["<string copied verbatim from the page .txt>", ...],
        "tag": "<TAG>", "page": <int>, "img": <true if read from an image, else false>}
     Tokens must be exact substrings of source/<TAG>/pNNN.txt (whitespace/dash/decimal-comma
     differences are tolerated). For values you read from a page image, set "img": true and copy
     the value as you read it.

CHECK (this is your done-test)
  {python} {skill}/scripts/check_chapter.py chapters/{NN}-{key}.tex
  - FAIL → fix and re-run. At most 2 fix rounds. Typical fixes: LaTeX error at the reported line;
    label without "{key}:" prefix; \src to a wrong page; ledger token not on the cited page (the
    report says on which page it was found — fix the tag/page, or fix the claim if the chapter
    was wrong). Never "fix" a ledger failure by deleting the entry while keeping the claim.
  - needs_second_read / warn_uncovered_numbers are not failures; add ledger entries for uncovered
    exam-critical numbers if you can find them on a page.
  Do not compile main.tex. Do not edit any file except your chapter and your ledger.

RETURN (≤ 8 lines, nothing else)
  RESULT: PASS | FAILED
  pages written ≈ N; ledger entries N; img entries N
  uncovered backbone points or source pages (if any): …
  missing macros/packages you needed (if any): …
  open issues: …
```

## Main-agent rules around the brief

- Read only the RETURN blocks and `build/check/<stem>/report.json`, not the chapters — protect the
  main context. Spot-read a chapter only when a report is unclear.
- `PASS` → status `PASS` in PLAN.md. `FAILED` after 2 rounds → status `FAILED (reason)`; continue
  with the other chapters; FAILED chapters are retried **once** at the end with a fresh subagent
  that gets the old report. Still failing → stop-and-report (SKILL.md).
- Missing macro/package requests → add to `preamble.tex` course-macro block once, then re-run
  `check_chapter.py` for the affected chapters.
- Pilot (step 6): the same brief for one chapter; afterwards look at its PDF pages
  (`render_preview.py build/check/<stem>/stub.pdf prev 1-6 70`) and fix template/spec problems
  before the wave starts.
