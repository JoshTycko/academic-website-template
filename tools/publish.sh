#!/usr/bin/env bash
# Publish the site with its history kept private (optional setup; see the
# deploy-site workflow, "Keep the history private").
#
#   origin  a PRIVATE repo holding the full history (where you normally push)
#   site    the PUBLIC repo GitHub Pages serves from (USERNAME.github.io)
#
# The public repo only ever holds ONE commit: a snapshot of main's site files,
# without the notes, workflows, and tools listed below. So it shows no history,
# past drafts, or commit emails, and the site doesn't serve internal files.
#
#   bash tools/publish.sh
#
# Only what is committed on main is published.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

# Kept out of the public repo and the live site. LICENSE and the font licenses
# stay in, since they must travel with the code and fonts.
PRIVATE_PATHS=(README.md AGENTS.md CLAUDE.md .claude tools docs snippets pdf/README.md .gitignore)

fail () { echo "ERROR: $*" >&2; exit 1; }

[[ "$(git rev-parse --abbrev-ref HEAD)" == "main" ]] || fail "check out main first."
git diff --quiet && git diff --cached --quiet || fail "uncommitted changes to tracked files. Commit or stash them first."
git remote get-url origin >/dev/null 2>&1 || fail "no 'origin' remote (the private repo)."
git remote get-url site >/dev/null 2>&1 || fail "no 'site' remote (the public GitHub Pages repo)."
[[ "$(git remote get-url origin)" != "$(git remote get-url site)" ]] || fail "'origin' and 'site' point at the same repo."

# If the GitHub CLI is available, confirm origin really is private and site public.
visibility () {  # prints PUBLIC/PRIVATE for a github.com remote, nothing otherwise
  local url slug
  url=$(git remote get-url "$1")
  slug=$(sed -E -n 's#^(https://github\.com/|git@github\.com:)([^/]+/[^/.]+)(\.git)?/?$#\2#p' <<<"$url")
  [[ -n "$slug" ]] && command -v gh >/dev/null && gh repo view "$slug" --json visibility -q .visibility 2>/dev/null || true
}
v=$(visibility origin); [[ -z "$v" || "$v" == "PRIVATE" ]] || fail "'origin' is $v; it must be a private repo."
v=$(visibility site);   [[ -z "$v" || "$v" == "PUBLIC" ]]  || fail "'site' is $v; GitHub Pages on a free plan needs a public repo."

# 1. Back up the full history to the private repo.
git push -q origin main

# 2. Build the public tree: main's files minus PRIVATE_PATHS.
tmp_index=$(mktemp)
trap 'rm -f "$tmp_index"' EXIT
GIT_INDEX_FILE="$tmp_index" git read-tree main
GIT_INDEX_FILE="$tmp_index" git rm -r -q --cached --ignore-unmatch -- "${PRIVATE_PATHS[@]}"
for p in "${PRIVATE_PATHS[@]}"; do
  if GIT_INDEX_FILE="$tmp_index" git ls-files --error-unmatch -- "$p" >/dev/null 2>&1; then
    fail "$p is still in the public tree."
  fi
done
GIT_INDEX_FILE="$tmp_index" git ls-files --error-unmatch index.html >/dev/null 2>&1 || fail "index.html missing from the public tree."
public_tree=$(GIT_INDEX_FILE="$tmp_index" git write-tree)

# 3. Replace the public repo's contents with a single parentless snapshot.
snapshot=$(git commit-tree "$public_tree" -m "Site snapshot")
git push -q --force site "$snapshot:refs/heads/main"
echo "Published $(git rev-parse --short main) as snapshot $(git rev-parse --short "$snapshot")."
echo "GitHub Pages rebuilds in about a minute."
