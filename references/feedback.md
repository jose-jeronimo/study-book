# Feedback report (step 12, only if chosen in planning)

Goal: a short, structured Markdown file the user can send to the skill's author. It describes how
the run went, not what the course is about. It is written from the record (PLAN.md, check
reports, logs), not from memory.

## When
- After step 11, if PLAN.md → Settings → Feedback report = `yes`.
- Also after any **stop-and-report**, if the setting is `yes`: write the report with the run status
  `stopped at step N`, then tell the user where it is.
- On resume, overwrite the earlier report; it always describes the latest state.

## Logging during the run (always, whatever the setting)
Whenever something goes wrong or needs a workaround, add a line to PLAN.md → Log:
`[issue:<area>] step N — what happened — what was done`. Areas: `planning`, `stage1` (reading
the sources), `chapter-plan` (structure), `scaffold`, `chapters`, `second-read`, `build`, `qa`,
`scripts`, `templates`, `install`, `tokens/cost`, `other`. Examples: a script failed and was retried, a
source had no text layer, coloured-question detection missed or over-detected, the backbone had
contradictions between sources, a chapter needed fix rounds, a LaTeX package was missing, the user
asked for many changes at a gate.

## Privacy rules
- **No course content:** no slide or textbook text, no claims, no lecturer or student names, no exam
  questions. Use counts, step numbers, TAGs, file names, error messages and log lines.
- Shorten error messages to the relevant lines; remove absolute paths above the book folder
  (replace with `<course>/`).
- Nothing is sent anywhere. The user reads the file and decides whether to send it.

## User comments
Ask once with AskUserQuestion: "Do you want to add your own comments to the feedback report?"
Options: no, write it as is (Recommended) / yes. If yes, ask in plain text for: what worked, what
was annoying or wrong, what they would change, and a rating of the book (1–5). Quote their answers
verbatim under **User comments**; do not rewrite them.

## File
`study-book-feedback_<YYYY-MM-DD>.md` in the book folder. Format (keep the headings exactly, so
the author can ingest it):

```markdown
# study-book feedback report

## Run
| Field | Value |
|---|---|
| Date | YYYY-MM-DD |
| Skill version | output of `git -C {skill} describe --tags --always` (e.g. `v0.1.0`, or `v0.1.0-3-gabc1234` = 3 commits after it), or "unknown" |
| OS / LaTeX / Python | e.g. Windows 11 / MiKTeX 24.1 / Python 3.12 |
| Claude model / plan | as far as known, else "unknown" |
| Status | finished / stopped at step N (reason) |
| Duration | first to last PLAN.md log entry, approximate |
| Resumes | number of times the run was resumed |

## Input
| Field | Value |
|---|---|
| Sources | N PDFs, N pages; roles: N slides, N text, N exam, N syllabus, N notebook |
| Scanned pages | N (N sources) |
| Source language → output language | e.g. de → en |
| Coloured-question candidates | N found, N confirmed by the user |

## Planning choices
Depth, audience, features OFF, notebook handling, council review yes/no, assumptions the user
corrected at the planning gate (count + kind, no content).

## Structure
- Chapters: N planned, N after the chapter-plan gate; changes the user requested (kind only:
  merge / split / reorder / rename / scope).
- Council suggestions: N made, N accepted (if used).
- Orphan / out-of-scope pages: N.

## Results
| Metric | Value |
|---|---|
| Book pages | N |
| Chapters PASS / FAILED | N / N |
| Chapter fix rounds (total) | N |
| Second-read items / mismatches | N / N |
| Full-build fix iterations | N |
| Source coverage | N % (N uncited pages) |
| Past-exam gap test | N questions, N gaps (or "no exams") |

## Issues
One row per `[issue:…]` log line, plus anything from check reports or the build log worth
reporting. Most severe first.

| # | Area | Step | What happened | What was done | Severity (blocker / major / minor) |
|---|---|---|---|---|---|

## User comments
Verbatim answers, or "none".
```

After writing it, tell the user the file path, that it contains no course content, and that they
can read and edit it before sending it to the skill's author.
