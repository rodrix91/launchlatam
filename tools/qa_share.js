// T-111 QA: shareable report + README badge. Usage: node qa_share.js local|live
// local: serves ./site under the real origin. GoatCounter stubbed (events recorded, nothing sent).
// GitHub + Worker are mocked with deterministic findings (incl. fake secrets) in local mode; live mode also runs real scans.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const MODE = process.argv[2] || 'local'; const BASE = 'https://rodrix91.github.io/launchlatam'; const SITE = path.join(__dirname, '..', 'site');
const WORKER = 'https://launchlatam-urlscan.rodrixlabs-launchlatam-cloudflare.workers.dev';
const FIX = 'https://whop.com/checkout/plan_zaTKde6gNjQM2';
const L = {
  es: { p: '/escaneo/', disc: 'Chequeo automático, no auditoría.', badge: 'Revisado con LaunchLatam', bR: 'Copiar informe', bB: 'Copiar insignia', scan: BASE + '/escaneo/?ref=badge', h: 'Informe de LaunchLatam', fix: 'Cómo corregirlo', real: 'https://www.python.org' },
  pt: { p: '/pt/', disc: 'Verificação automática, não auditoria.', badge: 'Revisado com LaunchLatam', bR: 'Copiar relatório', bB: 'Copiar selo', scan: BASE + '/pt/?ref=badge#escaneo', h: 'Relatório do LaunchLatam', fix: 'Como corrigir', real: 'https://www.debian.org' },
  en: { p: '/en/', disc: 'Automated check, not an audit.', badge: 'Reviewed with LaunchLatam', bR: 'Copy report', bB: 'Copy badge', scan: BASE + '/en/?ref=badge#escaneo', h: 'LaunchLatam report', fix: 'How to fix', real: 'https://www.w3.org' },
};
// fake secrets (match scanner patterns, never real)
const FAKE_SK = 'sk_live_' + 'QAFAKE0000000000000000000000';
const b64 = o => Buffer.from(JSON.stringify(o)).toString('base64url');
const FAKE_JWT = b64({ alg: 'HS256', typ: 'JWT' }) + '.' + b64({ role: 'service_role', iss: 'qa-fake' }) + '.QAFAKESIGNATURE0000000000';
const RAW_TOKEN = 'QAUNMASKEDTOKEN1234567890abcdefXYZ';
const MIME = { html: 'text/html; charset=utf-8', js: 'application/javascript', css: 'text/css', svg: 'image/svg+xml', png: 'image/png', xml: 'application/xml', json: 'application/json', woff2: 'font/woff2', txt: 'text/plain' };
const results = []; const ok = (lang, name, pass, info = '') => { results.push({ lang, name, pass: !!pass, info }); console.log((pass ? 'PASS' : 'FAIL'), lang, name, String(info).slice(0, 160)); };
const MOCK_URL = { ok: true, target: { host: 'qa-app.example' }, scanned: { js: 3 }, findings: [
  { id: 'stripe_secret', sev: 'critical', ev: 'sk_liv…QAFK', where: '/assets/index-qa.js' },
  { id: 'openai_key', sev: 'critical', ev: RAW_TOKEN, where: '/assets/app.js' },
  { id: 'csp_missing', sev: 'medium' }, { id: 'hsts_missing', sev: 'medium' }, { id: 'referrer_missing', sev: 'low' },
  { id: 'supabase_anon_key', sev: 'info', ev: 'eyJhbG…abcd', where: '/assets/index-qa.js' }, { id: 'https_ok', sev: 'ok' }] };
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--headless=new'] });
  const fixUrl = FIX + '?ref=report';
  for (const lang of Object.keys(L).filter(x => !process.env.ONLY || x === process.env.ONLY)) {
    const c = L[lang];
    for (const mode of ['repo', 'url']) {
      const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
      await ctx.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: 'https://rodrix91.github.io' });
      const pg = await ctx.newPage(); const errs = []; const ext = [];
      pg.on('pageerror', e => errs.push('pageerror ' + e.message)); pg.on('console', m => { if (m.type() === 'error') errs.push('console ' + m.text()); });
      pg.on('request', r => { const u = r.url(); if (!/^https:\/\/(rodrix91\.github\.io|api\.github\.com|raw\.githubusercontent\.com|gc\.zgo\.at|launchlatam\.goatcounter\.com)\//.test(u) && !u.startsWith(WORKER)) ext.push(u); });
      await pg.route('https://gc.zgo.at/**', r => r.fulfill({ contentType: 'application/javascript', body: 'window.__gc=[];window.goatcounter={count:function(o){window.__gc.push(o.path)}};' }));
      await pg.route('https://*.goatcounter.com/**', r => r.fulfill({ status: 204, body: '' }));
      if (MODE === 'local') {
        await pg.route(BASE + '/**', r => { let rel = new URL(r.request().url()).pathname.replace(/^\/launchlatam/, ''); if (rel.endsWith('/')) rel += 'index.html'; const f = path.join(SITE, rel); if (!fs.existsSync(f)) return r.fulfill({ status: 404, body: 'nf' }); r.fulfill({ status: 200, contentType: MIME[f.split('.').pop()] || 'application/octet-stream', body: fs.readFileSync(f) }); });
        await pg.route('https://api.github.com/**', r => { const u = r.request().url(); const h = { 'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json' };
          if (/\/git\/trees\//.test(u)) return r.fulfill({ headers: h, body: JSON.stringify({ tree: ['.env', 'src/lib/supabase.ts', 'supabase/migrations/001_init.sql', 'package.json'].map(p => ({ type: 'blob', path: p })) }) });
          return r.fulfill({ headers: h, body: JSON.stringify({ default_branch: 'main' }) }); });
        await pg.route('https://raw.githubusercontent.com/**', r => { const u = r.request().url(); const h = { 'Access-Control-Allow-Origin': '*' };
          let body = '{}'; if (u.endsWith('/.env')) body = 'STRIPE=' + FAKE_SK; else if (u.endsWith('supabase.ts')) body = 'const k="' + FAKE_JWT + '";const s="' + FAKE_SK + '";';
          else if (u.endsWith('.sql')) body = 'create table public.profiles (id uuid);\ncreate policy p on profiles using (true);';
          return r.fulfill({ headers: h, body }); });
        await pg.route(WORKER + '/**', r => r.fulfill({ headers: { 'Access-Control-Allow-Origin': 'https://rodrix91.github.io', 'Content-Type': 'application/json' }, body: JSON.stringify(MOCK_URL) }));
      }
      await pg.goto(BASE + c.p, { waitUntil: 'networkidle' });
      ok(lang, `${mode}: no share buttons before a result`, await pg.locator('[data-share]').count() === 0);
      if (mode === 'repo') { await pg.fill('#repo', MODE === 'local' ? 'qa-owner/qa-app' : 'david210690/lovable-supabase-mvp-starter'); await pg.click('#scan-form button'); }
      else { await pg.check('input[name=scanmode][value=url]'); await pg.fill('#appurl', MODE === 'local' ? 'https://qa-app.example' : c.real); await pg.check('#url-consent'); await pg.click('#url-form button'); }
      await pg.waitForFunction(() => !document.getElementById('scan-out').hidden && document.querySelector('#scan-out [data-share]'), null, { timeout: 60000 }).catch(() => {});
      const bR = pg.locator('[data-share=report]'), bB = pg.locator('[data-share=badge]');
      ok(lang, `${mode}: buttons visible after result`, await bR.isVisible() && await bB.isVisible() && (await bR.textContent()) === c.bR && (await bB.textContent()) === c.bB, `${await bR.textContent().catch(() => '')} | ${await bB.textContent().catch(() => '')}`);
      await pg.waitForFunction(() => { const i = document.querySelector('#scan-out .share img'); return i && i.complete && i.naturalWidth > 0; }, null, { timeout: 10000 }).catch(() => {});
      const img = await pg.$eval('#scan-out .share img', i => ({ w: i.naturalWidth, src: i.src, alt: i.alt })).catch(() => ({ w: 0 }));
      ok(lang, `${mode}: badge preview renders`, img.w > 0 && img.src === `${BASE}/assets/badge-${lang}.svg` && img.alt === c.badge, JSON.stringify(img));
      await bR.scrollIntoViewIfNeeded(); await bR.click(); await pg.waitForTimeout(300);
      const rep = await pg.evaluate(() => navigator.clipboard.readText());
      const st1 = await pg.textContent('#share-status');
      await pg.screenshot({ path: `/workspace/qa-shots/share-${MODE}-${lang}-${mode}.png` });
      fs.writeFileSync(`/workspace/qa-shots/share-${MODE}-${lang}-${mode}-report.md`, rep);
      ok(lang, `${mode}: report header + language`, rep.startsWith('## ' + c.h) && rep.includes(c.disc), rep.slice(0, 60));
      ok(lang, `${mode}: report has score`, /\d+\/100/.test(rep));
      ok(lang, `${mode}: findings grouped by severity with fixes`, /^### .+ \(\d+\)$/m.test(rep) && rep.includes(c.fix + ':'));
      ok(lang, `${mode}: Fix Pack link with ref=report`, rep.includes(fixUrl) && !rep.includes(FIX + '&') );
      ok(lang, `${mode}: no promise of total security`, !/100% segur|totalmente segur|fully secure|completely secure|garantizamos|garantimos|we guarantee/i.test(rep));
      if (MODE === 'local') ok(lang, `${mode}: no full secrets (fake keys absent, masked only)`, !rep.includes(FAKE_SK) && !rep.includes(FAKE_JWT) && !rep.includes(RAW_TOKEN) && !rep.includes('QAFAKESIGNATURE') && (mode === 'repo' || rep.includes('QAUNMA…fXYZ')), mode);
      ok(lang, `${mode}: status message after copy`, (st1 || '').trim().length > 0, st1);
      await bB.click(); await pg.waitForTimeout(300);
      const bmd = await pg.evaluate(() => navigator.clipboard.readText());
      const expB = `[![${c.badge}](${BASE}/assets/badge-${lang}.svg)](${c.scan})`;
      ok(lang, `${mode}: badge snippet exact (no score, ref=badge)`, bmd === expB && !/\d+\/100/.test(bmd), bmd);
      const gc = await pg.evaluate(() => window.__gc || []);
      ok(lang, `${mode}: events report_copy/${mode} + badge_copy/${mode}`, gc.includes('report_copy/' + mode) && gc.includes('badge_copy/' + mode), gc.join(','));
      ok(lang, `${mode}: no new external requests`, ext.length === 0, ext.join(' '));
      ok(lang, `${mode}: 0 JS/CSP errors`, errs.length === 0, errs.join(' | '));
      await ctx.close();
    }
    // badge link target + svg
    const ctx = await b.newContext(); const pg = await ctx.newPage();
    if (MODE === 'local') {
      const f = path.join(SITE, 'assets', `badge-${lang}.svg`); const s = fs.readFileSync(f, 'utf8');
      ok(lang, 'badge svg text only (no score)', s.includes(`aria-label="${c.badge}"`) && !/\d+\s*\/\s*100|score|puntaje/i.test(s));
      await pg.setContent(`<body style="margin:20px;background:#fff">${s}<br><br><div style="background:#0d1117;padding:10px">${s}</div></body>`); await pg.screenshot({ path: `/workspace/qa-shots/share-badge-${lang}.png`, clip: { x: 0, y: 0, width: 300, height: 110 } });
      const sp = c.scan.replace(BASE, '').split('?')[0]; const rel = sp.endsWith('/') ? sp + 'index.html' : sp;
      ok(lang, 'badge link target page exists', fs.existsSync(path.join(SITE, rel)), sp);
    } else {
      const r = await ctx.request.get(`${BASE}/assets/badge-${lang}.svg`); ok(lang, 'live badge svg 200 + image/svg+xml', r.status() === 200 && /svg/.test(r.headers()['content-type']), r.status() + ' ' + r.headers()['content-type']);
      const r2 = await ctx.request.get(c.scan.split('#')[0]); ok(lang, 'live badge link 200', r2.status() === 200, c.scan);
      const r3 = await pg.goto(`${BASE}/assets/badge-${lang}.svg`); await pg.screenshot({ path: `/workspace/qa-shots/share-live-badge-${lang}.png`, clip: { x: 0, y: 0, width: 260, height: 40 } }); ok(lang, 'live badge renders in browser', r3.status() === 200);
    }
    await ctx.close();
  }
  { // Fix Pack link with ref=report resolves (browser navigation)
    const ctx = await b.newContext(); const pg = await ctx.newPage(); let st = 0;
    try { const r = await pg.goto(fixUrl, { waitUntil: 'domcontentloaded', timeout: 45000 }); st = r.status(); } catch (e) { st = 'ERR ' + e.message.slice(0, 80); }
    ok('all', 'Fix Pack ?ref=report resolves 200', st === 200, st + ' ' + pg.url()); await pg.screenshot({ path: `/workspace/qa-shots/share-${MODE}-fixpack.png` }); await ctx.close();
  }
  await b.close();
  const by = {}; for (const r of results) { by[r.lang] = by[r.lang] || { pass: 0, fail: 0 }; by[r.lang][r.pass ? 'pass' : 'fail']++; }
  const tot = results.filter(r => r.pass).length; console.log('SUMMARY', MODE, JSON.stringify(by), `${tot}/${results.length}`);
  fs.writeFileSync(`/workspace/qa-shots/share-${MODE}-results.json`, JSON.stringify(results, null, 1));
})();
