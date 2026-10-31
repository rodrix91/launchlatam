# LaunchLatam

Static site for LaunchLatam — security, local payments and compliance for AI-built apps in LatAm.

- `build.py` + `content.py` generate everything in `site/` (ES at `/`, PT at `/pt/`, EN at `/en/`, blog, legal, sitemap, robots, llms.txt).
- `site/assets/scan.js` is the free scanner: runs in the browser against public GitHub repos (api.github.com + raw.githubusercontent.com). No backend, no secrets.
- Checkout links point to Whop plans (see `W` in build.py).
- Deploy: `./deploy.sh` (builds and force-pushes site/ to gh-pages; Pages serves that branch).
- Local preview: `BASE=http://localhost:8099/launchlatam OUT=/tmp/srv/launchlatam python3 build.py` then serve `/tmp/srv`.
- Tests: `tools/shots.js` (screenshots + overflow check), `tools/scantest.js` (scanner e2e).
- Python 3.12+ required (f-string syntax).

## Blog (ES/PT/EN)
- Posts live in `POSTS` (build.py): `lang` (es|pt|en), `slug`, `tkey`, `date`, `title`, `desc`; body HTML goes in `POST_BODIES[slug]` (content.py).
- Paths: ES `/blog/<slug>/`, PT `/pt/blog/<slug>/`, EN `/en/blog/<slug>/`. Same `tkey` = translations → hreflang (page + sitemap) is generated automatically.
- PT/EN blog indexes list native posts first, then Spanish originals without a translation (marked ES).
