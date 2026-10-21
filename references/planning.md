# Planning phase — inventory, questions, PLAN.md

Goal: every decision the run needs is made **before** any content is generated, and recorded in
`PLAN.md`. Ask everything here; later steps should not need to stop for questions except at the
stage-1 checkpoint.

## 1. Inventory (before asking anything)

```
{python} {skill}/scripts/inventory.py {source_dir} .
```
Default `{source_dir}` is `..` (the agent is opened in the book subfolder). If `..` contains no
PDFs, ask for the path first. Show the user `inventory.md` (the table plus coloured-question
candidates and pages without a text layer), condensed if long.

From the inventory, prepare defaults:
- **TAG** per source: short, unique, readable (`B1`, `L4`, `Intro`, `Ex2023`); ≤ 8 chars, letters/digits.
- **Role** per source: the inventory's guess (`slides`, `text`, `syllabus`, `exam`, `notebook`, `scanned`).
- **Language**: majority source language.
- **Lecturer-question candidates**: coloured lines with "?" — usually real exam hints, but can be
  headings or decoration. The user confirms.

## 2. Question rounds (AskUserQuestion, ≤ 4 questions per call, multiple choice with defaults)

Put the recommended default first and mark it "(Recommended)". Skip a question when the inventory
already answers it unambiguously, but list the assumption in the confirmation summary.

**Round 1 — course and exam**
1. Subject / course name and lecturers (offer what the inventory titles suggest).
2. Exam: date, time, format (written/oral/multiple choice/open questions), room — "unknown" is fine.
3. Any hints the lecturers gave about the exam (free text via "Other"; default "none").
4. Output language (default: source language; options: English, German, Spanish, source language).

**Round 2 — sources**
1. Confirm source roles + TAGs (show the proposed table in the question; "Other" to correct).
2. Are the coloured question candidates real lecturer/exam questions? (all / a subset — say which /
   none / there are other markers, e.g. a different colour or an icon).
3. Notebooks / code (only if any): worked-code section in the relevant chapter (Recommended) /
   separate appendix / ignore.
4. Scanned pages (only if any): read visually with a second independent read for numbers
   (Recommended) / skip those pages.

**Round 3 — the book**
1. Features to switch OFF (multiSelect; all ON by default): exam-critical/pitfall/key-idea boxes;
   objectives + take-home + self-test; lecturer-question boxes + appendix; figure crops;
   beyond-the-sources boxes + appendix; cheat sheet; corrections appendix; overview map.
2. Depth: standard (8–15 pages per chapter, Recommended) / compact (4–8) / exhaustive (15–25).
3. Audience: the course's own level (Recommended) / assume less background (more "beyond" boxes) / revision only.
4. Book title and PDF file name (default: "<Subject> Study Book", "<Subject> Study Guide.pdf").

**Round 4 — run**
1. Reuse an existing outline in the source folder (e.g. a `.md` backbone) instead of
   regenerating? (only if one exists)
2. Council review of the chapter plan (always ask): "Do you have the `council-review` skill
   installed, and should it review the backbone and chapter plan before you approve them? It runs
   several advisors and uses many tokens." Options: no / not installed (Recommended) / yes, review
   the chapter plan. Before asking, check whether `council-review` is among your available skills
   and say so in the question. If the user says yes but the skill is not available, tell them, set
   the setting to `no` and continue.
3. Feedback report (always ask): "At the end, should I write a feedback report for the skill's
   author? It lists the problems met during the run (reading the sources, structure, build) and
   your own comments if you want to add any. It contains no course content, and nothing is sent:
   you decide whether to send the file." Options: yes (Recommended) / no. See
   `references/feedback.md`.

## 3. Confirmation gate

Write `PLAN.md` from `{skill}/templates/PLAN.md`: Settings table, Sources table, confirmed lecturer
questions. Show the user a compact summary (≤ 20 lines) including every assumption you made
without asking. Proceed only on explicit confirmation. Tick steps 1–2 in PLAN.md.
