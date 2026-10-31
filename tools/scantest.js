const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:900}});
p.on('pageerror',e=>console.log('ERR',e.message));p.on('console',m=>{if(m.type()==='error')console.log('CONSOLE',m.text())});
await p.goto('http://localhost:8099/launchlatam/escaneo/');await p.fill('#repo','david210690/lovable-supabase-mvp-starter');await p.click('#scan-form button');
await p.waitForSelector('#scan-out:not([hidden])',{timeout:60000}).catch(()=>{});console.log(await p.textContent('#scan-status'));console.log((await p.textContent('#scan-out')).slice(0,900));
await p.screenshot({path:'/workspace/launchlatam/shots/scan-result.png',fullPage:false});
await p.click('details summary');await p.check('input[name=q0][value=no]');await p.check('input[name=q1][value=yes]');await p.click('#self-check button');console.log('SELF:',(await p.textContent('#self-out')).slice(0,200));await b.close()})()
