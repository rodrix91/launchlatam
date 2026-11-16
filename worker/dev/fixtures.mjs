// Offline fixtures: fake target apps + fake DNS-over-HTTPS, injected as env.__fetchForTests.
// Secret-looking values are assembled at runtime so no literal key pattern lives in the repo.
const b64u = s => Buffer.from(s).toString("base64").replace(/=+$/, "").replace(/\+/g, "-").replace(/\//g, "_");
const jwt = role => b64u('{"alg":"HS256","typ":"JWT"}') + "." + b64u(JSON.stringify({ iss: "supabase", ref: "abcdefghijklmnopqrst", role, iat: 1700000000, exp: 2000000000 })) + "." + "s1gnatureFAKEfixture0123456789abcdef";
const rep = (s, n) => s.repeat(Math.ceil(n / s.length)).slice(0, n);
export const SECRETS = {
  serviceRole: jwt("service_role"),
  anon: jwt("anon"),
  stripeLive: "sk" + "_live_" + rep("FiXtUrE0", 24),
  stripePk: "pk" + "_live_" + rep("PuBlIc00", 24),
  mpToken: "APP" + "_USR-1234567890123456-111222-" + rep("0123456789abcdef", 32) + "-123456789",
  mpPublic: "APP" + "_USR-" + "aaaabbbb-cccc-dddd-eeee-ffff00001111",
  aws: "AK" + "IA" + rep("FIXTURE2", 16),
  github: "gh" + "p_" + rep("FixtureToken", 36),
  google: "AI" + "za" + rep("FixtureKey_", 35),
  openai: "sk-" + "proj-" + rep("FixtureOpenAi", 48),
  sbSecret: "sb_" + "secret_" + rep("FixtureSecret", 32),
};
const SB = "https://abcdefghijklmnopqrst.supabase.co";
const GOOD_HEADERS = {
  "content-type": "text/html; charset=utf-8",
  "strict-transport-security": "max-age=31536000; includeSubDomains",
  "content-security-policy": "default-src 'self'; frame-ancestors 'none'",
  "x-content-type-options": "nosniff",
  "referrer-policy": "strict-origin-when-cross-origin",
  "permissions-policy": "camera=()",
};
const html = (scripts, extra = "") => `<!doctype html><html><head>${scripts.map(s => `<script type="module" crossorigin src="${s}"></script>`).join("")}</head><body><div id="root"></div>${extra}</body></html>`;

// host -> { path -> {status, headers, body} | function }
export const SITES = {
  "app.fixture-dirty.com": {
    "/": { headers: { "content-type": "text/html" }, body: html(["/assets/index-abc.js", "https://cdn.jsdelivr.net/npm/lib.js"]) },
    "/assets/index-abc.js": { headers: { "content-type": "text/javascript" }, body: `const u="${SB}",k="${SECRETS.anon}",admin="${SECRETS.serviceRole}";const s="${SECRETS.stripeLive}";const mp="${SECRETS.mpToken}";import("./chunk-1.js");loadStripe("${SECRETS.stripePk}")` },
    "/assets/chunk-1.js": { headers: { "content-type": "text/javascript" }, body: `const a="${SECRETS.aws}",g="${SECRETS.github}",o="${SECRETS.openai}",x="${SECRETS.sbSecret}",m="${SECRETS.google}";` },
  },
  "www.fixture-clean.com.ar": {
    "/": { headers: GOOD_HEADERS, body: html(["/assets/app-1.js"]) },
    "/assets/app-1.js": { headers: { "content-type": "text/javascript" }, body: `const u="${SB}",k="${SECRETS.anon}";const pk="${SECRETS.mpPublic}";new MercadoPago(pk);const r=[{path:"/privacidad"},{path:"/terminos"}];` },
  },
  "fixture-medium.com.br": {
    "/": { headers: { "content-type": "text/html", "strict-transport-security": "max-age=31536000", "x-content-type-options": "nosniff" }, body: html(["/main.js"], '<a href="/privacidade">Privacidade</a>') },
    "/main.js": { headers: { "content-type": "text/javascript" }, body: `const pix="copia e cola";fetch("https://api.mercadopago.com/v1/payments")` },
  },
  "big.fixture-big.com": {
    "/": { headers: GOOD_HEADERS, body: html(Array.from({ length: 15 }, (_, i) => `/js/${i}.js`)) },
    ...Object.fromEntries(Array.from({ length: 15 }, (_, i) => [`/js/${i}.js`, { headers: { "content-type": "text/javascript" }, body: i === 0 ? "x".repeat(3 * 1024 * 1024) : `var a${i}=1;` }])),
  },
  "loop.fixture-loop.com": { "*": (u) => ({ status: 302, headers: { location: "/r" + (Number(u.pathname.slice(2) || 0) + 1) } }) },
  "go.fixture-redirect.com": { "/": { status: 301, headers: { location: "http://127.0.0.1/admin" } } },
  "go2.fixture-redirect.com": { "/": { status: 302, headers: { location: "https://internal.fixture-private.com/" } } },
  "go3.fixture-redirect.com": { "/": { status: 302, headers: { location: "https://www.fixture-clean.com.ar/" } } },
  "internal.fixture-private.com": { "/": { headers: GOOD_HEADERS, body: "<p>secret intranet</p>" } },
  "slow.fixture-slow.com": { "/": "hang" },
};
// http:// behaviour per host: redirect to https or serve plain
const HTTP_REDIRECT = new Set(["www.fixture-clean.com.ar", "fixture-medium.com.br", "big.fixture-big.com"]);
const DNS = { "internal.fixture-private.com": "10.0.0.5", "cdn.jsdelivr.net": "151.101.1.229" };

export function makeFetch(log = []) {
  return async function fakeFetch(input, init = {}) {
    const u = new URL(typeof input === "string" ? input : input.url);
    const headers = new Headers(init.headers || {});
    log.push({ method: init.method || "GET", url: u.href, ua: headers.get("User-Agent"), cookie: headers.get("Cookie"), redirect: init.redirect });
    if (u.hostname === "cloudflare-dns.com") {
      const name = u.searchParams.get("name"), type = u.searchParams.get("type");
      const known = DNS[name] || (SITES[name] ? "93.184.216.34" : null);
      const ans = type === "A" && known ? [{ name, type: 1, data: known }] : [];
      return new Response(JSON.stringify({ Status: ans.length || type === "AAAA" ? 0 : 3, Answer: ans }), { headers: { "content-type": "application/dns-json" } });
    }
    const site = SITES[u.hostname];
    if (!site) throw new TypeError("fetch failed");
    if (u.protocol === "http:") {
      if (HTTP_REDIRECT.has(u.hostname)) return new Response(null, { status: 301, headers: { location: "https://" + u.hostname + u.pathname } });
      if (u.hostname !== "app.fixture-dirty.com") throw new TypeError("fetch failed");
    }
    let r = site[u.pathname] || site["*"];
    if (typeof r === "function") r = r(u);
    if (r === "hang") return new Promise((_, rej) => init.signal && init.signal.addEventListener("abort", () => { const e = new Error("aborted"); e.name = "AbortError"; rej(e); }));
    if (!r) return new Response("not found", { status: 404, headers: { "content-type": "text/plain" } });
    return new Response(r.body ?? null, { status: r.status || 200, headers: r.headers || {} });
  };
}
