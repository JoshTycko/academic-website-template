---
name: add-publications
description: Keep the site's publication record current. Finds and verifies new papers, preprints (and preprints that have since been published), press coverage such as News & Views, and patent status changes, then adds them in the site's markup and redeploys after approval. Use for "add my new paper", "check for new publications", "any press on my papers?", "update my website", or a periodic check.
---

# Add and update publications

This is the owner's public scholarly record. **Never fabricate.** Every title,
year, venue, DOI, author position, press link, and patent status must come from
a source you actually fetched. When you can't confirm something, tell the owner
and leave it out rather than guess.

## 1. Find what's new

Read the current list in `publications.html` first, then compare it against:

- **ORCID**: `https://pub.orcid.org/v3.0/<ORCID>/works` (JSON). Their ORCID iD
  is in the footer link.
- **PubMed** (an author search, or a PubMed MCP connector if one is attached)
  and **Crossref** (`https://api.crossref.org/works?query.author=...`).
- **bioRxiv/medRxiv/arXiv** for preprints. Also check whether any preprint on
  the site has since been published; if it has, update that entry to the
  journal version and change its `data-type` and badge.
- Google Scholar often blocks automated fetches. If it does, ask the owner to
  paste in recent items.

## 2. Verify each new item

- Title, venue, and **online** publication year from Crossref or the publisher.
- The owner's real author position and markers: `*` co-first, `#`
  co-corresponding, taken from the paper, not from a CV paraphrase.
- The DOI resolves: `curl -sI https://doi.org/<DOI>` returns 301 or 302.
- Confirm with the owner that each item is really theirs, since name collisions
  are common.

## 3. Look for press

Search for a News & Views, journal highlight, preLights, university press
release, or news feature about each new paper. **Only link a URL you fetched and
confirmed is about that paper.** If you can't confirm it, mention it to the
owner instead of linking it.

## 4. Patents (if the site has a Patents section)

Check Google Patents. A WO (PCT) record showing "Ceased" refers to the
international phase, not to whether the patent was granted. Grants show up in
national family members with grant kind codes (for example `US…B2`, `EP…B1`,
`JP…B2`). Confirm the owner is a named inventor before listing anything new.

## 5. Edit

- Copy an existing `<li>` in the `id="publications"` list, fill in the verified
  fields, keep newest first, set `data-type` and the matching badge, and wrap
  the owner's name in `<span class="self">`.
- Title links to the DOI. `PDF` links to a hosted file in `pdf/` (see
  `pdf/README.md` on what is safe to host) or to the PubMed Central page.
- Run `python3 tools/check.py --renumber`.
- Ask whether the new paper belongs among the **Selected** papers. If it does,
  mark it `data-selected` and mirror it into `index.html`. The check script fails
  if the two pages disagree.

## 6. Verify and deploy

Run `python3 tools/check.py`, run the **visual-check** workflow on
`publications.html` (and `index.html` if Selected changed), then summarize what
changed and what was left unconfirmed. Commit, and push only after the owner
approves.
