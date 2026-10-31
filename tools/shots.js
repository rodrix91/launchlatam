const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const U = process.env.U || 'http://localhost:8099/launchlatam/';
  const out = '/workspace/launchlatam/shots/';
  const errs = [];
  // OG image
  const og = await b.newPage({ viewport: { width: 1200, height: 630 } });
  await og.goto(U); await og.addStyleTag({content:'.dock,.mast,.lang{display:none!important}'});
  await og.setContent(`<html><head><link rel="stylesheet" href="${U}assets/site.css"></head><body style="margin:0;background:#1E1412;color:#F2DCC0;width:1200px;height:630px;display:flex;flex-direction:column;justify-content:center;padding:70px;box-sizing:border-box;font-family:Bricolage"><p class="mono" style="color:#E2522B;font-size:22px">LAUNCHLATAM · ADUANA PARA APPS HECHAS CON IA</p><h1 style="color:#F2DCC0;font-size:88px;margin:20px 0">Tu app ya funciona.<br><em style="color:#E2522B;background:none">Ahora que pase la aduana.</em></h1><p style="font-size:28px">Seguridad · Mercado Pago &amp; Pix · Cumplimiento de datos</p></body></html>`);
  await og.waitForTimeout(800); await og.screenshot({ path: '/workspace/launchlatam/site/assets/og.png' });
  for (const [name, w, h, path, full] of [['desktop-hero',1440,900,'',false],['tablet',834,1112,'',false],['mobile',390,844,'',false],['mobile-full',390,844,'',true],['pricing',1440,900,'#precios',false],['scan-en',1440,900,'en/#escaneo',false],['blog-post-mobile',390,844,'blog/checklist-seguridad-apps-vibe-coding/',false]]) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    p.on('console', m => { if (m.type()==='error') errs.push(name+': '+m.text()) });
    p.on('pageerror', e => errs.push(name+': '+e.message));
    await p.goto(U + path, { waitUntil: 'networkidle' }); await p.waitForTimeout(1200);
    await p.screenshot({ path: out + name + '.png', fullPage: full });
    const ov = await p.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    if (ov) errs.push(name + ': horizontal overflow');
    await p.close();
  }
  console.log(JSON.stringify(errs, null, 1));
  await b.close();
})();
