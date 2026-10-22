---
name: visual-check
description: Screenshot every page of the site at desktop and phone widths in light and dark mode, then actually inspect the images for layout, contrast, and content problems before anything is deployed. Use after any visual or content change, before every deploy, or when asked "does it look right?" or "check the site".
---

# Visual check

Never report that a page "looks good" without having looked at screenshots of it.

## 1. Run the structural check

```bash
python3 tools/check.py
```

Fix any ERROR lines first. They are real breakage: unbalanced tags, a broken
countdown, or Selected lists that disagree between pages.

## 2. Take screenshots

```bash
bash tools/screenshots.sh
```

This starts a local server, renders `index.html`, `publications.html`, and
`404.html` at 1280 px and 390 px wide in light and dark mode with headless
Chrome, and writes 12 PNGs to `screenshots/` (gitignored). It needs Google
Chrome or Chromium installed. If you have a browser tool of your own (such as a
built-in browser pane), you can use it instead.

## 3. Look at every image

Open each PNG and check:

- **Content:** no leftover placeholders, the owner's name is spelled the same
  everywhere, and nothing is cut off or overlapping.
- **Phone width:** no horizontal overflow, the nav fits, and long titles wrap
  cleanly.
- **Dark mode:** text and accent links are readable, and the photo and icons
  don't disappear against the background.
- **Publications:** the filter chips are visible, the countdown numbers are
  right, badges match entry types, and markers (`*`, `#`) render as
  superscripts.
- **Footer:** profile icons are present and point at the right profiles.

## 4. Report

Tell the owner what you checked, what you fixed, and anything you're unsure of,
and point them to the screenshots. For a change to the look, show before and
after side by side and let them choose.
