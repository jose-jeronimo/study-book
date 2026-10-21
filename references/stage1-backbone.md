# Stage 1 — Source notes, backbone, glossary

Stage 1 turns the sources into three files: `notes/<TAG>.md` (one per source), `backbone.md`
(the unified course outline) and `glossary.md` (shared terminology). It is a generalisation of the
prompt that produced the reference book's backbone. `{subject}`, `{n}` etc. come from PLAN.md.

---

## A. Source-notes subagent brief

Spawn one subagent per source (split sources > 60 pages into page ranges). Fill the brackets.

```
You are extracting study notes from ONE source of a university course on {subject}.
Source: {file} (TAG {TAG}, role {role}), pages {from}-{to}.
Per-page text: source/{TAG}/pNNN.txt. Pages without a text layer: source/{TAG}/pNNN.png
(read them with the Read tool, which shows images) — image pages: {image_pages}.
Also look at page images for slides whose text file is short or where figures carry content:
render with `{python} {skill}/scripts/render_preview.py ../{file} tmp_prev {pages} 80`.

Write notes/{TAG}.md (use the Write tool, never a shell heredoc) with, in page order:
- every topic, subtopic, definition, method (purpose/principle/workflow/strengths/limitations
  as far as the source gives them), comparison, workflow shown in a figure, equation (with
  variable meanings), number/threshold/parameter, example used by the lecturer;
- each item tagged with its page: "(p12)"; items read from an image tagged "(p12, img)";
- highlighted / coloured questions verbatim, marked "LQ:" with page;
- anything unclear marked [UNCLEAR IN SOURCE].
Copy numbers exactly as printed. Do not add knowledge that is not on the pages.
Role rules: syllabus -> list announced topics and learning outcomes; exam -> list each question
verbatim with page and the topic it tests; notebook -> list each task, the code steps and what
they compute; text (book/paper) -> only the parts relevant to the course topics.
Return: one line "DONE notes/{TAG}.md, N items, M LQ, K img items".
```

---

## B. Backbone (main agent merges the notes)

Read all `notes/*.md` (not the raw pages). Produce **one** `backbone.md`:

### Objective
Treat the sources as parts of **one coherent course**. Do not summarise per source. Identify all
concepts, methods, principles, workflows, applications and details and reorganise them into a
logical learning structure: a complete table of contents + conceptual map + detailed outline for
a study book on {subject} based specifically on this course.

### 1. Coverage first
The sources are authoritative. Do not omit a topic because it seems minor, obvious or repetitive.
Merge topics that occur in several sources into one canonical section, preserving unique details.
Use general knowledge only to resolve terminology, relate concepts, order topics and identify
prerequisites — and mark organisational inferences as such.

### 2. Reorganise logically
Source order is not necessarily study order. Build the progression that fits the content
(foundations → methods → data/analysis → applications → integration is a common shape, but do not
force it). Prerequisites come before what depends on them.

### 3. Deep hierarchy
Numbered main sections, nested bullets, as many levels as the material needs.

### 4. Self-contained bullets
Each important concept gets short explanatory bullets — enough to understand it without reopening
the source, but still an outline, not prose.

### 5. Connections
Where useful: **Depends on / Leads to / Used for / Alternative to / Complementary to / Main
distinction**. Selectively, not mechanically.

### 6. Methods in a consistent frame
Purpose · Principle · Workflow · Components · Input · Output · Question answered · Strengths ·
Limitations · Parameters · Applications · Relation to other methods. Omit categories the sources
do not cover — never invent them.

### 7. Comparisons
Explicit comparison sections for concepts students confuse — only those relevant to the course.

### 8. Exam orientation
Tags (sparingly): **[CORE] [METHOD] [COMPARE] [PROCESS] [FORMULA] [APPLICATION] [LIMITATION]**.
Weight with: repetition across sources, past-exam questions (role `exam`), lecturer questions,
syllabus learning outcomes.

### 9. Equations and technical details
Keep every equation (meaning, variables, use, course notation), number, threshold and parameter,
including those in figures, tables and captions. Keep the page reference "(TAG p12)".

### 10. Figures
Convert process figures into ordered bullet sequences.

### 11. Repetition
One canonical section per topic; repetition across sources → mark [CORE], do not duplicate.

### 12. No hallucination
Do not invent content or add textbook topics the course does not cover. Mark gaps
**[UNCLEAR IN SOURCE]** / **[SOURCE GAP]**. Material from role `text` sources goes under
"Beyond the sources" sub-bullets, never mixed into course content.

### 13. Role rules
- `syllabus`: defines scope. Announced topics with no material in other sources → section
  "Announced but not covered" (becomes the beyond appendix).
- `exam`: weights topics; each question becomes an extra lecturer question (assign to a section).
- `notebook`: becomes "Worked code" bullets under the method it implements.
- `scanned`: as its base role; keep the "img" marks on items.

### 14. Quality control before writing the file
Coverage (every source, every substantive topic, figures/tables considered, technical details
kept) · Integration (duplicates merged, prerequisites first) · Completeness (could serve as the
book's TOC) · Usability (core vs supporting details distinguishable).

### 15. Output format
```
# {subject} — Comprehensive Course Study Guide
## Course Map            (10–20 major areas showing the progression)
## 1. ...                (the unified hierarchy; page refs "(TAG p12)" on detailed bullets)
...
## Cross-Topic Connections
## Announced but not covered      (only if a syllabus exists)
## Coverage Audit        (per source file: major topics incorporated, and where)
```
Priority when trading off: completeness → logical organisation → accuracy → self-containedness →
exam usefulness → conciseness.

---

## C. Glossary (main agent, same pass)

`glossary.md` is read by every chapter writer so terminology does not drift:

```
# Glossary — {subject}
## Terms
| Term (canonical) | Also written as | Definition (one line) | First chapter |
## Symbols and units
| Symbol | Meaning | Unit | LaTeX |        e.g.  m/z | mass-to-charge ratio | Th | \mz
## Abbreviations
| Abbr. | Expansion |
## Notation decisions
- e.g. "use 'peptide-spectrum match (PSM)', never 'PSM match'"; decimal point, not comma.
```
Add the LaTeX macros the glossary needs (e.g. `\newcommand{\mz}{\ensuremath{m/z}}`,
`\DeclareSIUnit\Da{Da}`) to the `@@COURSE_MACROS@@` block of `preamble.tex`.
