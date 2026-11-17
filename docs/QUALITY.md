# LaunchLatam quality gates

This repository commits its generated GitHub Pages output in `site/`. The read-only quality workflow checks that published artifact on pull requests and changes to `main`, plus the Cloudflare URL scanner's existing offline tests.

## Run locally

From the repository root, with Python 3.12+ and Node.js 22+:

```bash
python3 -m py_compile build.py content.py tools/og.py tools/check_site.py
python3 tools/check_site.py
node --check site/assets/scan.js
node --check worker/src/index.js
(cd worker && npm test)
```

No credentials, network calls, Cloudflare account, GitHub token, or deployment commands are needed for these checks.

## What the checks cover

- Sitemap XML, unique entries, valid last-modified dates, and required locale/scanner pages.
- Every sitemap URL resolves to a committed HTML file, with a non-empty title and language and a matching canonical URL.
- Local links and assets referenced in published HTML resolve under `site/`. Off-site links are intentionally not fetched.
- JSON-LD scripts parse as JSON; each indexed page has a Content Security Policy with the required `object-src` and `base-uri` restrictions and no unprocessed placeholder.
- `robots.txt` points to the sitemap, and the web manifest is valid and points to this GitHub Pages project.
- Browser scanner and Worker JavaScript parse; the Worker's existing `node --test` regression suite completes.

## Scope and deployment safety

This workflow **does not deploy** the site, invoke real URL scans, test payment provider accounts, or alter customer data. It runs with read-only repository permissions.

The full `build.py` generator is intentionally not run in CI: it relies on externally managed legal Markdown in `/workspace/quiposa/legal` and on build-time dependencies/assets not currently vendored as a portable CI environment. Do not replace legal texts with placeholders or publish auto-generated legal copy simply to make CI pass. A future hermetic build pipeline should use approved, versioned source material and a reproducible dependency manifest.

A passing check validates committed artifacts and offline test cases; it does not establish that the live deployment, third-party checkout, or Cloudflare service is available. Continue manual or separately approved browser, legal, and production checks before deployment.
