#!/usr/bin/env python3
"""Print an email address as the character-code array the pages use.

The address never appears as plain text in the HTML, so naive scrapers can't
harvest it; a real browser rebuilds the mailto: link on load.

    python3 tools/encode-email.py you@your.edu

Paste the printed numbers into `var c = [...]` in BOTH index.html and
publications.html.
"""
import sys

if len(sys.argv) != 2 or "@" not in sys.argv[1]:
    sys.exit("usage: python3 tools/encode-email.py you@your.edu")
print(",".join(str(ord(ch)) for ch in sys.argv[1]))
