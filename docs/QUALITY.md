# LaunchLatam quality gates

This repository commits its generated GitHub Pages output in `site/`. The read-only quality workflow checks that published artifact on pull requests and changes to `main`, plus the Cloudflare URL scanner's existing offline tests.

## Run locally

From the repository root, with Python 3.12+ and Node.js 22+:

```bash
python3 -m py_compile build.py content.py tools/og.py tools/check_site.py
python3 tools/check_site.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --check site/assets/scan.js
node --check worker/src/index.js
(cd worker && npm test)
```

No credentials, network calls, Cloudflare account, GitHub token, or deployment commands are needed for these checks.

The isolated validator regression suite creates synthetic HTML, sitemap, assets, robots and manifest files in temporary directories. It verifies both a clean package and intentional failures (absolute and relative broken links, missing assets, wrong canonical, malformed JSON-LD, weak CSP, duplicate or invalid sitemap entries, invalid manifest, encoded traversal, and symlinks pointing outside the site artifact). It does not request external websites or modify the committed build.

## What the checks cover

- Sitemap XML, unique entries, valid last-modified dates, and required locale/scanner pages.
- Every sitemap URL resolves to a committed HTML file, with a non-empty title and language and a matching canonical URL.
- Absolute, document-relative, project-root-relative and protocol-relative same-host links resolve under `site/`; links that navigate outside the project root or symlink outside the artifact are rejected. External sites are never fetched. The validator rejects `javascript:`, `vbscript:` and `file:` links even when HTML character references are used to disguise their schemes; ordinary `mailto:` references remain allowed.
- JSON-LD scripts parse as JSON; each indexed page has a Content Security Policy with the required `object-src` and `base-uri` restrictions and no unprocessed placeholder.
- `robots.txt` points to the sitemap, and the web manifest is valid and points to this GitHub Pages project.
- Browser scanner and Worker JavaScript parse; the Worker's existing `node --test` regression suite completes.
- Every `url-form` exposed by the committed Pages artifact must direct visitor-submitted scan targets exclusively to the explicitly reviewed Cloudflare Worker origin. Missing, altered, duplicate, insecure or credential-bearing destinations fail the read-only artifact gate. Changing the Worker hostname requires a deliberate review and update of the approved constant, rather than a silent deployment. The synthetic regression suite verifies this rule and that the generator's default URL matches it. Ordinary forms without the scan form ID are unaffected.

## Scope and deployment safety

This workflow **does not deploy** the site, invoke real URL scans, test payment provider accounts, or alter customer data. It runs with read-only repository permissions.

The full `build.py` generator is intentionally not run in CI: it relies on externally managed legal Markdown in `/workspace/quiposa/legal` and on build-time dependencies/assets not currently vendored as a portable CI environment. Do not replace legal texts with placeholders or publish auto-generated legal copy simply to make CI pass. A future hermetic build pipeline should use approved, versioned source material and a reproducible dependency manifest.

A passing check validates committed artifacts and offline test cases; it does not establish that the live deployment, third-party checkout, or Cloudflare service is available. Continue manual or separately approved browser, legal, and production checks before deployment.

## GitHub Actions supply-chain controls

The quality workflow pins official checkout, Python and Node setup actions to immutable 40-character commit IDs rather than movable version tags. Its read-only permission scope, disabled credential persistence, unprivileged PR trigger and absence of deployment commands are protected by `tests/test_workflow_security.py`. This reduces the risk of action-reference drift; it is not a substitute for reviewing upstream action updates before updating a pin. All quality checks run on standard GitHub-hosted runners and require no production credentials.
