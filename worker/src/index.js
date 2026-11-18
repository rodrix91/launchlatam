// LaunchLatam URL scan — Level A (passive). Cloudflare Worker, plain JS module, free-plan features only.
// GET|POST /scan?url=<https://app>&consent=1  ->  JSON report with masked evidence.
// Never stores anything, never logs content (this file intentionally has no logging calls).
import {
  UA, LIMITS, checkTarget, checkHostname, isPrivateIPv4, isPrivateIPv6, isIPv4, extractScriptUrls, extractChunkUrls,
  isSameSiteScript, registrableDomain, scanText, signals, mergeSignals, checkHeaders, buildFindings, score, RateLimiter, ipKey,
} from "./lib.js";

const DEFAULT_ORIGINS = "https://rodrix91.github.io";
// Fixed-window limits per isolate (defaults: 10 scans / 10 min per client IP, 6 / 10 min per target domain).
const limiters = new Map();
function limiter(kind, n) { const k = kind + n; if (!limiters.has(k)) limiters.set(k, new RateLimiter(n, 10 * 60 * 1000)); return limiters.get(k); }

// In-memory limiter object (no ctx.storage calls: nothing is persisted).
export class Limiter {
  constructor() { this.l = new Map(); }
  get(kind, n) { const k = kind + n; if (!this.l.has(k)) this.l.set(k, new RateLimiter(n, 10 * 60 * 1000)); return this.l.get(k); }
  async fetch(request) {
    const b = await request.json();
    const ip = this.get("ip", +b.nIp || 10).hit(String(b.ip));
    const d = ip.ok ? this.get("d", +b.nD || 6).hit(String(b.d)) : { ok: true, retryAfter: 0 };
    return new Response(JSON.stringify({ ip, d }), { headers: { "Content-Type": "application/json" } });
  }
}

export default {
  async fetch(request, env, ctx) {
    try { return await handle(request, env || {}); }
    catch { return json({ ok: false, error: "internal" }, 500, null); }
  },
};

class ScanError extends Error { constructor(code, status = 502) { super(code); this.code = code; this.status = status; } }

const MAX_POST_BYTES = 4096;

// Request.text() buffers the entire caller-controlled body before slicing it.
// Reject oversized POSTs as they stream in, with a bound on decoded text too.
async function readBoundedPostBody(request) {
  const lengthHint = request.headers.get("Content-Length");
  if (lengthHint && /^\\d+$/.test(lengthHint) && Number(lengthHint) > MAX_POST_BYTES) {
    throw new ScanError("request_too_large", 413);
  }
  if (!request.body) return "";
  const reader = request.body.getReader();
  const decoder = new TextDecoder("utf-8", { fatal: true });
  const fragments = [];
  let used = 0;
  try {
    for (;;) {
      const { value, done } = await reader.read();
      if (done) return fragments.join("") + decoder.decode();
      used += value.byteLength;
      if (used > MAX_POST_BYTES) throw new ScanError("request_too_large", 413);
      fragments.push(decoder.decode(value, { stream: true }));
    }
  } catch (error) {
    try { await reader.cancel(); } catch {}
    throw error;
  } finally {
    reader.releaseLock();
  }
}

function allowedOrigins(env) { return String(env.ALLOWED_ORIGINS || DEFAULT_ORIGINS).split(",").map(s => s.trim()).filter(Boolean); }

function corsHeaders(origin) {
  return origin ? { "Access-Control-Allow-Origin": origin, "Access-Control-Allow-Methods": "GET, POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type", "Access-Control-Max-Age": "600", "Vary": "Origin" } : { "Vary": "Origin" };
}
function json(obj, status, origin, extra) {
  return new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer", ...corsHeaders(origin), ...(extra || {}) } });
}

export async function handle(request, env) {
  const url = new URL(request.url);
  const origin = request.headers.get("Origin");
  const okOrigin = origin && allowedOrigins(env).includes(origin) ? origin : null;
  if (url.pathname !== "/scan") return json({ ok: false, error: "not_found" }, 404, okOrigin);
  if (request.method === "OPTIONS") return new Response(null, { status: okOrigin ? 204 : 403, headers: corsHeaders(okOrigin) });
  if (request.method !== "GET" && request.method !== "POST") return json({ ok: false, error: "method_not_allowed" }, 405, okOrigin);
  if (!okOrigin) return json({ ok: false, error: "origin_not_allowed" }, 403, null);

  const p = Object.fromEntries(url.searchParams);
  if (request.method === "POST") {
    const ct = request.headers.get("Content-Type") || "";
    try {
      const body = await readBoundedPostBody(request);
      if (ct.includes("application/json")) Object.assign(p, JSON.parse(body || "{}"));
      else Object.assign(p, Object.fromEntries(new URLSearchParams(body)));
    } catch (error) {
      if (error instanceof ScanError) return json({ ok: false, error: error.code }, error.status, okOrigin);
      return json({ ok: false, error: "invalid_url" }, 400, okOrigin);
    }
  }
  if (String(p.consent) !== "1") return json({ ok: false, error: "consent_required" }, 400, okOrigin);
  const t = checkTarget(String(p.url || ""));
  if (!t.ok) return json({ ok: false, error: t.reason }, t.reason === "blocked_target" ? 403 : 400, okOrigin);

  const ip = ipKey(request.headers.get("CF-Connecting-IP") || "unknown");
  const dom = registrableDomain(t.url.hostname);
  let rl1 = limiter("ip", +env.RL_IP_PER_10MIN || 10).hit("ip:" + ip);
  let rl2 = limiter("d", +env.RL_DOMAIN_PER_10MIN || 6).hit("d:" + dom);
  // Cross-isolate limit: one in-memory Durable Object (free plan). Counters live only in its memory, never in storage,
  // so they reset if the object is evicted after idling. The per-isolate limiter above stays as a fallback.
  if (rl1.ok && rl2.ok && env.LIMITER) {
    try {
      const stub = env.LIMITER.get(env.LIMITER.idFromName("global"));
      const r = await (await stub.fetch("https://limiter/hit", { method: "POST", body: JSON.stringify({ ip: "ip:" + ip, d: "d:" + dom, nIp: +env.RL_IP_PER_10MIN || 10, nD: +env.RL_DOMAIN_PER_10MIN || 6 }) })).json();
      rl1 = r.ip; rl2 = r.d;
    } catch { /* limiter unavailable: keep per-isolate result */ }
  }
  // Optional cross-isolate limit with a KV namespace (free tier: 1k writes/day). Uncomment together with the binding in wrangler.toml.
  // if (env.RL_KV) { const k = "ip:" + ip + ":" + Math.floor(Date.now() / 600000); const n = +(await env.RL_KV.get(k) || 0) + 1; await env.RL_KV.put(k, String(n), { expirationTtl: 900 }); if (n > 20) return json({ ok: false, error: "rate_limited" }, 429, okOrigin, { "Retry-After": "600" }); }
  if (!rl1.ok || !rl2.ok) return json({ ok: false, error: "rate_limited", retry_after: Math.max(rl1.ok ? 0 : rl1.retryAfter, rl2.ok ? 0 : rl2.retryAfter) }, 429, okOrigin, { "Retry-After": String(Math.max(rl1.retryAfter, rl2.retryAfter)) });

  try {
    const report = await scan(t.url, env);
    return json({ ok: true, ...report }, 200, okOrigin);
  } catch (e) {
    const code = e instanceof ScanError ? e.code : (e && e.name === "AbortError" ? "timeout" : "unreachable");
    return json({ ok: false, error: code }, e instanceof ScanError ? e.status : 502, okOrigin);
  }
}

// ---------- network (all target traffic goes through here) ----------
function fetcher(env) { return typeof env.__fetchForTests === "function" ? env.__fetchForTests : fetch; }

async function timedFetch(env, href, init) {
  const ac = new AbortController();
  const timer = setTimeout(() => ac.abort(), LIMITS.timeoutMs);
  try {
    const res = await fetcher(env)(href, { ...init, signal: ac.signal });
    return { res, done: () => clearTimeout(timer), signal: ac.signal };
  } catch (e) { clearTimeout(timer); throw e; }
}

const dnsCache = new Map();
// Workers cannot resolve DNS before fetch(), so we ask Cloudflare's DoH resolver and reject private answers.
// This narrows (not closes) DNS-rebinding; Cloudflare's own egress also refuses private destinations.
async function dnsCheck(env, hostname) {
  if (env.DOH_CHECK === "0") return;
  if (dnsCache.has(hostname)) { if (!dnsCache.get(hostname)) throw new ScanError("blocked_target", 403); return; }
  let any = false, bad = false;
  for (const type of ["A", "AAAA"]) {
    const { res, done } = await timedFetch(env, "https://cloudflare-dns.com/dns-query?name=" + encodeURIComponent(hostname) + "&type=" + type, { headers: { Accept: "application/dns-json" } });
    let data;
    try { data = await res.json(); } catch { data = {}; } finally { done(); }
    for (const a of data.Answer || []) {
      if (a.type === 1) { any = true; if (!isIPv4(a.data) || isPrivateIPv4(a.data)) bad = true; }
      else if (a.type === 28) { any = true; if (isPrivateIPv6(a.data)) bad = true; }
      else if (a.type === 5 && !checkHostname(String(a.data)).ok) bad = true;
    }
  }
  if (!any) throw new ScanError("unresolvable", 502);
  dnsCache.set(hostname, !bad);
  if (dnsCache.size > 2000) dnsCache.clear();
  if (bad) throw new ScanError("blocked_target", 403);
}

async function readCapped(res, cap, budget, signal) {
  if (!res.body) return { text: "", truncated: false };
  const reader = res.body.getReader();
  const dec = new TextDecoder();
  let text = "", n = 0, truncated = false;
  for (;;) {
    if (signal && signal.aborted) { truncated = true; break; }
    const { value, done } = await reader.read();
    if (done) break;
    const room = Math.min(cap - n, LIMITS.maxTotalBytes - budget.bytes);
    if (value.byteLength > room) { if (room > 0) { text += dec.decode(value.subarray(0, room), { stream: true }); n += room; budget.bytes += room; } truncated = true; try { await reader.cancel(); } catch {} break; }
    n += value.byteLength; budget.bytes += value.byteLength;
    text += dec.decode(value, { stream: true });
  }
  return { text: text + dec.decode(), truncated };
}

// GET with manual redirects; every hop is re-validated (scheme, port, hostname, DoH). Max 3 redirects.
async function getFollow(env, startUrl, budget, accept) {
  let href = startUrl.href;
  for (let hop = 0; hop <= LIMITS.maxRedirects; hop++) {
    const t = checkTarget(href);
    if (!t.ok) throw new ScanError("blocked_target", 403);
    await dnsCheck(env, t.url.hostname);
    budget.requests++;
    const r = await timedFetch(env, t.url.href, { method: "GET", redirect: "manual", headers: { "User-Agent": UA, "Accept": accept } });
    const st = r.res.status;
    if (st >= 300 && st < 400 && r.res.headers.get("Location")) {
      const loc = r.res.headers.get("Location");
      try { await r.res.body?.cancel(); } catch {}
      r.done();
      try { href = new URL(loc, t.url).href; } catch { throw new ScanError("unreachable"); }
      continue;
    }
    return { ...r, url: t.url, hops: hop };
  }
  throw new ScanError("too_many_redirects");
}

async function httpRedirectsToHttps(env, host, budget) {
  try {
    budget.requests++;
    const r = await timedFetch(env, "http://" + host + "/", { method: "GET", redirect: "manual", headers: { "User-Agent": UA } });
    try { await r.res.body?.cancel(); } catch {}
    r.done();
    const loc = r.res.headers.get("Location") || "";
    if (r.res.status >= 300 && r.res.status < 400 && loc) {
      const u = new URL(loc, "http://" + host + "/");
      return u.protocol === "https:" && registrableDomain(u.hostname) === registrableDomain(host);
    }
    return false;
  } catch { return null; } // unknown (port 80 closed or timeout): no finding either way
}

export async function scan(target, env) {
  const budget = { bytes: 0, requests: 0 };
  const page = await getFollow(env, target, budget, "text/html,application/xhtml+xml");
  const finalUrl = page.url;
  const isHttps = finalUrl.protocol === "https:";
  const headerFindings = checkHeaders(page.res.headers, isHttps);
  let hits = [], sig = { legal: false, stripe: false, mercadopago: false, pix: false }, jsCount = 0, truncated = false;
  const extra = [];
  if (page.res.status >= 400) extra.push({ id: "http_status", sev: "info", ev: String(page.res.status) });
  const ctype = page.res.headers.get("Content-Type") || "";
  let html = "";
  if (page.res.status < 400 && /html/i.test(ctype)) {
    const r = await readCapped(page.res, LIMITS.maxFileBytes, budget, page.signal);
    html = r.text; truncated = truncated || r.truncated;
  } else { try { await page.res.body?.cancel(); } catch {} }
  page.done();

  let httpRedirects = null;
  if (target.protocol === "http:") httpRedirects = isHttps; // the redirect chain we just followed
  else if (isHttps) httpRedirects = await httpRedirectsToHttps(env, finalUrl.hostname, budget);

  if (html) {
    hits.push(...scanText(html, finalUrl.href));
    sig = mergeSignals(sig, signals(html));
    const queue = extractScriptUrls(html, finalUrl.href).filter(u => isSameSiteScript(u, finalUrl.href));
    html = ""; // drop page content as soon as possible
    const seen = new Set();
    while (queue.length && jsCount < LIMITS.maxJs && budget.bytes < LIMITS.maxTotalBytes) {
      const u = queue.shift();
      if (seen.has(u)) continue;
      seen.add(u);
      const t = checkTarget(u);
      if (!t.ok) continue;
      let r;
      try { r = await getFollow(env, t.url, budget, "application/javascript,text/javascript,*/*;q=0.1"); } catch { continue; }
      if (r.res.status !== 200 || !isSameSiteScript(r.url.href, finalUrl.href)) { try { await r.res.body?.cancel(); } catch {} r.done(); continue; }
      const body = await readCapped(r.res, LIMITS.maxFileBytes, budget, r.signal).catch(() => ({ text: "", truncated: true }));
      r.done();
      jsCount++;
      truncated = truncated || body.truncated;
      hits.push(...scanText(body.text, r.url.href));
      sig = mergeSignals(sig, signals(body.text));
      for (const c of extractChunkUrls(body.text, r.url.href)) if (!seen.has(c) && isSameSiteScript(c, finalUrl.href) && queue.length < 50) queue.push(c);
    }
  }
  const findings = buildFindings({ https: isHttps, httpRedirects, headerFindings, hits, sig }).concat(extra);
  return {
    target: { host: finalUrl.hostname, https: isHttps },
    scanned: { html: 1, js: jsCount, kb: Math.round(budget.bytes / 1024), truncated },
    score: score(findings),
    findings,
  };
}
