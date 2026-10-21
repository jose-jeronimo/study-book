"""Render selected PDF pages to PNG for visual checks.

Usage:
    python tools/render_preview.py <pdf> <out_dir> <pages> [dpi]

<pages> is a comma list of 1-based pages or ranges, e.g. "1,5-8".
"""
import sys
from pathlib import Path

import pymupdf

pymupdf.TOOLS.mupdf_display_errors(False)


def parse_pages(spec, n):
    pages = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            pages.extend(range(int(a), int(b) + 1))
        else:
            pages.append(int(part))
    return [p for p in pages if 1 <= p <= n]


def main():
    pdf, out_dir, spec = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
    dpi = int(sys.argv[4]) if len(sys.argv) > 4 else 60
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(pdf)
    stem = Path(pdf).stem
    for p in parse_pages(spec, doc.page_count):
        target = out_dir / f"{stem}_p{p}.png"
        doc[p - 1].get_pixmap(dpi=dpi).save(target)
        print(target)


if __name__ == "__main__":
    main()
