---
name: deploy-site
description: Publish this website for free on GitHub Pages, and optionally put it on a custom domain (DNS records, HTTPS). Use for "put my site online", "deploy", "publish my website", "use my own domain", or when a push isn't showing up live.
---

# Deploy on GitHub Pages

Publishing is public and outward-facing. Confirm with the owner before creating
a repo, pushing, or changing any setting. Explain each step in plain words.

## Prerequisites

- A GitHub account. Check `gh auth status`. If the GitHub CLI isn't installed or
  logged in, guide the owner through `gh auth login` (they run it themselves;
  never handle their password or token).
- Before the first push, run `python3 tools/check.py --strict` and the
  **visual-check** workflow.

## 1. Pick the address

- **`USERNAME.github.io`** (recommended): name the repository exactly
  `USERNAME.github.io` and the site serves at `https://USERNAME.github.io/`.
- **Any other repo name** serves at `https://USERNAME.github.io/REPO/`. Root
  pages work, but `404.html` uses absolute paths (`/css/...`) that assume the
  site is at the domain root, so its styling breaks under `/REPO/`. Prefer the
  first option or a custom domain.

GitHub Pages is free for **public** repositories. A private repository needs a
paid GitHub plan.

## 2. Create the repo and push

If this folder came from "Use this template" on GitHub, it already has a remote.
Otherwise:

```bash
gh repo create USERNAME.github.io --public --source . --remote origin --push
```

## 3. Turn on Pages

```bash
gh api -X POST repos/USERNAME/USERNAME.github.io/pages -f "source[branch]=main" -f "source[path]=/"
```

A 409 response means Pages is already on. Watch the build with
`gh api repos/USERNAME/USERNAME.github.io/pages/builds/latest`, then fetch the
live URL and confirm the owner's name is in the page. The first build takes a
minute or two.

From then on, **`git push` is the whole deploy.**

## 3b. Optional: tell Google about the site

Suggest the owner add the site to Google Search Console
(<https://search.google.com/search-console>), verify ownership (a DNS `TXT`
record for a custom domain, or an HTML file for `github.io`), and submit
`sitemap.xml`. That is the only way to see whether Google has indexed the site
and to request re-indexing after a move. The owner does this in their own
Google account; never handle their credentials.

## 4. Optional: custom domain

The owner buys a domain from any registrar. Then:

1. **DNS first**, at the registrar:
   - Apex (`example.com`): four `A` records to `185.199.108.153`,
     `185.199.109.153`, `185.199.110.153`, `185.199.111.153`. For IPv6, also
     add `AAAA` records to `2606:50c0:8000::153`, `2606:50c0:8001::153`,
     `2606:50c0:8002::153`, `2606:50c0:8003::153`.
   - `www`: a `CNAME` to `USERNAME.github.io`.
   - **Leave `MX` and other existing records alone.** They may carry the
     owner's email.
   - Check against GitHub's current docs ("Managing a custom domain for your
     GitHub Pages site"), since these addresses rarely change but can.
2. **Bind the domain:**
   `gh api -X PUT repos/USERNAME/USERNAME.github.io/pages -f cname=example.com`.
   This commits a `CNAME` file to the repo, so `git pull` afterwards, and never
   delete that file.
3. **Wait for the certificate**, then enforce HTTPS in a **separate** call (the
   two can't be combined, because HTTPS needs the certificate to exist first):
   `gh api -X PUT repos/USERNAME/USERNAME.github.io/pages -F https_enforced=true`.
   It can take up to an hour to appear.
4. Replace the old address with the new domain everywhere it appears:
   `index.html` (canonical, `og:url`, `og:image`, and the structured data),
   `publications.html`, `robots.txt`, and `sitemap.xml`. Then run
   `python3 tools/check.py`, which fails if any of them still disagree.
5. Recommend that the owner verify the domain in their GitHub account settings
   (Pages → Verified domains). This stops anyone else from claiming it.

Expect one failed Pages build at the moment the domain is set, from the
auto-commit that writes `CNAME`; the next build succeeds.

## Troubleshooting

- Change not live: check the latest build status (above), then hard-refresh.
  GitHub's CDN can serve a stale copy for a few minutes.
- 404 at the root: the repo name or Pages source branch is wrong.
- Fonts missing: the `fonts/` folder wasn't committed.
