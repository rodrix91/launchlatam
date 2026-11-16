// T-108 launch QA. Usage: node qa_launch.js local|live
// local: serves /workspace/launchlatam/site under https://rodrix91.github.io/launchlatam/ (real origin, so the Worker CORS check applies).
// GoatCounter is stubbed (events recorded, nothing sent) so QA does not pollute analytics.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const MODE = process.argv[2] || 'local'; const BASE = 'https://rodrix91.github.io/launchlatam'; const SITE = '/workspace/launchlatam/site';
const WORKER = 'https://launchlatam-urlscan.rodrixlabs-launchlatam-cloudflare.workers.dev';
const PAGES = MODE === 'live'
  ? [['es', '/', 'https://www.python.org'], ['pt', '/pt/', 'https://www.debian.org'], ['en', '/en/', 'https://www.w3.org'], ['es-escaneo', '/escaneo/', 'https://www.rust-lang.org']]
  : (process.env.ALT ? [['es', '/', 'https://www.kernel.org'], ['pt', '/pt/', 'https://www.apache.org'], ['en', '/en/', 'https://www.php.net'], ['es-escaneo', '/escaneo/', 'https://www.ruby-lang.org']]
     : [['es', '/', 'https://example.com'], ['pt', '/pt/', 'https://www.iana.org'], ['en', '/en/', 'https://www.wikipedia.org'], ['es-escaneo', '/escaneo/', 'https://www.mozilla.org']]);
const COPY = { es: 'En modo URL, la consulta pasa por nuestro relay', 'es-escaneo': 'En modo URL, la consulta pasa por nuestro relay', pt: 'No modo URL, a consulta passa pelo nosso relay', en: 'In URL mode, the request goes through our relay' };
const MIME = { html: 'text/html; charset=utf-8', js: 'application/javascript', css: 'text/css', svg: 'image/svg+xml', png: 'image/png', xml: 'application/xml', json: 'application/json', webp: 'image/webp', woff2: 'font/woff2', ico: 'image/x-icon', txt: 'text/plain' };
const results = []; const ok = (lang, name, pass, info = '') => { results.push({ lang, name, pass, info }); console.log((pass ? 'PASS' : 'FAIL'), lang, name, info); };
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--headless=new'] });
  for (const [lang, p, target] of PAGES.filter(x => !process.env.ONLY || x[0] === process.env.ONLY)) {
    const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } }); const pg = await ctx.newPage();
    const errs = []; const workerCalls = [];
    pg.on('pageerror', e => errs.push('pageerror ' + e.message)); pg.on('console', m => { if (m.type() === 'error' && !(/Failed to load resource/.test(m.text()) && (m.location().url || '').startsWith(WORKER))) errs.push('console ' + m.text()); });
    // expected: the browser logs "Failed to load resource" for the Worker's own 403/502/429 answers in the error-case tests; anything else counts
    await pg.route('https://gc.zgo.at/**', r => r.fulfill({ contentType: 'application/javascript', body: 'window.__gc=[];window.goatcounter={count:function(o){window.__gc.push(o.path)}};' }));
    await pg.route('https://*.goatcounter.com/**', r => r.fulfill({ status: 204, body: '' }));
    if (MODE === 'local') await pg.route(BASE + '/**', r => {
      let rel = new URL(r.request().url()).pathname.replace(/^\/launchlatam/, ''); if (rel.endsWith('/')) rel += 'index.html';
      const f = path.join(SITE, rel); if (!fs.existsSync(f)) return r.fulfill({ status: 404, body: 'nf' });
      r.fulfill({ status: 200, contentType: MIME[f.split('.').pop()] || 'application/octet-stream', body: fs.readFileSync(f) });
    });
    let mockRL = false;
    await pg.route(WORKER + '/**', async r => { workerCalls.push(r.request().url());
      if (mockRL) return r.fulfill({ status: 429, headers: { 'Access-Control-Allow-Origin': 'https://rodrix91.github.io', 'Content-Type': 'application/json' }, body: '{"ok":false,"error":"rate_limited","retry_after":600}' });
      return r.continue(); });
    await pg.goto(BASE + p, { waitUntil: 'networkidle' });
    ok(lang, 'scanner copy (repo vs URL relay)', (await pg.textContent('#escaneo')).includes(COPY[lang]));
    if (lang === 'es' || lang === 'en') { // repo mode still works (GitHub API, unauthenticated: keep it to 2 pages)
      await pg.fill('#repo', 'david210690/lovable-supabase-mvp-starter'); await pg.click('#scan-form button');
      await pg.waitForFunction(() => !document.getElementById('scan-out').hidden, null, { timeout: 60000 }).catch(() => {});
      const rt = (await pg.textContent('#scan-out')) || ''; ok(lang, 'repo mode scan renders', /\d+\/100|lovable-supabase-mvp-starter/.test(rt), rt.slice(0, 80).replace(/\s+/g, ' '));
      await pg.screenshot({ path: `/workspace/qa-shots/launch-${MODE}-${lang}-repo.png` });
    }
    ok(lang, 'url mode toggle present', await pg.locator('input[name=scanmode][value=url]').count() === 1);
    await pg.check('input[name=scanmode][value=url]');
    ok(lang, 'url form visible after toggle', await pg.isVisible('#url-form') && !(await pg.isVisible('#scan-form')));
    await pg.screenshot({ path: `/workspace/qa-shots/launch-${MODE}-${lang}-form.png` });
    await pg.fill('#appurl', target); await pg.click('#url-form button');
    const consentMsg = (await pg.textContent('#url-status')).trim();
    ok(lang, 'consent required (no Worker call)', consentMsg.length > 0 && workerCalls.length === 0, JSON.stringify(consentMsg));
    await pg.fill('#appurl', 'notaurl'); await pg.check('#url-consent'); await pg.click('#url-form button');
    ok(lang, 'invalid URL rejected client-side', (await pg.textContent('#url-status')).trim().length > 0 && workerCalls.length === 0);
    const run = async (u) => { await pg.fill('#appurl', u); await pg.click('#url-form button'); await pg.waitForFunction(() => !document.querySelector('#url-form button').disabled && !document.getElementById('scan-out').hidden, null, { timeout: 60000 }); return pg.textContent('#scan-out'); };
    const txt = await run(target);
    const host = new URL(target).hostname.replace(/^www\./, '');
    ok(lang, 'result renders (host + score)', txt.includes(host) && /\d+\/100/.test(txt), txt.slice(0, 90).replace(/\s+/g, ' '));
    await pg.screenshot({ path: `/workspace/qa-shots/launch-${MODE}-${lang}-result.png`, fullPage: false });
    for (const [kind, u] of [['blocked', 'http://127.0.0.1'], ['unreachable', 'https://nonexistent-launchlatam-qa-zz9.com']]) {
      await run(u); const c = await pg.getAttribute('#scan-out .ctas', 'data-cta');
      ok(lang, `error card ${kind}`, c === 'url_' + kind, c); await pg.screenshot({ path: `/workspace/qa-shots/launch-${MODE}-${lang}-${kind}.png` });
    }
    mockRL = true; await run('https://example.net'); mockRL = false;
    const c = await pg.getAttribute('#scan-out .ctas', 'data-cta'); ok(lang, 'error card rate_limited (mocked 429)', c === 'url_rate_limited', c);
    await pg.screenshot({ path: `/workspace/qa-shots/launch-${MODE}-${lang}-rate_limited.png` });
    const gc = await pg.evaluate(() => window.__gc || []);
    ok(lang, 'GoatCounter events', gc.filter(x => x === 'url_scan_run').length === 4 && gc.some(x => /^url_scan_result\/(0-49|50-79|80-100)$/.test(x)) && gc.includes('url_scan_result/blocked') && gc.includes('url_scan_result/unreachable') && gc.includes('url_scan_result/rate_limited'), gc.join(','));
    // internal links
    const links = await pg.$$eval('a[href]', as => as.map(a => a.href)); const bad = [];
    for (const l of [...new Set(links)].filter(h => h.startsWith('https://rodrix91.github.io/launchlatam/'))) {
      const u = new URL(l); if (MODE === 'local') { let rel = u.pathname.replace(/^\/launchlatam/, ''); if (rel.endsWith('/')) rel += 'index.html'; if (!fs.existsSync(path.join(SITE, rel))) bad.push(l); }
      else { const r = await ctx.request.get(u.origin + u.pathname); if (r.status() !== 200) bad.push(l + ' ' + r.status()); }
    }
    ok(lang, 'internal links resolve', bad.length === 0, bad.length ? bad.join(' ') : `${new Set(links).size} links`);
    ok(lang, '0 JS/CSP errors', errs.length === 0, errs.join(' | ').slice(0, 300));
    await ctx.close();
  }
  if (MODE === 'live' && !process.env.ONLY) { // real (not mocked) rate limit through the UI: 7 scans of one domain within 10 min -> 7th is rate_limited
    const ctx = await b.newContext(); const pg = await ctx.newPage();
    await pg.route('https://gc.zgo.at/**', r => r.fulfill({ contentType: 'application/javascript', body: 'window.goatcounter={count:function(){}};' }));
    await pg.goto(BASE + '/en/', { waitUntil: 'networkidle' }); await pg.check('input[name=scanmode][value=url]'); await pg.check('#url-consent');
    const seen = [];
    for (let i = 1; i <= 7; i++) { await pg.fill('#appurl', 'https://www.gnu.org'); await pg.click('#url-form button');
      await pg.waitForFunction(() => !document.querySelector('#url-form button').disabled && !document.getElementById('scan-out').hidden, null, { timeout: 60000 });
      seen.push((await pg.getAttribute('#scan-out .ctas', 'data-cta')) || 'result'); }
    ok('en', 'real rate limit (7th scan of same domain)', seen[6] === 'url_rate_limited' && seen.slice(0, 6).every(x => x !== 'url_rate_limited'), seen.join(','));
    await pg.screenshot({ path: '/workspace/qa-shots/launch-live-en-real-rate_limited.png' }); await ctx.close();
  }
  // legal pages
  const LEGAL = [['es', '/terminos/', '16 de noviembre de 2026'], ['es', '/privacidad/', '16 de noviembre de 2026'], ['pt', '/pt/termos/', '16 de novembro de 2026'], ['pt', '/pt/privacidade/', '16 de novembro de 2026'], ['en', '/en/terms/', 'November 16, 2026'], ['en', '/en/privacy/', 'November 16, 2026']];
  for (const [lang, p, d] of LEGAL) {
    const ctx = await b.newContext(); const pg = await ctx.newPage(); const errs = [];
    pg.on('pageerror', e => errs.push(e.message)); pg.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    await pg.route('https://gc.zgo.at/**', r => r.fulfill({ contentType: 'application/javascript', body: 'window.goatcounter={count:function(){}};' }));
    if (MODE === 'local') await pg.route(BASE + '/**', r => { let rel = new URL(r.request().url()).pathname.replace(/^\/launchlatam/, ''); if (rel.endsWith('/')) rel += 'index.html'; const f = path.join(SITE, rel); if (!fs.existsSync(f)) return r.fulfill({ status: 404, body: 'nf' }); r.fulfill({ status: 200, contentType: MIME[f.split('.').pop()] || 'application/octet-stream', body: fs.readFileSync(f) }); });
    const resp = await pg.goto(BASE + p, { waitUntil: 'networkidle' }); const t = await pg.textContent('body');
    ok(lang, `legal ${p} 200 + dated ${d}`, resp.status() === 200 && t.includes(d)); 
    ok(lang, `legal ${p} mentions URL scan`, /URL/.test(t));
    ok(lang, `legal ${p} 0 JS/CSP errors`, errs.length === 0, errs.join('|').slice(0, 200));
    await pg.screenshot({ path: `/workspace/qa-shots/launch-${MODE}-legal-${p.replace(/\//g, '_')}.png` }); await ctx.close();
  }
  await b.close();
  const by = {}; for (const r of results) { by[r.lang] = by[r.lang] || { pass: 0, fail: 0 }; by[r.lang][r.pass ? 'pass' : 'fail']++; }
  console.log('SUMMARY', MODE, JSON.stringify(by)); fs.writeFileSync(`/workspace/qa-shots/launch-${MODE}-results.json`, JSON.stringify(results, null, 1));
})();
