#!/usr/bin/env bash
# Build and publish site/ to the gh-pages branch (GitHub Pages, branch mode).
set -euo pipefail
cd "$(dirname "$0")"
python3 build.py
tmp=$(mktemp -d); cp -r site/. "$tmp"/
cd "$tmp" && git init -q -b gh-pages && git add -A && git -c user.name=rodrix91 -c user.email=rodrix91@users.noreply.github.com commit -qm "deploy $(date -u +%FT%TZ)"
git push -qf https://github.com/rodrix91/launchlatam.git gh-pages
echo deployed
