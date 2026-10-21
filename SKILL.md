---
name: study-book
description: Turn a set of course PDFs (lecture slides, textbook chapters, papers, syllabus, past exams, scanned pages, notebook printouts) into a complete, structured study book compiled from LaTeX to PDF. Always starts with a planning phase (source inventory + all questions asked up front), then builds a course outline (backbone) for review, then writes chapters in parallel with per-chapter compile and source-page checks, and ends with a compiled, QA-checked PDF. Use when the user wants a study guide, study book, exam-prep book, revision book or course script made from PDFs/lecture slides, or says "study-book".
---

# Study book from course PDFs

Produces a LaTeX study book (like a hand-made exam book: boxes, lecturer questions with model
answers, source-page tags, figures, self-tests, overview map, cheat sheet) from the PDFs of a
course, and compiles it. The run is long; it is driven by `PLAN.md` so it can resume.

**Skill folder** `{skill}` = the directory of this file. **Book folder** = the current working
directory (the user opens the agent inside it). **Sources** default to `..`.
`{python}` = the interpreter chosen in preflight (venv in the book folder if needed).

## Non-negotiables

1. **Plan first.** No content is generated before the planning Q&A is confirmed (step 2).
2. **Two gates with the user:** planning summary (step 2) and backbone + chapter plan (step 4).
3. **Grounded:** content comes from the sources; anything else is in a "Beyond the sources" box.
   Every factual paragraph carries `\src{TAG}{page}`. Tags are citations — never call content
   "verified".
4. **A step is done only when its done-test passes**, never because a box was ticked.
5. **Retry caps:** chapter = 2 fix rounds (+1 fresh retry at the end); full build = 3 fix
   iterations; any script/tool failure = 2 attempts. Past the cap → **stop-and-report**: write the
   state and the failure to PLAN.md → Log, tell the user what failed, what was tried, and what they
   can do; do not continue silently and do not fake a result.
6. **Write `.tex`/`.json` files with the Write/Edit tools**, never with shell heredocs or sed (the
   shell collapses `\\`). Tell subagents the same.
7. **Protect the main context:** subagents read pages and write chapters; the main agent reads
   notes, reports and return blocks, not raw pages or full chapters.

## Resume

If `PLAN.md` exists in the book folder: read it, re-run the done-test of the last ticked step and
of every chapter with status PASS (`check_chapter.py --no-compile` is enough for unchanged files),
then continue at the first step whose done-test fails. Tell the user where you resume and why.

## Steps

| # | Step | Read | Output | Done-test |
|---|---|---|---|---|
| 0 | Preflight | `references/qa.md` §Preflight | `{python}`, MiKTeX auto-install, test compile | template preamble compiles |
| 1 | Inventory | `references/planning.md` §1 | `inventory.json`, `inventory.md` | every source listed |
| 2 | Planning Q&A | `references/planning.md` §2–3 | `PLAN.md` (settings, sources, lecturer Qs) | **user confirmed** |
| 3 | Stage 1 | `references/stage1-backbone.md` | `source/`, `notes/`, `backbone.md`, `glossary.md` | coverage audit lists every source |
| 4 | Chapter plan | below | PLAN.md chapter table, figures list, council verdict (if chosen) | **user approved** |
| 5 | Scaffold | `references/stage2-book-spec.md` §1, §7–8 | `main.tex`, `preamble.tex`, `00-howto`, `00-overview`, figures | `latexmk` builds the skeleton |
| 6 | Pilot chapter | `references/chapter-writer-brief.md` | 1 chapter + ledger | `check_chapter.py` PASS + pages look right |
| 7 | Chapters | `references/chapter-writer-brief.md` | all chapters + ledgers | every chapter PASS or FAILED-after-retry |
| 8 | Second read | `references/qa.md` §Second read | ledger `second_read`, `\unsure` | no item left in needs_second_read |
| 9 | Appendices | `references/stage2-book-spec.md` §9 | A–E per features | `check_chapter.py <file> --appendix` PASS |
| 10 | Full build | `references/qa.md` §Full build | `build/<PDF name>.pdf` | no errors, no undefined refs |
| 11 | QA + report | `references/qa.md` §QA | `coverage.md`, report, spot-check list | report delivered |
| 12 | Feedback report (if chosen) | `references/feedback.md` | `study-book-feedback_<date>.md` | file written, path told to user |

Tick each step in PLAN.md after its done-test passes; log decisions and failures there. Log every
problem or workaround as it happens as `[issue:<area>] step N — what happened — what was done`
(areas in `references/feedback.md`); the feedback report is built from these lines. If the
feedback report was chosen, a stop-and-report also writes it (`references/feedback.md` §When).

### Step 3 details
Run `{python} {skill}/scripts/extract_sources.py {source_dir} tags.json` (write `tags.json` =
`{file: TAG}` from PLAN.md first). Spawn the source-notes subagents in parallel (one message), then
merge into `backbone.md` + `glossary.md` yourself.

### Step 4 — chapter plan (main agent)
From the backbone, fill the PLAN.md chapter table:
- 8–16 chapters is typical; one chapter ≈ one coherent topic of the backbone, 8–15 pages; group
  into parts. Order = prerequisites first.
- Per chapter: `NN`, `key` (short, lowercase, unique — it prefixes all labels), title, part,
  **source pages** (every relevant source page belongs to ≥ 1 chapter — no orphan pages), backbone
  sections, dependencies (mark *inferred* ones), assigned lecturer questions, ≤ 3 figures.
- **Council review** (only if PLAN.md → Settings says `yes`): invoke the `council-review` skill
  once, before the gate, on the backbone outline, the chapter table, the orphan/out-of-scope pages
  and the settings (audience, depth, exam format, exam-weighted topics). Ask it about structure
  only: chapter order and prerequisites, chapter size, whether inferred dependencies are
  plausible, and whether exam-weighted topics get enough room — not about individual facts. Do not
  apply its suggestions yourself; log the verdict in PLAN.md → Log and present its concrete
  suggestions at the gate as options the user can accept or reject.
- Present: backbone outline (Course Map + section titles), glossary size, the chapter table,
  orphan/out-of-scope pages, and the council suggestions if any. Ask for approval or changes
  (AskUserQuestion). Apply changes, then tick step 4. Do not re-run the council after changes.

### Step 5 — scaffold
Copy from `{skill}/templates/`: `preamble.tex`, `main.tex`, `howto.tex` → `chapters/00-howto.tex`,
`overview.tex` → `chapters/00-overview.tex`, `latexmkrc` → `.latexmkrc`,
`vscode-settings.json` → `.vscode/settings.json`, `README.md`. Replace every `@@…@@`
placeholder (babel language name: `english`, `ngerman`, `spanish`, …). In `main.tex` `@@BODY@@`,
list `\part{…}` + `\input{chapters/NN-key}` for all chapters and `@@APPENDICES@@` for the
appendices that are ON. Until a chapter exists, keep its `\input` commented out. Draw the real
overview map. Crop figures (spec §7). Build with `latexmk`.

### Steps 6–7 — chapters
Pilot = the chapter with the fewest dependencies. Then spawn the rest in waves of ≤ 6 parallel
`general-purpose` subagents with the filled brief. Uncomment each chapter's `\input` in `main.tex`
when it passes.

### Step 11 — finish
Deliver the final report from `references/qa.md` §QA, ending with the human spot-check list and the
plain statement of what the checks do and do not guarantee. Then, if chosen, write the feedback
report (step 12).

## Scripts (`{skill}/scripts/`, run from the book folder)

| Script | Purpose |
|---|---|
| `inventory.py <src> [out]` | sources table, text vs image pages, coloured question candidates |
| `extract_sources.py <src> tags.json [dpi]` | `source/<TAG>/pNNN.txt` (+ `.png` for image-only pages), notebooks → `code.txt` |
| `extract_figures.py <src> [names]` | crops from `figures/manifest.json` |
| `check_chapter.py chapters/NN-key.tex [--no-compile] [--appendix]` | chapter done-test (compile, labels, refs, ledger) |
| `coverage.py [chapters] [source]` | uncited source pages → `coverage.md` |
| `render_preview.py <pdf> <out> <pages> [dpi]` | PNG previews for visual checks |
