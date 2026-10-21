"""Crop figures from the source PDFs into figures/.

Usage (from the book folder):
    python <skill>/scripts/extract_figures.py <source_dir> [name ...]

Reads figures/manifest.json:
    {"name": {"file": "Deck.pdf", "page": 12, "clip": [x0, y0, x1, y1]}, ...}
page is 1-based; clip is given as page fractions (0..1). Output: figures/<name>.png.
Pass names to re-crop only those.
"""
import json
import sys
from pathlib import Path

import pymupdf

pymupdf.TOOLS.mupdf_display_errors(False)

DPI = 200


def crop(src_dir, out_dir, name, spec):
    doc = pymupdf.open(src_dir / spec["file"])
    pg = doc[spec["page"] - 1]
    x0, y0, x1, y1 = spec.get("clip", [0, 0, 1, 1])
    r = pg.rect
    clip = pymupdf.Rect(r.x0 + x0 * r.width, r.y0 + y0 * r.height,
                        r.x0 + x1 * r.width, r.y0 + y1 * r.height)
    pg.get_pixmap(dpi=DPI, clip=clip).save(out_dir / f"{name}.png")
    print(f"{name:24s} <- {spec['file']} p{spec['page']}")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src_dir = Path(sys.argv[1])
    out_dir = Path("figures")
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    for name in sys.argv[2:] or list(manifest):
        crop(src_dir, out_dir, name, manifest[name])


if __name__ == "__main__":
    main()
