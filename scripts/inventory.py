"""Inventory the source material of a study book.

Usage (from the book folder):
    python <skill>/scripts/inventory.py <source_dir> [out_dir]

Scans <source_dir> (non-recursive) for PDFs and notebooks (.ipynb/.py/.R/.Rmd).
For each PDF: page count, pages with a text layer, title, language guess, role
guess and coloured question candidates (coloured spans on a line containing "?").
Writes <out_dir>/inventory.json and <out_dir>/inventory.md (default out_dir: .).
"""
import json
import re
import sys
from pathlib import Path

import pymupdf

pymupdf.TOOLS.mupdf_display_errors(False)

NOTEBOOK_EXT = {".ipynb", ".py", ".r", ".rmd"}
MIN_TEXT_CHARS = 20

STOPWORDS = {
    "en": "the and of to in is for that with are this from by as on be which".split(),
    "de": "der die und das ist nicht mit von den für auf im eine sich des zu".split(),
    "es": "el la de que los las en por una con para del se es como".split(),
    "fr": "le la les de des et est une pour dans que qui sur pas du".split(),
    "it": "il la di che e per una con del della sono non gli le".split(),
    "pt": "o a de que e do da em um para com não uma os no".split(),
}

ROLE_PATTERNS = [
    ("exam", r"exam|klausur|pr[uü]fung|test|quiz|question|fragen|midterm|final"),
    ("syllabus", r"syllab|outline|curricul|modul|course.?info|overview"),
    ("notebook", r"notebook|jupyter|ipynb|exercise|uebung|übung|lab|tutorial|practical"),
    ("text", r"chapter|kapitel|book|paper|review|article|reading|script|skript"),
]


def guess_language(text):
    words = re.findall(r"[a-zäöüßéèàáíóúñç]+", text.lower())
    if not words:
        return "?"
    scores = {lang: sum(words.count(w) for w in sw) for lang, sw in STOPWORDS.items()}
    lang, best = max(scores.items(), key=lambda kv: kv[1])
    return lang if best >= 5 else "?"


def is_coloured(rgb_int):
    r, g, b = (rgb_int >> 16) & 255, (rgb_int >> 8) & 255, rgb_int & 255
    # grey/black/white = all channels close together
    return max(r, g, b) - min(r, g, b) > 80


def colour_name(rgb_int):
    r, g, b = (rgb_int >> 16) & 255, (rgb_int >> 8) & 255, rgb_int & 255
    if r > 150 and g < 110 and b < 110:
        return "red"
    if r > 180 and g > 100 and b < 80:
        return "orange"
    if b > 150 and r < 110:
        return "blue"
    if g > 130 and r < 110 and b < 110:
        return "green"
    return f"#{rgb_int:06x}"


def coloured_questions(page):
    found = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            spans = line["spans"]
            text = "".join(s["text"] for s in spans).strip()
            if "?" not in text or len(text) < 4:
                continue
            col = [s for s in spans if s["text"].strip() and is_coloured(s["color"])]
            if col:
                found.append({"text": text, "colour": colour_name(col[0]["color"])})
    return found


def guess_title(doc):
    meta = (doc.metadata or {}).get("title") or ""
    if len(meta.strip()) > 3 and not meta.lower().startswith(("microsoft", "untitled")):
        return meta.strip()
    if doc.page_count == 0:
        return ""
    best, size = "", 0
    for block in doc[0].get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for s in line["spans"]:
                if s["size"] > size and len(s["text"].strip()) > 3:
                    best, size = s["text"].strip(), s["size"]
    return best


def guess_role(path, doc, text_pages, sample_text):
    name = path.stem.lower()
    for role, pat in ROLE_PATTERNS:
        if re.search(pat, name):
            return role
    if doc.page_count and text_pages / doc.page_count < 0.5:
        return "scanned"
    r = doc[0].rect if doc.page_count else None
    if r is not None and r.width > r.height:
        return "slides"
    if re.search(r"^\s*(In \[\d*\]|>>>|import |library\()", sample_text, re.M):
        return "notebook"
    return "text"


def inspect_pdf(path):
    doc = pymupdf.open(path)
    text_pages, image_pages, sample, questions = 0, [], [], []
    for i, page in enumerate(doc, start=1):
        txt = page.get_text("text", sort=True)
        if len(txt.strip()) >= MIN_TEXT_CHARS:
            text_pages += 1
            if len(sample) < 15:
                sample.append(txt)
            for q in coloured_questions(page):
                q["page"] = i
                questions.append(q)
        else:
            image_pages.append(i)
    sample_text = "\n".join(sample)
    return {
        "file": path.name,
        "kind": "pdf",
        "pages": doc.page_count,
        "text_pages": text_pages,
        "image_pages": image_pages,
        "title": guess_title(doc),
        "language": guess_language(sample_text),
        "role_guess": guess_role(path, doc, text_pages, sample_text),
        "orientation": "landscape" if doc.page_count and doc[0].rect.width > doc[0].rect.height else "portrait",
        "coloured_questions": questions,
    }


def inspect_notebook(path):
    if path.suffix.lower() == ".ipynb":
        nb = json.loads(path.read_text(encoding="utf-8"))
        cells = nb.get("cells", [])
        lines = sum(len(c.get("source", [])) for c in cells)
        desc = f"{len(cells)} cells"
    else:
        lines = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
        desc = f"{lines} lines"
    return {"file": path.name, "kind": "notebook", "pages": 0, "size": desc, "lines": lines,
            "role_guess": "notebook", "language": "?", "title": path.stem,
            "text_pages": 0, "image_pages": [], "coloured_questions": []}


def to_markdown(items):
    out = ["| # | File | Kind | Pages | Text pages | Image-only | Lang | Role guess | Coloured ?-lines |",
           "|---|---|---|---|---|---|---|---|---|"]
    for i, it in enumerate(items, 1):
        pages = it["pages"] if it["kind"] == "pdf" else it.get("size", "")
        out.append(f"| {i} | {it['file']} | {it['kind']} | {pages} | {it['text_pages']} | "
                   f"{len(it['image_pages'])} | {it['language']} | {it['role_guess']} | "
                   f"{len(it['coloured_questions'])} |")
    qs = [(it["file"], q) for it in items for q in it["coloured_questions"]]
    if qs:
        out += ["", "## Coloured question candidates", ""]
        for f, q in qs:
            out.append(f"- **{f}** p{q['page']} ({q['colour']}): {q['text']}")
    scanned = [(it["file"], it["image_pages"]) for it in items if it["image_pages"]]
    if scanned:
        out += ["", "## Pages without a text layer (need visual reading)", ""]
        for f, pages in scanned:
            out.append(f"- **{f}**: {len(pages)} pages ({compress(pages)})")
    return "\n".join(out) + "\n"


def compress(pages):
    runs = []
    for p in pages:
        if runs and p == runs[-1][1] + 1:
            runs[-1][1] = p
        else:
            runs.append([p, p])
    return ", ".join(str(a) if a == b else f"{a}-{b}" for a, b in runs)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")
    out.mkdir(parents=True, exist_ok=True)
    items = []
    for p in sorted(src.iterdir()):
        if not p.is_file():
            continue
        ext = p.suffix.lower()
        if ext == ".pdf":
            items.append(inspect_pdf(p))
        elif ext in NOTEBOOK_EXT:
            items.append(inspect_notebook(p))
    (out / "inventory.json").write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    md = to_markdown(items)
    (out / "inventory.md").write_text(md, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
