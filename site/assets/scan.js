// LaunchLatam free scan: runs 100% in the visitor's browser against PUBLIC GitHub repos.
// Nothing is sent to LaunchLatam servers. Uses api.github.com (60 req/h unauthenticated) + raw.githubusercontent.com.
(function(){
"use strict";
var L=(document.documentElement.lang||"es").slice(0,2);
var T={
es:{bad:"Ingresá un repositorio público de GitHub, por ejemplo usuario/mi-app o https://github.com/usuario/mi-app.",nf:"No encontramos ese repositorio. ¿Es público? Si es privado, usá el chequeo guiado de abajo.",rl:"GitHub limitó las consultas desde tu red (60 por hora). Probá en unos minutos o usá el chequeo guiado.",run:"Escaneando",files:"archivos revisados",crit:"Crítico",high:"Alto",med:"Medio",ok:"Bien",none:"No encontramos problemas en lo que pudimos revisar. Esto no garantiza que la app sea segura: no revisamos tu base de datos en vivo ni tu configuración en Supabase.",score:"Puntaje de lanzamiento",cta:"Corregir esto por $29",cta2:"Ver el lanzamiento completo",clean:"El escaneo automático no encontró problemas en lo que revisa; no reemplaza una auditoría completa. Si vas a lanzar o cobrar, podemos dejar lista la seguridad completa, un cobro local y páginas legales básicas.",ctaL:"Lanzamiento Esencial por $149",urg:"Hay hallazgos críticos o altos: conviene corregirlos antes de empezar a cobrar.",rec:"Solo encontramos puntos de severidad media o baja: corregirlos es recomendado, sin urgencia.",ctaN:"Recibir el boletín gratis",title:"Resultado del escaneo",note:"Revisamos el código del repositorio, no la app en vivo. Los hallazgos son automáticos: confirmalos antes de actuar."},
pt:{bad:"Informe um repositório público do GitHub, por exemplo usuario/meu-app ou https://github.com/usuario/meu-app.",nf:"Não encontramos esse repositório. Ele é público? Se for privado, use o checklist guiado abaixo.",rl:"O GitHub limitou as consultas da sua rede (60 por hora). Tente em alguns minutos ou use o checklist guiado.",run:"Escaneando",files:"arquivos revisados",crit:"Crítico",high:"Alto",med:"Médio",ok:"Ok",none:"Não encontramos problemas no que conseguimos revisar. Isso não garante que o app seja seguro: não revisamos seu banco ao vivo nem a configuração do Supabase.",score:"Pontuação de lançamento",cta:"Corrigir isso por US$29",cta2:"Ver o lançamento completo",clean:"O scan automático não encontrou problemas no que ele verifica; isso não substitui uma auditoria completa. Se você vai lançar ou cobrar, podemos deixar prontas a segurança completa, um meio de pagamento local e páginas legais básicas.",ctaL:"Lançamento Essencial por US$149",urg:"Há achados críticos ou altos: o ideal é corrigi-los antes de começar a cobrar.",rec:"Encontramos apenas pontos de severidade média ou baixa: corrigi-los é recomendado, sem urgência.",ctaN:"Receber a newsletter grátis",title:"Resultado do scan",note:"Revisamos o código do repositório, não o app ao vivo. Os achados são automáticos: confirme antes de agir."},
en:{bad:"Enter a public GitHub repo, e.g. user/my-app or https://github.com/user/my-app.",nf:"We couldn't find that repo. Is it public? If it's private, use the guided check below.",rl:"GitHub rate-limited your network (60 requests/hour). Try again in a few minutes or use the guided check.",run:"Scanning",files:"files checked",crit:"Critical",high:"High",med:"Medium",ok:"Good",none:"We found no problems in what we could check. That doesn't guarantee the app is secure: we don't inspect your live database or Supabase settings.",score:"Launch score",cta:"Fix this for $29",cta2:"See the full launch",clean:"The automated scan found no problems in what it checks; it doesn't replace a full audit. If you're about to launch or charge, we can set up full security, one local payment method and basic legal pages.",ctaL:"Essential Launch for $149",urg:"There are critical or high findings: it's best to fix them before you start charging.",rec:"We only found medium- or low-severity items: fixing them is recommended, not urgent.",ctaN:"Get the free newsletter",title:"Scan result",note:"We check the repository code, not the live app. Findings are automated: confirm them before acting."}
}[L]||{};
var F={ // finding texts
env:{es:"Archivo de entorno subido al repo: ",pt:"Arquivo de ambiente no repositório: ",en:"Environment file committed: "},
sec:{es:"Posible secreto en el código (",pt:"Possível segredo no código (",en:"Possible secret in code ("},
srv:{es:"Clave service_role de Supabase en el código: salta toda la seguridad de la base. Rotala ya en Supabase.",pt:"Chave service_role do Supabase no código: ignora toda a segurança do banco. Gere outra já no Supabase.",en:"Supabase service_role key in code: it bypasses all database security. Rotate it now in Supabase."},
rls:{es:"Tablas creadas sin activar Row Level Security: ",pt:"Tabelas criadas sem ativar Row Level Security: ",en:"Tables created without Row Level Security: "},
tru:{es:"Política RLS que deja pasar a todos (using (true)) en ",pt:"Política RLS que libera todos (using (true)) em ",en:"RLS policy open to everyone (using (true)) in "},
hdr:{es:"No hay cabeceras de seguridad (Content-Security-Policy) configuradas en el repo.",pt:"Não há cabeçalhos de segurança (Content-Security-Policy) configurados no repositório.",en:"No security headers (Content-Security-Policy) configured in the repo."},
pay0:{es:"No detectamos ningún sistema de cobro. Si vas a vender en LatAm, Mercado Pago o un cobro local suele convertir mejor que solo tarjeta internacional.",pt:"Não detectamos nenhum sistema de pagamento. Para vender no Brasil, Pix via Mercado Pago ou outro meio local costuma converter melhor.",en:"No payment system detected. Selling in LatAm usually converts better with Mercado Pago or another local method."},
payS:{es:"Solo cobros con Stripe: Stripe abre cuentas locales en LatAm solo en México y Brasil. Sumá un método local (Mercado Pago, Pix, OXXO).",pt:"Só pagamentos com Stripe: na América Latina, Stripe só abre contas locais no México e no Brasil. Adicione um meio local (Pix, Mercado Pago).",en:"Stripe-only payments: in LatAm, Stripe only offers local accounts in Mexico and Brazil. Add a local method (Mercado Pago, Pix, OXXO)."},
payOK:{es:"Detectamos un cobro local (Mercado Pago / Pix).",pt:"Detectamos um meio de pagamento local (Mercado Pago / Pix).",en:"Local payment method detected (Mercado Pago / Pix)."},
leg:{es:"No encontramos página de privacidad ni términos. Las leyes de datos de la región (LGPD en Brasil, Ley 25.326 en Argentina, LFPDPPP en México) piden informar cómo usás los datos.",pt:"Não encontramos página de privacidade nem termos. A LGPD exige informar como você usa dados pessoais.",en:"No privacy or terms page found. Data laws in the region (Brazil's LGPD, Argentina's Law 25.326, Mexico's LFPDPPP) require telling users how you use their data."},
legOK:{es:"Hay páginas de privacidad o términos.",pt:"Há páginas de privacidade ou termos.",en:"Privacy or terms pages present."},
dbg:{es:"Rutas de debug o seed en el código: ",pt:"Rotas de debug ou seed no código: ",en:"Debug or seed routes in code: "}
};
function t(k){return (F[k]&&F[k][L])||F[k].en}
var PAT=[["Stripe live",/sk_live_[0-9a-zA-Z]{16,}/],["Stripe test",/sk_test_[0-9a-zA-Z]{16,}/],["OpenAI",/sk-(proj-)?[A-Za-z0-9_-]{32,}/],["Anthropic",/sk-ant-[A-Za-z0-9_-]{20,}/],["AWS",/AKIA[0-9A-Z]{16}/],["GitHub",/gh[pousr]_[A-Za-z0-9]{36}/],["Mercado Pago",/APP_USR-\d{6,}-\d{6}-[a-f0-9]{32}-\d+/],["Private key",/-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----/],["Google API",/AIza[0-9A-Za-z_-]{35}/],["Resend",/re_[A-Za-z0-9]{8}_[A-Za-z0-9]{20,}/]];
var JWT=/eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}/g;
function isServiceRole(j){try{var p=j.split(".")[1].replace(/-/g,"+").replace(/_/g,"/");return /"role"\s*:\s*"service_role"/.test(atob(p+"===".slice((p.length+3)%4)))}catch(e){return false}}
function parse(v){v=(v||"").trim().replace(/\.git$/,"").replace(/\/$/,"");var m=v.match(/^(?:https?:\/\/)?(?:www\.)?github\.com\/([\w.-]+)\/([\w.-]+)/i)||v.match(/^([\w.-]+)\/([\w.-]+)$/);return m?{o:m[1],r:m[2]}:null}
function esc(s){return String(s).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})}
async function gh(u){var r=await fetch("https://api.github.com"+u,{headers:{Accept:"application/vnd.github+json"}});if(r.status===403||r.status===429)throw "rl";if(!r.ok)throw "nf";return r.json()}
async function scan(repo,out,status){
 var meta=await gh("/repos/"+repo.o+"/"+repo.r);var br=meta.default_branch;
 var tree=await gh("/repos/"+repo.o+"/"+repo.r+"/git/trees/"+encodeURIComponent(br)+"?recursive=1");
 var paths=(tree.tree||[]).filter(function(x){return x.type==="blob"}).map(function(x){return x.path}).filter(function(p){return !/(^|\/)(node_modules|dist|build|\.next|vendor)\//.test(p)});
 var f=[];
 paths.filter(function(p){return /(^|\/)\.env(\.[\w-]+)?$/.test(p)&&!/example|sample|template/i.test(p)}).forEach(function(p){f.push(["crit",t("env")+p])});
 var code=paths.filter(function(p){return /\.(t|j)sx?$|\.mjs$|\.vue$|\.svelte$|\.py$|\.env(\.[\w-]+)?$|\.toml$|\.ya?ml$|\.json$/.test(p)&&!/lock|\.d\.ts$|test|spec|example/i.test(p)});
 code.sort(function(a,b){var s=function(p){return /supabase|api|server|lib|config|env|integrations|functions/i.test(p)?0:1};return s(a)-s(b)});
 code=code.slice(0,60);
 var sql=paths.filter(function(p){return /\.sql$/.test(p)}).slice(0,40);
 var all=code.concat(sql),n=0,joined="",secrets={},srv=false,noRls=[],openPol=[],debug=[];
 var base="https://raw.githubusercontent.com/"+repo.o+"/"+repo.r+"/"+br+"/";
 for(var i=0;i<all.length;i+=8){
  var chunk=all.slice(i,i+8);
  var txts=await Promise.all(chunk.map(function(p){return fetch(base+p.split("/").map(encodeURIComponent).join("/")).then(function(r){return r.ok?r.text():""}).catch(function(){return ""})}));
  txts.forEach(function(s,k){var p=chunk[k];n++;if(s.length>400000)return;joined+=s.slice(0,20000)+"\n";
   PAT.forEach(function(pt){if(pt[1].test(s))(secrets[pt[0]]=secrets[pt[0]]||[]).push(p)});
   (s.match(JWT)||[]).forEach(function(j){if(isServiceRole(j))srv=true});
   if(/\.sql$/.test(p)){var tb=[],re=/create\s+table\s+(?:if\s+not\s+exists\s+)?(?:public\.)?"?(\w+)"?/gi,m;while((m=re.exec(s)))tb.push(m[1]);
    tb.forEach(function(x){if(!new RegExp("alter\\s+table\\s+(public\\.)?\"?"+x+"\"?\\s+enable\\s+row\\s+level\\s+security","i").test(joined+s))noRls.push(x)});
    if(/using\s*\(\s*true\s*\)/i.test(s))openPol.push(p)}
   if(/["'`]\/api\/(debug|seed|test-data)\b/.test(s))debug.push(p);
  });
  status.textContent=T.run+"… "+n+"/"+all.length;
 }
 if(srv)f.push(["crit",t("srv")]);
 Object.keys(secrets).forEach(function(k){f.push([k==="Stripe test"?"high":"crit",t("sec")+k+"): "+secrets[k].slice(0,3).join(", ")])});
 noRls=noRls.filter(function(x){return !new RegExp("alter\\s+table\\s+(public\\.)?\"?"+x+"\"?\\s+enable\\s+row\\s+level\\s+security","i").test(joined)});
 if(noRls.length)f.push(["crit",t("rls")+Array.from(new Set(noRls)).slice(0,8).join(", ")]);
 if(openPol.length)f.push(["high",t("tru")+openPol.slice(0,3).join(", ")]);
 if(debug.length)f.push(["med",t("dbg")+debug.slice(0,3).join(", ")]);
 var hasHdr=paths.some(function(p){return /(^|\/)(_headers|vercel\.json|netlify\.toml)$/.test(p)})&&/content-security-policy/i.test(joined);
 if(!hasHdr)f.push(["med",t("hdr")]);
 var mp=/mercadopago|mercado-pago|mercado_pago|\bpix\b/i.test(joined),st=/stripe/i.test(joined),pd=/paddle|lemonsqueezy/i.test(joined);
 if(mp)f.push(["ok",t("payOK")]);else if(st)f.push(["high",t("payS")]);else if(!pd)f.push(["med",t("pay0")]);
 var leg=paths.some(function(p){return /privac|terms|termin|legal/i.test(p)});
 f.push(leg?["ok",t("legOK")]:["med",t("leg")]);
 return {f:f,n:n,repo:repo.o+"/"+repo.r};
}
// T-101: cookie-less GoatCounter events (no-op if analytics disabled). Only coarse buckets, never repo names/URLs.
function gcEvent(name){try{if(window.goatcounter&&window.goatcounter.count)window.goatcounter.count({path:name,title:name,event:true})}catch(e){}}
function bucket(sc){return sc>=80?"80-100":sc>=50?"50-79":"0-49"}
// Post-scan CTA: findings -> Fix Pack; clean -> Launch or free newsletter (no paid fix offer).
var WL={fix:"https://whop.com/checkout/plan_zaTKde6gNjQM2",launch:"https://whop.com/checkout/plan_klbC3rVIhgyog",news:"https://whop.com/checkout/plan_rO1ouDQJcQy2D"};
function ctas(hasFindings,scanText,sev){
 if(hasFindings)return (sev?'<p data-sev="'+sev+'">'+(sev==="urgent"?T.urg:T.rec)+'</p>':'')+'<div class="ctas" data-cta="findings"><a class="btn a" data-gc="fix" href="'+WL.fix+'" rel="noopener">'+T.cta+'</a><a class="btn s" style="color:var(--sal);border-color:var(--sal)" data-gc="plans" href="#precios">'+T.cta2+"</a></div>";
 return (scanText?'<p>'+T.clean+'</p>':'')+'<div class="ctas" data-cta="clean"><a class="btn a" data-gc="launch" href="'+WL.launch+'" rel="noopener">'+T.ctaL+'</a><a class="btn s" style="color:var(--sal);border-color:var(--sal)" data-gc="news" href="'+WL.news+'" rel="noopener">'+T.ctaN+"</a></div>";
}
function render(res,out){
 var w={crit:30,high:15,med:6,ok:0},sc=100;res.f.forEach(function(x){sc-=w[x[0]]});sc=Math.max(0,sc);
 var lbl={crit:T.crit,high:T.high,med:T.med,ok:T.ok},cls={crit:"bad",high:"bad",med:"bad",ok:"ok"};
 var h='<h3 tabindex="-1" id="scan-title">'+T.title+": "+esc(res.repo)+'</h3><p class="mono">'+T.score+": "+sc+"/100 · "+res.n+" "+T.files+"</p>";
 var probs=res.f.filter(function(x){return x[0]!=="ok"});
 res.f.forEach(function(x){h+='<div class="finding"><span class="pill '+cls[x[0]]+'">'+lbl[x[0]]+"</span> "+esc(x[1])+"</div>"});
 h+='<p class="muted" style="color:#CDB59B">'+T.note+'</p>'+ctas(probs.length>0,true,probs.some(function(x){return x[0]==="crit"||x[0]==="high"})?"urgent":"recommended");
 out.innerHTML=h;out.hidden=false;document.getElementById("scan-title").focus();
 return sc;
}
document.addEventListener("DOMContentLoaded",function(){
 var form=document.getElementById("scan-form");if(form){
 var out=document.getElementById("scan-out"),status=document.getElementById("scan-status"),btn=form.querySelector("button");
 form.addEventListener("submit",async function(e){e.preventDefault();var repo=parse(form.repo.value);
  if(!repo){status.textContent=T.bad;return}
  btn.disabled=true;status.textContent=T.run+"…";out.hidden=true;gcEvent("scan_run");
  try{var r=await scan(repo,out,status);status.textContent="";gcEvent("scan_result/"+bucket(render(r,out)))}
  catch(err){status.textContent=err==="rl"?T.rl:T.nf;gcEvent("scan_result/"+(err==="rl"?"rate_limited":"not_found"))}
  finally{btn.disabled=false}
 });}
 document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest("[data-gc]");if(!a)return;var box=a.closest("[data-cta]");gcEvent("cta_click/"+(box?box.getAttribute("data-cta"):"x")+"/"+a.getAttribute("data-gc"))});
 var q=document.getElementById("self-check");if(q){q.addEventListener("submit",function(e){e.preventDefault();
  var fs=q.querySelectorAll("fieldset"),bad=[];fs.forEach(function(x){var c=x.querySelector("input:checked");if(!c||c.value==="no")bad.push(x.dataset.fix)});
  var o=document.getElementById("self-out");var sc=Math.round(100*(fs.length-bad.length)/fs.length);
  o.innerHTML='<h3 tabindex="-1" id="self-title">'+T.score+": "+sc+"/100</h3>"+(bad.length?bad.map(function(b){return '<div class="finding"><span class="pill bad">!</span> '+esc(b)+"</div>"}).join(""):"<p>"+T.none+"</p>")+ctas(bad.length>0,false);
  o.hidden=false;document.getElementById("self-title").focus()})}
});
})();
