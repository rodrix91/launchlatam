// T-110 QA: scan box embedded + attributed in 3 blog articles (pilot). Usage: node qa_blog.js local|live
// local: serves ./site under the real origin; GitHub + Worker mocked. live: real site, real Worker (CORS from blog pages),
// GitHub mocked except for one real repo scan (keeps the 60/h unauthenticated quota). GoatCounter always stubbed.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const MODE = process.argv[2] || 'local'; const BASE = 'https://rodrix91.github.io/launchlatam'; const SITE = path.join(__dirname, '..', 'site');
const WORKER = 'https://launchlatam-urlscan.rodrixlabs-launchlatam-cloudflare.workers.dev';
const FIX = 'https://whop.com/checkout/plan_zaTKde6gNjQM2';
const PLANS = ['2WjdjdlCxW2uV', 'CcT1YHEXdjCOq', 'GV6POEXZk97P9', 'aZyftwaVpIhup', 'klbC3rVIhgyog', 'rO1ouDQJcQy2D', 'zaTKde6gNjQM2'];
const SP = { es: 'En modo repo, el escaneo corre en tu navegador contra repos públicos de GitHub y tu código nunca pasa por nuestros servidores. En modo URL, la consulta pasa por nuestro relay, que no guarda ni registra nada.',
  pt: 'No modo repo, o scan roda no seu navegador sobre repos públicos do GitHub e seu código nunca passa pelos nossos servidores. No modo URL, a consulta passa pelo nosso relay, que não guarda nem registra nada.' };
const DISC = { es: /chequeo automático, no auditoría/i, pt: /verificação automática, não auditoria/i };
const ART = [
  { lang: 'es', slug: 'mercado-pago-en-apps-lovable', p: '/blog/mercado-pago-en-apps-lovable/', scan: '/escaneo/?ref=blog-mercado-pago-en-apps-lovable', home: '/', topic: [/access token de Mercado Pago/, /service_role/, /RLS/], realRepo: true, url: 'https://www.python.org' },
  { lang: 'es', slug: 'stripe-no-funciona-en-mi-pais', p: '/blog/stripe-no-funciona-en-mi-pais/', scan: '/escaneo/?ref=blog-stripe-no-funciona-en-mi-pais', home: '/', topic: [/solo Stripe/, /Mercado Pago o Pix/, /privacidad y términos/], url: 'https://www.debian.org' },
  { lang: 'pt', slug: 'app-feito-com-ia-e-seguro', p: '/pt/blog/app-feito-com-ia-e-seguro/', scan: '/pt/?ref=blog-app-feito-com-ia-e-seguro#escaneo', home: '/pt/', topic: [/service_role/, /RLS/, /Pix ou Mercado Pago/, /privacidade e termos/], url: 'https://www.w3.org' },
];
const OTHERS = ['/blog/checklist-seguridad-apps-vibe-coding/', '/blog/rls-supabase-lovable/', '/blog/service-role-expuesta-supabase/', '/blog/webhooks-mercado-pago-supabase/', '/pt/blog/pix-no-lovable/'];
const PROMISE = /100% segur|totalmente segur|fully secure|completely secure|garantizamos|garantimos|garantiza que|we guarantee|sin riesgos|sem riscos|aprobad[oa] por|certificad/i;
const MIME = { html: 'text/html; charset=utf-8', js: 'application/javascript', css: 'text/css', svg: 'image/svg+xml', png: 'image/png', xml: 'application/xml', json: 'application/json', woff2: 'font/woff2', txt: 'text/plain' };
const results = []; const ok = (lang, name, pass, info = '') => { results.push({ lang, name, pass: !!pass, info }); console.log((pass ? 'PASS' : 'FAIL'), lang, name, String(info).slice(0, 180)); };
const FAKE_SK = 'sk_live_' + 'QAFAKE0000000000000000000000';
const MOCK_URL = { ok: true, target: { host: 'qa-app.example' }, scanned: { js: 3 }, findings: [{ id: 'stripe_secret', sev: 'critical', ev: 'sk_liv…QAFK', where: '/assets/index-qa.js' }, { id: 'csp_missing', sev: 'medium' }, { id: 'https_ok', sev: 'ok' }] };
async function setup(b, { mockGH = true, mockWorker = MODE === 'local', delayScan = 0 } = {}) {
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 }); const pg = await ctx.newPage();
  const errs = [], ext = [], reqs = [], workerCalls = [];
  pg.on('pageerror', e => errs.push('pageerror ' + e.message)); pg.on('console', m => { if (m.type() === 'error') errs.push('console ' + m.text()); });
  pg.on('request', r => { const u = r.url(); reqs.push(u); if (u.startsWith(WORKER)) workerCalls.push(u); if (!/^https:\/\/(rodrix91\.github\.io|api\.github\.com|raw\.githubusercontent\.com|gc\.zgo\.at|launchlatam\.goatcounter\.com)\//.test(u) && !u.startsWith(WORKER) && !u.startsWith('data:')) ext.push(u); });
  await pg.route('https://gc.zgo.at/**', r => r.fulfill({ contentType: 'application/javascript', body: 'window.__gc=[];window.goatcounter={count:function(o){window.__gc.push(o.path)}};' }));
  await pg.route('https://*.goatcounter.com/**', r => r.fulfill({ status: 204, body: '' }));
  if (MODE === 'local') await pg.route(BASE + '/**', async r => { let rel = new URL(r.request().url()).pathname.replace(/^\/launchlatam/, ''); if (rel.endsWith('/')) rel += 'index.html'; const f = path.join(SITE, rel); if (!fs.existsSync(f)) return r.fulfill({ status: 404, body: 'nf' }); if (delayScan && rel === '/assets/scan.js') await new Promise(z => setTimeout(z, delayScan)); r.fulfill({ status: 200, contentType: MIME[f.split('.').pop()] || 'application/octet-stream', body: fs.readFileSync(f) }); });
  else if (delayScan) await pg.route(BASE + '/assets/scan.js', async r => { await new Promise(z => setTimeout(z, delayScan)); r.continue(); });
  if (mockGH) {
    await pg.route('https://api.github.com/**', r => { const u = r.request().url(); const h = { 'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json' };
      if (/\/git\/trees\//.test(u)) return r.fulfill({ headers: h, body: JSON.stringify({ tree: ['.env', 'src/lib/pay.ts', 'supabase/migrations/001_init.sql', 'package.json'].map(p => ({ type: 'blob', path: p })) }) });
      return r.fulfill({ headers: h, body: JSON.stringify({ default_branch: 'main' }) }); });
    await pg.route('https://raw.githubusercontent.com/**', r => { const u = r.request().url(); let body = '{}'; if (u.endsWith('/.env')) body = 'STRIPE=' + FAKE_SK; else if (u.endsWith('pay.ts')) body = 'import Stripe from "stripe";const s="' + FAKE_SK + '";'; else if (u.endsWith('.sql')) body = 'create table public.profiles (id uuid);'; r.fulfill({ headers: { 'Access-Control-Allow-Origin': '*' }, body }); });
  }
  if (mockWorker) await pg.route(WORKER + '/**', r => r.fulfill({ headers: { 'Access-Control-Allow-Origin': 'https://rodrix91.github.io', 'Content-Type': 'application/json' }, body: JSON.stringify(MOCK_URL) }));
  return { ctx, pg, errs, ext, reqs, workerCalls };
}
const scanLoaded = reqs => reqs.some(u => u === BASE + '/assets/scan.js');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--headless=new'] });
  for (const a of ART) {
    const L = a.lang, ref = 'blog-' + a.slug, tag = a.slug.split('-').slice(0, 3).join('-');
    // ---- static structure + lazy load
    let { ctx, pg, errs, ext, reqs } = await setup(b);
    const resp = await pg.goto(BASE + a.p, { waitUntil: 'networkidle' }); await pg.waitForTimeout(500);
    ok(a.slug, 'page 200', resp.status() === 200, resp.status());
    ok(a.slug, 'lazy: scan-lazy.js loaded, scan.js NOT loaded at top of page', reqs.includes(BASE + '/assets/scan-lazy.js') && !scanLoaded(reqs), reqs.filter(u => /assets\/scan/.test(u)).join(' '));
    const st = await pg.evaluate(() => { const art = document.querySelector('article'); const h2 = [...art.querySelectorAll(':scope > h2')]; const box = document.querySelectorAll('#escaneo'); const notes = document.querySelectorAll('.scan-note'); const n = notes[0];
      return { boxes: box.length, inArticle: box[0] && art.contains(box[0]), last: art.lastElementChild === box[0], notes: notes.length, noteBeforeSecondH2: !!(n && h2[1] && n.nextElementSibling === h2[1]), noteHref: n && n.querySelector('a').href, scanForms: document.querySelectorAll('#scan-form').length, urlForms: document.querySelectorAll('#url-form').length, oldBox: [...art.querySelectorAll(':scope > .report h3')].length, boxText: box[0] ? box[0].innerText : '', dref: box[0] && box[0].getAttribute('data-ref'), csp: document.querySelector('meta[http-equiv=Content-Security-Policy]').content, whop: [...document.querySelectorAll('a[href*="whop.com"]')].map(x => x.href), boxFix: [...document.querySelectorAll('#escaneo a[href*="whop.com"]')].map(x => x.href) }; });
    ok(a.slug, 'exactly one scan box (1 #escaneo, 1 repo form, 1 URL form)', st.boxes === 1 && st.scanForms === 1 && st.urlForms === 1, JSON.stringify([st.boxes, st.scanForms, st.urlForms]));
    ok(a.slug, 'box is the last block of the article (after FAQ), generic CTA box replaced', st.inArticle && st.last && st.oldBox === 0);
    ok(a.slug, 'one light text link right after the first section', st.notes === 1 && st.noteBeforeSecondH2);
    ok(a.slug, 'text link -> scan page with ref=' + ref, st.noteHref === BASE + a.scan, st.noteHref);
    ok(a.slug, 'box data-ref', st.dref === ref, st.dref);
    ok(a.slug, 'copy: automated check, not an audit', DISC[L].test(st.boxText));
    ok(a.slug, 'copy: exact published privacy sentence (sp)', st.boxText.includes(SP[L]));
    ok(a.slug, 'copy: topic-focused (' + a.topic.length + ' terms)', a.topic.every(r => r.test(st.boxText)), a.topic.filter(r => !r.test(st.boxText)).join(','));
    ok(a.slug, 'copy: no promised results', !PROMISE.test(st.boxText) && !PROMISE.test(await pg.textContent('.scan-note')));
    ok(a.slug, 'box Fix Pack link = existing plan + ref', st.boxFix.length === 1 && st.boxFix[0] === FIX + '?ref=' + ref, st.boxFix.join(' '));
    ok(a.slug, 'only existing Whop plans on page', st.whop.every(u => PLANS.some(p => u.includes('plan_' + p))), st.whop.join(' '));
    ok(a.slug, 'CSP: worker in connect-src, script-src self (no inline)', st.csp.includes(WORKER) && /script-src 'self' https:\/\/gc\.zgo\.at;/.test(st.csp), st.csp.slice(0, 120));
    await pg.evaluate(() => { const n = document.querySelector('.scan-note'); window.scrollTo(0, n.getBoundingClientRect().top + scrollY - 250); }); await pg.waitForTimeout(200);
    await pg.screenshot({ path: `/workspace/qa-shots/blog-embed-${MODE}-${tag}-note.png` });
    ok(a.slug, 'lazy: scan.js still not loaded while reading the first section', !scanLoaded(reqs));
    await pg.locator('#escaneo').scrollIntoViewIfNeeded(); await pg.waitForFunction(() => window.__gc !== undefined, null).catch(() => {}); await pg.waitForTimeout(1200);
    ok(a.slug, 'lazy: scan.js loads when the box approaches', scanLoaded(reqs));
    await pg.screenshot({ path: `/workspace/qa-shots/blog-embed-${MODE}-${tag}-box.png`, fullPage: false });
    // repo scan
    const useReal = MODE === 'live' && a.realRepo;
    if (useReal) { await ctx.close(); ({ ctx, pg, errs, ext, reqs } = await setup(b, { mockGH: false })); await pg.goto(BASE + a.p, { waitUntil: 'networkidle' }); await pg.locator('#escaneo').scrollIntoViewIfNeeded(); await pg.waitForTimeout(1200); }
    await pg.fill('#repo', useReal ? 'david210690/lovable-supabase-mvp-starter' : 'qa-owner/qa-app'); await pg.click('#scan-form button');
    await pg.waitForFunction(() => !document.getElementById('scan-out').hidden && document.querySelector('#scan-out .ctas'), null, { timeout: 60000 }).catch(() => {});
    const out = await pg.evaluate(() => ({ t: document.getElementById('scan-out').innerText, links: [...document.querySelectorAll('#scan-out .ctas a')].map(x => [x.getAttribute('data-gc'), x.href]) }));
    ok(a.slug, 'repo scan renders a result' + (useReal ? ' (real GitHub)' : ''), /\d+\/100/.test(out.t), out.t.slice(0, 80).replace(/\s+/g, ' '));
    const fx = out.links.find(x => x[0] === 'fix'), pl = out.links.find(x => x[0] === 'plans'), la = out.links.find(x => x[0] === 'launch');
    ok(a.slug, 'result CTA -> Fix Pack/Launch with ref=' + ref, (fx && fx[1] === FIX + '?ref=' + ref) || (la && la[1].endsWith('?ref=' + ref)), JSON.stringify(out.links));
    ok(a.slug, 'result "plans" link -> home #precios (no dead anchor)', !pl || pl[1] === BASE + a.home + '#precios', pl && pl[1]);
    await pg.locator('#scan-out').scrollIntoViewIfNeeded(); await pg.screenshot({ path: `/workspace/qa-shots/blog-embed-${MODE}-${tag}-repo.png`, fullPage: false });
    // CTA click (navigation prevented, event recorded)
    await pg.evaluate(() => { window.__pd = e => { if (e.target.closest('a')) e.preventDefault(); }; document.addEventListener('click', window.__pd); });
    await pg.click('#scan-out .ctas a[data-gc]'); await pg.click('#escaneo .ctas[data-cta=blog] a');
    await pg.evaluate(() => document.removeEventListener('click', window.__pd));
    // URL scan (real Worker in live: proves Origin/CORS from a blog page)
    await pg.check('input[name=scanmode][value=url]'); await pg.fill('#appurl', MODE === 'local' ? 'https://qa-app.example' : a.url); await pg.check('#url-consent'); await pg.click('#url-form button');
    await pg.waitForFunction(() => { const o = document.getElementById('scan-out'); return !o.hidden && o.querySelector('.ctas[data-cta^=url_]'); }, null, { timeout: 60000 }).catch(() => {});
    const uo = await pg.evaluate(() => ({ t: document.getElementById('scan-out').innerText, cta: (document.querySelector('#scan-out .ctas') || {}).getAttribute && document.querySelector('#scan-out .ctas').getAttribute('data-cta') }));
    ok(a.slug, 'URL scan via Worker renders a result' + (MODE === 'live' ? ' (real Worker, Origin accepted)' : ''), /\d+\/100/.test(uo.t) && /^url_(findings|clean)$/.test(uo.cta || ''), (uo.cta || '') + ' ' + uo.t.slice(0, 70).replace(/\s+/g, ' '));
    await pg.locator('#scan-out').scrollIntoViewIfNeeded(); await pg.screenshot({ path: `/workspace/qa-shots/blog-embed-${MODE}-${tag}-url.png`, fullPage: false });
    const gc = await pg.evaluate(() => window.__gc || []);
    ok(a.slug, 'events: scan_run + scan_run/' + ref, gc.includes('scan_run') && gc.includes('scan_run/' + ref), gc.join(','));
    ok(a.slug, 'events: url_scan_run + url_scan_run/' + ref, gc.includes('url_scan_run') && gc.includes('url_scan_run/' + ref));
    ok(a.slug, 'events: scan_result/* and url_scan_result/* unchanged', gc.some(x => /^scan_result\/(0-49|50-79|80-100)$/.test(x)) && gc.some(x => /^url_scan_result\/(0-49|50-79|80-100)$/.test(x)));
    ok(a.slug, 'events: cta_click/<box>/<gc> + cta_click/' + ref + '/<box>/<gc> (result + box)', gc.some(x => /^cta_click\/(findings|clean)\/(fix|launch|plans|news)$/.test(x)) && gc.some(x => new RegExp('^cta_click/' + ref + '/(findings|clean)/').test(x)) && gc.includes('cta_click/blog/fix') && gc.includes('cta_click/' + ref + '/blog/fix'));
    ok(a.slug, 'events: no repo names/URLs in event paths', !gc.some(x => /qa-owner|lovable-supabase|python|debian|w3|qa-app/.test(x)));
    ok(a.slug, 'no unexpected external requests', ext.length === 0, ext.join(' '));
    ok(a.slug, '0 JS/CSP errors', errs.length === 0, errs.join(' | '));
    await ctx.close();
    // ---- held submit: Enter pressed before scan.js is ready -> replayed, no native submit/navigation
    ({ ctx, pg, errs, reqs } = await setup(b, { delayScan: 2500 }));
    await pg.goto(BASE + a.p, { waitUntil: 'domcontentloaded' }); await pg.evaluate(() => { const s = document.getElementById('escaneo'); window.scrollTo(0, s.getBoundingClientRect().top + scrollY - 2000); });
    await pg.fill('#repo', 'qa-owner/qa-app'); await pg.press('#repo', 'Enter');
    await pg.waitForFunction(() => !document.getElementById('scan-out').hidden, null, { timeout: 20000 }).catch(() => {});
    const held = await pg.evaluate(() => ({ url: location.href, shown: !document.getElementById('scan-out').hidden, gc: window.__gc || [] }));
    ok(a.slug, 'early submit is held and replayed after lazy load (no page navigation)', held.url === BASE + a.p && held.shown && held.gc.filter(x => x === 'scan_run').length === 1, JSON.stringify(held).slice(0, 160));
    ok(a.slug, 'held-submit run 0 JS/CSP errors', errs.length === 0, errs.join(' | '));
    await ctx.close();
    // ---- text link target
    ({ ctx, pg, errs } = await setup(b));
    const r2 = await pg.goto(BASE + a.scan, { waitUntil: 'networkidle' });
    ok(a.slug, 'text link target 200 with scanner', r2.status() === 200 && await pg.locator('#scan-form').count() === 1, r2.status());
    await pg.fill('#repo', 'qa-owner/qa-app'); await pg.click('#scan-form button'); await pg.waitForFunction(() => !document.getElementById('scan-out').hidden, null, { timeout: 30000 }).catch(() => {});
    const g2 = await pg.evaluate(() => window.__gc || []); const f2 = await pg.evaluate(() => (document.querySelector('#scan-out a[data-gc=fix]') || {}).href);
    ok(a.slug, 'scan page with ?ref=' + ref + ': attributed scan_run + Fix Pack ref', g2.includes('scan_run') && g2.includes('scan_run/' + ref) && f2 === FIX + '?ref=' + ref, g2.join(',') + ' ' + f2);
    ok(a.slug, 'scan page with ref: 0 JS/CSP errors', errs.length === 0, errs.join(' | '));
    await ctx.close();
  }
  // ---- regressions: /escaneo/ without ref and with ref=report keeps the old events exactly; other articles untouched
  for (const q of ['', '?ref=report']) {
    const { ctx, pg, errs } = await setup(b); await pg.goto(BASE + '/escaneo/' + q, { waitUntil: 'networkidle' });
    await pg.fill('#repo', 'qa-owner/qa-app'); await pg.click('#scan-form button'); await pg.waitForFunction(() => !document.getElementById('scan-out').hidden, null, { timeout: 30000 }).catch(() => {});
    await pg.evaluate(() => document.addEventListener('click', e => e.preventDefault())); await pg.click('#scan-out .ctas a[data-gc]');
    const g = await pg.evaluate(() => window.__gc || []); const f = await pg.evaluate(() => [...document.querySelectorAll('#scan-out .ctas a')].map(x => x.getAttribute('href')));
    ok('escaneo' + q, 'events unchanged (no blog attribution)', g.includes('scan_run') && !g.some(x => /blog-/.test(x)) && g.some(x => /^cta_click\/(findings|clean)\//.test(x)), g.join(','));
    ok('escaneo' + q, 'CTA links unchanged (no ref, #precios local)', f.includes(FIX) || f.some(x => /plan_klbC3rVIhgyog$/.test(x)), f.join(' '));
    ok('escaneo' + q, '0 JS/CSP errors', errs.length === 0, errs.join(' | ')); await ctx.close();
  }
  for (const o of OTHERS) {
    const { ctx, pg, errs, reqs } = await setup(b); const r = await pg.goto(BASE + o, { waitUntil: 'networkidle' });
    const s = await pg.evaluate(() => ({ box: document.querySelectorAll('#escaneo,.scan-note,[data-lazy-scan]').length, old: document.querySelectorAll('article > .report h3').length }));
    ok(o, 'non-pilot article untouched (no embed, generic CTA, scan.js eager)', r.status() === 200 && s.box === 0 && s.old === 1 && scanLoaded(reqs) && errs.length === 0, JSON.stringify(s)); await ctx.close();
  }
  if (MODE === 'live') { // checkouts 7/7 + ref variants
    const ctx = await b.newContext();
    for (const p of PLANS) { let s = 0; try { s = (await ctx.request.get('https://whop.com/checkout/plan_' + p, { timeout: 30000 })).status(); } catch (e) { s = 'ERR'; } ok('whop', 'checkout plan_' + p + ' 200', s === 200, s); }
    for (const a of ART) { const u = FIX + '?ref=blog-' + a.slug; let s = 0; try { s = (await ctx.request.get(u, { timeout: 30000 })).status(); } catch (e) { s = 'ERR'; } ok('whop', 'Fix Pack ?ref=blog-' + a.slug + ' 200', s === 200, s); }
    await ctx.close();
  }
  await b.close();
  const by = {}; for (const r of results) { const k = r.lang.split('/')[0]; by[k] = by[k] || { pass: 0, fail: 0 }; by[k][r.pass ? 'pass' : 'fail']++; }
  const tot = results.filter(r => r.pass).length; console.log('SUMMARY', MODE, JSON.stringify(by), `${tot}/${results.length}`);
  fs.writeFileSync(`/workspace/qa-shots/blog-embed-${MODE}-results.json`, JSON.stringify(results, null, 1));
})();
