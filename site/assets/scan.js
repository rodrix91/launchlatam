// LaunchLatam free scan: runs 100% in the visitor's browser against PUBLIC GitHub repos.
// Nothing is sent to LaunchLatam servers. Uses api.github.com (60 req/h unauthenticated) + raw.githubusercontent.com.
(function(){
"use strict";
var L=(document.documentElement.lang||"es").slice(0,2);
var T={
es:{bad:"Ingresá un repositorio público de GitHub, por ejemplo usuario/mi-app o https://github.com/usuario/mi-app.",nf:"No encontramos ese repositorio. Puede ser privado o no existir. Hacerlo público en GitHub es opcional: si preferís no publicarlo, usá el chequeo guiado.",rl:"GitHub limitó las consultas desde tu red (60 por hora). Podés esperar a que se libere el cupo o usar el chequeo guiado.",run:"Escaneando",files:"archivos revisados",crit:"Crítico",high:"Alto",med:"Medio",ok:"Bien",none:"No encontramos problemas en lo que pudimos revisar. Esto no garantiza que la app sea segura: no revisamos tu base de datos en vivo ni tu configuración en Supabase.",score:"Puntaje de lanzamiento",cta:"Corregir esto por $29",cta2:"Ver el lanzamiento completo",clean:"El escaneo automático no encontró problemas en lo que revisa; no reemplaza una auditoría completa. Si vas a lanzar o cobrar, podemos dejar lista la seguridad completa, un cobro local y páginas legales básicas.",ctaL:"Lanzamiento Esencial por $149",urg:"Hay hallazgos críticos o altos: conviene corregirlos antes de empezar a cobrar.",rec:"Solo encontramos puntos de severidad media o baja: corregirlos es recomendado, sin urgencia.",ctaN:"Recibir el boletín gratis",title:"Resultado del escaneo",note:"Revisamos el código del repositorio, no la app en vivo. Los hallazgos son automáticos: confirmalos antes de actuar.",ctaG:"Hacer el chequeo guiado (2 min)",recov:"No pudimos completar el escaneo",rlWait:"El cupo suele liberarse en unos 60 minutos. Es una estimación: GitHub no indicó la hora exacta.",rlLeft:"Podés reintentar en %t (tiempo indicado por GitHub).",rlNow:"Ya podés reintentar el escaneo.",low:"Bajo",info:"Info",uBad:"Ingresá la URL pública de tu app, por ejemplo https://mi-app.lovable.app.",uConsent:"Para revisar una URL tenés que confirmar que la app es tuya o que tenés permiso.",uRun:"Revisando",uJs:"archivos JavaScript revisados",uNote:"Revisamos solo lo público de la app en vivo: la página, hasta 10 archivos JavaScript propios y las cabeceras HTTP. No es una auditoría ni un pentest. Los hallazgos son automáticos: confirmalos antes de actuar.",uBlocked:"Esa dirección no se puede revisar. Solo aceptamos dominios públicos con http o https en los puertos estándar (no IPs, localhost ni redes internas).",uUnreach:"No pudimos abrir la URL: no respondió, tardó más de 8 segundos o redirigió demasiadas veces.",uRl:"Hiciste muchas revisiones seguidas. Probá de nuevo en unos minutos, o usá el chequeo guiado.",uRepo:"Escanear el repo"},
pt:{bad:"Informe um repositório público do GitHub, por exemplo usuario/meu-app ou https://github.com/usuario/meu-app.",nf:"Não encontramos esse repositório. Ele pode ser privado ou não existir. Deixá-lo público no GitHub é opcional: se preferir não publicá-lo, use o checklist guiado.",rl:"O GitHub limitou as consultas da sua rede (60 por hora). Você pode esperar o limite ser liberado ou usar o checklist guiado.",run:"Escaneando",files:"arquivos revisados",crit:"Crítico",high:"Alto",med:"Médio",ok:"Ok",none:"Não encontramos problemas no que conseguimos revisar. Isso não garante que o app seja seguro: não revisamos seu banco ao vivo nem a configuração do Supabase.",score:"Pontuação de lançamento",cta:"Corrigir isso por US$29",cta2:"Ver o lançamento completo",clean:"O scan automático não encontrou problemas no que ele verifica; isso não substitui uma auditoria completa. Se você vai lançar ou cobrar, podemos deixar prontas a segurança completa, um meio de pagamento local e páginas legais básicas.",ctaL:"Lançamento Essencial por US$149",urg:"Há achados críticos ou altos: o ideal é corrigi-los antes de começar a cobrar.",rec:"Encontramos apenas pontos de severidade média ou baixa: corrigi-los é recomendado, sem urgência.",ctaN:"Receber a newsletter grátis",title:"Resultado do scan",note:"Revisamos o código do repositório, não o app ao vivo. Os achados são automáticos: confirme antes de agir.",ctaG:"Fazer o checklist guiado (2 min)",recov:"Não conseguimos concluir o scan",rlWait:"O limite costuma ser liberado em cerca de 60 minutos. Esta é uma estimativa: o GitHub não indicou o horário exato.",rlLeft:"Você pode tentar de novo em %t (tempo informado pelo GitHub).",rlNow:"Você já pode tentar o scan de novo.",low:"Baixo",info:"Info",uBad:"Informe a URL pública do seu app, por exemplo https://meu-app.lovable.app.",uConsent:"Para verificar uma URL, confirme que o app é seu ou que você tem permissão.",uRun:"Verificando",uJs:"arquivos JavaScript verificados",uNote:"Verificamos apenas o que é público no app ao vivo: a página, até 10 arquivos JavaScript próprios e os cabeçalhos HTTP. Não é uma auditoria nem um pentest. Os achados são automáticos: confirme antes de agir.",uBlocked:"Esse endereço não pode ser verificado. Aceitamos apenas domínios públicos com http ou https nas portas padrão (sem IPs, localhost ou redes internas).",uUnreach:"Não conseguimos abrir a URL: ela não respondeu, demorou mais de 8 segundos ou redirecionou vezes demais.",uRl:"Você fez muitas verificações seguidas. Tente de novo em alguns minutos ou use o checklist guiado.",uRepo:"Escanear o repo"},
en:{bad:"Enter a public GitHub repo, e.g. user/my-app or https://github.com/user/my-app.",nf:"We couldn't find that repo. It may be private or it may not exist. Making it public on GitHub is optional: if you'd rather not, use the guided check.",rl:"GitHub rate-limited your network (60 requests/hour). You can wait for the limit to lift, or use the guided check.",run:"Scanning",files:"files checked",crit:"Critical",high:"High",med:"Medium",ok:"Good",none:"We found no problems in what we could check. That doesn't guarantee the app is secure: we don't inspect your live database or Supabase settings.",score:"Launch score",cta:"Fix this for $29",cta2:"See the full launch",clean:"The automated scan found no problems in what it checks; it doesn't replace a full audit. If you're about to launch or charge, we can set up full security, one local payment method and basic legal pages.",ctaL:"Essential Launch for $149",urg:"There are critical or high findings: it's best to fix them before you start charging.",rec:"We only found medium- or low-severity items: fixing them is recommended, not urgent.",ctaN:"Get the free newsletter",title:"Scan result",note:"We check the repository code, not the live app. Findings are automated: confirm them before acting.",ctaG:"Take the guided check (2 min)",recov:"We couldn't complete the scan",rlWait:"The limit usually lifts in about 60 minutes. That's an estimate: GitHub didn't tell us the exact time.",rlLeft:"You can try again in %t (time provided by GitHub).",rlNow:"You can try the scan again now.",low:"Low",info:"Info",uBad:"Enter your app's public URL, e.g. https://my-app.lovable.app.",uConsent:"To check a URL, confirm that you own the app or have permission.",uRun:"Checking",uJs:"JavaScript files checked",uNote:"We only check what is public in the live app: the page, up to 10 of its own JavaScript files and the HTTP headers. It is not an audit or a pentest. Findings are automated: confirm them before acting.",uBlocked:"That address can't be checked. We only accept public domains over http or https on standard ports (no IPs, localhost or internal networks).",uUnreach:"We couldn't open the URL: it didn't respond, took longer than 8 seconds or redirected too many times.",uRl:"You ran many checks in a row. Try again in a few minutes, or use the guided check.",uRepo:"Scan the repo"}
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
var FU={ // T-108 URL scan finding texts (by worker finding id)
supabase_service_role:{es:"Clave service_role de Supabase en el JavaScript público: cualquiera puede saltarse toda la seguridad de tu base. Rotala ya en Supabase.",pt:"Chave service_role do Supabase no JavaScript público: qualquer pessoa ignora toda a segurança do banco. Gere outra já no Supabase.",en:"Supabase service_role key in public JavaScript: anyone can bypass all database security. Rotate it now in Supabase."},
supabase_secret_key:{es:"Clave secreta de Supabase (sb_secret_) en el JavaScript público. Rotala ya.",pt:"Chave secreta do Supabase (sb_secret_) no JavaScript público. Gere outra já.",en:"Supabase secret key (sb_secret_) in public JavaScript. Rotate it now."},
stripe_secret:{es:"Clave secreta de Stripe (live) en el JavaScript público: permite cobrar, reembolsar y leer clientes. Rotala ya en Stripe.",pt:"Chave secreta do Stripe (live) no JavaScript público: permite cobrar, reembolsar e ler clientes. Gere outra já no Stripe.",en:"Live Stripe secret key in public JavaScript: it can charge, refund and read customers. Roll it now in Stripe."},
stripe_test_secret:{es:"Clave secreta de prueba de Stripe en el JavaScript público.",pt:"Chave secreta de teste do Stripe no JavaScript público.",en:"Stripe test secret key in public JavaScript."},
mp_access_token:{es:"Access token de producción de Mercado Pago en el JavaScript público: permite operar tu cuenta. Renovalo ya.",pt:"Access token de produção do Mercado Pago no JavaScript público: permite operar sua conta. Renove já.",en:"Mercado Pago production access token in public JavaScript: it can operate your account. Renew it now."},
mp_test_access_token:{es:"Access token de prueba de Mercado Pago en el JavaScript público.",pt:"Access token de teste do Mercado Pago no JavaScript público.",en:"Mercado Pago test access token in public JavaScript."},
aws_access_key:{es:"ID de clave de acceso de AWS en el JavaScript público. Revisá si la clave secreta también quedó expuesta y desactivala.",pt:"ID de chave de acesso da AWS no JavaScript público. Verifique se a chave secreta também ficou exposta e desative-a.",en:"AWS access key ID in public JavaScript. Check whether the secret key is exposed too and deactivate it."},
openai_key:{es:"Clave de API de OpenAI en el JavaScript público: cualquiera puede gastar tu saldo. Rotala ya.",pt:"Chave de API da OpenAI no JavaScript público: qualquer pessoa pode gastar seu saldo. Gere outra já.",en:"OpenAI API key in public JavaScript: anyone can spend your credit. Rotate it now."},
anthropic_key:{es:"Clave de API de Anthropic en el JavaScript público. Rotala ya.",pt:"Chave de API da Anthropic no JavaScript público. Gere outra já.",en:"Anthropic API key in public JavaScript. Rotate it now."},
github_token:{es:"Token de GitHub en el JavaScript público. Revocalo ya.",pt:"Token do GitHub no JavaScript público. Revogue já.",en:"GitHub token in public JavaScript. Revoke it now."},
private_key:{es:"Clave privada en el JavaScript público.",pt:"Chave privada no JavaScript público.",en:"Private key in public JavaScript."},
google_api_key:{es:"Clave de API de Google en el JavaScript público. Suele ser pública (Maps, Firebase), pero confirmá que esté restringida por dominio y por API.",pt:"Chave de API do Google no JavaScript público. Costuma ser pública (Maps, Firebase), mas confirme que está restrita por domínio e por API.",en:"Google API key in public JavaScript. It is often public (Maps, Firebase), but make sure it is restricted by domain and API."},
supabase_anon_key:{es:"Clave anon de Supabase: es pública por diseño. Tu seguridad depende de que todas las tablas tengan RLS.",pt:"Chave anon do Supabase: é pública por design. Sua segurança depende de todas as tabelas terem RLS.",en:"Supabase anon key: public by design. Your security depends on RLS being on for every table."},
supabase_publishable_key:{es:"Clave publicable de Supabase: es pública por diseño. Revisá que todas las tablas tengan RLS.",pt:"Chave publicável do Supabase: é pública por design. Verifique se todas as tabelas têm RLS.",en:"Supabase publishable key: public by design. Make sure every table has RLS."},
supabase_url:{es:"Proyecto de Supabase detectado.",pt:"Projeto do Supabase detectado.",en:"Supabase project detected."},
stripe_publishable:{es:"Clave publicable de Stripe: es pública por diseño.",pt:"Chave publicável do Stripe: é pública por design.",en:"Stripe publishable key: public by design."},
mp_public_key:{es:"Public key de Mercado Pago: es pública por diseño.",pt:"Public key do Mercado Pago: é pública por design.",en:"Mercado Pago public key: public by design."},
no_https:{es:"La app no usa HTTPS: los datos viajan sin cifrar.",pt:"O app não usa HTTPS: os dados trafegam sem criptografia.",en:"The app doesn't use HTTPS: data travels unencrypted."},
no_http_redirect:{es:"La versión http:// no redirige a https://.",pt:"A versão http:// não redireciona para https://.",en:"The http:// version doesn't redirect to https://."},
https_ok:{es:"HTTPS activo y http:// redirige a https://.",pt:"HTTPS ativo e http:// redireciona para https://.",en:"HTTPS on, and http:// redirects to https://."},
hsts_missing:{es:"Falta la cabecera Strict-Transport-Security (HSTS).",pt:"Falta o cabeçalho Strict-Transport-Security (HSTS).",en:"Missing Strict-Transport-Security (HSTS) header."},
hsts_short:{es:"HSTS con duración corta (menos de 6 meses).",pt:"HSTS com duração curta (menos de 6 meses).",en:"HSTS max-age is short (under 6 months)."},
csp_missing:{es:"Falta la cabecera Content-Security-Policy.",pt:"Falta o cabeçalho Content-Security-Policy.",en:"Missing Content-Security-Policy header."},
csp_weak:{es:"La Content-Security-Policy permite 'unsafe-eval' o scripts de cualquier origen.",pt:"A Content-Security-Policy permite 'unsafe-eval' ou scripts de qualquer origem.",en:"The Content-Security-Policy allows 'unsafe-eval' or scripts from any origin."},
frame_missing:{es:"Sin protección contra clickjacking (X-Frame-Options o frame-ancestors).",pt:"Sem proteção contra clickjacking (X-Frame-Options ou frame-ancestors).",en:"No clickjacking protection (X-Frame-Options or frame-ancestors)."},
nosniff_missing:{es:"Falta X-Content-Type-Options: nosniff.",pt:"Falta X-Content-Type-Options: nosniff.",en:"Missing X-Content-Type-Options: nosniff."},
referrer_missing:{es:"Falta la cabecera Referrer-Policy.",pt:"Falta o cabeçalho Referrer-Policy.",en:"Missing Referrer-Policy header."},
permissions_missing:{es:"Falta la cabecera Permissions-Policy.",pt:"Falta o cabeçalho Permissions-Policy.",en:"Missing Permissions-Policy header."},
pay_local:{es:"Detectamos un cobro local (Mercado Pago / Pix).",pt:"Detectamos um meio de pagamento local (Mercado Pago / Pix).",en:"Local payment method detected (Mercado Pago / Pix)."},
pay_stripe_only:{es:"Solo detectamos Stripe: en LatAm abre cuentas locales solo en México y Brasil. Sumá un método local (Mercado Pago, Pix, OXXO).",pt:"Detectamos só o Stripe: na América Latina, ele só abre contas locais no México e no Brasil. Adicione um meio local (Pix, Mercado Pago).",en:"Only Stripe detected: in LatAm it only offers local accounts in Mexico and Brazil. Add a local method (Mercado Pago, Pix, OXXO)."},
pay_none:{es:"No vimos un sistema de cobro en lo público (puede estar detrás del login).",pt:"Não vimos um sistema de pagamento na parte pública (pode estar atrás do login).",en:"No payment system seen in the public part (it may be behind the login)."},
legal_ok:{es:"Hay enlaces a privacidad o términos.",pt:"Há links para privacidade ou termos.",en:"Privacy or terms links present."},
legal_missing:{es:"No encontramos enlaces a privacidad ni términos. Las leyes de datos de la región (LGPD en Brasil, Ley 25.326 en Argentina) piden informar cómo usás los datos.",pt:"Não encontramos links para privacidade nem termos. A LGPD exige informar como você usa dados pessoais.",en:"No privacy or terms links found. Data laws in the region (Brazil's LGPD, Argentina's Law 25.326) require telling users how you use their data."},
http_status:{es:"La página respondió con el código HTTP ",pt:"A página respondeu com o código HTTP ",en:"The page answered with HTTP status "}
};
function tu(id){var o=FU[id];return o?(o[L]||o.en):id}
var PAT=[["Stripe live",/sk_live_[0-9a-zA-Z]{16,}/],["Stripe test",/sk_test_[0-9a-zA-Z]{16,}/],["OpenAI",/sk-(proj-)?[A-Za-z0-9_-]{32,}/],["Anthropic",/sk-ant-[A-Za-z0-9_-]{20,}/],["AWS",/AKIA[0-9A-Z]{16}/],["GitHub",/gh[pousr]_[A-Za-z0-9]{36}/],["Mercado Pago",/APP_USR-\d{6,}-\d{6}-[a-f0-9]{32}-\d+/],["Private key",/-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----/],["Google API",/AIza[0-9A-Za-z_-]{35}/],["Resend",/re_[A-Za-z0-9]{8}_[A-Za-z0-9]{20,}/]];
var JWT=/eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}/g;
function isServiceRole(j){try{var p=j.split(".")[1].replace(/-/g,"+").replace(/_/g,"/");return /"role"\s*:\s*"service_role"/.test(atob(p+"===".slice((p.length+3)%4)))}catch(e){return false}}
function parse(v){v=(v||"").trim().replace(/\.git$/,"").replace(/\/$/,"");var m=v.match(/^(?:https?:\/\/)?(?:www\.)?github\.com\/([\w.-]+)\/([\w.-]+)/i)||v.match(/^([\w.-]+)\/([\w.-]+)$/);return m?{o:m[1],r:m[2]}:null}
function esc(s){return String(s).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})}
async function gh(u){var r=await fetch("https://api.github.com"+u,{headers:{Accept:"application/vnd.github+json"}});if(r.status===403||r.status===429){var rst=parseInt(r.headers.get("x-ratelimit-reset")||"",10);var e=new Error("rl");e.kind="rl";e.reset=rst>0?rst:0;throw e}if(!r.ok){var e=new Error("nf");e.kind="nf";throw e}return r.json()}
async function scan(repo,out,status){
 var meta=await gh("/repos/"+repo.o+"/"+repo.r);var br=meta.default_branch;
 var tree=await gh("/repos/"+repo.o+"/"+repo.r+"/git/trees/"+encodeURIComponent(br)+"?recursive=1");
 var paths=(tree.tree||[]).filter(function(x){return x.type==="blob"}).map(function(x){return x.path}).filter(function(p){return !/(^|\/)(node_modules|dist|build|\.next|vendor)\//.test(p)});
 var f=[];
 paths.filter(function(p){return /(^|\/)\.env(\.[\w-]+)?$/.test(p)&&!/example|sample|template/i.test(p)}).forEach(function(p){f.push(["crit",t("env")+p,"","env"])});
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
 if(srv)f.push(["crit",t("srv"),"","srv"]);
 Object.keys(secrets).forEach(function(k){f.push([k==="Stripe test"?"high":"crit",t("sec")+k+"): "+secrets[k].slice(0,3).join(", "),"","sec"])});
 noRls=noRls.filter(function(x){return !new RegExp("alter\\s+table\\s+(public\\.)?\"?"+x+"\"?\\s+enable\\s+row\\s+level\\s+security","i").test(joined)});
 if(noRls.length)f.push(["crit",t("rls")+Array.from(new Set(noRls)).slice(0,8).join(", "),"","rls"]);
 if(openPol.length)f.push(["high",t("tru")+openPol.slice(0,3).join(", "),"","tru"]);
 if(debug.length)f.push(["med",t("dbg")+debug.slice(0,3).join(", "),"","dbg"]);
 var hasHdr=paths.some(function(p){return /(^|\/)(_headers|vercel\.json|netlify\.toml)$/.test(p)})&&/content-security-policy/i.test(joined);
 if(!hasHdr)f.push(["med",t("hdr"),"","hdr"]);
 var mp=/mercadopago|mercado-pago|mercado_pago|\bpix\b/i.test(joined),st=/stripe/i.test(joined),pd=/paddle|lemonsqueezy/i.test(joined);
 if(mp)f.push(["ok",t("payOK"),"","payOK"]);else if(st)f.push(["high",t("payS"),"","payS"]);else if(!pd)f.push(["med",t("pay0"),"","pay0"]);
 var leg=paths.some(function(p){return /privac|terms|termin|legal/i.test(p)});
 f.push(leg?["ok",t("legOK"),"","legOK"]:["med",t("leg"),"","leg"]);
 return {f:f,n:n,repo:repo.o+"/"+repo.r,mode:"repo"};
}
// T-101: cookie-less GoatCounter events (no-op if analytics disabled). Only coarse buckets, never repo names/URLs/findings.
function gcEvent(name){try{if(window.goatcounter&&window.goatcounter.count)window.goatcounter.count({path:name,title:name,event:true})}catch(e){}}
function bucket(sc){return sc>=80?"80-100":sc>=50?"50-79":"0-49"}
// Post-scan CTA: findings -> Fix Pack; clean -> Launch or free newsletter (no paid fix offer).
var WL={fix:"https://whop.com/checkout/plan_zaTKde6gNjQM2",launch:"https://whop.com/checkout/plan_klbC3rVIhgyog",news:"https://whop.com/checkout/plan_rO1ouDQJcQy2D"};
function ctas(hasFindings,scanText,sev,pref){pref=pref||"";
 if(hasFindings)return (sev?'<p data-sev="'+sev+'">'+(sev==="urgent"?T.urg:T.rec)+'</p>':'')+'<div class="ctas" data-cta="'+pref+'findings"><a class="btn a" data-gc="fix" href="'+WL.fix+'" rel="noopener">'+T.cta+'</a><a class="btn s" style="color:var(--sal);border-color:var(--sal)" data-gc="plans" href="#precios">'+T.cta2+"</a></div>";
 return (scanText?'<p>'+T.clean+'</p>':'')+'<div class="ctas" data-cta="'+pref+'clean"><a class="btn a" data-gc="launch" href="'+WL.launch+'" rel="noopener">'+T.ctaL+'</a><a class="btn s" style="color:var(--sal);border-color:var(--sal)" data-gc="news" href="'+WL.news+'" rel="noopener">'+T.ctaN+"</a></div>";
}
var retryTimer=null;
function stopRetry(){if(retryTimer){clearInterval(retryTimer);retryTimer=null}}
function fmtWait(sec){var h=Math.floor(sec/3600),m=Math.floor((sec%3600)/60),s=sec%60;function z(n){return (n<10?"0":"")+n}return h?h+":"+z(m)+":"+z(s):m+":"+z(s)}
function retryText(reset){if(!reset)return T.rlWait;var sec=Math.max(0,reset-Math.floor(Date.now()/1000));if(sec<=0)return T.rlNow;return T.rlLeft.replace("%t",fmtWait(sec))}
function startCountdown(reset){stopRetry();retryTimer=setInterval(function(){var el=document.getElementById("scan-retry");if(!el){stopRetry();return}el.textContent=retryText(reset);if(Math.floor(Date.now()/1000)>=reset)stopRetry()},1000)}
function openGuided(){var q=document.getElementById("self-check");if(!q)return;var d=q.closest("details");if(d)d.open=true;var reduce=window.matchMedia&&window.matchMedia("(prefers-reduced-motion: reduce)").matches;q.scrollIntoView({behavior:reduce?"auto":"smooth",block:"start"});var h=q.querySelector("h3");if(h){h.setAttribute("tabindex","-1");h.focus()}}
function isRL(err){return err==="rl"||(err&&err.kind==="rl")}
function recover(kind,reset,out,status){stopRetry();status.textContent="";var h='<h3 tabindex="-1" id="scan-title">'+T.recov+"</h3><p>"+(kind==="rate_limited"?T.rl:T.nf)+"</p>";if(kind==="rate_limited")h+='<p id="scan-retry" class="mono" aria-live="off">'+retryText(reset)+"</p>";h+='<div class="ctas" data-cta="'+kind+'"><a class="btn a" data-gc="guided" href="#self-check">'+T.ctaG+'</a><a class="btn s" style="color:var(--sal);border-color:var(--sal)" data-gc="fix" href="'+WL.fix+'" rel="noopener">'+T.cta+"</a></div>";out.innerHTML=h;out.hidden=false;document.getElementById("scan-title").focus();if(kind==="rate_limited"&&reset)startCountdown(reset)}
function render(res,out,o){o=o||{};
 var w={crit:30,high:15,med:6,low:2,info:0,ok:0},sc=100;res.f.forEach(function(x){sc-=w[x[0]]||0});sc=Math.max(0,sc);
 var lbl={crit:T.crit,high:T.high,med:T.med,low:T.low,info:T.info,ok:T.ok},cls={crit:"bad",high:"bad",med:"bad",low:"bad",info:"info",ok:"ok"};
 var h='<h3 tabindex="-1" id="scan-title">'+T.title+": "+esc(res.repo)+'</h3><p class="mono">'+T.score+": "+sc+"/100 · "+res.n+" "+(o.files||T.files)+"</p>";
 var probs=res.f.filter(function(x){return x[0]!=="ok"&&x[0]!=="info"});
 res.f.forEach(function(x){h+='<div class="finding"><span class="pill '+cls[x[0]]+'">'+lbl[x[0]]+"</span> "+esc(x[1])+(x[2]?' <code>'+esc(x[2])+'</code>':'')+"</div>"});
 h+='<p class="muted" style="color:#CDB59B">'+(o.note||T.note)+'</p>'+ctas(probs.length>0,true,probs.some(function(x){return x[0]==="crit"||x[0]==="high"})?"urgent":"recommended",o.pref)+shareBox();
 lastRes={f:res.f,n:res.n,target:res.repo,mode:res.mode||"repo",sc:sc,files:o.files||T.files};
 out.innerHTML=h;out.hidden=false;document.getElementById("scan-title").focus();
 return sc;
}
// T-111 shareable report + README badge. 100% client-side: builds Markdown from the result already on screen,
// copies it to the clipboard and stores nothing. Evidence stays masked; the badge never shows a score.
var SITE="https://rodrix91.github.io/launchlatam";
var SCANP={es:"/escaneo/",pt:"/pt/",en:"/en/"},SCANH={es:"",pt:"#escaneo",en:"#escaneo"};
var R={
es:{h:"Informe de LaunchLatam",target:"Objetivo",mRepo:"repo público de GitHub",mUrl:"URL pública de la app",mode:"Modo",date:"Fecha",fix:"Cómo corregirlo",ev:"Evidencia (mascarada)",none:"No encontramos problemas en lo que revisa el escaneo.",info:"Información",ok:"Sin problemas detectados",disc:"Chequeo automático, no auditoría.",dRepo:"Revisa solo el código de un repo público de GitHub (no la app en vivo ni la base de datos), puede tener falsos positivos o pasar por alto fallas y no es una garantía de seguridad.",dUrl:"Revisa solo lo que cualquier visitante ve de la app (la página, el JavaScript público y las cabeceras HTTP), puede tener falsos positivos o pasar por alto fallas y no es una garantía de seguridad.",fp:"¿Querés ayuda para corregirlo? Fix Pack, USD 29, pago único: corrección de hasta 5 fallas críticas del escaneo con un pull request revisable.",gen:"Generado con el escaneo gratis de LaunchLatam",bR:"Copiar informe",bB:"Copiar insignia",sh:"Compartir el resultado",shp:"El informe se copia en Markdown, con las claves mascaradas. La insignia para tu README muestra solo «Revisado con LaunchLatam», sin puntaje.",okR:"Informe copiado. Pegalo en un issue, un README o un mensaje.",okB:"Insignia copiada. Pegala en tu README.",fail:"No pudimos copiar automáticamente. Seleccioná el texto de abajo y copialo.",badge:"Revisado con LaunchLatam"},
pt:{h:"Relatório do LaunchLatam",target:"Alvo",mRepo:"repositório público do GitHub",mUrl:"URL pública do app",mode:"Modo",date:"Data",fix:"Como corrigir",ev:"Evidência (mascarada)",none:"Não encontramos problemas no que o scan verifica.",info:"Informação",ok:"Sem problemas detectados",disc:"Verificação automática, não auditoria.",dRepo:"Verifica apenas o código de um repositório público do GitHub (não o app no ar nem o banco de dados), pode ter falsos positivos ou deixar passar falhas e não é uma garantia de segurança.",dUrl:"Verifica apenas o que qualquer visitante vê do app (a página, o JavaScript público e os cabeçalhos HTTP), pode ter falsos positivos ou deixar passar falhas e não é uma garantia de segurança.",fp:"Quer ajuda para corrigir? Fix Pack, US$ 29, pagamento único: correção de até 5 falhas críticas do scan com um pull request revisável.",gen:"Gerado com o scan grátis do LaunchLatam",bR:"Copiar relatório",bB:"Copiar selo",sh:"Compartilhar o resultado",shp:"O relatório é copiado em Markdown, com as chaves mascaradas. O selo para o seu README mostra apenas “Revisado com LaunchLatam”, sem pontuação.",okR:"Relatório copiado. Cole em uma issue, um README ou uma mensagem.",okB:"Selo copiado. Cole no seu README.",fail:"Não conseguimos copiar automaticamente. Selecione o texto abaixo e copie.",badge:"Revisado com LaunchLatam"},
en:{h:"LaunchLatam report",target:"Target",mRepo:"public GitHub repo",mUrl:"public app URL",mode:"Mode",date:"Date",fix:"How to fix",ev:"Evidence (masked)",none:"We found no issues in what the scan checks.",info:"Info",ok:"No issues detected",disc:"Automated check, not an audit.",dRepo:"It only reviews the code of a public GitHub repo (not the live app or the database), may produce false positives or miss issues, and is not a security guarantee.",dUrl:"It only reviews what any visitor sees of the app (the page, public JavaScript and HTTP headers), may produce false positives or miss issues, and is not a security guarantee.",fp:"Want help fixing it? Fix Pack, USD 29, one-time: we fix up to 5 critical scan findings in a reviewable pull request.",gen:"Generated with the LaunchLatam free scan",bR:"Copy report",bB:"Copy badge",sh:"Share the result",shp:"The report is copied as Markdown, with keys masked. The README badge only says “Reviewed with LaunchLatam”, with no score.",okR:"Report copied. Paste it into an issue, a README or a message.",okB:"Badge copied. Paste it into your README.",fail:"We couldn't copy automatically. Select the text below and copy it.",badge:"Reviewed with LaunchLatam"}
}[L]||{};
var SECRET_FIX={es:"Rotá o revocá la clave ya en el panel del proveedor, sacala del código del frontend y usala solo desde el servidor (backend o Edge Function).",pt:"Gere uma nova chave ou revogue a atual já no painel do provedor, tire-a do código do frontend e use-a só no servidor (backend ou Edge Function).",en:"Rotate or revoke the key now in the provider's dashboard, remove it from frontend code and use it only server-side (backend or Edge Function)."};
var HDR_FIX={es:"Configurá una Content-Security-Policy y las demás cabeceras de seguridad en tu hosting (vercel.json, netlify.toml o _headers).",pt:"Configure uma Content-Security-Policy e os demais cabeçalhos de segurança na sua hospedagem (vercel.json, netlify.toml ou _headers).",en:"Set a Content-Security-Policy and the other security headers in your hosting config (vercel.json, netlify.toml or _headers)."};
var PAY_FIX={es:"Si vas a cobrar en LatAm, sumá un método local (Mercado Pago, Pix u OXXO).",pt:"Se for cobrar no Brasil ou na América Latina, adicione um meio local (Pix ou Mercado Pago).",en:"If you will charge in LatAm, add a local method (Mercado Pago, Pix or OXXO)."};
var LEG_FIX={es:"Publicá una política de privacidad y términos de uso y enlazalos desde la app.",pt:"Publique uma política de privacidade e termos de uso e coloque links para eles no app.",en:"Publish a privacy policy and terms of use and link them from the app."};
var RLS_FIX={es:"Activá Row Level Security en cada tabla (alter table … enable row level security) y creá políticas filtradas por auth.uid().",pt:"Ative Row Level Security em cada tabela (alter table … enable row level security) e crie políticas filtradas por auth.uid().",en:"Enable Row Level Security on every table (alter table … enable row level security) and add policies filtered by auth.uid()."};
var FX={
env:{es:"Borrá el archivo del repo, agregalo a .gitignore y rotá todas las claves que contenía: siguen en el historial de git.",pt:"Remova o arquivo do repositório, adicione-o ao .gitignore e gere novas chaves para tudo o que ele continha: elas continuam no histórico do git.",en:"Delete the file from the repo, add it to .gitignore and rotate every key it contained: they remain in the git history."},
sec:SECRET_FIX,
srv:{es:"Rotá la clave en Supabase y usala solo en el servidor o en Edge Functions, nunca en el frontend.",pt:"Gere uma nova chave no Supabase e use-a só no servidor ou em Edge Functions, nunca no frontend.",en:"Rotate the key in Supabase and use it only on the server or in Edge Functions, never in the frontend."},
rls:RLS_FIX,
tru:{es:"Reemplazá using (true) por una condición real, por ejemplo using (auth.uid() = user_id).",pt:"Substitua using (true) por uma condição real, por exemplo using (auth.uid() = user_id).",en:"Replace using (true) with a real condition, e.g. using (auth.uid() = user_id)."},
dbg:{es:"Eliminá esas rutas o protegelas con autenticación antes de publicar.",pt:"Remova essas rotas ou proteja-as com autenticação antes de publicar.",en:"Remove those routes or put them behind authentication before going live."},
hdr:HDR_FIX,pay0:PAY_FIX,payS:PAY_FIX,pay_stripe_only:PAY_FIX,pay_none:PAY_FIX,leg:LEG_FIX,legal_missing:LEG_FIX,
supabase_service_role:SECRET_FIX,supabase_secret_key:SECRET_FIX,stripe_secret:SECRET_FIX,stripe_test_secret:SECRET_FIX,mp_access_token:SECRET_FIX,mp_test_access_token:SECRET_FIX,aws_access_key:SECRET_FIX,openai_key:SECRET_FIX,anthropic_key:SECRET_FIX,github_token:SECRET_FIX,private_key:SECRET_FIX,
google_api_key:{es:"Restringí la clave por dominio (HTTP referrer) y por API en Google Cloud Console.",pt:"Restrinja a chave por domínio (HTTP referrer) e por API no Google Cloud Console.",en:"Restrict the key by domain (HTTP referrer) and by API in Google Cloud Console."},
supabase_anon_key:RLS_FIX,supabase_publishable_key:RLS_FIX,
no_https:{es:"Activá HTTPS en tu hosting; la mayoría lo ofrece sin costo.",pt:"Ative HTTPS na sua hospedagem; a maioria oferece sem custo.",en:"Turn on HTTPS in your hosting; most providers include it at no cost."},
no_http_redirect:{es:"Configurá una redirección 301 de http:// a https://.",pt:"Configure um redirecionamento 301 de http:// para https://.",en:"Set up a 301 redirect from http:// to https://."},
hsts_missing:{es:"Agregá la cabecera Strict-Transport-Security: max-age=31536000; includeSubDomains.",pt:"Adicione o cabeçalho Strict-Transport-Security: max-age=31536000; includeSubDomains.",en:"Add the header Strict-Transport-Security: max-age=31536000; includeSubDomains."},
csp_missing:{es:"Definí una Content-Security-Policy que permita solo tus propios orígenes.",pt:"Defina uma Content-Security-Policy que permita apenas as suas próprias origens.",en:"Define a Content-Security-Policy that only allows your own origins."},
csp_weak:{es:"Quitá 'unsafe-eval' y los comodines (*) de script-src.",pt:"Remova 'unsafe-eval' e os curingas (*) de script-src.",en:"Remove 'unsafe-eval' and wildcards (*) from script-src."},
frame_missing:{es:"Agregá X-Frame-Options: DENY o frame-ancestors 'none' en la CSP.",pt:"Adicione X-Frame-Options: DENY ou frame-ancestors 'none' na CSP.",en:"Add X-Frame-Options: DENY or frame-ancestors 'none' in the CSP."},
nosniff_missing:{es:"Agregá la cabecera X-Content-Type-Options: nosniff.",pt:"Adicione o cabeçalho X-Content-Type-Options: nosniff.",en:"Add the header X-Content-Type-Options: nosniff."},
referrer_missing:{es:"Agregá Referrer-Policy: strict-origin-when-cross-origin.",pt:"Adicione Referrer-Policy: strict-origin-when-cross-origin.",en:"Add Referrer-Policy: strict-origin-when-cross-origin."},
permissions_missing:{es:"Agregá Permissions-Policy y desactivá lo que no usás, por ejemplo camera=(), microphone=(), geolocation=().",pt:"Adicione Permissions-Policy e desative o que não usa, por exemplo camera=(), microphone=(), geolocation=().",en:"Add Permissions-Policy and disable what you don't use, e.g. camera=(), microphone=(), geolocation=()."},
http_status:{es:"Revisá que la URL pública responda con 200.",pt:"Verifique se a URL pública responde com 200.",en:"Make sure the public URL answers with 200."}
};
function fx(id){var o=id&&FX[id];return o?(o[L]||o.en):""}
// Defence in depth: the Worker already masks evidence (first 6 + last 4); mask any long unmasked token again.
function maskEv(s){return String(s||"").replace(/-----BEGIN[^-]*-----[\s\S]*?(-----END[^-]*-----|$)/g,"-----BEGIN…KEY-----").replace(/[A-Za-z0-9_\-+\/=.]{24,}/g,function(m){return /^\/\//.test(m)||/\.(m?js|css|html?)$/.test(m)?m:m.slice(0,6)+"…"+m.slice(-4)})}
var lastRes=null;
function withRef(u,ref){var i=u.indexOf("#"),h=i<0?"":u.slice(i);u=i<0?u:u.slice(0,i);return u+(u.indexOf("?")<0?"?":"&")+"ref="+ref+h}
function scanUrl(ref){return SITE+withRef(SCANP[L]+SCANH[L],ref)}
function badgeSrc(){return SITE+"/assets/badge-"+L+".svg"}
function badgeMd(){return "[!["+R.badge+"]("+badgeSrc()+")]("+scanUrl("badge")+")"}
function md1(s){return String(s).replace(/[\r\n]+/g," ").replace(/([\\`*_[\]<>|])/g,"\\$1")}
function reportMd(r){
 var lbl={crit:T.crit,high:T.high,med:T.med,low:T.low,info:R.info,ok:R.ok},out=[],day=new Date(),z=function(n){return (n<10?"0":"")+n};
 out.push("## "+R.h,"");
 out.push("- **"+R.target+":** "+md1(r.target),"- **"+R.mode+":** "+(r.mode==="url"?R.mUrl:R.mRepo),"- **"+T.score+":** "+r.sc+"/100 ("+r.n+" "+r.files+")","- **"+R.date+":** "+day.getFullYear()+"-"+z(day.getMonth()+1)+"-"+z(day.getDate()),"");
 var probs=r.f.filter(function(x){return x[0]!=="ok"&&x[0]!=="info"});
 if(!probs.length)out.push(R.none,"");
 ["crit","high","med","low","info","ok"].forEach(function(sv){var g=r.f.filter(function(x){return x[0]===sv});if(!g.length)return;
  out.push("### "+lbl[sv]+" ("+g.length+")","");
  g.forEach(function(x){out.push("- "+md1(x[1]));var ev=x[2]?maskEv(x[2]):"";if(ev)out.push("  - "+R.ev+": `"+ev.replace(/`/g,"'")+"`");if(sv!=="ok"){var h=fx(x[3]);if(h)out.push("  - "+R.fix+": "+h)}});
  out.push("")});
 out.push("> **"+R.disc+"** "+(r.mode==="url"?R.dUrl:R.dRepo),"");
 out.push((probs.length?R.fp:R.fp.replace(/^[^?]*\?\s*/,""))+" "+withRef(WL.fix,"report"),"");
 out.push("_"+R.gen+": "+scanUrl("report")+"_");
 return out.join("\n")+"\n";
}
function shareBox(){return '<div class="share"><p class="mono">'+R.sh+'</p><p class="muted">'+R.shp+'</p><div class="share-row"><button type="button" class="btn s" data-share="report">'+R.bR+'</button><button type="button" class="btn s" data-share="badge">'+R.bB+'</button><img src="'+badgeSrc()+'" alt="'+R.badge+'" width="'+({es:198,pt:202,en:205}[L]||205)+'" height="20"></div><p id="share-status" class="share-status" role="status" aria-live="polite"></p></div>'}
async function copyText(txt){
 try{if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(txt);return true}}catch(e){}
 try{var ta=document.createElement("textarea");ta.value=txt;ta.setAttribute("readonly","");ta.style.position="fixed";ta.style.opacity="0";document.body.appendChild(ta);ta.select();var ok=document.execCommand("copy");ta.remove();return ok}catch(e){return false}
}
async function doShare(kind){if(!lastRes)return;var txt=kind==="badge"?badgeMd():reportMd(lastRes),st=document.getElementById("share-status");
 var ok=await copyText(txt);gcEvent((kind==="badge"?"badge_copy/":"report_copy/")+(lastRes.mode==="url"?"url":"repo"));
 if(!st)return;if(ok){st.textContent=kind==="badge"?R.okB:R.okR;var old=st.parentNode.querySelector("textarea.share-fallback");if(old)old.remove()}
 else{st.textContent=R.fail;var ta=st.parentNode.querySelector("textarea.share-fallback");if(!ta){ta=document.createElement("textarea");ta.className="share-fallback";ta.setAttribute("readonly","");ta.setAttribute("aria-label",kind==="badge"?R.bB:R.bR);st.parentNode.appendChild(ta)}ta.value=txt;ta.focus();ta.select()}
}
// T-108 URL scan (Level A): calls the passive Worker. Mode exists only if the build set a worker origin.
var SEVMAP={critical:"crit",high:"high",medium:"med",low:"low",info:"info",ok:"ok"};
function urlResult(r){
 var f=(r.findings||[]).map(function(x){var ev=[x.ev,x.where].filter(Boolean).join(" · ");return [SEVMAP[x.sev]||"info",tu(x.id)+(x.id==="http_status"?x.ev:""),x.id==="http_status"||x.id==="pay_local"||x.id==="pay_stripe_only"?"":maskEv(ev),x.id]});
 return {f:f,n:(r.scanned&&r.scanned.js)||0,repo:(r.target&&r.target.host)||"",mode:"url"};
}
function urlRecover(kind,out,status){stopRetry();status.textContent="";var msg=kind==="blocked"?T.uBlocked:kind==="rate_limited"?T.uRl:T.uUnreach;
 out.innerHTML='<h3 tabindex="-1" id="scan-title">'+T.recov+"</h3><p>"+msg+'</p><div class="ctas" data-cta="url_'+kind+'"><a class="btn a" data-gc="guided" href="#self-check">'+T.ctaG+'</a><a class="btn s" style="color:var(--sal);border-color:var(--sal)" data-gc="repo" href="#scan-form">'+T.uRepo+"</a></div>";
 out.hidden=false;document.getElementById("scan-title").focus()}
function setMode(m){var rf=document.getElementById("scan-form"),uf=document.getElementById("url-form");if(!uf)return;rf.hidden=m==="url";uf.hidden=m!=="url";var r=document.querySelector('input[name=scanmode][value="'+m+'"]');if(r)r.checked=true;var out=document.getElementById("scan-out");if(out)out.hidden=true}
async function urlScan(worker,target){
 var ac=new AbortController(),tm=setTimeout(function(){ac.abort()},45000);
 try{var res=await fetch(worker+"/scan?"+new URLSearchParams({url:target,consent:"1"}),{method:"GET",mode:"cors",credentials:"omit",cache:"no-store",referrerPolicy:"no-referrer",signal:ac.signal});
  var j=await res.json().catch(function(){return {ok:false,error:"unreachable"}});return j}
 catch(e){return {ok:false,error:"unreachable"}}finally{clearTimeout(tm)}
}
function urlErrKind(e){return e==="blocked_target"||e==="invalid_url"?"blocked":e==="rate_limited"?"rate_limited":"unreachable"}
document.addEventListener("DOMContentLoaded",function(){
 var form=document.getElementById("scan-form");if(form){
 var out=document.getElementById("scan-out"),status=document.getElementById("scan-status"),btn=form.querySelector("button");
 form.addEventListener("submit",async function(e){e.preventDefault();var repo=parse(form.repo.value);
  if(!repo){status.textContent=T.bad;return}
  btn.disabled=true;status.textContent=T.run+"…";out.hidden=true;stopRetry();gcEvent("scan_run");
  try{var r=await scan(repo,out,status);status.textContent="";gcEvent("scan_result/"+bucket(render(r,out)))}
  catch(err){var rl=isRL(err);recover(rl?"rate_limited":"not_found",rl&&err.reset,out,status);gcEvent("scan_result/"+(rl?"rate_limited":"not_found"))}
  finally{btn.disabled=false}
 });}
 var uf=document.getElementById("url-form"),worker=uf&&uf.getAttribute("data-worker");
 if(uf&&worker){
  document.querySelectorAll("input[name=scanmode]").forEach(function(r){r.addEventListener("change",function(){if(r.checked){setMode(r.value);var s1=document.getElementById("scan-status"),s2=document.getElementById("url-status");s1.textContent="";s2.textContent=""}})});
  var cm=document.querySelector("input[name=scanmode]:checked");if(cm&&cm.value==="url")setMode("url"); // browser may restore the radio on back/forward
  window.addEventListener("pageshow",function(){var c=document.querySelector("input[name=scanmode]:checked");if(c)setMode(c.value)});
  var uout=document.getElementById("scan-out"),ust=document.getElementById("url-status"),ubtn=uf.querySelector("button"),ucb=document.getElementById("url-consent");
  uf.addEventListener("submit",async function(e){e.preventDefault();var v=(uf.appurl.value||"").trim();
   if(!/^(https?:\/\/)?[^\s\/?#]+\.[^\s\/?#]+/i.test(v)){ust.textContent=T.uBad;uf.appurl.focus();return}
   if(!ucb.checked){ust.textContent=T.uConsent;ucb.focus();return}
   ubtn.disabled=true;ust.textContent=T.uRun+"…";uout.hidden=true;gcEvent("url_scan_run");
   try{var j=await urlScan(worker,v);
    if(j&&j.ok){ust.textContent="";gcEvent("url_scan_result/"+bucket(render(urlResult(j),uout,{files:T.uJs,note:T.uNote,pref:"url_"})))}
    else{var k=urlErrKind(j&&j.error);urlRecover(k,uout,ust);gcEvent("url_scan_result/"+k)}}
   finally{ubtn.disabled=false}
  });
 }
 document.addEventListener("click",function(e){var sh=e.target.closest&&e.target.closest("[data-share]");if(sh){e.preventDefault();doShare(sh.getAttribute("data-share"));return}var a=e.target.closest&&e.target.closest("[data-gc]");if(!a)return;var box=a.closest("[data-cta]");gcEvent("cta_click/"+(box?box.getAttribute("data-cta"):"x")+"/"+a.getAttribute("data-gc"));if(a.getAttribute("data-gc")==="guided"){e.preventDefault();openGuided()}else if(a.getAttribute("data-gc")==="repo"){e.preventDefault();setMode("repo");var ri=document.getElementById("repo");if(ri)ri.focus()}});
 var q=document.getElementById("self-check");if(q){q.addEventListener("submit",function(e){e.preventDefault();
  var fs=q.querySelectorAll("fieldset"),bad=[];fs.forEach(function(x){var c=x.querySelector("input:checked");if(!c||c.value==="no")bad.push(x.dataset.fix)});
  var o=document.getElementById("self-out");var sc=Math.round(100*(fs.length-bad.length)/fs.length);
  o.innerHTML='<h3 tabindex="-1" id="self-title">'+T.score+": "+sc+"/100</h3>"+(bad.length?bad.map(function(b){return '<div class="finding"><span class="pill bad">!</span> '+esc(b)+"</div>"}).join(""):"<p>"+T.none+"</p>")+ctas(bad.length>0,false);
  o.hidden=false;document.getElementById("self-title").focus()})}
});
})();
