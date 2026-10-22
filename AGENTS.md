# Academic website template: instructions for coding agents

This repo is a hand-coded static academic website: plain HTML and CSS,
self-hosted fonts, no build step, no packages. It deploys free on GitHub Pages.
It ships with placeholder content ("Your Name", "Name Y", `href="#"`) that the
owner replaces with their own.

This file follows the `AGENTS.md` convention. `CLAUDE.md` imports it for Claude
Code.

## First thing in every session

Run `python3 tools/check.py`. If it reports template placeholders, the site has
not been set up yet: offer to run the setup workflow in
`.claude/skills/setup-site/SKILL.md`.

## Workflows

Each workflow is a plain Markdown file under `.claude/skills/`. Claude Code
loads them as skills automatically. With any other tool, read the file and
follow its steps.

| Workflow | Use it to |
|---|---|
| `setup-site` | Replace every placeholder with the owner's real, verified content |
| `add-publications` | Find, verify, and add new papers, preprints, press, and patents |
| `visual-check` | Screenshot every page (desktop/phone, light/dark) and inspect them |
| `deploy-site` | Publish on GitHub Pages, optionally with a custom domain |

## Where to edit what

| To change… | Edit… |
|---|---|
| Name, role line, about text | `index.html` |
| Research interests | `index.html` (the `.interests` list) |
| Full publication list | `publications.html`, inside `id="publications"` |
| Selected papers | Mark entries `data-selected` in `publications.html` **and** mirror the same papers, in the same order, into the homepage's Selected list in `index.html` |
| Patents, other writing | `publications.html`, `id="patents"` and `id="other"`. Delete a section you don't need, together with its `.secnav__link` in the left rail |
| Headshot | `img/portrait.jpg` (square, at least 600×600), then point the `<img>` in `index.html` at it |
| Favicon | The initials in the `<text>` element of `img/favicon.svg` |
| Link preview | The `og:` and `twitter:` tags in each page's head: the headshot as `og:image` (with `twitter:card` `summary`), or, with no photo, a card rendered by `python3 tools/make-og-image.py`. `og:description` is the role and affiliation only |
| Search-engine info | The `application/ld+json` block in `index.html` (who the site is about), plus `robots.txt` and `sitemap.xml`. Add any new page to `sitemap.xml` |
| Profile icons | The `.socials` row in the footer of both pages. Extra icons (Bluesky, GitHub, Mastodon, website) are in `snippets/social-icons.html` |
| Email | `python3 tools/encode-email.py you@your.edu`, paste the numbers into `var c = [...]` in both `index.html` and `publications.html` |
| Colors, spacing, type | `index.html` has its own inlined `<style>`; `publications.html` and `404.html` use `css/style.css`. Both define the same custom properties in `:root` (light) and in a `prefers-color-scheme: dark` block, so a palette change goes in **both files and both modes** |

## Conventions

- Publications are newest first. The "All work" list carries a countdown
  (`.pubs__num`) that runs N down to 1. After adding or removing an entry, run
  `python3 tools/check.py --renumber`.
- Each entry has `data-type` (`research`, `review`, `protocol`, or `preprint`)
  and a matching badge (`pubs__tag`, `pubs__tag--review`, `pubs__tag--protocol`,
  `pubs__tag--preprint`). The CSS-only filter chips depend on these.
- The owner's name in an author list is wrapped in `<span class="self">`.
  `<sup>*</sup>` marks equal contribution and `<sup>#</sup>` co-corresponding
  authorship. When co-first authors are not in contribution order, add a
  `.pubs__note` line under the authors ("listed alphabetically", or "can be
  reported in any order"), using the owner's own wording.
- Press links (`News & Views`, `Feature`, `preLights`, and so on) appear only on
  papers that actually have that coverage.
- `404.html` uses absolute paths (`/css/...`) because GitHub Pages serves it at
  any URL depth. Keep them absolute.
- Keep it dependency-free: no frameworks, no CDNs, no trackers. The site makes
  no third-party requests and sets no cookies.

## Rules

- **Never fabricate.** Every title, year, venue, DOI, author position, press
  link, and patent status must come from a real source you actually checked
  (the owner's CV, Crossref, PubMed, ORCID, the publisher's page). If you cannot
  verify something, say so and leave it out, or leave an HTML comment, rather
  than guessing. This is the owner's public scholarly record.
- **When sources disagree, ask.** For a publication's title, venue, and year,
  the publisher's record (via Crossref or PubMed) normally wins over a CV.
  Author markers come from the paper itself. Any disagreement between the CV,
  ORCID, and the publisher goes to the owner as a question, never a silent
  choice.
- **Fail loudly.** If a source is missing or a check fails, stop and report it.
  Don't silently skip an entry.
- **Ask before publishing.** Deploying makes changes public within a minute.
  Commit freely, but confirm with the owner before every deploy. If the repo
  has a `site` remote, the site uses private history (see `deploy-site`): deploy
  with `bash tools/publish.sh`, never by pushing to `site` directly.
- **Look before you claim it works.** After any visual change, run the
  `visual-check` workflow and actually look at the screenshots.
- Keep the design consistent. If you propose a visual change, show a before and
  after and let the owner choose.
