# Stage 2 — Book specification

What the finished book looks like and the rules every chapter follows. The main agent reads
this whole file; chapter subagents get the relevant parts through `chapter-writer-brief.md`.

## 1. Book anatomy

```
main.tex          title page · TOC · How to use this book · Overview map · Parts/Chapters · Appendices
preamble.tex      from {skill}/templates/preamble.tex (+ course macros from glossary.md)
chapters/00-howto.tex      exam table, structure, box legend, tag table, trust note
chapters/00-overview.tex   one-page TikZ map of chapters + dependencies + reading paths
chapters/NN-key.tex        one per chapter (NN = 01, 02, …; key = short lowercase id)
chapters/A-beyond.tex      announced/missing topics + textbook context        (feature: beyond)
chapters/B-cheatsheet.tex  high-yield comparisons, numbers, formulas, workflows (feature: cheatsheet)
chapters/C-lecturerq.tex   all lecturer questions in source order, linked     (feature: lecturerq)
chapters/D-corrections.tex conflicts, uncheckable items, \unsure list          (feature: corrections)
chapters/E-code.tex        worked code, only if notebooks → appendix was chosen
```
Parts group chapters (e.g. per lecturer or per course block); use `\part{}` when there are ≥ 2
natural blocks. Appendix letters follow the features that are ON (drop gaps).

## 2. Chapter anatomy (fixed order)

```latex
% ============================================================
\chapter{Title}\label{key:ch}
% ============================================================
\begin{objectives}          % 4–7 items, "explain / compare / calculate / outline …"
  \item …
\end{objectives}

\section{…}                 % content sections follow the backbone order
  prose + itemize + tables, \src tags on every factual paragraph/bullet group
  boxes where they earn their place (see §3)
  figures / \workflow chevrons / comparison tables
  lecturer questions at the point where the slide asks them

\takehome                   % 4–6 bullets, the chapter in one breath (+ \src where specific)
\selftest                   % 5–8 questions mixing recall, comparison, application
\begin{answers} … \end{answers}   % one \item per question, concise model answers
```

## 3. Boxes — when to use which

| Box | Use for | Density |
|---|---|---|
| `examcritical` | definitions, numbers, mechanisms the exam will ask; optional title suffix `[ -- topic]` | 2–5 per chapter |
| `lecturerq{key:label}{Question}{TAG}{page}` | every confirmed lecturer/past-exam question, with a model answer you could write in the exam | all assigned to the chapter |
| `pitfall` | pairs students confuse (A vs. B), sign/unit traps | 1–3 |
| `keyidea` | the single idea a section hinges on | 0–3 |
| `beyondslides` | context not in the sources (textbook, general knowledge) — always marked | as needed, never for course facts |
| `codebox[Python]{title}` | short code from notebooks (≤ 30 lines), then explain what it computes | notebook chapters |

Do not nest boxes. Do not put whole sections in boxes. A box with `\src` tags inside is fine.

## 4. Source tags and claims

- `\src{TAG}{12}`, `\src{TAG}{12--14}`, `\src{TAG}{3,7}` — after the claim it supports, at
  paragraph or bullet-group granularity. **Every factual paragraph carries at least one tag.**
- Tags point to PDF page numbers (the `pNNN` files), not printed slide numbers.
- Material from role `text` sources may carry its tag but goes in `beyondslides` unless the
  syllabus makes it course content.
- **Ledger:** every number, threshold, formula constant, date, named value and key definition in
  the chapter gets an entry in `ledger/NN-key.json` (format in chapter-writer-brief.md). Tokens are
  copied verbatim from the page text file so `check_chapter.py` can match them.
- Values that could not be confirmed (unreadable, contradictory, second read disagreed) are
  wrapped in `\unsure{…}` and listed in the corrections appendix.
- Never write "verified" or "confirmed" about content. Tags are citations.

## 5. Writing style

- Language from PLAN.md; follow `glossary.md` for every term, symbol, unit and abbreviation.
- Explanatory textbook prose, compact: short paragraphs, then bullets/tables for lists and
  comparisons. Explain *why*, not only *what*. Define each term at first use in the chapter.
- Course-specific: prefer the lecturer's examples, numbers and notation over generic ones.
- Comparisons → `tabularx` with `booktabs`; multi-step processes → `\workflow{A,B,C}` (≤ 7 steps)
  or an enumerated list; equations → `equation`/`align` with variables explained below.
- Chemistry `\ce{}`, units `\SI{}{}`/`\si{}`, ranges `\SIrange{}{}{}` or `--`.
- Cross-references: `\cref{key:label}` to own labels; to other chapters use `\cref{otherkey:ch}`
  only for chapters listed as dependencies in PLAN.md (labels `<key>:ch` always exist).

## 6. LaTeX safety rules (the build fails without these)

- Write `.tex` and `.json` files with the **Write tool**, never with shell heredocs/echo/sed —
  the shell collapses `\\` and breaks LaTeX.
- All labels start with the chapter key: `\label{key:…}`, lecturer-question labels `key:…`.
- Escape `% & _ # $ { }` in text; `~` for non-breaking space; `\,` before units when not using siunitx.
- Use only packages loaded in `preamble.tex`. Need another? Report it, do not add `\usepackage`
  in a chapter.
- `\includegraphics` only for files listed in `figures/manifest.json` (no extension, path relative
  to `figures/`). Width ≤ `\linewidth`; figures `[htbp]` with a `\caption{… \src{TAG}{p}}`.
- No `\chapter*`, no page-layout commands, no `\newcommand` in chapters (ask for a macro in the report).
- Long tables: `longtable`; wide content: `adjustbox{max width=\linewidth}`.

## 7. Figures

The main agent selects figures in the chapter plan (≤ 3 per chapter; diagrams that carry content
text cannot: pathways, instrument schematics, workflow figures, structures). For each, it renders
the page (`render_preview.py ... 80`), estimates the clip box as page fractions, writes
`figures/manifest.json` and runs `extract_figures.py {source_dir}`. It looks at each crop once and
adjusts the clip if cut off. Prefer a TikZ redraw (`\workflow`, small diagrams) when the original is
low quality or mostly text.

## 8. Overview map (`00-overview.tex`, feature: overview)

- One `ovchap` node per chapter (`c01`, `c02`, …), framed per part with `ovpart` (`fit` library).
- Layout by dependency depth: foundations at the top, applications at the bottom (or left→right).
- `ovdep` (solid) = dependency the sources state ("as discussed in…", explicit prerequisite slide,
  syllabus order); `ovinf` (dashed) = inferred by the editor. The legend under the map says so.
- ≤ 1 page: `adjustbox{max width=\linewidth,max height=0.72\textheight}`.
- Below the map: **Reading paths** — 2–4 short routes (e.g. "fast revision: 1 → 4 → 7 → cheat
  sheet"; "method focus: …"), and one sentence per part on what it builds.

## 9. Appendices

- **Beyond / not covered**: open with a `beyondslides` box stating that nothing here is from the
  sources; per announced-but-missing topic a compact textbook summary; tell the reader to check
  exam relevance with the lecturers.
- **Cheat sheet**: `longtable` of high-yield comparisons (A vs. B); key numbers table; key
  formulas; the main workflows as `\workflow`. Every row is a pointer back to the chapter content —
  no new facts here.
- **Lecturer questions**: in source order, grouped per source, each with link + page to its
  model answer:
  `\newcommand{\lqitem}[3]{\item[\textbf{Q\ref{lq:#1}}] #2 \hfill {\small\color{gray}#3, answer p.\,\pageref{lq:#1}}}`
  (define it inside the appendix file; this is the one allowed exception to the no-newcommand rule).
- **Corrections**: (1) where the backbone/glossary disagreed with the sources and what was chosen;
  (2) contradictions between sources; (3) every `\unsure{}` value with source page and the two
  readings; (4) ledger items that could not be matched and were rewritten or removed.
- **Worked code** (if chosen): per notebook task a `codebox` + explanation + link to the method chapter.

## 10. Style exemplar (illustrative chapter, abridged)

```latex
\chapter{Phosphoproteomics}\label{phospho:ch}
\begin{objectives}
  \item define PTM, phosphorylation, phosphopeptide and phosphosite;
  \item explain the four analytical challenges (stoichiometry, enzymes during handling, ionisation, neutral loss) and their fixes;
  \item describe the workflow and compare IMAC, MOAC (TiO\textsubscript{2}) and antibody enrichment;
\end{objectives}

\section{PTMs and phosphorylation}
A \textbf{post-translational modification (PTM)} is a chemical alteration of an amino-acid side chain \emph{after} translation.
Some PTMs are completely reversible, and they can change fast or stay stable over the protein's lifetime \src{L4}{5}.

\begin{examcritical}[ -- phosphorylation facts]
\src{L4}{6}
\begin{itemize}
  \item On \textbf{Ser, Thr and Tyr}, with a ratio of roughly \textbf{86 : 12 : 2}.
  \item Added by \textbf{kinases} ($\sim$\textbf{500} in human) in an ATP-consuming reaction; removed by
        \textbf{phosphatases} ($\sim$\textbf{200}) by hydrolysis.
  \item First described as a protein on/off switch by \textbf{Fischer \& Krebs} (1955, Nobel Prize 1992) \src{L4}{12}.
\end{itemize}
\end{examcritical}

\subsection{Dynamic range and stoichiometry}
\src{L4}{14}
Phosphorylation is often \textbf{sub-stoichiometric}: only a fraction of a protein pool is phosphorylated at any time. Site occupancy ranges from
$<$1\,\% to nearly quantitative, and only $\sim$\textbf{1\,\% of all peptides} in a digest are phosphopeptides.
\begin{lecturerq}{phospho:whatcanwedo}{What can we do?}{L4}{14}
\begin{itemize}[leftmargin=1.2em]
  \item \textbf{Enrich} phosphopeptides (IMAC, TiO\textsubscript{2}, anti-pTyr antibodies) so that they are no longer a 1\,\% minority.
  \item \textbf{Increase input} and \textbf{fractionate} (high-pH RP, SCX, HILIC) for depth.
  \item Stop artefactual changes during sample prep (fast denaturing lysis, phosphatase inhibitors).
\end{itemize}
\end{lecturerq}
…
\takehome
\begin{itemize}
  \item \textbf{Analytically demanding}: sub-stoichiometric ($\sim$1\,\% of peptides), enzymes active after lysis, neutral loss of 98\,Da.
\end{itemize}
\selftest
\begin{enumerate}
  \item Which enrichment favours multiply phosphorylated peptides?
\end{enumerate}
\begin{answers}
  \item IMAC.
\end{answers}
```
Matching ledger entries:
```json
[{"claim": "S:T:Y ratio roughly 86:12:2", "tokens": ["86:12:2"], "tag": "L4", "page": 6},
 {"claim": "~500 kinases, ~200 phosphatases", "tokens": ["500 kinases", "200 phosphatases"], "tag": "L4", "page": 6},
 {"claim": "Fischer & Krebs 1955", "tokens": ["1955"], "tag": "L4", "page": 12}]
```
