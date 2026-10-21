"""Extract per-page source files for reading by the chapter writers.

Usage (from the book folder):
    python <skill>/scripts/extract_sources.py <source_dir> <tags.json> [dpi]

<tags.json> maps source file name -> short TAG, e.g. {"Lecture04.pdf": "L4"}.
Output, per TAG:
    source/<TAG>/p001.txt ...   text layer of each page (layout-sorted)
    source/<TAG>/p001.png ...   rendered page, only for pages without a text layer
    source/<TAG>/code.txt       notebooks only: cells/lines with [cell n] markers
    source/<TAG>/index.json     {"file", "pages", "image_pages"}
"""
import json
import shutil
import sys
from pathlib import Path

import pymupdf

pymupdf.TOOLS.mupdf_display_errors(False)

MIN_TEXT_CHARS = 20


def extract_pdf(path, out, dpi):
    doc = pymupdf.open(path)
    image_pages = []
    for i, page in enumerate(doc, start=1):
        txt = page.get_text("text", sort=True)
        (out / f"p{i:03d}.txt").write_text(txt, encoding="utf-8")
        if len(txt.strip()) < MIN_TEXT_CHARS:
            image_pages.append(i)
            page.get_pixmap(dpi=dpi).save(out / f"p{i:03d}.png")
    return {"file": path.name, "pages": doc.page_count, "image_pages": image_pages}


def extract_notebook(path, out):
    if path.suffix.lower() == ".ipynb":
        nb = json.loads(path.read_text(encoding="utf-8"))
        parts = []
        for n, cell in enumerate(nb.get("cells", []), start=1):
            src = "".join(cell.get("source", []))
            parts.append(f"# [cell {n}] ({cell.get('cell_type', '?')})\n{src}\n")
        (out / "code.txt").write_text("\n".join(parts), encoding="utf-8")
    else:
        shutil.copyfile(path, out / "code.txt")
    return {"file": path.name, "pages": 0, "image_pages": []}


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    tags = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 150
    for fname, tag in tags.items():
        path = src / fname
        out = Path("source") / tag
        out.mkdir(parents=True, exist_ok=True)
        if path.suffix.lower() == ".pdf":
            info = extract_pdf(path, out, dpi)
        else:
            info = extract_notebook(path, out)
        (out / "index.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
        print(f"{tag:10s} <- {fname}: {info['pages']} pages, {len(info['image_pages'])} image-only")


if __name__ == "__main__":
    main()
