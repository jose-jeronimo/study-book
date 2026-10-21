# Study book plan: @@TITLE@@

Created @@DATE@@ by the study-book skill. This file is the single source of truth for a run:
the skill resumes from it. Do not delete sections; tick steps only when their done-test passed.

## Steps
- [ ] 0 Preflight (toolchain, venv, test compile)
- [ ] 1 Inventory (`inventory.md`)
- [ ] 2 Planning Q&A confirmed by user
- [ ] 3 Stage 1: `notes/`, `backbone.md`, `glossary.md`
- [ ] 4 Chapter plan below. **Checkpoint: approved by user**
- [ ] 5 Scaffold compiled (empty skeleton builds)
- [ ] 6 Pilot chapter passes `check_chapter.py` + visual check
- [ ] 7 All chapters written (see table: every row PASS or FAILED)
- [ ] 8 Second read of image-sourced items (skip if no scanned sources)
- [ ] 9 Appendices
- [ ] 10 Full build clean -> `build/@@PDF_NAME@@.pdf`
- [ ] 11 QA + final report
- [ ] 12 Feedback report (skip if not chosen)

## Settings (planning answers)
| Setting | Value |
|---|---|
| Subject / course | |
| Lecturers | |
| Exam (date, time, format, room) | |
| Lecturer hints about the exam | |
| Output language (babel) | |
| Source directory | `..` |
| Audience level | |
| Target length per chapter | 8–15 pages |
| Features ON | examcritical, pitfall, keyidea, objectives, takehome, selftest, lecturerq, figures, beyond, cheatsheet, corrections, overview |
| Features OFF | |
| Notebook handling | worked-code section in the relevant chapter |
| Book title / PDF name | |
| Council review of chapter plan | no |
| Feedback report | no |

## Sources
| TAG | File | Role | Pages | Image-only pages | Notes |
|---|---|---|---|---|---|

Roles: `slides` / `text` (textbook, paper) / `syllabus` / `exam` / `notebook` / `scanned` (+ base role).

## Confirmed lecturer questions
| # | TAG | Page | Question | Chapter |
|---|---|---|---|---|

## Chapter plan
| NN | key | Title | Part | Source pages | Depends on (solid / *inferred*) | Lecturer Qs | Figures | Status |
|---|---|---|---|---|---|---|---|---|

Status values: `todo` / `writing` / `PASS` / `FAILED (reason)`. Status is re-derived from
`check_chapter.py` on resume; this column is only a record.

## Figures
Managed in `figures/manifest.json`.

## Log
Failures, retries, stop-and-report events, user decisions (newest last).
Problems and workarounds as `[issue:<area>] step N — what happened — what was done`.
