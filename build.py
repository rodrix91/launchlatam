#!/usr/bin/env python3
"""LaunchLatam static site generator. Run: python3 build.py -> writes ./site"""
import json, os, html, datetime
BASE = os.environ.get("BASE", "https://rodrix91.github.io/launchlatam")
ROOT = os.environ.get("OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "site"))
TODAY = datetime.date.today().isoformat()
MAIL = "rodrixlabs@mail.grokbot.com"
W = {  # Whop checkout links
 "fix": "https://whop.com/checkout/plan_zaTKde6gNjQM2",
 "l149": "https://whop.com/checkout/plan_klbC3rVIhgyog",
 "l299": "https://whop.com/checkout/plan_CcT1YHEXdjCOq",
 "l499": "https://whop.com/checkout/plan_2WjdjdlCxW2uV",
 "m29": "https://whop.com/checkout/plan_GV6POEXZk97P9",
 "m79": "https://whop.com/checkout/plan_aZyftwaVpIhup",
 "news": "https://whop.com/checkout/plan_rO1ouDQJcQy2D",
}
SRC = {
 "sym": "https://www.symbioticsec.ai/blog/we-scanned-1-072-vibe-coded-apps-98-had-security-flaws",
 "cve": "https://mattpalmer.io/posts/2025/05/statement-on-CVE-2025-48757/",
 "stripe": "https://stripe.com/global",
}
LOGO = '<svg viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-dasharray="4 3"/><path d="M11 25 L20 10 L29 25 Z" fill="#E2522B"/><path d="M14 29h12" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>'
PERSON = {"@type":"Person","name":"Rodrigo Pantoja Navajas","jobTitle":"Data Science Manager","url":BASE+"/sobre/","sameAs":["https://x.com/RODRX_NOVA","https://www.linkedin.com/in/rodrigo-p-625862153"]}
LOCALES = {"es": ("es-419", "/"), "pt": ("pt-BR", "/pt/"), "en": ("en", "/en/")}

def page(lang, path, title, desc, body, alts=None, schema=None, dock=None, og=None):
    ogi = BASE + (og or "/assets/og.png")
    hl, _ = LOCALES[lang]
    url = BASE + path
    alts = alts or {lang: path}
    alt_links = "".join(f'<link rel="alternate" hreflang="{LOCALES[l][0]}" href="{BASE}{p}">' for l, p in alts.items())
    if "es" in alts: alt_links += f'<link rel="alternate" hreflang="x-default" href="{BASE}{alts["es"]}">'
    lk=[]
    for l in LOCALES:
        cur=' aria-current="true"' if l==lang else ''
        lk.append(f'<a href="{BASE}{alts.get(l, LOCALES[l][1])}" hreflang="{LOCALES[l][0]}" lang="{LOCALES[l][0]}"{cur}>{l.upper()}</a>')
    langs="".join(lk)
    sch = "".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in (schema or []))
    D = DOCK[lang] if dock is None else dock
    home = LOCALES[lang][1]
    items=[]
    for i,(t,h) in enumerate(D):
        if i==len(D)-1: items.append(f'<a class="go" href="{BASE}{home}{h}">{t}</a>')
        else:
            cl=' class="hide-s"' if i in (1,3) else ''
            items.append(f'<a{cl} href="{BASE}{home}{h}"><span class="n">{i+1:02d}</span>{t}</a>')
    nav_lbl={"es":"Principal","pt":"Principal","en":"Main"}[lang]
    dock_html = f'<nav class="dock" aria-label="{nav_lbl}">' + "".join(items) + '</nav>'

    return f'''<!doctype html><html lang="{hl}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">{alt_links}
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'sha256-PLACEHOLDER'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src https://api.github.com https://raw.githubusercontent.com; form-action 'self'; base-uri 'self'; object-src 'none'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="google-site-verification" content="ZtPoEPg8NinMyCsJ78acEyxd46AO3bJxT2z6dfDGVHA" />
<meta name="theme-color" content="#1E1412"><link rel="icon" href="{BASE}/assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="{BASE}/fonts/bricolage.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{BASE}/assets/site.css">
<meta property="og:type" content="website"><meta property="og:site_name" content="LaunchLatam"><meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{ogi}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:locale" content="{hl.replace('-','_')}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{ogi}">
{sch}<script src="{BASE}/assets/scan.js" defer></script></head><body>
<a class="skip" href="#main">{ {"es":"Saltar al contenido","pt":"Pular para o conteúdo","en":"Skip to content"}[lang] }</a>
<header class="wrap mast"><a class="brand" href="{BASE}{home}">{LOGO}<span>LaunchLatam</span></a><div class="lang" aria-label="Idioma / Language">{langs}</div></header>
<main id="main">{body}</main>{FOOT[lang]}{dock_html}</body></html>'''

DOCK = {
 "es": [("Problema","#problema"),("Cómo funciona","#como"),("Precios","#precios"),("FAQ","#faq"),("Escaneo gratis","#escaneo")],
 "pt": [("Problema","#problema"),("Como funciona","#como"),("Preços","#precios"),("FAQ","#faq"),("Scan grátis","#escaneo")],
 "en": [("Problem","#problema"),("How it works","#como"),("Pricing","#precios"),("FAQ","#faq"),("Free scan","#escaneo")],
}
def foot(lang, tag, news, legal, links):
    return f'''<footer><div class="wrap fgrid"><div><a class="brand" href="{BASE}{LOCALES[lang][1]}" style="color:var(--sal)">{LOGO}<span>LaunchLatam</span></a><p>{tag}</p><p>{news}</p><div class="news"><a class="btn a" href="{W["news"]}" rel="noopener">{ {"es":"Suscribirme gratis","pt":"Assinar grátis","en":"Subscribe free"}[lang] }</a></div></div>
<div><p class="mono">{ {"es":"Recursos","pt":"Recursos","en":"Resources"}[lang] }</p><ul>{links}</ul></div><div><p class="mono">Legal</p><ul>{legal}</ul></div></div>
<div class="wrap"><p style="margin-top:2rem">© 2026 LaunchLatam · <a href="mailto:{MAIL}">{MAIL}</a></p></div></footer>'''
FOOT = {
 "es": foot("es","Dejamos tu app hecha con IA lista para lanzar y cobrar en Latinoamérica.","Boletín semanal: seguridad, cobros y lanzamiento de apps hechas con IA. Sin spam, te das de baja cuando quieras.",
   f'<li><a href="{BASE}/privacidad/">Privacidad</a></li><li><a href="{BASE}/terminos/">Términos</a></li>',
   f'<li><a href="{BASE}/blog/">Blog</a></li><li><a href="{BASE}/sobre/">Sobre nosotros</a></li><li><a href="{BASE}/escaneo/">Escaneo gratis</a></li><li><a href="{BASE}/llms.txt">llms.txt</a></li>'),
 "pt": foot("pt","Deixamos seu app feito com IA pronto para lançar e cobrar na América Latina.","Boletim semanal (em espanhol): segurança, pagamentos e lançamento de apps feitos com IA.",
   f'<li><a href="{BASE}/en/privacy/">Privacidade (EN)</a></li><li><a href="{BASE}/en/terms/">Termos (EN)</a></li>',
   f'<li><a href="{BASE}/pt/blog/">Blog</a></li><li><a href="{BASE}/pt/sobre/">Sobre nós</a></li><li><a href="{BASE}/pt/#escaneo">Scan grátis</a></li>'),
 "en": foot("en","We make your AI-built app ready to launch and get paid in Latin America.","Weekly newsletter (in Spanish): security, payments and launching AI-built apps.",
   f'<li><a href="{BASE}/en/privacy/">Privacy</a></li><li><a href="{BASE}/en/terms/">Terms</a></li>',
   f'<li><a href="{BASE}/en/blog/">Blog</a></li><li><a href="{BASE}/en/about/">About</a></li><li><a href="{BASE}/en/#escaneo">Free scan</a></li>'),
}

# ---------- HOME COPY ----------
C = {
"es": dict(
 title="LaunchLatam · Tu app hecha con IA, lista para cobrar en LatAm",
 desc="Seguridad, Mercado Pago y cumplimiento de datos para apps hechas con Lovable, Bolt, Cursor o Replit. Escaneo gratis, correcciones desde $29.",
 kicker="Aduana para apps hechas con IA",
 h1="Tu app ya funciona. <em>Ahora que pase la aduana.</em>",
 lede="Revisamos, corregimos y dejamos lista para cobrar tu app de Lovable, Bolt, Cursor o Replit: seguridad, Mercado Pago o Pix y lo básico de protección de datos de tu país.",
 c1="Escanear mi repo gratis", c2="Ver precios",
 pp=[("Row Level Security","bad","FALTA"),("Clave service_role","bad","EXPUESTA"),("Cobro local","bad","SOLO STRIPE"),("Política de privacidad","bad","NO HAY"),("Cabeceras CSP","ok","LISTO")],
 stamp="APTA<br>PARA<br>COBRAR",
 pk="01 · Problema", ph="La IA te arma la app en una tarde. El control de aduana no viene incluido.",
 ev=[("98%","de 1.072 apps hechas con IA sobre Supabase tenían al menos una falla de seguridad; 16% tenía una crítica.","Symbiotic Security, junio 2026","sym"),
     ("170","apps de Lovable dejaban leer o escribir su base de datos sin login (10,3% de 1.645 analizadas).","Matt Palmer, CVE-2025-48757","cve"),
     ("2","países de Latinoamérica donde Stripe abre cuentas locales: México y Brasil. El resto queda afuera o paga más.","Stripe Global","stripe")],
 hk="02 · Cómo funciona", hh="Cuatro controles, una sola fila.",
 steps=[("Escaneo gratis","Pegás tu repo público de GitHub. En segundos ves secretos expuestos, tablas sin RLS, cobros y páginas legales que faltan."),
        ("Fix Pack","Por $29 corregimos las fallas críticas y te mandamos un pull request para que revises cada cambio."),
        ("Lanzamiento","Conectamos Mercado Pago, Pix u OXXO, agregamos privacidad y términos para tu país y dejamos el deploy listo."),
        ("Mantenimiento","Cada semana re-escaneamos, parchamos dependencias y te avisamos de cambios normativos. Cancelás cuando quieras.")],
 sk="03 · Escaneo gratis", sh="Escaneá tu repo antes de que lo haga otro.",
 sp="El escaneo corre en tu navegador contra repos públicos de GitHub. Tu código no pasa por nuestros servidores.",
 slab="Repositorio de GitHub", sph="usuario/mi-app", sbtn="Escanear",
 priv="¿Repo privado o sin GitHub?", privp="Usá el chequeo guiado (2 minutos) o escribinos a",
 prk="04 · Precios", prh="Pagás por resultado, no por horas.",
 prp="Precios en USD. Whop acepta tarjeta, Mercado Pago, Pix, OXXO y más según tu país.",
 tiers=[("Fix Pack","29","pago único",["Corrección de hasta 5 fallas críticas del escaneo","Pull request revisable, nada se aplica sin tu OK","Entrega en 72 h hábiles"],"fix","Corregir mi app",False),
        ("Lanzamiento Pro","299","pago único",["Todo el Fix Pack, sin límite de fallas críticas","Mercado Pago, Pix u OXXO + suscripciones","Privacidad y términos para 1 país","Deploy en producción con cabeceras seguras"],"l299","Lanzar mi app",True),
        ("Lanzamiento Regional","499","pago único",["Todo Pro, para hasta 3 países","2 pasarelas de pago locales","Versión en español y portugués","Checklist de cumplimiento por país"],"l499","Lanzar en 3 países",False)],
 ess=("Lanzamiento Esencial","149","Seguridad completa + 1 cobro local + páginas legales básicas.","l149","Elegir Esencial"),
 subs=[("Mantenimiento Base","29","Escaneo semanal, parches de seguridad y dependencias al día.","m29"),("Mantenimiento Pro","79","Todo Base + monitoreo de cobros, cambios normativos y 2 h de mejoras al mes.","m79")],
 mes=" cada 30 días", sub="Suscribirme",
 fk="05 · Preguntas", fh="Preguntas frecuentes",
 faq=[("¿Qué es LaunchLatam?","Un servicio operado por agentes de IA, con revisión y aprobación antes de aplicar cualquier cambio en tu app, que deja apps hechas con Lovable, Bolt, Cursor o Replit listas para lanzar y cobrar en Latinoamérica: seguridad, pagos locales y lo básico de protección de datos."),
      ("¿El escaneo gratis es seguro para mi código?","Sí. Corre en tu navegador y lee solo repos públicos de GitHub mediante la API pública de GitHub. No guardamos ni recibimos tu código. Revisa el código del repo, no tu app en vivo ni tu base de datos."),
      ("¿Tocan mi app sin permiso?","No. Todo cambio llega como pull request en tu repositorio. Vos lo revisás y lo aprobás. Nunca te pedimos la clave service_role ni contraseñas por correo."),
      ("¿Qué pasarelas de pago integran?","Mercado Pago (Argentina, México, Brasil, Chile, Colombia, Perú, Uruguay), Pix en Brasil, OXXO en México y Stripe donde tenga sentido. Elegimos según tu país y el de tus clientes."),
      ("¿Esto reemplaza a un abogado?","No. Agregamos páginas de privacidad y términos basadas en la ley de datos de cada país (por ejemplo LGPD en Brasil o Ley 25.326 en Argentina) y una checklist. Para casos sensibles, como salud o finanzas, te recomendamos revisión legal."),
      ("¿Cuánto tarda?","El Fix Pack, 72 horas hábiles. Un lanzamiento, de 5 a 10 días hábiles según países y pasarelas."),
      ("¿Y si no quedo conforme?","Si no corregimos las fallas acordadas, te devolvemos el dinero del Fix Pack. Las condiciones están en los términos.")],
 ak="06 · Quiénes somos", ah="Un equipo chico, con agentes que no se cansan.",
 ap="LaunchLatam nace en Bolivia, de Rodrigo Pantoja, data scientist manager que construye con agentes de IA todos los días. Los agentes hacen el escaneo y el primer borrador de cada corrección, con revisión y aprobación antes de aplicar cualquier cambio en tu app. Todavía no tenemos clientes que mostrar: preferimos decírtelo a inventarlos.",
 bk="Recursos", bh="Del blog",
),
"pt": dict(
 title="LaunchLatam · Seu app feito com IA, pronto para cobrar na América Latina",
 desc="Segurança, Pix, Mercado Pago e LGPD para apps feitos com Lovable, Bolt, Cursor ou Replit. Scan grátis, correções a partir de US$29.",
 kicker="Alfândega para apps feitos com IA",
 h1="Seu app já funciona. <em>Agora ele passa na alfândega.</em>",
 lede="Revisamos, corrigimos e deixamos seu app do Lovable, Bolt, Cursor ou Replit pronto para cobrar: segurança, Pix ou Mercado Pago e o básico da LGPD.",
 c1="Escanear meu repo grátis", c2="Ver preços",
 pp=[("Row Level Security","bad","FALTA"),("Chave service_role","bad","EXPOSTA"),("Pagamento local","bad","SÓ STRIPE"),("Política de privacidade","bad","NÃO TEM"),("Cabeçalhos CSP","ok","OK")],
 stamp="APTO<br>PARA<br>COBRAR",
 pk="01 · Problema", ph="A IA monta o app em uma tarde. A alfândega não vem incluída.",
 ev=[("98%","de 1.072 apps feitos com IA sobre Supabase tinham ao menos uma falha de segurança; 16% tinham uma crítica.","Symbiotic Security, junho 2026","sym"),
     ("170","apps do Lovable deixavam ler ou gravar o banco sem login (10,3% de 1.645 analisados).","Matt Palmer, CVE-2025-48757","cve"),
     ("2","países da América Latina onde a Stripe abre contas locais: México e Brasil.","Stripe Global","stripe")],
 hk="02 · Como funciona", hh="Quatro controles, uma só fila.",
 steps=[("Scan grátis","Cole seu repo público do GitHub. Em segundos você vê segredos expostos, tabelas sem RLS, pagamentos e páginas legais que faltam."),
        ("Fix Pack","Por US$29 corrigimos as falhas críticas e enviamos um pull request para você revisar."),
        ("Lançamento","Conectamos Pix e Mercado Pago, adicionamos privacidade e termos conforme a LGPD e deixamos o deploy pronto."),
        ("Manutenção","Toda semana re-escaneamos, atualizamos dependências e avisamos sobre mudanças regulatórias.")],
 sk="03 · Scan grátis", sh="Escaneie seu repo antes que outra pessoa o faça.",
 sp="O scan roda no seu navegador sobre repos públicos do GitHub. Seu código não passa pelos nossos servidores.",
 slab="Repositório do GitHub", sph="usuario/meu-app", sbtn="Escanear",
 priv="Repo privado ou sem GitHub?", privp="Use o checklist guiado (2 minutos) ou escreva para",
 prk="04 · Preços", prh="Você paga pelo resultado, não por hora.",
 prp="Preços em USD. A Whop aceita cartão, Pix, Mercado Pago e mais, conforme seu país.",
 tiers=[("Fix Pack","29","pagamento único",["Correção de até 5 falhas críticas do scan","Pull request revisável, nada sem o seu OK","Entrega em 72 h úteis"],"fix","Corrigir meu app",False),
        ("Lançamento Pro","299","pagamento único",["Tudo do Fix Pack, sem limite de falhas críticas","Pix, Mercado Pago + assinaturas","Privacidade e termos (LGPD)","Deploy em produção com cabeçalhos seguros"],"l299","Lançar meu app",True),
        ("Lançamento Regional","499","pagamento único",["Tudo do Pro, para até 3 países","2 gateways de pagamento locais","Versão em português e espanhol","Checklist de conformidade por país"],"l499","Lançar em 3 países",False)],
 ess=("Lançamento Essencial","149","Segurança completa + 1 pagamento local + páginas legais básicas.","l149","Escolher Essencial"),
 subs=[("Manutenção Base","29","Scan semanal, patches de segurança e dependências em dia.","m29"),("Manutenção Pro","79","Tudo do Base + monitoramento de pagamentos, mudanças regulatórias e 2 h de melhorias por mês.","m79")],
 mes=" a cada 30 dias", sub="Assinar",
 fk="05 · Perguntas", fh="Perguntas frequentes",
 faq=[("O que é a LaunchLatam?","Um serviço operado por agentes de IA, com revisão e aprovação antes de aplicar qualquer mudança no seu app, que deixa apps feitos com Lovable, Bolt, Cursor ou Replit prontos para lançar e cobrar na América Latina."),
      ("O scan grátis é seguro para o meu código?","Sim. Ele roda no seu navegador e lê apenas repos públicos pela API pública do GitHub. Não recebemos nem guardamos seu código."),
      ("Vocês mexem no app sem permissão?","Não. Toda mudança chega como pull request no seu repositório, e você aprova."),
      ("Quais meios de pagamento vocês integram?","Pix e Mercado Pago no Brasil, Mercado Pago no resto da região, OXXO no México e Stripe quando faz sentido."),
      ("Isso substitui um advogado?","Não. Criamos páginas de privacidade e termos com base na LGPD e um checklist. Para dados sensíveis, recomendamos revisão jurídica."),
      ("Quanto tempo leva?","Fix Pack: 72 horas úteis. Lançamento: 5 a 10 dias úteis.")],
 ak="06 · Quem somos", ah="Uma equipe pequena, com agentes que não se cansam.",
 ap="A LaunchLatam nasceu na Bolívia, criada por Rodrigo Pantoja, gerente de ciência de dados que constrói com agentes de IA todos os dias. Os agentes fazem o scan e o primeiro rascunho de cada correção, com revisão e aprovação antes de aplicar qualquer mudança no seu app. Ainda não temos clientes para mostrar, e preferimos dizer isso a inventá-los.",
 bk="Recursos", bh="Do blog (em espanhol)",
),
"en": dict(
 title="LaunchLatam · Make your AI-built app ready to get paid in Latin America",
 desc="Security fixes, Mercado Pago and Pix payments, and data-protection basics for apps built with Lovable, Bolt, Cursor or Replit. Free scan, fixes from $29.",
 kicker="Customs check for AI-built apps",
 h1="Your app works. <em>Now get it through customs.</em>",
 lede="We review, fix and make your Lovable, Bolt, Cursor or Replit app ready to charge in Latin America: security, Mercado Pago or Pix, and per-country data-protection basics.",
 c1="Scan my repo free", c2="See pricing",
 pp=[("Row Level Security","bad","MISSING"),("service_role key","bad","EXPOSED"),("Local payments","bad","STRIPE ONLY"),("Privacy policy","bad","NONE"),("CSP headers","ok","READY")],
 stamp="CLEARED<br>TO<br>CHARGE",
 pk="01 · Problem", ph="AI builds the app in an afternoon. Customs isn't included.",
 ev=[("98%","of 1,072 AI-built Supabase apps had at least one security flaw; 16% had a critical one.","Symbiotic Security, June 2026","sym"),
     ("170","Lovable apps let anyone read or write their database without logging in (10.3% of 1,645 analyzed).","Matt Palmer, CVE-2025-48757","cve"),
     ("2","Latin American countries where Stripe offers local accounts: Mexico and Brazil.","Stripe Global","stripe")],
 hk="02 · How it works", hh="Four checkpoints, one line.",
 steps=[("Free scan","Paste your public GitHub repo. In seconds you see exposed secrets, tables without RLS, and missing payments or legal pages."),
        ("Fix Pack","For $29 we fix the critical issues and send a pull request you review."),
        ("Launch","We wire Mercado Pago, Pix or OXXO, add privacy and terms for your country, and ship the deploy."),
        ("Maintenance","Weekly rescans, dependency patches and regulatory alerts. Cancel anytime.")],
 sk="03 · Free scan", sh="Scan your repo before someone else does.",
 sp="The scan runs in your browser against public GitHub repos. Your code never touches our servers.",
 slab="GitHub repository", sph="user/my-app", sbtn="Scan",
 priv="Private repo or no GitHub?", privp="Use the 2-minute guided check, or email",
 prk="04 · Pricing", prh="Pay for outcomes, not hours.",
 prp="Prices in USD. Whop accepts cards, Mercado Pago, Pix, OXXO and more depending on your country.",
 tiers=[("Fix Pack","29","one-time",["Fix up to 5 critical scan findings","Reviewable pull request, nothing ships without your OK","Delivered in 72 business hours"],"fix","Fix my app",False),
        ("Launch Pro","299","one-time",["Everything in Fix Pack, no cap on critical issues","Mercado Pago, Pix or OXXO + subscriptions","Privacy & terms for 1 country","Production deploy with secure headers"],"l299","Launch my app",True),
        ("Regional Launch","499","one-time",["Everything in Pro, for up to 3 countries","2 local payment gateways","Spanish and Portuguese versions","Per-country compliance checklist"],"l499","Launch in 3 countries",False)],
 ess=("Essential Launch","149","Full security + 1 local payment method + basic legal pages.","l149","Choose Essential"),
 subs=[("Maintenance Base","29","Weekly scan, security patches, dependencies kept current.","m29"),("Maintenance Pro","79","Everything in Base + payment monitoring, regulatory changes and 2 h of improvements a month.","m79")],
 mes=" every 30 days", sub="Subscribe",
 fk="05 · Questions", fh="FAQ",
 faq=[("What is LaunchLatam?","An agent-operated service, with review and approval before any change is applied to your app, that makes apps built with Lovable, Bolt, Cursor or Replit ready to launch and get paid in Latin America: security, local payments and data-protection basics."),
      ("Is the free scan safe for my code?","Yes. It runs in your browser and only reads public repos via GitHub's public API. We never receive or store your code. It checks repo code, not your live app or database."),
      ("Will you change my app without permission?","No. Every change arrives as a pull request you review and approve."),
      ("Which payment providers do you integrate?","Mercado Pago across the region, Pix in Brazil, OXXO in Mexico, and Stripe where it fits."),
      ("Does this replace a lawyer?","No. We add privacy and terms pages based on each country's data law (e.g. Brazil's LGPD) plus a checklist. For sensitive data, get legal review."),
      ("How long does it take?","Fix Pack: 72 business hours. Launch: 5–10 business days.")],
 ak="06 · About", ah="A small team, with agents that don't get tired.",
 ap="LaunchLatam was started in Bolivia by Rodrigo Pantoja, a data science manager who builds with AI agents every day. Agents run the scan and draft each fix, with review and approval before any change is applied to your app. We don't have customers to show yet, and we'd rather say so than invent them.",
 bk="Resources", bh="From the blog (Spanish)",
)}

SELF = {
 "es": ("Chequeo guiado",[("¿Activaste Row Level Security en todas las tablas de Supabase?","Activar RLS y políticas por usuario en cada tabla."),("¿Tus claves secretas (service_role, Stripe sk_, OpenAI) están solo en el servidor?","Mover las claves secretas a variables del servidor y rotarlas."),("¿Podés cobrar con un método local de tu país (Mercado Pago, Pix, OXXO)?","Integrar un cobro local."),("¿Tenés política de privacidad y términos publicados?","Publicar privacidad y términos según la ley de tu país."),("¿Confirmás el email de los usuarios al registrarse?","Activar confirmación de email en la autenticación."),("¿Tenés copias de seguridad de la base de datos?","Activar backups automáticos.")],"Sí","No","Ver mi puntaje"),
 "pt": ("Checklist guiado",[("Você ativou Row Level Security em todas as tabelas do Supabase?","Ativar RLS e políticas por usuário em cada tabela."),("Suas chaves secretas (service_role, Stripe sk_, OpenAI) estão só no servidor?","Mover chaves secretas para o servidor e gerar novas."),("Você aceita Pix ou Mercado Pago?","Integrar um pagamento local."),("Você tem política de privacidade e termos (LGPD)?","Publicar privacidade e termos conforme a LGPD."),("Você confirma o email dos usuários no cadastro?","Ativar confirmação de email."),("Você tem backups do banco?","Ativar backups automáticos.")],"Sim","Não","Ver minha pontuação"),
 "en": ("Guided check",[("Is Row Level Security enabled on every Supabase table?","Enable RLS with per-user policies on every table."),("Are secret keys (service_role, Stripe sk_, OpenAI) server-side only?","Move secret keys server-side and rotate them."),("Can customers pay with a local method (Mercado Pago, Pix, OXXO)?","Add a local payment method."),("Do you publish a privacy policy and terms?","Publish privacy and terms per your country's law."),("Do you confirm user emails at signup?","Turn on email confirmation."),("Do you back up your database?","Turn on automated backups.")],"Yes","No","See my score"),
}

def scan_block(lang, c, standalone=False):
    st, qs, y, n, b = SELF[lang]
    fs = "".join(f'<fieldset class="q" data-fix="{html.escape(fix)}"><legend>{html.escape(q)}</legend><label><input type="radio" name="q{i}" value="yes"> {y}</label><label><input type="radio" name="q{i}" value="no"> {n}</label></fieldset>' for i,(q,fix) in enumerate(qs))
    hx = "h1" if standalone else "h2"
    return f'''<section id="escaneo"><div class="wrap"><p class="mono">{c["sk"]}</p><{hx}>{c["sh"]}</{hx}><p class="muted" style="max-width:60ch">{c["sp"]}</p>
<form id="scan-form" class="field" style="max-width:640px" novalidate><label for="repo">{c["slab"]}</label><div style="display:flex;gap:.6rem;flex-wrap:wrap"><input id="repo" name="repo" type="text" inputmode="url" autocomplete="off" spellcheck="false" placeholder="{c["sph"]}" required style="flex:1;min-width:220px"><button class="btn p" type="submit">{c["sbtn"]}</button></div><p id="scan-status" role="status" aria-live="polite" class="mono"></p></form>
<div id="scan-out" class="report" hidden aria-live="polite"></div>
<details style="margin-top:2rem;max-width:760px"><summary>{c["priv"]}</summary><p>{c["privp"]} <a href="mailto:{MAIL}">{MAIL}</a>.</p>
<form id="self-check"><h3>{st}</h3>{fs}<button class="btn p" type="submit">{b}</button></form><div id="self-out" class="report" hidden aria-live="polite"></div></details></div></section>'''

# Blog posts. lang: es|pt|en. tkey groups translations of the same article (drives hreflang).
# To add a PT/EN article: append a dict here and its HTML body to POST_BODIES in content.py (key = slug).
POSTS = [
 dict(lang="es", slug="mercado-pago-en-apps-lovable", tkey="mp-lovable", date="2026-10-31", title="Cómo cobrar con Mercado Pago en una app hecha con Lovable (sin exponer tus claves)", desc="Guía paso a paso para integrar Mercado Pago Checkout Pro en una app de Lovable con Supabase Edge Functions, webhooks y claves seguras."),
 dict(lang="es", slug="checklist-seguridad-apps-vibe-coding", tkey="checklist", date="2026-10-31", title="Checklist de seguridad para apps hechas con IA: 12 controles antes de lanzar", desc="Los 12 controles que tenés que revisar antes de lanzar una app hecha con Lovable, Bolt, Cursor o Replit, con datos de estudios reales."),
 dict(lang="es", slug="stripe-no-funciona-en-mi-pais", tkey="stripe-latam", date="2026-10-31", title="¿Stripe no está disponible en tu país? Opciones para cobrar en Latinoamérica", desc="Qué hacer si Stripe no abre cuentas en tu país: Mercado Pago, dLocal, Paddle, Lemon Squeezy y Whop comparados para creadores latinoamericanos."),
]
BLOG_ROOT = {"es": "/blog/", "pt": "/pt/blog/", "en": "/en/blog/"}
def post_path(p): return BLOG_ROOT[p["lang"]] + p["slug"] + "/"
def post_alts(p): return {q["lang"]: post_path(q) for q in POSTS if q["tkey"] == p["tkey"]}
def posts_for(lang):
    """Native posts first, then Spanish originals with no translation in `lang`."""
    native = [p for p in POSTS if p["lang"] == lang]
    have = {p["tkey"] for p in native}
    return native + [p for p in POSTS if p["lang"] == "es" and lang != "es" and p["tkey"] not in have]
MONTHS = {"es": "ene feb mar abr may jun jul ago sep oct nov dic", "pt": "jan fev mar abr mai jun jul ago set out nov dez", "en": "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec"}
def fdate(d, lang):
    y, m, dd = d.split("-"); mo = MONTHS[lang].split()[int(m)-1]
    return f"{mo} {int(dd)}, {y}" if lang == "en" else f"{int(dd)} {mo} {y}"
BT = {
 "es": dict(t="Blog de LaunchLatam: seguridad, cobros y lanzamiento de apps hechas con IA", d="Guías prácticas en español para lanzar y cobrar apps hechas con Lovable, Bolt, Cursor o Replit en Latinoamérica.", h1="Guías para lanzar y cobrar", other="", home="Inicio",
   ch="¿Querés saber cómo está tu app?", cp="Escaneá tu repo gratis en segundos, sin crear cuenta.", cb="Escaneo gratis →", scan="/escaneo/", faq="Preguntas frecuentes"),
 "pt": dict(t="Blog da LaunchLatam: segurança, pagamentos e lançamento de apps feitos com IA", d="Guias práticos para lançar e cobrar apps feitos com Lovable, Bolt, Cursor ou Replit no Brasil e na América Latina.", h1="Guias para lançar e cobrar", other="Em espanhol", home="Início",
   ch="Quer saber como está o seu app?", cp="Escaneie seu repo grátis em segundos, sem criar conta.", cb="Scan grátis →", scan="/pt/#escaneo", faq="Perguntas frequentes"),
 "en": dict(t="LaunchLatam blog: security, payments and launching AI-built apps", d="Practical guides to launch and get paid with apps built on Lovable, Bolt, Cursor or Replit in Latin America.", h1="Guides to launch and get paid", other="In Spanish", home="Home",
   ch="Want to know how your app is doing?", cp="Scan your repo free in seconds, no account needed.", cb="Free scan →", scan="/en/#escaneo", faq="FAQ"),
}
def card(p, lang, hx="h3", tag=True):
    la = "" if p["lang"] == lang else f' hreflang="{LOCALES[p["lang"]][0]}" lang="{LOCALES[p["lang"]][0]}"'
    k = f'<p class="mono">Blog{" · ES" if p["lang"] != lang else ""}</p>' if tag else ""
    st = ' style="font-size:1.4rem"' if hx == "h2" else ""
    return f'<a class="card" href="{BASE}{post_path(p)}"{la}>{k}<{hx}{st}>{p["title"]}</{hx}><p class="muted">{p["desc"]}</p></a>'

def home(lang):
    c = C[lang]; home_p = LOCALES[lang][1]
    rows = "".join(f'<div class="row"><span>{a}</span><span class="pill {k}">{v}</span></div>' for a,k,v in c["pp"])
    ev = "".join(f'<div class="ev"><b>{n}</b><p>{t}</p><p class="mono"><a href="{SRC[s]}" rel="noopener">{src} ↗</a></p></div>' for n,t,src,s in c["ev"])
    steps = "".join(f'<li><h3>{a}</h3><p class="muted">{b}</p></li>' for a,b in c["steps"])
    tk = ""
    for name, price, per, feats, key, cta, hot in c["tiers"]:
        tk += f'<article class="ticket{" hot" if hot else ""}"><p class="mono">{name}</p><p class="price">${price} <small>{per}</small></p><ul>{"".join(f"<li>{f}</li>" for f in feats)}</ul><a class="btn p" href="{W[key]}" rel="noopener">{cta}</a></article>'
    en, ep, ed, ek, ec = c["ess"]
    subs = "".join(f'<div class="sub"><div><h3>{a} · ${p}{c["mes"]}</h3><p class="muted" style="margin:0">{d}</p></div><a class="btn s" href="{W[k]}" rel="noopener">{c["sub"]}</a></div>' for a,p,d,k in c["subs"])
    subs += f'<div class="sub"><div><h3>{en} · ${ep}</h3><p class="muted" style="margin:0">{ed}</p></div><a class="btn s" href="{W[ek]}" rel="noopener">{ec}</a></div>'
    faq = "".join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in c["faq"])
    blog = "".join(card(p, lang) for p in posts_for(lang)[:3])
    if any(p["lang"] == lang for p in POSTS) and lang != "es": c = dict(c, bh={"pt":"Do blog","en":"From the blog"}[lang])
    body = f'''<div class="wrap hero"><div><span class="kicker mono">{c["kicker"]}</span><h1>{c["h1"]}</h1><p class="lede">{c["lede"]}</p>
<div class="ctas"><a class="btn a" href="#escaneo">{c["c1"]} →</a><a class="btn s" href="#precios">{c["c2"]}</a></div></div>
<div class="passport" aria-hidden="true"><p class="mono" style="margin:0 0 .4rem;opacity:.7">LAUNCH CHECK · LATAM</p>{rows}<div class="stamp">{c["stamp"]}</div></div></div>
<section id="problema" class="band"><div class="wrap"><p class="mono">{c["pk"]}</p><h2>{c["ph"]}</h2><div class="evidence">{ev}</div></div></section>
<section id="como"><div class="wrap"><p class="mono">{c["hk"]}</p><h2>{c["hh"]}</h2><ol class="route">{steps}</ol></div></section>
{scan_block(lang, c)}
<section id="precios" style="background:var(--arena-2)"><div class="wrap"><p class="mono">{c["prk"]}</p><h2>{c["prh"]}</h2><p class="muted">{c["prp"]}</p><div class="tickets">{tk}</div><div class="subs">{subs}</div></div></section>
<section id="faq"><div class="wrap" style="max-width:860px"><p class="mono">{c["fk"]}</p><h2>{c["fh"]}</h2>{faq}</div></section>
<section id="nosotros" class="band"><div class="wrap"><p class="mono">{c["ak"]}</p><h2>{c["ah"]}</h2><p class="muted" style="max-width:62ch;font-size:1.15rem">{c["ap"]}</p></div></section>
<section><div class="wrap"><p class="mono">{c["bk"]}</p><h2>{c["bh"]}</h2><div class="cards">{blog}</div></div></section>'''
    schema = [
     {"@context":"https://schema.org","@type":"Organization","name":"LaunchLatam","url":BASE+"/","logo":BASE+"/assets/favicon.svg","email":MAIL,"founder":{"@type":"Person","name":"Rodrigo Pantoja Navajas"},"areaServed":"Latin America"},
     {"@context":"https://schema.org","@type":"Service","name":"LaunchLatam","serviceType":"Security, payments and compliance for AI-built apps","provider":{"@type":"Organization","name":"LaunchLatam"},"areaServed":"Latin America",
      "offers":[{"@type":"Offer","name":t[0],"price":t[1],"priceCurrency":"USD","url":W[t[4]]} for t in c["tiers"]]+[{"@type":"Offer","name":s[0],"price":s[1],"priceCurrency":"USD","url":W[s[3]]} for s in c["subs"]]},
     {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in c["faq"]]},
    ]
    return page(lang, home_p, c["title"], c["desc"], body, {l:LOCALES[l][1] for l in LOCALES}, schema)

def write(path, content):
    fp = os.path.join(ROOT, path.strip("/"), "index.html") if not path.endswith((".html",".txt",".xml",".svg",".json",".webmanifest")) else os.path.join(ROOT, path.strip("/"))
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w", encoding="utf-8").write(content)

def prose_page(lang, path, title, desc, inner, alts=None, schema=None, og=None):
    return page(lang, path, title, desc, f'<article class="wrap prose" style="padding:3rem 0 5rem">{inner}</article>', alts, schema, og=og)

from content import POST_BODIES, LEGAL, POST_FAQ, ABOUT
import sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")); import og
urls = []
for l in LOCALES:
    write(LOCALES[l][1], home(l)); urls.append((LOCALES[l][1], "1.0"))
write("/escaneo/", page("es", "/escaneo/", "Escaneo de seguridad gratis para apps hechas con IA · LaunchLatam", "Escaneá gratis tu repo de GitHub hecho con Lovable, Bolt, Cursor o Replit: secretos expuestos, tablas sin RLS, cobros y páginas legales.", scan_block("es", C["es"], True) + f'<section id="precios"><div class="wrap"><a class="btn p" href="{BASE}/#precios">Ver precios →</a></div></section>'))
urls.append(("/escaneo/","0.9"))
# blog (index per language + articles)
BLOG_ALTS = dict(BLOG_ROOT)
for lang in LOCALES:
    bt = BT[lang]; ps = posts_for(lang)
    nat = "".join(card(p, lang, "h2", False) for p in ps if p["lang"] == lang)
    oth = "".join(card(p, lang, "h2") for p in ps if p["lang"] != lang)
    inner = f'<div class="wrap" style="padding:3rem 0 5rem"><p class="mono">Blog</p><h1>{bt["h1"]}</h1>'
    if nat: inner += f'<div class="cards">{nat}</div>'
    if oth: inner += f'<h2 class="mono" style="margin-top:2.5rem">{bt["other"]}</h2><div class="cards">{oth}</div>'
    inner += '</div>'
    write(BLOG_ROOT[lang], page(lang, BLOG_ROOT[lang], bt["t"], bt["d"], inner, BLOG_ALTS)); urls.append((BLOG_ROOT[lang], "0.8", BLOG_ALTS))
for p in POSTS:
    lang = p["lang"]; bt = BT[lang]; path = post_path(p); alts = post_alts(p)
    sch=[{"@context":"https://schema.org","@type":"Article","headline":p["title"],"description":p["desc"],"inLanguage":LOCALES[lang][0],"datePublished":p["date"],"dateModified":TODAY,"author":PERSON,"publisher":{"@type":"Organization","name":"LaunchLatam"},"mainEntityOfPage":BASE+path}]
    faqs = POST_FAQ.get(p["slug"], [])
    sch.append({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":bt["home"],"item":BASE+LOCALES[lang][1]},
        {"@type":"ListItem","position":2,"name":"Blog","item":BASE+BLOG_ROOT[lang]},
        {"@type":"ListItem","position":3,"name":p["title"],"item":BASE+path}]})
    if faqs: sch.append({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":ans}} for q,ans in faqs]})
    faq_html = (f'<h2>{bt["faq"]}</h2>' + "".join(f'<details><summary>{q}</summary><p>{ans}</p></details>' for q,ans in faqs)) if faqs else ""
    inner = f'<nav aria-label="Breadcrumb" class="mono"><a href="{BASE}{LOCALES[lang][1]}">{bt["home"]}</a> / <a href="{BASE}{BLOG_ROOT[lang]}">Blog</a> · {fdate(p["date"], lang)}</nav><h1 style="font-size:clamp(2rem,4.5vw,3.4rem)">{p["title"]}</h1>' + POST_BODIES[p["slug"]] + faq_html + f'<div class="report"><h3>{bt["ch"]}</h3><p>{bt["cp"]}</p><div class="ctas"><a class="btn a" href="{BASE}{bt["scan"]}">{bt["cb"]}</a><a class="btn s" style="color:var(--sal);border-color:var(--sal)" href="{W["fix"]}" rel="noopener">Fix Pack $29</a></div></div>'
    ogp = f"/assets/og/{lang}-{p['slug']}.png"
    og.make(ROOT + ogp, "LaunchLatam · Blog", p["title"], f"rodrix91.github.io/launchlatam · {fdate(p['date'], lang)}", {"es":"APTA","pt":"APTO","en":"CLEARED"}[lang])
    sch[0]["image"] = BASE + ogp
    write(path, prose_page(lang, path, p["title"]+" · LaunchLatam", p["desc"], inner, alts, schema=sch, og=ogp)); urls.append((path, "0.7", alts))
ABOUT_ALTS = {"es": "/sobre/", "pt": "/pt/sobre/", "en": "/en/about/"}
for lang, (title, desc, kick, inner) in ABOUT.items():
    path = ABOUT_ALTS[lang]; ogp = f"/assets/og/{lang}-about.png"
    og.make(ROOT + ogp, "LaunchLatam · " + kick, title, "rodrix91.github.io/launchlatam", {"es":"APTA","pt":"APTO","en":"CLEARED"}[lang])
    sch = [{"@context":"https://schema.org","@type":"AboutPage","name":title,"url":BASE+path,"inLanguage":LOCALES[lang][0],"mainEntity":{"@id":BASE+"/sobre/#rodrigo"}},
           dict({"@context":"https://schema.org","@id":BASE+"/sobre/#rodrigo"}, **PERSON, worksFor={"@type":"Organization","name":"LaunchLatam","url":BASE+"/"}, address={"@type":"PostalAddress","addressCountry":"BO"})]
    write(path, prose_page(lang, path, title+" · LaunchLatam", desc, inner, ABOUT_ALTS, sch, og=ogp)); urls.append((path, "0.5", ABOUT_ALTS))
for (lang, path, title, inner, alt) in LEGAL:
    write(path, prose_page(lang, path, title+" · LaunchLatam", title+" de LaunchLatam" if lang=="es" else "LaunchLatam "+title, inner, alt)); urls.append((path,"0.3",alt))
write("/gracias/", page("es","/gracias/","Gracias por tu compra · LaunchLatam","Próximos pasos después de tu compra en LaunchLatam.", f'<div class="wrap prose" style="padding:3rem 0 5rem"><p class="mono">Pedido recibido</p><h1>Listo. Tu app ya está en la fila.</h1><p>Recibirás un correo de Whop con tu recibo. En las próximas 24 horas hábiles te escribimos desde <a href="mailto:{MAIL}">{MAIL}</a> para pedirte acceso de lectura al repositorio (como colaborador en GitHub, nunca con contraseñas).</p><p>Mientras tanto: no compartas tu clave <code>service_role</code> con nadie, ni con nosotros.</p><p><a class="btn p" href="{BASE}/">Volver al inicio</a></p></div>'))
open(os.path.join(ROOT,"404.html"),"w").write(page("es","/404.html","Página no encontrada · LaunchLatam","Esta página no existe.", f'<div class="wrap prose" style="padding:4rem 0 6rem"><p class="mono">Error 404</p><h1>Esta ruta no pasó la aduana.</h1><p>La página que buscás no existe o cambió de lugar.</p><p><a class="btn p" href="{BASE}/">Ir al inicio</a> <a class="btn s" href="{BASE}/escaneo/">Escaneo gratis</a></p></div>').replace('<meta name="description"','<meta name="robots" content="noindex"><meta name="description"'))
# sitemap / robots / llms
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
HOME_ALTS = {l: LOCALES[l][1] for l in LOCALES}
for u in urls:
    p, pr = u[0], u[1]
    al = u[2] if len(u) > 2 else (HOME_ALTS if p in HOME_ALTS.values() else None)
    extra = ""
    if al and len(al) > 1:
        extra = "".join(f'<xhtml:link rel="alternate" hreflang="{LOCALES[l][0]}" href="{BASE}{q}"/>' for l, q in al.items())
        if "es" in al: extra += f'<xhtml:link rel="alternate" hreflang="x-default" href="{BASE}{al["es"]}"/>'
    sm += f"<url><loc>{BASE}{p}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority>{extra}</url>"
write("/sitemap.xml", sm+"</urlset>")
write("/robots.txt", f"User-agent: *\nAllow: /\n\n# AI crawlers welcome\nUser-agent: GPTBot\nAllow: /\nUser-agent: ClaudeBot\nAllow: /\nUser-agent: PerplexityBot\nAllow: /\nUser-agent: Google-Extended\nAllow: /\nUser-agent: OAI-SearchBot\nAllow: /\nUser-agent: ChatGPT-User\nAllow: /\nUser-agent: Perplexity-User\nAllow: /\nUser-agent: Applebot-Extended\nAllow: /\nUser-agent: Bingbot\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
c=C["es"]
llms = f"""# LaunchLatam

> LaunchLatam makes apps built with AI tools (Lovable, Bolt, Cursor, Replit) ready to launch and get paid in Latin America: security fixes, local payments (Mercado Pago, Pix, OXXO) and per-country data-protection basics, then ongoing maintenance. Agent-operated, with review and approval before any change is applied to the client's app. Founded in Bolivia by Rodrigo Pantoja. Languages: Spanish (primary), Portuguese, English.

## Offers (USD)
- Free scan: browser-based scan of a public GitHub repo (exposed secrets, Supabase tables without Row Level Security, payments, legal pages): {BASE}/escaneo/
- Fix Pack, $29 one-time: fix up to 5 critical findings via pull request: {W['fix']}
- Essential Launch, $149: {W['l149']}
- Launch Pro, $299: {W['l299']}
- Regional Launch (up to 3 countries), $499: {W['l499']}
- Maintenance Base, $29 every 30 days: {W['m29']}
- Maintenance Pro, $79 every 30 days: {W['m79']}

## Key pages
- [Home (es)]({BASE}/) · [Português]({BASE}/pt/) · [English]({BASE}/en/)
- [Blog (es)]({BASE}/blog/) · [Blog (pt)]({BASE}/pt/blog/) · [Blog (en)]({BASE}/en/blog/)
""" + "".join(f"- [{p['title']}]({BASE}{post_path(p)}) ({p['lang']}): {p['desc']}\n" for p in POSTS) + f"""
## FAQ
""" + "".join(f"- **{q}** {a}\n" for q,a in C["en"]["faq"]) + f"""
## Preguntas frecuentes (es)
""" + "".join(f"- **{q}** {a}\n" for q,a in C["es"]["faq"]) + """
## Perguntas frequentes (pt)
""" + "".join(f"- **{q}** {a}\n" for q,a in C["pt"]["faq"]) + f"""
## Contact
{MAIL}
"""
write("/llms.txt", llms)
write("/assets/favicon.svg", LOGO.replace('aria-hidden="true"','xmlns="http://www.w3.org/2000/svg"').replace("currentColor","#1E1412"))
write("/site.webmanifest", json.dumps({"name":"LaunchLatam","short_name":"LaunchLatam","start_url":"/launchlatam/","display":"browser","background_color":"#F2DCC0","theme_color":"#1E1412","icons":[{"src":"assets/favicon.svg","sizes":"any","type":"image/svg+xml"}]}))
open(os.path.join(ROOT,".nojekyll"),"w").write("")
# no inline scripts except JSON-LD (not executed): drop the placeholder hash
import glob
for f in glob.glob(ROOT+"/**/*.html", recursive=True):
    s=open(f).read().replace(" 'sha256-PLACEHOLDER'",""); open(f,"w").write(s)
print("built", len(urls), "urls")
