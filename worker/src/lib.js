// LaunchLatam URL scan (Level A) — pure helpers, no I/O. Imported by the Worker and by the node tests.
// Rules: never return or log full secrets or page content. Evidence is masked (first 6 + last 4).

export const UA = "LaunchLatamScan/1.0 (+https://rodrix91.github.io/launchlatam/)";
export const LIMITS = Object.freeze({
  timeoutMs: 8000,      // per request
  maxRedirects: 3,
  maxJs: 10,            // same-site JS bundles
  maxFileBytes: 2 * 1024 * 1024,
  maxTotalBytes: 5 * 1024 * 1024,
  maxUrlLength: 2048,
});

// ---------- SSRF guard ----------
const BLOCKED_SUFFIXES = [
  "localhost", "local", "internal", "intranet", "lan", "home", "corp", "private", "localdomain",
  "home.arpa", "arpa", "test", "example", "invalid", "onion", "alt",
];
// Public wildcard-DNS services that resolve to embedded/private IPs.
const BLOCKED_DOMAINS = ["nip.io", "sslip.io", "xip.io", "traefik.me", "localtest.me", "lvh.me", "vcap.me", "lacolhost.com", "fbi.com"];
// Host strings that a resolver/URL parser may treat as an IPv4 address (decimal, hex, octal, short forms).
const NUMERIC_HOST = /^(0x[0-9a-f]*|\d+)(\.(0x[0-9a-f]*|\d+)){0,3}\.?$/i;

export function isIPv4(h) { return /^\d{1,3}(\.\d{1,3}){3}$/.test(h) && h.split(".").every(o => +o <= 255); }
export function isIPv6Literal(h) { return h.startsWith("[") || h.includes(":"); }

// True if an IPv4 is NOT publicly routable (private, loopback, link-local, CGNAT, reserved, multicast...).
export function isPrivateIPv4(ip) {
  if (!isIPv4(ip)) return true;
  const [a, b, c] = ip.split(".").map(Number);
  return a === 0 || a === 10 || a === 127 || a >= 224 ||
    (a === 100 && b >= 64 && b <= 127) ||          // CGNAT 100.64/10
    (a === 169 && b === 254) ||                     // link-local / cloud metadata
    (a === 172 && b >= 16 && b <= 31) ||
    (a === 192 && b === 168) ||
    (a === 192 && b === 0 && (c === 0 || c === 2)) || // IETF / TEST-NET-1
    (a === 192 && b === 88 && c === 99) ||
    (a === 198 && (b === 18 || b === 19)) ||        // benchmarking
    (a === 198 && b === 51 && c === 100) ||
    (a === 203 && b === 0 && c === 113);
}

// True if an IPv6 is NOT publicly routable. Only 2000::/3 global unicast counts as public (minus doc/special ranges).
export function isPrivateIPv6(ip) {
  let h = String(ip).toLowerCase().replace(/^\[|\]$/g, "").split("%")[0];
  const v4 = h.match(/(\d+\.\d+\.\d+\.\d+)$/);
  if (v4) return true; // ::ffff:a.b.c.d, ::a.b.c.d, 64:ff9b::a.b.c.d — mapped/translated: never allowed
  const first = parseInt((h.split(":")[0] || "0"), 16) || 0;
  if ((first & 0xe000) !== 0x2000) return true; // ::1, ::, fc00::/7 ULA, fe80::/10, ff00::/8, ...
  if (h.startsWith("2001:db8") || h.startsWith("2001:0db8")) return true; // documentation
  if (/^2001:0{0,4}:/.test(h) || h.startsWith("2001::")) return true;      // Teredo
  if (h.startsWith("2002:")) return true;                                   // 6to4 (embeds IPv4)
  return false;
}

function rawHost(input) {
  const m = String(input).trim().match(/^[a-z][a-z0-9+.-]*:\/\/([^/?#]*)/i);
  if (!m) return "";
  return m[1].replace(/^.*@/, "").replace(/:\d*$/, "").toLowerCase();
}

// Validate a target URL string. Returns {ok:true,url} or {ok:false,reason}.
export function checkTarget(input) {
  if (typeof input !== "string" || !input.trim()) return { ok: false, reason: "invalid_url" };
  let s = input.trim();
  if (s.length > LIMITS.maxUrlLength) return { ok: false, reason: "invalid_url" };
  if (!/^[a-z][a-z0-9+.-]*:\/\//i.test(s)) s = "https://" + s; // "mi-app.com" -> https
  if (/[\u0000-\u001f\\]/.test(s)) return { ok: false, reason: "invalid_url" };
  const raw = rawHost(s);
  if (raw && (NUMERIC_HOST.test(raw) || raw.startsWith("["))) return { ok: false, reason: "blocked_target" };
  let u;
  try { u = new URL(s); } catch { return { ok: false, reason: "invalid_url" }; }
  if (u.protocol !== "https:" && u.protocol !== "http:") return { ok: false, reason: "invalid_url" };
  if (u.username || u.password) return { ok: false, reason: "invalid_url" };
  if (u.port !== "") return { ok: false, reason: "blocked_target" }; // only default 80/443
  const r = checkHostname(u.hostname);
  if (!r.ok) return r;
  u.hash = "";
  return { ok: true, url: u };
}

export function checkHostname(hostname) {
  let h = String(hostname || "").toLowerCase();
  if (h.endsWith(".")) h = h.slice(0, -1);
  if (!h || h.length > 253) return { ok: false, reason: "invalid_url" };
  if (isIPv6Literal(h) || isIPv4(h) || NUMERIC_HOST.test(h)) return { ok: false, reason: "blocked_target" };
  const labels = h.split(".");
  if (labels.length < 2) return { ok: false, reason: "blocked_target" }; // "localhost", "intranet"
  if (!labels.every(l => /^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$/.test(l))) return { ok: false, reason: "invalid_url" };
  const tld = labels[labels.length - 1];
  if (!/^(?:[a-z]{2,63}|xn--[a-z0-9-]{2,59})$/.test(tld)) return { ok: false, reason: "blocked_target" };
  for (const suf of BLOCKED_SUFFIXES) if (h === suf || h.endsWith("." + suf)) return { ok: false, reason: "blocked_target" };
  for (const d of BLOCKED_DOMAINS) if (h === d || h.endsWith("." + d)) return { ok: false, reason: "blocked_target" };
  // Labels that are pure hex/octal/decimal IPv4 fragments in front of a blocked-looking host (e.g. "0x7f.1") are caught above;
  // hostnames embedding a dashed/dotted IPv4 (127-0-0-1.example.com) are resolved and checked via DoH in the Worker.
  return { ok: true, hostname: h };
}

// ---------- registrable domain (small built-in list instead of the full PSL) ----------
const MULTI_SUFFIX = new Set([
  "com.ar", "net.ar", "org.ar", "gob.ar", "com.br", "net.br", "org.br", "gov.br", "com.bo", "net.bo", "org.bo", "gob.bo",
  "com.py", "net.py", "org.py", "gov.py", "com.mx", "org.mx", "gob.mx", "com.co", "com.pe", "com.uy", "com.ec", "co.uk", "org.uk",
  "com.au", "co.nz", "co.jp", "com.cl", "com.ve",
  // hosting platforms where every customer gets its own subdomain (PSL "private" section)
  "lovable.app", "lovableproject.com", "vercel.app", "netlify.app", "pages.dev", "workers.dev", "github.io", "web.app",
  "firebaseapp.com", "replit.app", "repl.co", "onrender.com", "herokuapp.com", "fly.dev", "bolt.new", "stackblitz.io",
  "supabase.co", "glitch.me", "surge.sh", "azurewebsites.net", "cloudfront.net", "amplifyapp.com", "railway.app", "up.railway.app",
]);
export function registrableDomain(host) {
  const labels = String(host).toLowerCase().replace(/\.$/, "").split(".");
  for (let n = 3; n >= 2; n--) {
    if (labels.length > n && MULTI_SUFFIX.has(labels.slice(-n).join("."))) return labels.slice(-(n + 1)).join(".");
  }
  return labels.slice(-2).join(".");
}
// CDNs that commonly serve an app's OWN build output (not third-party libraries).
const APP_CDN = [/\.cloudfront\.net$/, /\.azureedge\.net$/, /\.b-cdn\.net$/, /\.vercel-storage\.com$/, /\.r2\.dev$/];
export function isSameSiteScript(scriptUrl, pageUrl) {
  let s, p;
  try { s = new URL(scriptUrl); p = new URL(pageUrl); } catch { return false; }
  if (s.protocol !== "https:" && s.protocol !== "http:") return false;
  if (registrableDomain(s.hostname) === registrableDomain(p.hostname)) return true;
  return APP_CDN.some(re => re.test(s.hostname));
}

// ---------- HTML parsing (regex-based, enough for script src + links) ----------
export function extractScriptUrls(html, pageUrl) {
  const out = [];
  const re = /<script\b[^>]*\bsrc\s*=\s*["']?([^"'\s>]+)/gi;
  const re2 = /<link\b[^>]*\brel\s*=\s*["']?(?:modulepreload|preload)["']?[^>]*>/gi;
  let m;
  while ((m = re.exec(html))) push(m[1]);
  while ((m = re2.exec(html))) {
    const tag = m[0];
    if (/\brel\s*=\s*["']?preload/i.test(tag) && !/\bas\s*=\s*["']?script/i.test(tag)) continue;
    const h = tag.match(/\bhref\s*=\s*["']?([^"'\s>]+)/i);
    if (h) push(h[1]);
  }
  function push(src) {
    try {
      const u = new URL(src.replace(/&amp;/g, "&"), pageUrl);
      u.hash = "";
      if (!out.includes(u.href)) out.push(u.href);
    } catch { /* ignore */ }
  }
  return out;
}
// Relative chunk imports inside a bundle (Vite/webpack): "./index-abc.js", "/assets/x.js"
export function extractChunkUrls(js, jsUrl) {
  const out = [];
  const re = /["'`]((?:\.{1,2}\/|\/)[A-Za-z0-9_\-./]+?\.m?js)["'`]/g;
  let m, n = 0;
  while ((m = re.exec(js)) && n < 200) {
    n++;
    try { const u = new URL(m[1], jsUrl); if (!out.includes(u.href)) out.push(u.href); } catch { /* ignore */ }
  }
  return out;
}

// ---------- masking ----------
export function mask(s) {
  s = String(s || "");
  if (s.length >= 20) return s.slice(0, 6) + "…" + s.slice(-4);
  if (s.length >= 8) return s.slice(0, 4) + "…";
  return "…";
}

function b64urlDecode(p) {
  p = p.replace(/-/g, "+").replace(/_/g, "/");
  p += "===".slice((p.length + 3) % 4);
  try { return typeof atob === "function" ? atob(p) : Buffer.from(p, "base64").toString("binary"); } catch { return ""; }
}
export function jwtRole(jwt) {
  const parts = String(jwt).split(".");
  if (parts.length !== 3) return null;
  try { const o = JSON.parse(b64urlDecode(parts[1])); return typeof o.role === "string" ? o.role : null; } catch { return null; }
}

// ---------- detectors over public JS/HTML text ----------
// Each: id, sev, re (global). Order matters for de-dup (more specific first).
export const DETECTORS = [
  { id: "stripe_secret", sev: "critical", re: /\b(?:sk|rk)_live_[0-9a-zA-Z]{16,}/g },
  { id: "stripe_test_secret", sev: "high", re: /\bsk_test_[0-9a-zA-Z]{16,}/g },
  { id: "stripe_publishable", sev: "info", re: /\bpk_live_[0-9a-zA-Z]{16,}/g },
  { id: "mp_access_token", sev: "critical", re: /\bAPP_USR-\d{10,20}-\d{6}-[a-f0-9]{32}-\d{6,12}\b/g },
  { id: "mp_test_access_token", sev: "high", re: /\bTEST-\d{10,20}-\d{6}-[a-f0-9]{32}-\d{6,12}\b/g },
  { id: "mp_public_key", sev: "info", re: /\b(?:APP_USR|TEST)-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b/g },
  { id: "supabase_secret_key", sev: "critical", re: /\bsb_secret_[A-Za-z0-9_-]{20,}/g },
  { id: "supabase_publishable_key", sev: "info", re: /\bsb_publishable_[A-Za-z0-9_-]{20,}/g },
  { id: "aws_access_key", sev: "high", re: /\b(?:AKIA|ASIA)[0-9A-Z]{16}\b/g },
  { id: "anthropic_key", sev: "critical", re: /\bsk-ant-[A-Za-z0-9_-]{20,}/g },
  { id: "openai_key", sev: "critical", re: /\bsk-(?:proj-|svcacct-|admin-)[A-Za-z0-9_-]{40,}|\bsk-[A-Za-z0-9]{20}T3BlbkFJ[A-Za-z0-9]{20}|\bsk-[A-Za-z0-9]{48}\b/g },
  { id: "github_token", sev: "critical", re: /\bgh[pousr]_[A-Za-z0-9]{36}\b|\bgithub_pat_[A-Za-z0-9_]{60,}/g },
  { id: "google_api_key", sev: "low", re: /\bAIza[0-9A-Za-z_-]{35}\b/g },
  { id: "private_key", sev: "critical", re: /-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----/g },
];
const JWT_RE = /\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}/g;
const SUPABASE_URL_RE = /https:\/\/([a-z0-9]{20})\.supabase\.co\b/g;

// Scan one text blob. Returns an array of raw hits {id, sev, ev(masked), where}. Never keeps the raw value.
export function scanText(text, where) {
  const hits = [];
  const w = shortWhere(where);
  for (const d of DETECTORS) {
    d.re.lastIndex = 0;
    let m, n = 0;
    while ((m = d.re.exec(text)) && n < 5) { n++; hits.push({ id: d.id, sev: d.sev, ev: d.id === "private_key" ? "-----BEGIN…KEY-----" : mask(m[0]), where: w }); }
  }
  JWT_RE.lastIndex = 0;
  let m, n = 0;
  while ((m = JWT_RE.exec(text)) && n < 20) {
    n++;
    const role = jwtRole(m[0]);
    if (role === "service_role") hits.push({ id: "supabase_service_role", sev: "critical", ev: mask(m[0]), where: w });
    else if (role === "anon") hits.push({ id: "supabase_anon_key", sev: "info", ev: mask(m[0]), where: w });
  }
  SUPABASE_URL_RE.lastIndex = 0;
  n = 0;
  while ((m = SUPABASE_URL_RE.exec(text)) && n < 3) { n++; hits.push({ id: "supabase_url", sev: "info", ev: mask(m[1]) + ".supabase.co", where: w }); }
  return hits;
}
function shortWhere(where) {
  try { const u = new URL(where); const p = u.pathname || "/"; return p.length > 80 ? "…" + p.slice(-79) : p; } catch { return ""; }
}

// Presence signals (no evidence kept, just booleans)
export function signals(text) {
  return {
    legal: /href\s*=\s*["'][^"']*(privac|terms|termin|termos|legal|aviso-de-privacidad)[^"']*["']/i.test(text) ||
      /["'`]\/(privacy|privacy-policy|privacidad|privacidade|politica-de-privacidad|terms|terms-of-service|terminos|termos|legal)\/?["'`]/i.test(text),
    stripe: /js\.stripe\.com|\bpk_(live|test)_[0-9a-zA-Z]{8,}|@stripe\/stripe-js|loadStripe\(/i.test(text),
    mercadopago: /sdk\.mercadopago\.com|mercadopago|mercado-pago|\b(APP_USR|TEST)-[a-f0-9]{8}-/i.test(text),
    pix: /\bpix\b|copia e cola|brcode/i.test(text),
  };
}
export function mergeSignals(a, b) { const o = {}; for (const k of Object.keys(a)) o[k] = a[k] || b[k]; return o; }

// ---------- headers ----------
function hget(h, k) { return typeof h.get === "function" ? h.get(k) : h[k.toLowerCase()]; }
export function checkHeaders(h, isHttps) {
  const f = [];
  const hsts = hget(h, "strict-transport-security");
  const csp = hget(h, "content-security-policy");
  const xfo = hget(h, "x-frame-options");
  if (isHttps) {
    if (!hsts) f.push({ id: "hsts_missing", sev: "medium" });
    else { const ma = +((hsts.match(/max-age\s*=\s*(\d+)/i) || [])[1] || 0); if (ma < 15552000) f.push({ id: "hsts_short", sev: "low" }); }
  }
  if (!csp) f.push({ id: "csp_missing", sev: "medium" });
  else if (/unsafe-eval/.test(csp) || /script-src[^;]*\*(?![.\w])/.test(csp)) f.push({ id: "csp_weak", sev: "low" });
  if (!xfo && !(csp && /frame-ancestors/i.test(csp))) f.push({ id: "frame_missing", sev: "low" });
  if (!/nosniff/i.test(hget(h, "x-content-type-options") || "")) f.push({ id: "nosniff_missing", sev: "low" });
  if (!hget(h, "referrer-policy")) f.push({ id: "referrer_missing", sev: "low" });
  if (!hget(h, "permissions-policy")) f.push({ id: "permissions_missing", sev: "info" });
  return f;
}

// ---------- final report ----------
const SEV_ORDER = { critical: 0, high: 1, medium: 2, low: 3, info: 4, ok: 5 };
export function buildFindings({ https, httpRedirects, headerFindings, hits, sig }) {
  const f = [];
  if (!https) f.push({ id: "no_https", sev: "high" });
  else if (httpRedirects === false) f.push({ id: "no_http_redirect", sev: "medium" });
  else if (httpRedirects === true) f.push({ id: "https_ok", sev: "ok" });
  f.push(...headerFindings);
  const seen = new Set();
  for (const h of hits) {
    const k = h.id + "|" + h.ev;
    if (seen.has(k)) continue;
    seen.add(k);
    f.push(h);
  }
  // Supabase anon key alone is public by design: keep a single info line, the advice is about RLS.
  const pays = [];
  if (sig.mercadopago) pays.push("mercadopago");
  if (sig.pix) pays.push("pix");
  if (sig.stripe) pays.push("stripe");
  if (sig.mercadopago || sig.pix) f.push({ id: "pay_local", sev: "ok", ev: pays.join(", ") });
  else if (sig.stripe) f.push({ id: "pay_stripe_only", sev: "medium", ev: "stripe" });
  else f.push({ id: "pay_none", sev: "info" });
  f.push(sig.legal ? { id: "legal_ok", sev: "ok" } : { id: "legal_missing", sev: "medium" });
  // cap per id to keep the payload small
  const per = {};
  const capped = f.filter(x => (per[x.id] = (per[x.id] || 0) + 1) <= 3);
  capped.sort((a, b) => SEV_ORDER[a.sev] - SEV_ORDER[b.sev]);
  return capped;
}
export function score(findings) {
  const w = { critical: 30, high: 15, medium: 6, low: 2, info: 0, ok: 0 };
  return Math.max(0, findings.reduce((s, x) => s - (w[x.sev] || 0), 100));
}

// ---------- rate limiting (fixed window, per isolate) ----------
// Rate-limit key for a client IP: IPv4 as is, IPv6 by its /64 prefix (one host usually owns a whole /64 and rotates inside it).
export function ipKey(ip) {
  ip = String(ip || "unknown").trim().toLowerCase();
  if (!ip.includes(":")) return ip;
  const [h, t = ""] = ip.split("::");
  const head = h ? h.split(":") : [], tail = ip.includes("::") ? (t ? t.split(":") : []) : [];
  const full = ip.includes("::") ? [...head, ...Array(Math.max(0, 8 - head.length - tail.length)).fill("0"), ...tail] : head;
  return full.slice(0, 4).map(x => (parseInt(x, 16) || 0).toString(16)).join(":") + "::/64";
}
export class RateLimiter {
  constructor(limit, windowMs, now = () => Date.now()) { this.limit = limit; this.windowMs = windowMs; this.now = now; this.m = new Map(); }
  hit(key) {
    const t = this.now();
    let e = this.m.get(key);
    if (!e || t - e.start >= this.windowMs) { e = { start: t, n: 0 }; this.m.set(key, e); }
    e.n++;
    if (this.m.size > 5000) for (const [k, v] of this.m) if (t - v.start >= this.windowMs) this.m.delete(k);
    return { ok: e.n <= this.limit, retryAfter: Math.ceil((e.start + this.windowMs - t) / 1000) };
  }
}
