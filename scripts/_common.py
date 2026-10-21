"""Helpers shared by check_chapter.py and coverage.py."""
import json
import re
import unicodedata
from pathlib import Path


def brace_args(text, pos, n):
    """Read n balanced {...} arguments starting at text[pos]. Returns (args, end) or (None, pos)."""
    args = []
    for _ in range(n):
        while pos < len(text) and text[pos] in " \t\n":
            pos += 1
        if pos >= len(text) or text[pos] != "{":
            return None, pos
        depth, start = 0, pos
        while pos < len(text):
            c = text[pos]
            if c == "\\":
                pos += 2
                continue
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    break
            pos += 1
        args.append(text[start + 1:pos])
        pos += 1
    return args, pos


def strip_comments(tex):
    return re.sub(r"(?<!\\)%.*", "", tex)


def source_refs(tex, macro="src"):
    """Yield (tag, page_spec, line) for \\src{TAG}{p} and lecturerq{label}{q}{TAG}{p}."""
    tex = strip_comments(tex)
    for m in re.finditer(r"\\%s(?![a-zA-Z])" % macro, tex):
        args, _ = brace_args(tex, m.end(), 2)
        if args:
            yield args[0].strip(), args[1].strip(), tex.count("\n", 0, m.start()) + 1
    for m in re.finditer(r"\\begin\{lecturerq\}", tex):
        args, _ = brace_args(tex, m.end(), 4)
        if args:
            yield args[2].strip(), args[3].strip(), tex.count("\n", 0, m.start()) + 1


def parse_pages(spec):
    """'12' | '12--14' | '12-14' | '12,15' -> [12, ...]; raises ValueError."""
    pages = []
    for part in re.split(r"\s*,\s*", spec.replace("~", "").strip()):
        if not part:
            continue
        m = re.fullmatch(r"(\d+)\s*-{1,3}\s*(\d+)", part)
        if m:
            pages.extend(range(int(m.group(1)), int(m.group(2)) + 1))
        else:
            pages.append(int(part))
    return pages


def load_index(source_dir, tag):
    f = Path(source_dir) / tag / "index.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def page_text(source_dir, tag, page):
    f = Path(source_dir) / tag / f"p{page:03d}.txt"
    return f.read_text(encoding="utf-8") if f.exists() else None


def norm(s):
    """Normalise for verbatim matching: NFKC, unify dashes/minus, decimal comma, drop whitespace, lower."""
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"[\u2212\u2012\u2013\u2014\u2010\u2011]", "-", s)
    s = re.sub(r"(?<=\d),(?=\d)", ".", s)
    s = re.sub(r"\s+", "", s)
    return s.lower()
