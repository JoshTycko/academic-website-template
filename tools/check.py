#!/usr/bin/env python3
"""Sanity checks for the site. Exits non-zero, loudly, if anything is wrong.

    python3 tools/check.py              # check everything
    python3 tools/check.py --renumber   # also rewrite the countdown N..1, then check

Checks:
  1. Every page's tags are balanced (Python's html.parser, which is HTML5-aware;
     xmlns-style validators give false positives on valid HTML5).
  2. The "All work" countdown on publications.html runs N down to 1 with no gaps.
  3. The homepage's Selected list has the same number of papers as the entries
     marked data-selected on publications.html, with matching titles.
  4. Search and sharing metadata is consistent: the structured data (JSON-LD)
     parses and names the same person as the <h1>, the link-preview image
     exists, and every absolute URL (canonical, og:url, og:image, sitemap,
     robots.txt) uses the same site address.
  5. Leftover template placeholders are reported (a warning while you are
     still setting up, an error with --strict once the site should be done).
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["index.html", "publications.html", "404.html"]
SEO_FILES = ["robots.txt", "sitemap.xml"]
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "source", "track", "wbr"}
# Strings that only exist in the untouched template.
PLACEHOLDERS = ["Your Name", "Your Institution", "Your Role", "YOUR_SCHOLAR_ID",
                "your_handle", "0000-0000-0000-0000", "example.github.io",
                "Name Y", "Journal Name",
                # sample text from the template's About, Research, and lists
                "Lorem ipsum", "Duis aute irure", "Sed ut perspiciatis",
                "Research interest one", "Title of a",
                ",".join(str(ord(c)) for c in "you@example.edu")]

errors, warnings = [], []


class Balance(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.problems = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.problems.append(f"line {self.getpos()[0]}: stray </{tag}>")
            return
        open_tag, line = self.stack.pop()
        if open_tag != tag:
            self.problems.append(
                f"line {self.getpos()[0]}: </{tag}> closes <{open_tag}> opened on line {line}")


def titles(html, selected_only=False):
    out = []
    for li in re.findall(r"<li\b([^>]*)>(.*?)</li>", html, re.S):
        attrs, inner = li
        if selected_only and "data-selected" not in attrs:
            continue
        m = re.search(r'class="pubs__title"><a[^>]*>(.*?)</a>', inner, re.S)
        if m:
            out.append(re.sub(r"\s+", " ", m.group(1)).strip())
    return out


def main():
    renumber = "--renumber" in sys.argv
    strict = "--strict" in sys.argv

    for name in PAGES:
        path = ROOT / name
        if not path.exists():
            errors.append(f"{name}: missing")
            continue
        p = Balance()
        p.feed(path.read_text())
        p.close()
        errors.extend(f"{name}: {x}" for x in p.problems)
        errors.extend(f"{name}: <{t}> on line {l} never closed" for t, l in p.stack)

    pubs_path = ROOT / "publications.html"
    pubs = pubs_path.read_text()
    m = re.search(r'<ol class="pubs pubs--numbered">(.*?)</ol>', pubs, re.S)
    if not m:
        errors.append('publications.html: no <ol class="pubs pubs--numbered"> list found')
    else:
        block = m.group(1)
        nums = [int(n) for n in re.findall(r'<span class="pubs__num">(\d+)</span>', block)]
        n_items = len(re.findall(r"<li\b", block))
        if len(nums) != n_items:
            errors.append(f"publications.html: {n_items} entries but {len(nums)} pubs__num spans")
        want = list(range(n_items, 0, -1))
        if nums != want:
            if renumber:
                it = iter(want)
                new_block = re.sub(r'(<span class="pubs__num">)\d+(</span>)',
                                   lambda mm: f"{mm.group(1)}{next(it)}{mm.group(2)}", block)
                pubs = pubs.replace(block, new_block, 1)
                pubs_path.write_text(pubs)
                print(f"renumbered countdown {n_items}..1")
            else:
                errors.append(f"publications.html: countdown is {nums}, expected {want} "
                              "(run with --renumber to fix)")

    home = (ROOT / "index.html").read_text()
    sel_pubs = titles(pubs, selected_only=True)
    m = re.search(r'id="selected".*?<ol class="pubs">(.*?)</ol>', home, re.S)
    sel_home = titles(m.group(1)) if m else []
    if sel_home != sel_pubs:
        errors.append("Selected papers differ between pages:\n"
                      f"    index.html:        {sel_home}\n"
                      f"    publications.html: {sel_pubs} (entries with data-selected)")

    for name in PAGES:
        text = (ROOT / name).read_text()
        hits = sorted({ph for ph in PLACEHOLDERS if ph in text})
        # The email icon starts as href="#" by design; a script fills it in.
        dead = len(re.findall(r'href="#"', text)) - text.count('id="email-link" href="#"')
        if hits:
            warnings.append(f"{name}: template placeholders still present: {hits}")
        if dead:
            warnings.append(f'{name}: {dead} placeholder link(s) href="#"')

    # Search and sharing metadata
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', home, re.S)
    if not m:
        errors.append("index.html: no structured data (<script type=\"application/ld+json\">)")
    else:
        try:
            ld = json.loads(m.group(1))
        except json.JSONDecodeError as e:
            errors.append(f"index.html: structured data is not valid JSON: {e}")
            ld = {}
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", home, re.S)
        h1 = re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else ""
        if ld and ld.get("name") != h1:
            errors.append(f'index.html: structured-data name "{ld.get("name")}" differs from <h1> "{h1}"')
    canon = re.search(r'<link rel="canonical" href="(https?://[^/"]+)', home)
    if not canon:
        errors.append("index.html: no absolute <link rel=\"canonical\">")
    else:
        base = canon.group(1)
        # Every URL that names this site must use the same address.
        own = {
            "index.html": r'<link rel="canonical" href="([^"]+)"|<meta property="og:(?:url|image)" content="([^"]+)"|"(?:url|image)": "([^"]+)"',
            "publications.html": r'<link rel="canonical" href="([^"]+)"|<meta property="og:(?:url|image)" content="([^"]+)"',
            "robots.txt": r"Sitemap: (\S+)",
            "sitemap.xml": r"<loc>([^<]+)</loc>",
        }
        for name, pattern in own.items():
            path = ROOT / name
            if not path.exists():
                errors.append(f"{name}: missing")
                continue
            for groups in re.findall(pattern, path.read_text()):
                url = next(u for u in (groups if isinstance(groups, tuple) else (groups,)) if u)
                if not url.startswith(base):
                    errors.append(f"{name}: {url} is not on the site address {base} "
                                  "(taken from the canonical link in index.html)")
        og = re.search(r'<meta property="og:image" content="([^"]+)"', home)
        if not og:
            errors.append("index.html: no og:image (link-preview image)")
        elif not (ROOT / og.group(1).replace(base, "").lstrip("/")).exists():
            errors.append(f"index.html: og:image {og.group(1)} has no matching local file "
                          "(run python3 tools/make-og-image.py)")
    for name in SEO_FILES:
        path = ROOT / name
        if path.exists() and "example.github.io" in path.read_text():
            warnings.append(f"{name}: still uses the placeholder address example.github.io")

    favicon = (ROOT / "img" / "favicon.svg").read_text()
    if ">YN<" in favicon:
        warnings.append('img/favicon.svg: still shows the template initials "YN"')

    for w in warnings:
        print("WARN ", w)
    if strict:
        errors.extend(warnings)
    for e in errors:
        print("ERROR", e)
    if errors:
        sys.exit(f"\n{len(errors)} problem(s) found.")
    print(f"OK: {len(PAGES)} pages balanced, countdown contiguous, selected lists match"
          + (f", {len(warnings)} warning(s)" if warnings else ""))


if __name__ == "__main__":
    main()
