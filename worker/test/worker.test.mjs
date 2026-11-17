// node --test test/   (offline: all network is faked by dev/fixtures.mjs)
import test from "node:test";
import assert from "node:assert/strict";
import { checkTarget, isPrivateIPv4, isPrivateIPv6, mask, scanText, jwtRole, checkHeaders, extractScriptUrls, extractChunkUrls, isSameSiteScript, registrableDomain, RateLimiter, signals, buildFindings, score, ipKey } from "../src/lib.js";
import worker, { handle } from "../src/index.js";
import { makeFetch, SECRETS } from "../dev/fixtures.mjs";

const ORIGIN = "https://rodrix91.github.io";
let ipN = 0;
async function call(target, { consent = "1", origin = ORIGIN, method = "GET", log = [], ip, env = {} } = {}) {
  const q = new URLSearchParams({ url: target, ...(consent ? { consent } : {}) });
  const req = new Request("https://w.example.workers.dev/scan?" + q, { method, headers: { ...(origin ? { Origin: origin } : {}), "CF-Connecting-IP": ip || "198.51.100." + (++ipN % 250) } });
  const res = await worker.fetch(req, { ALLOWED_ORIGINS: ORIGIN, __fetchForTests: makeFetch(log), ...env });
  const text = await res.text();
  return { status: res.status, body: JSON.parse(text), text, headers: res.headers };
}

test("SSRF: rejects IP literals, numeric encodings, private names, ports, schemes, userinfo", () => {
  const bad = [
    "http://127.0.0.1/", "http://localhost/", "http://LOCALHOST./", "https://foo.localhost/", "http://2130706433/", "http://0x7f000001/", "http://0x7f.0.0.1/",
    "http://017700000001/", "http://0177.0.0.1/", "http://127.1/", "http://0/", "http://[::1]/", "http://[fd00::1]/", "http://[::ffff:127.0.0.1]/",
    "http://10.0.0.1/", "http://169.254.169.254/latest/meta-data/", "http://100.64.0.1/", "http://192.168.1.1/", "http://172.16.0.1/", "http://8.8.8.8/",
    "https://printer.local/", "http://metadata.google.internal/", "https://intranet/", "https://app.corp/", "https://x.home.arpa/", "https://a.test/",
    "https://127.0.0.1.nip.io/", "https://10-0-0-1.sslip.io/", "https://lvh.me/",
    "https://mi-app.com:8443/", "http://mi-app.com:443/", "https://mi-app.com:80/", "ftp://mi-app.com/", "file:///etc/passwd", "javascript:alert(1)", "gopher://x.com/",
    "https://user:pass@mi-app.com/", "https://evil.com\\@good.com/", "", "https://" + "a".repeat(2100) + ".com/", "https://app.123/", "https://xn--tienda-n3a.com/",
  ];
  for (const u of bad) assert.equal(checkTarget(u).ok, false, u);
  for (const u of ["https://mi-app.lovable.app", "mi-tienda.com.ar", "http://shop.example-app.com.br/path?q=1", "https://xn--bcher-kva.de/", "https://bücher.de/", "https://www.fixture-clean.com.ar/#x"]) {
    const r = checkTarget(u); assert.equal(r.ok, true, u); assert.equal(r.url.hash, "");
  }
  assert.equal(checkTarget("mi-tienda.com.ar").url.protocol, "https:");
});

test("private ranges v4/v6", () => {
  for (const ip of ["10.1.2.3", "127.0.0.1", "0.0.0.0", "100.100.0.1", "169.254.1.1", "172.31.255.255", "192.168.0.1", "192.0.0.8", "198.18.0.1", "224.0.0.1", "255.255.255.255", "203.0.113.7"]) assert.equal(isPrivateIPv4(ip), true, ip);
  for (const ip of ["93.184.216.34", "8.8.8.8", "172.32.0.1", "100.128.0.1"]) assert.equal(isPrivateIPv4(ip), false, ip);
  for (const ip of ["::1", "::", "fd12:3456::1", "fc00::1", "fe80::1", "ff02::1", "::ffff:10.0.0.1", "2001:db8::1", "2002:a00:1::1", "64:ff9b::10.0.0.1"]) assert.equal(isPrivateIPv6(ip), true, ip);
  for (const ip of ["2606:4700:4700::1111", "2a00:1450:4001:80b::200e"]) assert.equal(isPrivateIPv6(ip), false, ip);
});

test("masking keeps first 6 + last 4 only", () => {
  const fake = "sk" + "_live_" + "ABCDEFGHIJKLMNOPQRST1234"; assert.equal(mask(fake), "sk_liv…1234");
  assert.equal(mask("short"), "…");
  assert.equal(mask("abcdefghij"), "abcd…");
  const m = mask(SECRETS.serviceRole);
  assert.ok(m.length <= 11 && !SECRETS.serviceRole.includes(m.replace("…", "")));
});

test("detectors on fixtures: severity + masked evidence, never raw secrets", () => {
  const blob = Object.values(SECRETS).join(" ; ") + ' const u="https://abcdefghijklmnopqrst.supabase.co"';
  const hits = scanText(blob, "https://app.x.com/assets/index.js");
  const by = id => hits.find(h => h.id === id);
  assert.equal(jwtRole(SECRETS.serviceRole), "service_role");
  assert.equal(by("supabase_service_role").sev, "critical");
  assert.equal(by("supabase_anon_key").sev, "info");
  assert.equal(by("supabase_url").sev, "info");
  assert.equal(by("stripe_secret").sev, "critical");
  assert.equal(by("stripe_publishable").sev, "info");
  assert.equal(by("mp_access_token").sev, "critical");
  assert.equal(by("mp_public_key").sev, "info");
  assert.equal(by("aws_access_key").sev, "high");
  assert.equal(by("github_token").sev, "critical");
  assert.equal(by("openai_key").sev, "critical");
  assert.equal(by("supabase_secret_key").sev, "critical");
  assert.equal(by("google_api_key").sev, "low");
  assert.equal(hits.filter(h => h.id === "mp_access_token").length, 1, "MP public key must not count as access token");
  const out = JSON.stringify(hits);
  for (const s of Object.values(SECRETS)) assert.ok(!out.includes(s), "raw secret leaked");
  for (const h of hits) assert.ok(h.ev.length <= 30, h.id);
  assert.equal(hits[0].where, "/assets/index.js");
  // no false positives on ordinary minified code
  assert.deepEqual(scanText('function sk(){return "sk-learn"};var task_live_1=2;const AIzb=1;', "https://a.com/x.js"), []);
});

test("signals: legal links, payment providers", () => {
  assert.equal(signals('<a href="/privacidad">x</a>').legal, true);
  assert.equal(signals('routes:[{path:"/terms"}]').legal, true);
  assert.equal(signals("<p>hola</p>").legal, false);
  const s = signals('import{loadStripe}from"@stripe/stripe-js";sdk.mercadopago.com;"Pix copia e cola"');
  assert.equal(s.stripe && s.mercadopago && s.pix, true);
});

test("headers check", () => {
  const none = checkHeaders(new Headers({}), true).map(x => x.id);
  assert.deepEqual(none, ["hsts_missing", "csp_missing", "frame_missing", "nosniff_missing", "referrer_missing", "permissions_missing"]);
  const good = checkHeaders(new Headers({ "strict-transport-security": "max-age=63072000", "content-security-policy": "default-src 'self'; frame-ancestors 'self'", "x-content-type-options": "nosniff", "referrer-policy": "no-referrer", "permissions-policy": "camera=()" }), true);
  assert.deepEqual(good, []);
  assert.deepEqual(checkHeaders(new Headers({ "strict-transport-security": "max-age=300", "content-security-policy": "script-src 'unsafe-eval'", "x-frame-options": "DENY", "x-content-type-options": "nosniff", "referrer-policy": "x", "permissions-policy": "x" }), true).map(x => x.id), ["hsts_short", "csp_weak"]);
});

test("script discovery is same-site only", () => {
  const h = '<script src="/a.js"></script><script src="https://cdn.app.com/b.js"></script><script src="https://www.googletagmanager.com/gtm.js"></script><link rel="modulepreload" href="/c.js"><link rel="preload" href="/f.woff2" as="font">';
  const all = extractScriptUrls(h, "https://www.app.com/");
  assert.deepEqual(all, ["https://www.app.com/a.js", "https://cdn.app.com/b.js", "https://www.googletagmanager.com/gtm.js", "https://www.app.com/c.js"]);
  assert.deepEqual(all.filter(u => isSameSiteScript(u, "https://www.app.com/")), ["https://www.app.com/a.js", "https://cdn.app.com/b.js", "https://www.app.com/c.js"]);
  assert.equal(registrableDomain("mi-app.lovable.app"), "mi-app.lovable.app");
  assert.equal(isSameSiteScript("https://otra.lovable.app/x.js", "https://mi-app.lovable.app/"), false);
  assert.equal(registrableDomain("www.tienda.com.ar"), "tienda.com.ar");
  assert.deepEqual(extractChunkUrls('import("./chunk-9.js");n="/assets/v.js"', "https://a.com/assets/i.js"), ["https://a.com/assets/chunk-9.js", "https://a.com/assets/v.js"]);
});

test("ipKey: IPv4 as is, IPv6 by /64", () => {
  assert.equal(ipKey("198.51.100.7"), "198.51.100.7");
  assert.equal(ipKey("2a09:bac1:1f80:12::3:1"), "2a09:bac1:1f80:12::/64");
  assert.equal(ipKey("2a09:BAC1:1f80:0012:aaaa:bbbb:cccc:dddd"), "2a09:bac1:1f80:12::/64");
  assert.equal(ipKey("2001:db8::1"), "2001:db8:0:0::/64");
  assert.equal(ipKey("::1"), "0:0:0:0::/64");
  assert.equal(ipKey(""), "unknown");
});

test("rate limiter fixed window", () => {
  let t = 0; const rl = new RateLimiter(2, 1000, () => t);
  assert.equal(rl.hit("a").ok, true); assert.equal(rl.hit("a").ok, true); assert.equal(rl.hit("a").ok, false);
  assert.equal(rl.hit("b").ok, true);
  t = 1000; assert.equal(rl.hit("a").ok, true);
});

test("score and findings", () => {
  const f = buildFindings({ https: true, httpRedirects: true, headerFindings: [], hits: [], sig: { legal: true, stripe: false, mercadopago: true, pix: false } });
  assert.equal(score(f), 100);
  assert.ok(f.every(x => x.sev === "ok"));
});

// ---------- Worker end to end (fake network) ----------
test("worker: consent, origin, method, path", async () => {
  assert.equal((await call("https://www.fixture-clean.com.ar/", { consent: "" })).body.error, "consent_required");
  const o = await call("https://www.fixture-clean.com.ar/", { origin: "https://evil.example.org" });
  assert.equal(o.status, 403); assert.equal(o.body.error, "origin_not_allowed"); assert.equal(o.headers.get("Access-Control-Allow-Origin"), null);
  assert.equal((await call("https://www.fixture-clean.com.ar/", { origin: null })).status, 403);
  const pre = await worker.fetch(new Request("https://w.dev/scan", { method: "OPTIONS", headers: { Origin: ORIGIN } }), { ALLOWED_ORIGINS: ORIGIN });
  assert.equal(pre.status, 204); assert.equal(pre.headers.get("Access-Control-Allow-Origin"), ORIGIN);
  const del = await worker.fetch(new Request("https://w.dev/scan?url=x", { method: "DELETE", headers: { Origin: ORIGIN } }), { ALLOWED_ORIGINS: ORIGIN });
  assert.equal(del.status, 405);
  assert.equal((await call("http://169.254.169.254/latest/meta-data/")).body.error, "blocked_target");
});

test("worker: dirty app -> critical findings, masked, only GET, UA set, no cookies", async () => {
  const log = [];
  const r = await call("https://app.fixture-dirty.com/", { log });
  assert.equal(r.status, 200);
  const ids = r.body.findings.map(f => f.id);
  for (const id of ["supabase_service_role", "stripe_secret", "mp_access_token", "aws_access_key", "github_token", "openai_key", "supabase_secret_key", "csp_missing", "hsts_missing", "no_http_redirect", "pay_stripe_only", "legal_missing"]) assert.ok(ids.includes(id), id);
  assert.equal(r.body.findings[0].sev, "critical");
  assert.equal(r.body.scanned.js, 2, "index + imported chunk, third-party CDN skipped");
  for (const s of Object.values(SECRETS)) assert.ok(!r.text.includes(s), "raw secret in response");
  assert.ok(!r.text.includes("const u="), "no page content in response");
  const target = log.filter(l => !l.url.startsWith("https://cloudflare-dns.com"));
  assert.ok(target.every(l => l.method === "GET" && l.redirect === "manual" && l.ua.startsWith("LaunchLatamScan/1.0") && !l.cookie));
  assert.ok(!target.some(l => l.url.includes("jsdelivr")));
});

test("worker: clean app", async () => {
  const r = await call("https://www.fixture-clean.com.ar/");
  assert.equal(r.status, 200);
  assert.ok(r.body.findings.every(f => f.sev === "ok" || f.sev === "info"), JSON.stringify(r.body.findings));
  assert.ok(r.body.findings.some(f => f.id === "https_ok") && r.body.findings.some(f => f.id === "pay_local") && r.body.findings.some(f => f.id === "legal_ok"));
  assert.equal(r.body.score, 100);
});

test("worker: redirects re-validated (private IP literal, private DNS, loop), http->https", async () => {
  assert.equal((await call("https://go.fixture-redirect.com/")).body.error, "blocked_target");
  assert.equal((await call("https://go2.fixture-redirect.com/")).body.error, "blocked_target");
  assert.equal((await call("https://internal.fixture-private.com/")).body.error, "blocked_target");
  const loopLog = [];
  assert.equal((await call("https://loop.fixture-loop.com/", { log: loopLog })).body.error, "too_many_redirects");
  assert.equal(loopLog.filter(l => l.url.startsWith("https://loop.")).length, 4, "1 + 3 redirects max");
  const ok = await call("https://go3.fixture-redirect.com/");
  assert.equal(ok.status, 200); assert.equal(ok.body.target.host, "www.fixture-clean.com.ar");
  const http = await call("http://www.fixture-clean.com.ar/");
  assert.ok(http.body.findings.some(f => f.id === "https_ok"));
  assert.equal((await call("https://nope.fixture-unknown.com/")).body.error, "unresolvable");
});

test("worker: caps — max 10 JS, 2 MB per file", async () => {
  const log = [];
  const r = await call("https://big.fixture-big.com/", { log });
  assert.equal(r.body.scanned.js, 10);
  assert.equal(r.body.scanned.truncated, true);
  assert.ok(r.body.scanned.kb <= 5 * 1024);
  assert.equal(log.filter(l => l.url.includes("/js/")).length, 10);
});

test("worker: rate limit per target domain", async () => {
  let last;
  for (let i = 0; i < 7; i++) last = await call("https://fixture-medium.com.br/");
  assert.equal(last.status, 429); assert.equal(last.body.error, "rate_limited"); assert.ok(+last.headers.get("Retry-After") > 0);
});

test("worker: cross-isolate limiter object (per IP and per domain, memory only)", async () => {
  const { Limiter } = await import("../src/index.js");
  const mkNs = () => { const obj = new Limiter(); return { idFromName: (n) => n, get: () => ({ fetch: (u, init) => obj.fetch(new Request(u, init)) }) }; };
  const env = { LIMITER: mkNs(), RL_IP_PER_10MIN: "2" };
  assert.notEqual((await call("https://app.fixture-dirty.com/", { ip: "203.0.113.9", env })).status, 429);
  assert.notEqual((await call("https://app.fixture-dirty.com/", { ip: "203.0.113.9", env })).status, 429);
  const third = await call("https://app.fixture-dirty.com/", { ip: "203.0.113.9", env });
  assert.equal(third.status, 429); assert.equal(third.body.error, "rate_limited");
  const envD = { LIMITER: mkNs(), RL_DOMAIN_PER_10MIN: "1" };
  assert.notEqual((await call("https://go3.fixture-redirect.com/", { env: envD })).status, 429);
  assert.equal((await call("https://go3.fixture-redirect.com/", { env: envD })).body.error, "rate_limited");
  const broken = { LIMITER: { idFromName: () => { throw new Error("x"); } } };
  assert.notEqual((await call("https://big.fixture-big.com/", { env: broken })).status, 429);
  assert.ok(!/storage/.test(Limiter.toString()));
});

test("worker: timeout after 8 s", { timeout: 15000 }, async () => {
  const t0 = Date.now();
  const r = await call("https://slow.fixture-slow.com/");
  assert.equal(r.body.error, "timeout");
  assert.ok(Date.now() - t0 >= 7900);
});

test("worker source never logs", async () => {
  const fs = await import("node:fs");
  for (const f of ["src/index.js", "src/lib.js"]) assert.ok(!/console\./.test(fs.readFileSync(new URL("../" + f, import.meta.url), "utf8")), f);
});
