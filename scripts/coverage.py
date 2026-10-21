"""Source-page coverage of the book: which source pages are never cited.

Usage (from the book folder):
    python <skill>/scripts/coverage.py [chapters_dir] [source_dir] [--macro NAME]

Counts \\src{TAG}{p} (or \\NAME{TAG}{p} with --macro) and lecturerq TAG/page arguments
in all .tex files of chapters_dir (default: chapters) against the pages listed in
source_dir/<TAG>/index.json (default: source). Pages with < 80 characters of text
that are not image-only (title/divider slides) are excluded from the percentage.
A cited page counts as covered; it does NOT mean its content is correct or complete.
Writes coverage.md and prints it.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import page_text, parse_pages, source_refs  # noqa: E402

TRIVIAL_CHARS = 80


def compress(pages):
    runs = []
    for p in pages:
        if runs and p == runs[-1][1] + 1:
            runs[-1][1] = p
        else:
            runs.append([p, p])
    return ", ".join(str(a) if a == b else f"{a}-{b}" for a, b in runs)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    macro = "src"
    if "--macro" in sys.argv:
        macro = sys.argv[sys.argv.index("--macro") + 1]
        args.remove(macro)
    chapters = Path(args[0]) if args else Path("chapters")
    source = Path(args[1]) if len(args) > 1 else Path("source")

    cited = defaultdict(set)
    unknown = defaultdict(int)
    for f in sorted(chapters.glob("*.tex")):
        for tag, spec, _ in source_refs(f.read_text(encoding="utf-8"), macro):
            try:
                cited[tag].update(parse_pages(spec))
            except ValueError:
                unknown[f"{tag} '{spec}'"] += 1

    rows, total_c, total_n = [], 0, 0
    for idx_file in sorted(source.glob("*/index.json")):
        tag = idx_file.parent.name
        idx = json.loads(idx_file.read_text(encoding="utf-8"))
        if idx["pages"] == 0:
            continue
        trivial = [p for p in range(1, idx["pages"] + 1)
                   if p not in idx["image_pages"]
                   and len((page_text(source, tag, p) or "").strip()) < TRIVIAL_CHARS]
        relevant = [p for p in range(1, idx["pages"] + 1) if p not in trivial]
        uncovered = [p for p in relevant if p not in cited[tag]]
        c = len(relevant) - len(uncovered)
        total_c += c
        total_n += len(relevant)
        pct = 100 * c / len(relevant) if relevant else 100
        rows.append(f"| {tag} | {idx['file']} | {c}/{len(relevant)} | {pct:.0f}% | {compress(uncovered)} |")

    pct = 100 * total_c / total_n if total_n else 0
    out = [f"# Coverage: {total_c}/{total_n} relevant source pages cited ({pct:.0f}%)", "",
           "| TAG | File | Cited | % | Uncovered pages |", "|---|---|---|---|---|", *rows]
    if unknown:
        out += ["", "Unparseable citations: " + ", ".join(unknown)]
    stray = sorted(set(cited) - {p.parent.name for p in source.glob("*/index.json")})
    if stray:
        out += ["", "Citations to unknown TAGs: " + ", ".join(stray)]
    text = "\n".join(out) + "\n"
    Path("coverage.md").write_text(text, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
