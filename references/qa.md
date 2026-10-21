# Build, checks and QA

## Preflight (step 0)

1. **TeX**: `pdflatex --version`, `latexmk --version`. Missing → stop-and-report with install hint
   (Windows: MiKTeX; macOS: MacTeX; Linux: texlive-full) — the skill cannot produce a PDF without it.
2. **MiKTeX unattended installs** (Windows): check `initexmf --show-config-value=[MPM]AutoInstall`;
   if it is not `1`, run `initexmf --set-config-value=[MPM]AutoInstall=1` (user scope; tell the user). Without it, a missing package opens a dialog and the
   build hangs. TeX Live: missing packages need `tlmgr install …` — report them.
3. **Python + PyMuPDF**: try `python -c "import pymupdf"`. If it fails, create a venv in the book
   folder: `python -m venv .venv` then `.venv/Scripts/python -m pip install -r {skill}/scripts/requirements.txt`
   (`.venv/bin/…` on macOS/Linux). Use that interpreter as `{python}` for every script.
4. **Test compile of the template**: copy `preamble.tex` + a minimal `main.tex` into
   `build/preflight/`, compile once (this triggers all package installs up front, ~1–3 min the
   first time). Must succeed before step 1.

## Chapter done-test — `check_chapter.py`

```
{python} {skill}/scripts/check_chapter.py chapters/NN-key.tex [--no-compile]
```
Compiles the chapter alone (stub with the shared preamble, `build/check/NN-key/`), checks label
prefixes, `\src` targets, and the ledger: every token must occur on the cited page text.
`PASS` = no compile errors, labels OK, refs OK, no ledger failures. `needs_second_read` (image
pages) and `warn_uncovered_numbers` (numbers in examcritical boxes without ledger token) are
reported but do not fail. Report: `build/check/NN-key/report.json`.

What it proves: the chapter builds; the cited pages exist; the copied numbers/terms are on those
pages. What it does **not** prove: that the sentence around them is correct or complete. Keep that
distinction in every message to the user.

## Second read (step 8, only if any ledger item has `img: true` or an image page)

Collect all items listed under `needs_second_read` across reports. Spawn one subagent (or one per
~40 items) that gets **only** the list of (TAG, page, what to read — e.g. "the voltage on the ESI
needle") and the page PNGs — *not* the chapter text or the first reading. It returns the value
it reads per item. The main agent compares:
- same value → add `"second_read": {"value": "…", "match": true}` to the ledger item;
- different / unreadable → `"match": false`, wrap the value in the chapter in `\unsure{…}`, add a
  corrections-appendix row (both readings, TAG, page). Re-run `check_chapter.py --no-compile`.

## Full build (step 10)

```
latexmk            (in the book folder; uses .latexmkrc → build/main.pdf)
```
Then read `build/main.log`:
- lines starting `!` or `file:line:` → errors (fix in the named file);
- `Reference … undefined` → wrong cross-chapter label (labels are `<key>:…`);
- `Overfull \hbox` > 20pt → fix (adjustbox, `\linewidth`, break long tokens); smaller ones ignore;
- `Float too large` / figures drifting far → reduce width or use `[H]`.
Max **3** fix iterations, then stop-and-report with the remaining log lines. Finally copy
`build/main.pdf` to `build/<PDF name>.pdf`.

## QA (step 11)

1. **Coverage**: `{python} {skill}/scripts/coverage.py` → `coverage.md`. For each uncovered page:
   cite it where its content already is, add the missing content to the right chapter (subagent),
   or list it in the report with a reason (title slide, duplicate, out of scope).
2. **Visual check**: `{python} {skill}/scripts/render_preview.py build/main.pdf prev <pages> 70` for
   ~10 pages: title, how-to, overview, the first page of 3 chapters, a page with a figure, a table,
   a lecturer-question box, the cheat sheet. Read the PNGs; fix overlaps, cut-off boxes,
   unreadable figures, empty pages.
3. **Past-exam gap test** (only with role `exam` sources): one subagent gets the questions and the
   book PDF text (`build/main.pdf`), answers each from the book alone and lists questions with no
   or only partial answer + where it looked. Gaps → add to the relevant chapter or report.
   This finds gaps; it certifies nothing.
4. **Final report to the user** (also appended to PLAN.md → Log):
   - PDF path, pages, chapters (PASS/FAILED), lecturer questions answered
   - coverage % and uncovered pages with reasons
   - `\unsure` count and the corrections-appendix page
   - **Human spot-check list**: ~15 high-stakes items — exam-critical numbers/formulas and all
     image-read values — each as "claim — TAG p.N — book p.M". Say plainly: tags are citations,
     the checks matched numbers to pages, the prose itself was not independently verified.
