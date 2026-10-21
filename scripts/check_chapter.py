"""Done-test for one chapter: standalone compile + labels + source refs + claim ledger.

Usage (from the book folder):
    python <skill>/scripts/check_chapter.py chapters/07-dbsearch.tex [--no-compile] [--appendix]

--appendix: for appendices/front matter — skips the ledger and the "has citations" rule.

Expects: preamble.tex, source/<TAG>/ (extract_sources.py), ledger/<stem>.json:
    [{"claim": "...", "tokens": ["79.966", "98"], "tag": "L4", "page": 6, "img": false}, ...]
Tokens are copied verbatim from source/<TAG>/pNNN.txt. Each token must occur on the
cited page (after normalisation: whitespace, dashes, decimal comma). Items whose page
has no text layer are reported as NEEDS-SECOND-READ, not as failures.

Checks:
  1. compile   the chapter alone inside the shared preamble (errors fail; undefined
               cross-chapter references are ignored)
  2. labels    every \\label and lecturerq label starts with "<key>:" (key = stem without "NN-")
  3. refs      every \\src{TAG}{p} / lecturerq TAG+page exists in source/
  4. ledger    exists, non-empty, every item has tokens, tokens found on cited page
  5. warn      numbers inside examcritical boxes that no ledger token covers
Writes build/check/<stem>/report.json. Exit code 0 = PASS, 1 = FAIL.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (brace_args, load_index, norm, page_text, parse_pages,  # noqa: E402
                     source_refs, strip_comments)

SOURCE = Path("source")

STUB = r"""\documentclass[11pt,a4paper,twoside,openany]{book}
\input{preamble}
\begin{document}
\input{%s}
\end{document}
"""


def compile_chapter(chapter, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    stub = out_dir / "stub.tex"
    stub.write_text(STUB % chapter.with_suffix("").as_posix(), encoding="utf-8")
    cmd = ["pdflatex", "-interaction=nonstopmode", "-file-line-error", "-halt-on-error",
           f"-output-directory={out_dir.as_posix()}", stub.as_posix()]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600,
                              encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return ["pdflatex timed out after 600 s (package-install prompt? see preflight in qa.md)"]
    log = (out_dir / "stub.log")
    log_text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else proc.stdout
    errors = []
    lines = log_text.splitlines()
    for i, line in enumerate(lines):
        if re.match(r"^(\S.*?):(\d+): ", line) or line.startswith("! "):
            ctx = " | ".join(l.strip() for l in lines[i + 1:i + 3] if l.strip())
            errors.append(f"{line.strip()}  {ctx}".strip())
    if proc.returncode != 0 and not errors:
        errors.append(f"pdflatex exit code {proc.returncode}; see {log}")
    return errors[:15]


def check_labels(tex, key):
    bad = []
    t = strip_comments(tex)
    for m in re.finditer(r"\\label\{([^}]*)\}", t):
        if not m.group(1).startswith(key + ":"):
            bad.append(m.group(1))
    for m in re.finditer(r"\\begin\{lecturerq\}", t):
        args, _ = brace_args(t, m.end(), 1)
        if args and not args[0].startswith(key + ":"):
            bad.append(f"lecturerq:{args[0]}")
    return bad


def check_refs(tex):
    bad, n = [], 0
    for tag, spec, line in source_refs(tex):
        n += 1
        idx = load_index(SOURCE, tag)
        if idx is None:
            bad.append(f"line {line}: unknown TAG '{tag}'")
            continue
        try:
            pages = parse_pages(spec)
        except ValueError:
            bad.append(f"line {line}: bad page spec '{spec}' for {tag}")
            continue
        for p in pages:
            if not 1 <= p <= idx["pages"]:
                bad.append(f"line {line}: {tag} p{p} out of range (1-{idx['pages']})")
    return bad, n


def find_elsewhere(tag, token, idx):
    hits = []
    for p in range(1, idx["pages"] + 1):
        txt = page_text(SOURCE, tag, p)
        if txt and norm(token) in norm(txt):
            hits.append(p)
    return hits[:5]


def check_ledger(ledger_path):
    if not ledger_path.exists():
        return [f"ledger missing: {ledger_path}"], [], [], []
    try:
        items = json.loads(ledger_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"ledger is not valid JSON: {e}"], [], [], []
    if not items:
        return ["ledger is empty"], [], [], []
    fails, second, unsure, tokens = [], [], [], []
    for i, it in enumerate(items):
        label = f"#{i} '{it.get('claim', '')[:60]}'"
        toks, tag, page = it.get("tokens") or [], it.get("tag"), it.get("page")
        tokens += toks
        if not toks:
            fails.append(f"{label}: no tokens")
            continue
        idx = load_index(SOURCE, tag) if tag else None
        if idx is None or not isinstance(page, int) or not 1 <= page <= idx["pages"]:
            fails.append(f"{label}: bad source {tag} p{page}")
            continue
        sr = it.get("second_read")
        if page in idx["image_pages"]:
            if sr is None:
                second.append(f"{label}: {tag} p{page} is image-only")
            elif not sr.get("match"):
                unsure.append(f"{label}: second read disagrees ({sr.get('value')})")
            continue
        txt = norm(page_text(SOURCE, tag, page) or "")
        missing = [t for t in toks if norm(t) not in txt]
        if missing:
            if it.get("img"):
                if sr is None:
                    second.append(f"{label}: {missing} read from image on {tag} p{page}")
                elif not sr.get("match"):
                    unsure.append(f"{label}: second read disagrees ({sr.get('value')})")
                continue
            hints = {t: find_elsewhere(tag, t, idx) for t in missing}
            hint = "; ".join(f"'{t}' found on p{h}" if h else f"'{t}' not in {tag}"
                             for t, h in hints.items())
            fails.append(f"{label}: not on {tag} p{page}: {hint}")
    return fails, second, unsure, tokens


def uncovered_numbers(tex, tokens):
    covered = {norm(t) for t in tokens}
    covered_blob = " ".join(covered)
    out = []
    t = strip_comments(tex)
    for m in re.finditer(r"\\begin\{examcritical\}(.*?)\\end\{examcritical\}", t, re.S):
        body = re.sub(r"\\src\{[^}]*\}\{[^}]*\}", "", m.group(1))
        body = re.sub(r"\d+(\.\d+)?\s*(pt|mm|cm|em|ex)\b", "", body)
        for num in re.findall(r"(?<![\w.])\d+(?:[.,]\d+)?", body):
            if len(num) >= 2 and norm(num) not in covered_blob:
                out.append(num)
    return sorted(set(out))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    chapter = Path(sys.argv[1])
    stem = chapter.stem
    key = re.sub(r"^[0-9A-Za-z]{1,3}-", "", stem)
    tex = chapter.read_text(encoding="utf-8")
    out_dir = Path("build") / "check" / stem

    report = {"chapter": str(chapter), "key": key}
    report["compile_errors"] = [] if "--no-compile" in sys.argv else compile_chapter(chapter, out_dir)
    report["bad_labels"] = check_labels(tex, key)
    report["bad_refs"], report["n_refs"] = check_refs(tex)
    appendix = "--appendix" in sys.argv
    if appendix:
        fails, second, unsure, tokens = [], [], [], []
    else:
        fails, second, unsure, tokens = check_ledger(Path("ledger") / f"{stem}.json")
    report["ledger_fail"], report["needs_second_read"], report["unsure"] = fails, second, unsure
    report["warn_uncovered_numbers"] = [] if appendix else uncovered_numbers(tex, tokens)
    if report["n_refs"] == 0 and not appendix:
        report["bad_refs"].append("no \\src citations at all")
    ok = not (report["compile_errors"] or report["bad_labels"] or report["bad_refs"] or fails)
    report["result"] = "PASS" if ok else "FAIL"

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"{report['result']}  {chapter}  ({report['n_refs']} citations)")
    for k in ("compile_errors", "bad_labels", "bad_refs", "ledger_fail",
              "needs_second_read", "unsure", "warn_uncovered_numbers"):
        if report[k]:
            print(f"  {k} ({len(report[k])}):")
            for x in report[k][:15]:
                print(f"    - {x}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
