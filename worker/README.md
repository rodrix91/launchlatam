# LaunchLatam URL scan — Level A (passive) · T-108

Cloudflare Worker (plain JS module, free plan only) behind the "URL de la app" mode of the free scanner.
**Status: branch only. Not deployed, not linked from the live site.** Launch needs: Cloudflare account (John),
updated Terms + Privacy (proposals in `/workspace/quiposa/legal-proposals/urlscan-2026-11-16/`) and Rodrigo's OK.

## API
`GET /scan?url=<app url>&consent=1` (also `POST /scan` with JSON or form body; the UI uses GET = no CORS preflight).

- `consent=1` is mandatory (UI checkbox: "I own this app or have permission").
- `Origin` must be in `ALLOWED_ORIGINS` (default `https://rodrix91.github.io`); otherwise 403. CORS echoes only that origin.
- 200 → `{ok:true, target:{host,https}, scanned:{html:1, js, kb, truncated}, score, findings:[{id, sev, ev?, where?}]}`
- Errors → `{ok:false, error}`: `consent_required`/`invalid_url` (400), `blocked_target`/`origin_not_allowed` (403),
  `rate_limited` (429 + `Retry-After`), `unreachable`/`unresolvable`/`timeout`/`too_many_redirects` (502).
- `sev` ∈ critical, high, medium, low, info, ok. `ev` is **masked** (first 6 + last 4 chars; shorter values show at most 4).
  `where` is only the path of the public file where it was seen. Copy (ES/PT/EN) lives in `site/assets/scan.js` (`FU`).

## What it does (and doesn't)
Only `GET`, no cookies, no auth headers, `User-Agent: LaunchLatamScan/1.0 (+https://rodrix91.github.io/launchlatam/)`.
Fetches 1 HTML page + at most 10 same-site JS bundles (`<script src>`, `modulepreload`, and relative chunk imports found
inside those bundles; same registrable domain or a CDN that serves the app's own build such as `*.cloudfront.net`;
third-party libraries like jsDelivr/GTM are skipped). Each file ≤ 2 MB, total ≤ 5 MB, 8 s timeout per request.
Plus one `GET http://<host>/` (no follow) to see whether http redirects to https.
No logins, no form submission, no writes, no probing of paths like `/.env` (that is Level B, not approved).

Checks: HTTPS and http→https; HSTS, CSP, X-Frame-Options/frame-ancestors, X-Content-Type-Options, Referrer-Policy,
Permissions-Policy; in HTML/JS: Supabase URL + JWT role decoding (anon = info, **service_role = critical**),
`sb_secret_` (critical) / `sb_publishable_` (info), Stripe `sk_live_`/`rk_live_` (critical), `sk_test_` (high), `pk_live_` (info),
Mercado Pago `APP_USR-…` access tokens (critical) vs UUID public keys (info), AWS `AKIA` (high), OpenAI `sk-proj-…` (critical),
Anthropic, GitHub `ghp_`/`github_pat_` (critical), Google `AIza` (low: usually public, check restrictions), private keys;
privacy/terms links (also SPA routes in bundles); payment providers (Stripe, Mercado Pago, Pix).

Nothing is stored and nothing is logged: page and bundle text live only in memory during the request and are dropped;
`src/` has no logging calls (a test enforces it). Enable no Workers Logs / Logpush / Tail for this Worker.

## SSRF defences
- Only `http:`/`https:`, no userinfo, **default ports only** (`url.port === ""`), URL ≤ 2048 chars.
- Hostname must be a public DNS name: IP literals (v4/v6) rejected; numeric/hex/octal encodings (`2130706433`, `0x7f.1`,
  `0177.0.0.1`, `127.1`) rejected both on the raw string and after WHATWG parsing; `localhost`, `*.local`, `*.internal`,
  `*.lan`, `*.home.arpa`, `*.corp`, `*.test`, `*.onion`… rejected; wildcard-DNS services (`nip.io`, `sslip.io`, `lvh.me`…) rejected;
  single-label and numeric-TLD hosts rejected.
- Redirects are handled manually (`redirect: "manual"`), max 3, and **every hop is re-validated** with the same rules.
- **Workers cannot resolve DNS before `fetch()`.** As a best-effort extra layer the Worker asks Cloudflare's DoH resolver
  (`cloudflare-dns.com/dns-query`, A + AAAA) and rejects private/reserved/link-local/CGNAT/ULA/mapped answers (and CNAMEs to blocked
  names). This is a time-of-check test (DNS rebinding can still change the answer), so we **also rely on Cloudflare's own
  block of Worker subrequests to private/internal address space**. `DOH_CHECK = "0"` disables it (not recommended).

## Abuse limits
Per isolate fixed window: 10 scans / 10 min per client IP (`CF-Connecting-IP`) and 6 / 10 min per target registrable domain
(`RL_IP_PER_10MIN`, `RL_DOMAIN_PER_10MIN`). Isolates are not global, so for production also add (free plan) one
Cloudflare **WAF rate-limiting rule** on `/scan`, and optionally the KV-based counter (commented out in `wrangler.toml` and `src/index.js`).

## Run locally (no account, no login, no network)
```
npm test                      # node --test, offline fixtures (dev/fixtures.mjs)
ALLOWED_ORIGINS=http://127.0.0.1:8767 node dev/serve.mjs   # real src/index.js under Node; targets are fake fixture apps
URLSCAN_WORKER=http://127.0.0.1:8787 BASE=http://127.0.0.1:8767/launchlatam OUT=/tmp/urlqa/www/launchlatam python3 ../build.py
```
`dev/serve.mjs` injects `env.__fetchForTests`; this cannot be set from `wrangler.toml` (functions aren't bindable), so it never applies in production.

## Deploy (later, by decision of John + OK from Rodrigo — NOT now)
1. John creates the free Cloudflare account; set `name` in `wrangler.toml` (no `account_id` committed; use `CLOUDFLARE_ACCOUNT_ID` env).
2. `npx wrangler deploy` → `https://<name>.<subdomain>.workers.dev`.
3. Set `URLSCAN_WORKER` in `build.py` to that origin (adds it to the page CSP `connect-src` and renders the toggle).
4. Publish updated Terms/Privacy first, then the site.
