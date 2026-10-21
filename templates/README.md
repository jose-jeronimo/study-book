# @@TITLE@@

LaTeX sources of a study book generated with the `study-book` skill from the PDFs in `@@SOURCE_DIR@@`.

## Build
- **CLI:** `latexmk` inside this folder (uses `.latexmkrc`), or `pdflatex -output-directory=build main.tex` twice.
- **VS Code:** open this folder (so `.vscode/settings.json` is picked up), open `main.tex`, run
  *LaTeX Workshop: Build LaTeX project*. The PDF goes to `build/main.pdf`; the final copy is `build/@@PDF_NAME@@.pdf`.

## Layout
| Path | Content |
|---|---|
| `PLAN.md` | planning answers, sources, chapter plan, step status, log |
| `inventory.md` | scan of the source material |
| `backbone.md`, `glossary.md` | stage-1 outline and shared terminology |
| `notes/` | per-source topic notes (stage 1) |
| `source/<TAG>/` | per-page text (`pNNN.txt`) and images of pages without a text layer |
| `main.tex`, `preamble.tex` | book skeleton, boxes and macros (`\src`, `lecturerq`, `\unsure`, `codebox`, `\workflow`) |
| `chapters/` | `00-howto`, `00-overview`, one file per chapter, appendices |
| `ledger/` | per-chapter claim ledgers (claim -> tokens -> source page) |
| `figures/` | crops from the PDFs (`manifest.json`) |
| `coverage.md` | source pages never cited |

## Scripts (in the skill folder)
`<skill>/scripts/`: `inventory.py`, `extract_sources.py`, `extract_figures.py`, `check_chapter.py`, `coverage.py`, `render_preview.py`.
Run them from this folder with `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python`.
