---
name: setup-site
description: First-time setup of this academic website template. Interviews the owner, then replaces every placeholder (name, role, bio, research interests, publications, links, photo, email, favicon) with their real, verified content. Use when the site still shows "Your Name", when tools/check.py reports placeholders, or when the user says "set up my website", "make this my site", or "fill this in for me".
---

# Set up the site for its owner

Goal: by the end, `python3 tools/check.py --strict` passes, every page shows
the owner's real content, and the owner has seen screenshots and approved them.

Work in this order. Ask questions in small batches, not one giant form. Offer
sensible defaults so the owner can just say "yes".

## 1. Collect source material first

Ask for these up front. They answer most later questions:

- **A CV** (PDF or .docx path, or pasted text). This is the best single source
  for the bio, research areas, and publication list.
- **ORCID iD** and/or **Google Scholar** profile URL.
- **A square headshot** (path to a .jpg or .png, at least 600×600). Optional.
  The placeholder silhouette stays until they provide one.

Read the CV fully before drafting anything.

## 2. Identity and links

Confirm, then edit `index.html`, `publications.html`, and `404.html`:

- Display name (nav brand, `<h1>`, `<title>`, footer, `alt` text, og tags)
- Role line, for example `Assistant Professor · University of X` (the hero eyebrow)
- Footer line: institution and city
- Email: `python3 tools/encode-email.py their@address` and paste the numbers
  into `var c = [...]` in **both** `index.html` and `publications.html`
- Profile icons in the footer of both pages: Google Scholar, ORCID, X. Fill in
  the real URLs. **Delete** the icon for any profile they don't want shown, and
  don't invent handles. Ready-made icons for Bluesky, GitHub, Mastodon, and a
  personal website are in `snippets/social-icons.html`. Before linking any
  profile, confirm the page exists; if it doesn't, tell the owner and leave it
  out.
- Favicon: change the initials in `img/favicon.svg`.
- The site address: replace `https://example.github.io` everywhere it
  appears (`index.html`, `publications.html`, `robots.txt`, `sitemap.xml`)
  with their final address. If they don't know it yet, use
  `https://USERNAME.github.io` and fix it at deploy time. `tools/check.py`
  fails if these disagree.
- Structured data: the `application/ld+json` block in `index.html` head.
  Fill in `name` (exactly as in the `<h1>`), `url`, `image` (their photo's
  full URL), `jobTitle`, `affiliation`, and `alumniOf` from the CV. `sameAs`
  lists the same profile URLs as the footer icons, and only those. Delete
  `alumniOf` or `affiliation` rather than guess.

## 3. Bio (About section)

Draft three or four short paragraphs from the CV, in the first person, in plain
words: where they are now and what they work on; their training; optionally
teaching, service, or outreach; optionally anything else notable. Show the
draft and revise until they approve it. Don't add claims that aren't in their
materials.

## 4. Research interests

Propose two to four interests as short parallel verb phrases, each with one or
two sentences. Get approval.

## 5. Publications

Build the full list in `publications.html` (the `id="publications"` list).

1. Gather candidates from the CV, then cross-check against ORCID
   (`https://pub.orcid.org/v3.0/<ORCID>/works`, request JSON) and/or PubMed.
2. For **every** entry, verify against Crossref
   (`https://api.crossref.org/works/<DOI>`) or PubMed: exact title, venue,
   **online** publication year, and the owner's author position. Take co-first
   (`*`) and co-corresponding (`#`) markers from the paper itself. If the paper
   can't be reached, use the owner's CV and list that entry as unconfirmed.
   - **When sources disagree** (CV vs. Crossref vs. ORCID: title, year, author
     list, markers), don't pick silently. Use the publisher's record if it is
     clearly correct, and list every disagreement for the owner to decide.
   - **If the owner isn't in the paper's author list, leave the paper out** and
     tell them. Name collisions and CV errors both happen.
   - **Items on ORCID or PubMed but not on the CV:** ask before adding them.
3. Write each entry in the existing markup (copy a placeholder `<li>`): title
   links to `https://doi.org/<DOI>`, owner's name in `<span class="self">`,
   long author lists shortened with `&hellip;` around the owner's position,
   correct `data-type` and badge, newest first.
4. Links: `DOI`; `PDF` to a hosted file in `pdf/` or to the PubMed Central
   page; press links only where real coverage exists and you fetched the page.
5. Run `python3 tools/check.py --renumber` to set the countdown.
6. Ask which three to five papers are **Selected**. Mark them `data-selected` and
   mirror the same papers into the homepage list in `index.html`, in the same
   newest-first order as the full list (`tools/check.py` enforces this). The
   homepage entries use the shorter homepage markup; copy an existing one.
7. Patents and Other writing: fill them in from the CV, or delete the section
   and its `.secnav__link` if they have none.
8. The line under the list links to their Google Scholar profile. Delete it if
   they have no profile.
9. Tidy what the list doesn't use: remove a filter chip whose type has no
   entries (both its `<input class="pubfilter__radio">` and its `<label>`), and
   remove the `*`/`#` key under the page heading if no entry uses either
   marker.

List anything you could not verify, and ask about it. Don't drop it silently.

## 6. Photo

Copy their image to `img/portrait.jpg` (crop to square if needed, using `sips`
on macOS or Python's PIL; show the owner the crop), change the hero `<img src>`
in `index.html` from `img/portrait.svg` to `img/portrait.jpg`, and delete
`img/portrait.svg`.

The design renders the photo as a circle, grayscale until hovered. Ask whether
they want to keep that. To show it in color, remove the grayscale `filter`, the
hover rule, and the `transition` from `.portrait` in **both** `index.html`
(inline `<style>`) and `css/style.css`.

## 7. Optional: make the look their own

The default look is warm off-white paper, near-black ink, one burnt-amber accent,
a Newsreader serif for headings, and Inter for body text. Ask whether they want
to change the accent color. If they do:

- Change `--accent` and `--accent-soft` in **four** places: the light and dark
  `:root` blocks in `index.html`'s inline `<style>` and in `css/style.css`.
- The dark-mode accent needs to be lighter than the light-mode one. Check that
  text contrast is at least 4.5:1 against `--paper` in both modes.
- Update the favicon colors in `img/favicon.svg` only if they also change the
  paper and ink colors.

Show before and after screenshots before keeping a change.

## 8. Link preview

The preview shown when the site is shared (Slack, iMessage, X, LinkedIn) is the
page title, `og:description`, and `og:image`, set in the head of both pages.

- `og:description` on the homepage: just the role and affiliation, for example
  `Assistant Professor, University of X`. Keep research summaries out of it;
  previews truncate them. (The separate `<meta name="description">` is what
  search engines show, and can say more.)
- **With a headshot (preferred):** set `og:image` to the photo's full URL
  (`https://SITE/img/portrait.jpg`), `og:image:width`/`height` to its pixel
  size, `og:image:alt` to their name, and `twitter:card` to `summary`, which
  shows a square image. Then delete `img/og.png`.
- **Without a headshot:** run `python3 tools/make-og-image.py`, which renders
  `img/og.png`, a 1200×630 card with the name and role line in the site's fonts
  and colors. Keep `twitter:card` as `summary_large_image`. Re-run it if the
  name, role, or accent color changes.

Do both pages.

## 9. Verify

1. `python3 tools/check.py --strict` must pass with no warnings.
2. Resolve every DOI (`curl -sI https://doi.org/<DOI>` should return 301 or 302).
3. Run the **visual-check** workflow and look at every screenshot.
4. Show the owner the screenshots, or have them open
   `python3 -m http.server 8000` → <http://localhost:8000>.

## 10. Hand off

Commit the work. Then offer the **deploy-site** workflow to put it online. Don't
push without the owner's go-ahead.
