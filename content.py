# Long-form content for LaunchLatam (blog bodies + legal pages)
B = "https://rodrix91.github.io/launchlatam"
MAIL = "rodrixlabs@mail.grokbot.com"
SYM = "https://www.symbioticsec.ai/blog/we-scanned-1-072-vibe-coded-apps-98-had-security-flaws"
CVE = "https://mattpalmer.io/posts/2025/05/statement-on-CVE-2025-48757/"

POST_BODIES = {
"mercado-pago-en-apps-lovable": f"""
<p>Lovable trae integraciones nativas con Stripe y Paddle. Si vivís en Argentina, Chile, Colombia, Perú o Uruguay, o si tus clientes pagan con Mercado Pago, eso no alcanza. Esta guía muestra cómo integrar <strong>Mercado Pago Checkout Pro</strong> en una app de Lovable con Supabase, sin dejar tu clave secreta en el navegador.</p>
<h2>La regla de oro: dos claves, dos lugares</h2>
<p>Mercado Pago te da dos credenciales en <em>Tus integraciones → Credenciales</em>:</p>
<ul><li><strong>Public key</strong> (empieza con <code>APP_USR-</code> y es corta): puede ir en el frontend.</li><li><strong>Access token</strong> (también empieza con <code>APP_USR-</code>, pero es larga): es secreta. Con ella se puede crear cobros y leer pagos de tu cuenta. <strong>Nunca</strong> va en el código de React.</li></ul>
<p>El error más común en apps hechas con IA es pedirle al asistente “integrá Mercado Pago” y que pegue el access token en un archivo del frontend. Cualquier visitante lo puede leer abriendo las herramientas del navegador.</p>
<h2>Paso 1: guardar el access token como secreto en Supabase</h2>
<p>En tu proyecto de Supabase, andá a <em>Edge Functions → Secrets</em> y creá <code>MP_ACCESS_TOKEN</code>. También podés hacerlo desde la terminal:</p>
<pre><code>supabase secrets set MP_ACCESS_TOKEN=APP_USR-xxxxxxxx</code></pre>
<h2>Paso 2: una Edge Function que crea la preferencia de pago</h2>
<p>Checkout Pro funciona con “preferencias”: tu servidor le dice a Mercado Pago qué se vende y cuánto cuesta, y Mercado Pago devuelve un link de pago. El precio se define en el servidor, no en el navegador, para que nadie pueda cambiarlo.</p>
<pre><code>// supabase/functions/crear-pago/index.ts
Deno.serve(async (req) =&gt; {{
  const {{ planId }} = await req.json();
  const PLANES = {{ pro: {{ title: "Plan Pro", price: 9900 }} }}; // precio en tu moneda
  const plan = PLANES[planId];
  if (!plan) return new Response("Plan inválido", {{ status: 400 }});
  const r = await fetch("https://api.mercadopago.com/checkout/preferences", {{
    method: "POST",
    headers: {{
      Authorization: `Bearer ${{Deno.env.get("MP_ACCESS_TOKEN")}}`,
      "Content-Type": "application/json",
    }},
    body: JSON.stringify({{
      items: [{{ title: plan.title, quantity: 1, unit_price: plan.price, currency_id: "ARS" }}],
      back_urls: {{ success: "https://tuapp.com/gracias" }},
      notification_url: "https://TU-PROYECTO.supabase.co/functions/v1/webhook-mp",
    }}),
  }});
  const pref = await r.json();
  return Response.json({{ url: pref.init_point }});
}});</code></pre>
<p>En el frontend, el botón “Pagar” solo llama a esta función y redirige a <code>url</code>.</p>
<h2>Paso 3: confirmar el pago con un webhook (no con la URL de regreso)</h2>
<p>Que el usuario vuelva a <code>/gracias</code> <strong>no prueba</strong> que pagó: cualquiera puede escribir esa URL. La fuente de verdad es la notificación que Mercado Pago envía a tu <code>notification_url</code>. En el webhook:</p>
<ol><li>Leé el <code>id</code> del pago que llega en la notificación.</li><li>Consultá <code>GET https://api.mercadopago.com/v1/payments/{{id}}</code> con tu access token.</li><li>Si <code>status</code> es <code>approved</code>, activá el plan del usuario en tu tabla.</li><li>Validá la firma del encabezado <code>x-signature</code> con la clave secreta de webhooks que te da Mercado Pago, para descartar notificaciones falsas.</li></ol>
<h2>Paso 4: proteger la tabla de suscripciones</h2>
<p>Si guardás el plan del usuario en una tabla <code>subscriptions</code>, activá Row Level Security y dejá que <strong>solo</strong> la Edge Function (con la clave de servicio, del lado del servidor) pueda escribir. Si no, un usuario podría marcarse a sí mismo como “pro” desde el navegador.</p>
<pre><code>alter table public.subscriptions enable row level security;
create policy "leer la propia" on public.subscriptions
  for select using ((select auth.uid()) = user_id);
-- sin políticas de insert/update: solo el servidor escribe</code></pre>
<h2>Checklist final</h2>
<ul><li>El access token está solo en secretos de Supabase.</li><li>El precio se define en el servidor.</li><li>El plan se activa por webhook, no por la URL de regreso.</li><li>La tabla de suscripciones tiene RLS y nadie puede escribirla desde el navegador.</li><li>Probaste con las credenciales de prueba antes de pasar a producción.</li></ul>
<p>Si preferís que lo hagamos nosotros, el <a href="{B}/#precios">Lanzamiento Pro</a> incluye Mercado Pago, suscripciones y webhook verificado, entregado como pull request.</p>
""",
"checklist-seguridad-apps-vibe-coding": f"""
<p>En junio de 2026, Symbiotic Security escaneó 1.072 apps hechas con Lovable, v0, Bolt.new, Replit y Windsurf sobre Supabase. El 98% tenía al menos una falla y el 16% tenía una crítica; 172 sitios permitían borrar registros sin iniciar sesión (<a href="{SYM}" rel="noopener">fuente</a>). Un año antes, Matt Palmer había encontrado 170 apps de Lovable con la base de datos abierta, el caso registrado como CVE-2025-48757 (<a href="{CVE}" rel="noopener">fuente</a>).</p>
<p>La buena noticia: la mayoría de esas fallas se corrigen con una lista corta. Estos son los 12 controles que revisamos antes de lanzar.</p>
<h2>Base de datos</h2>
<ol><li><strong>Row Level Security en todas las tablas.</strong> La clave <code>anon</code> de Supabase es pública por diseño: lo que protege tus datos es RLS. Sin RLS, cualquiera con esa clave lee y escribe todo.</li>
<li><strong>Nada de <code>using (true)</code>.</strong> Una política que deja pasar a todos equivale a no tener RLS. Filtrá por <code>auth.uid()</code>.</li>
<li><strong>Columnas sensibles fuera de la API.</strong> Emails, teléfonos o tokens no deberían poder consultarse desde el navegador si no hace falta.</li>
<li><strong>Funciones RPC revisadas.</strong> Una función <code>security definer</code> ignora RLS; asegurate de que valide al usuario.</li></ol>
<h2>Claves y secretos</h2>
<ol start="5"><li><strong>La clave <code>service_role</code> nunca en el frontend.</strong> Salta toda la seguridad. Si alguna vez estuvo en tu repo, rotala.</li>
<li><strong>Ningún <code>.env</code> en GitHub.</strong> Agregalo a <code>.gitignore</code> y revisá el historial.</li>
<li><strong>Claves de OpenAI, Stripe o Mercado Pago solo en el servidor.</strong> Llamá a esas APIs desde Edge Functions, no desde React.</li></ol>
<h2>Autenticación</h2>
<ol start="8"><li><strong>Confirmación de email activada.</strong> Evita cuentas falsas y spam.</li>
<li><strong>Límite de intentos en el login.</strong> Supabase trae límites; no los desactives.</li></ol>
<h2>Navegador y despliegue</h2>
<ol start="10"><li><strong>Cabeceras de seguridad.</strong> Content-Security-Policy, X-Content-Type-Options y Referrer-Policy en tu hosting (Vercel, Netlify o Cloudflare).</li>
<li><strong>Rutas de prueba eliminadas.</strong> Nada de <code>/api/debug</code>, <code>/api/seed</code> ni paneles de admin sin login.</li></ol>
<h2>Legal y cobros</h2>
<ol start="12"><li><strong>Privacidad y términos publicados</strong>, según la ley de tu país: LGPD en Brasil, Ley 25.326 en Argentina, LFPDPPP en México. Si cobrás, el webhook de pagos es el único que activa planes.</li></ol>
<h2>Cómo revisar todo esto en 30 segundos</h2>
<p>Nuestro <a href="{B}/escaneo/">escaneo gratis</a> revisa los puntos 1, 2, 5, 6, 7, 10, 11 y 12 en cualquier repo público de GitHub, desde tu navegador. Si tu repo es privado, el mismo página tiene un chequeo guiado.</p>
""",
"stripe-no-funciona-en-mi-pais": f"""
<p>Si alguna vez intentaste abrir una cuenta de Stripe desde Bolivia, Argentina, Colombia o Perú, ya sabés el final: tu país no aparece en la lista. Según la <a href="https://stripe.com/global" rel="noopener">página de disponibilidad de Stripe</a>, en Latinoamérica solo México y Brasil tienen cuentas locales. Y muchas herramientas de IA, como Lovable, traen integradas justamente Stripe y Paddle.</p>
<p>Estas son las opciones reales para cobrar desde Latinoamérica, y cuándo conviene cada una.</p>
<h2>1. Mercado Pago</h2>
<p><strong>Para quién:</strong> si vendés dentro de Argentina, México, Brasil, Chile, Colombia, Perú o Uruguay. Tus clientes ya lo usan y pueden pagar con saldo, tarjeta local o efectivo.</p>
<p><strong>A tener en cuenta:</strong> necesitás cuenta en el país donde cobrás y la integración es por país. Tiene suscripciones (“preapproval”). Ver nuestra <a href="{B}/blog/mercado-pago-en-apps-lovable/">guía para Lovable</a>.</p>
<h2>2. Merchant of Record: Paddle, Lemon Squeezy, Whop</h2>
<p><strong>Para quién:</strong> si vendés software o productos digitales a todo el mundo y no querés lidiar con impuestos de cada país. El “merchant of record” vende en tu nombre, cobra los impuestos y te paga.</p>
<p><strong>A tener en cuenta:</strong> cobran comisiones más altas que una pasarela directa, revisan tu negocio antes de aprobarte y no todos pagan en todos los países. Revisá en su documentación si pueden enviarte pagos a tu país antes de integrar.</p>
<h2>3. dLocal y pasarelas regionales</h2>
<p><strong>Para quién:</strong> empresas con volumen que necesitan métodos locales en muchos países (Pix, OXXO, PSE, Yape) con una sola integración. Suelen pedir un mínimo de facturación.</p>
<h2>4. Stripe a través de una empresa en otro país</h2>
<p>Algunos fundadores abren una LLC en Estados Unidos con servicios como Stripe Atlas para usar Stripe. Funciona, pero suma costos fijos anuales, obligaciones fiscales en dos países y no resuelve que tus clientes locales prefieran pagar con métodos locales.</p>
<h2>¿Cuál elegir?</h2>
<ul><li><strong>Clientes en un país de Mercado Pago:</strong> Mercado Pago.</li><li><strong>Clientes en Brasil:</strong> Pix (vía Mercado Pago u otra pasarela) además de tarjeta.</li><li><strong>Clientes globales y producto digital:</strong> un merchant of record.</li><li><strong>Ambos:</strong> combiná dos; es lo que hacemos en el <a href="{B}/#precios">Lanzamiento Regional</a>.</li></ul>
<p>Antes de elegir, confirmá dos cosas en la documentación oficial de cada proveedor: que acepta tu país para abrir la cuenta y que puede pagarte a una cuenta bancaria o billetera que tengas.</p>
""",
}

PRIV_ES = f"""<p class="mono">Última actualización: 31 de octubre de 2026</p><h1>Política de privacidad</h1>
<p>LaunchLatam (“nosotros”) respeta tu privacidad. Esta política explica qué datos tratamos y por qué.</p>
<h2>Qué datos recogemos</h2><ul><li><strong>Escaneo gratis:</strong> se ejecuta en tu navegador. El nombre del repositorio y su código se consultan directamente a GitHub y <strong>no</strong> se envían a nuestros servidores.</li><li><strong>Compras y boletín:</strong> los gestiona Whop (whop.com), que procesa tu nombre, email y datos de pago según su propia política de privacidad. Nosotros recibimos tu email, el producto comprado y los datos que escribas en el formulario de compra (por ejemplo, la URL de tu app).</li><li><strong>Correo:</strong> si nos escribís a {MAIL}, guardamos el intercambio para responderte.</li><li><strong>Acceso a tu repositorio:</strong> solo si compraste un servicio y nos invitás como colaborador. Lo usamos únicamente para el trabajo contratado y podés quitar el acceso cuando quieras.</li></ul>
<h2>Qué no hacemos</h2><ul><li>No usamos cookies de seguimiento ni publicidad en este sitio.</li><li>No vendemos tus datos.</li><li>No te pedimos contraseñas ni la clave service_role de Supabase.</li></ul>
<h2>Base legal y conservación</h2><p>Tratamos tus datos para cumplir el servicio que contrataste y, en el caso del boletín, con tu consentimiento. Conservamos los datos de clientes mientras dure la relación y hasta 5 años después por obligaciones contables.</p>
<h2>Tus derechos</h2><p>Podés pedir acceso, corrección o eliminación de tus datos, y darte de baja del boletín en cualquier momento, escribiendo a {MAIL}. Si estás en Brasil, estos derechos se rigen por la LGPD; en Argentina, por la Ley 25.326; en México, por la LFPDPPP.</p>
<h2>Proveedores</h2><p>GitHub (alojamiento del sitio y escaneo), Whop (pagos y boletín).</p>"""
TERMS_ES = f"""<p class="mono">Última actualización: 31 de octubre de 2026</p><h1>Términos del servicio</h1>
<h2>El servicio</h2><p>LaunchLatam revisa y modifica apps creadas con herramientas de IA para mejorar su seguridad, integrar pagos y agregar páginas legales básicas. El trabajo lo realizan agentes de IA con revisión humana y se entrega como pull request en tu repositorio. Vos decidís si lo aplicás.</p>
<h2>Escaneo gratis</h2><p>Es automático, revisa solo el código de repos públicos y puede tener falsos positivos o pasar por alto fallas. No es una auditoría ni una garantía de seguridad.</p>
<h2>Pagos y reembolsos</h2><p>Los pagos se procesan con Whop en USD. Si no entregamos las correcciones acordadas del Fix Pack o del Lanzamiento, te reembolsamos el monto pagado por ese servicio. Las suscripciones de mantenimiento se pueden cancelar en cualquier momento desde Whop y no se cobran meses siguientes.</p>
<h2>Tus responsabilidades</h2><p>Sos responsable de revisar y aprobar los cambios, de tus credenciales y de cumplir la ley aplicable a tu negocio. Las páginas legales que entregamos son plantillas base y no constituyen asesoramiento jurídico.</p>
<h2>Límite de responsabilidad</h2><p>Nuestra responsabilidad total por cualquier reclamo se limita al monto que pagaste por el servicio en cuestión durante los últimos 12 meses.</p>
<h2>Contacto</h2><p>{MAIL}</p>"""
PRIV_EN = f"""<p class="mono">Last updated: October 31, 2026</p><h1>Privacy policy</h1>
<p>The free scan runs in your browser: repo names and code are fetched directly from GitHub and are <strong>not</strong> sent to our servers. Purchases and newsletter signups are handled by Whop (whop.com), which processes your name, email and payment data under its own policy; we receive your email, the product bought, and anything you type in the checkout form. If you email {MAIL}, we keep the thread to reply. Repository access is used only for work you purchased and can be revoked at any time.</p>
<p>We use no tracking or advertising cookies, we don't sell data, and we never ask for passwords or your Supabase service_role key. You can request access, correction or deletion, or unsubscribe, by emailing {MAIL}. Rights are governed by applicable law, including Brazil's LGPD, Argentina's Law 25.326 and Mexico's LFPDPPP. Processors: GitHub (hosting), Whop (payments, newsletter).</p>"""
TERMS_EN = f"""<p class="mono">Last updated: October 31, 2026</p><h1>Terms of service</h1>
<p>LaunchLatam reviews and modifies AI-built apps to improve security, integrate payments and add basic legal pages. Work is done by AI agents with human review and delivered as a pull request you choose whether to merge.</p>
<p>The free scan is automated, covers public repo code only, and may produce false positives or miss issues. It is not an audit or a security guarantee.</p>
<p>Payments are processed by Whop in USD. If we don't deliver the agreed fixes for a Fix Pack or Launch, we refund that service. Maintenance subscriptions can be canceled anytime in Whop. Legal pages we provide are templates, not legal advice. Our total liability is limited to what you paid for the service in the last 12 months. Contact: {MAIL}.</p>"""
LEGAL = [
 ("es","/privacidad/","Política de privacidad",PRIV_ES,{"es":"/privacidad/","en":"/en/privacy/"}),
 ("es","/terminos/","Términos del servicio",TERMS_ES,{"es":"/terminos/","en":"/en/terms/"}),
 ("en","/en/privacy/","Privacy policy",PRIV_EN,{"es":"/privacidad/","en":"/en/privacy/"}),
 ("en","/en/terms/","Terms of service",TERMS_EN,{"es":"/terminos/","en":"/en/terms/"}),
]

# Per-article FAQ (rendered visibly on the article and as FAQPage JSON-LD). Key = slug.
POST_FAQ = {
"mercado-pago-en-apps-lovable": [
 ("¿Puedo poner el access token de Mercado Pago en el frontend de Lovable?", "No. El access token es secreto: con él se pueden crear cobros y leer pagos de tu cuenta. Guardalo como secreto en Supabase (MP_ACCESS_TOKEN) y usalo solo desde una Edge Function. En el frontend solo va la public key."),
 ("¿Cómo sé si un pago de Mercado Pago fue aprobado?", "Con el webhook, no con la URL de regreso. Consultá el pago en la API de Mercado Pago con su id, activá el plan solo si el status es approved y validá la firma del encabezado x-signature."),
 ("¿Dónde se define el precio del producto?", "En el servidor, dentro de la Edge Function que crea la preferencia de pago, para que nadie pueda cambiarlo desde el navegador."),
],
"checklist-seguridad-apps-vibe-coding": [
 ("¿La clave anon de Supabase es secreta?", "No. Es pública por diseño. Lo que protege tus datos es Row Level Security con políticas que filtren por auth.uid() en cada tabla."),
 ("¿Qué hago si mi clave service_role estuvo en el repositorio?", "Rotala de inmediato en Supabase, sacala del código y del historial, y usala solo del lado del servidor."),
 ("¿Qué controles revisa el escaneo gratis?", "Los puntos 1, 2, 5, 6, 7, 10, 11 y 12 de la checklist, en cualquier repo público de GitHub, desde tu navegador. Para repos privados hay un chequeo guiado."),
],
"stripe-no-funciona-en-mi-pais": [
 ("¿En qué países de Latinoamérica abre cuentas locales Stripe?", "Según la página de disponibilidad de Stripe, solo en México y Brasil."),
 ("¿Qué uso si vendo dentro de un país con Mercado Pago?", "Mercado Pago: tus clientes ya lo usan y pueden pagar con saldo, tarjeta local o efectivo. Necesitás cuenta en el país donde cobrás."),
 ("¿Qué es un merchant of record?", "Un proveedor como Paddle, Lemon Squeezy o Whop que vende en tu nombre, cobra los impuestos de cada país y te paga. Cobra comisiones más altas y revisa tu negocio antes de aprobarte."),
],
}

# About pages (es /sobre/, pt /pt/sobre/, en /en/about/): title, meta description, kicker, HTML
_X = "https://x.com/RODRX_NOVA"; _LI = "https://www.linkedin.com/in/rodrigo-p-625862153"
def _about(k, h1, lede, h_who, who, h_how, how, h_not, nots, h_c, contact, cta, scan):
    return f"""<p class="mono">{k}</p><h1>{h1}</h1><p style="font-size:1.2rem">{lede}</p>
<h2>{h_who}</h2><p>{who}</p><p class="mono"><a href="{_X}" rel="me noopener">X · @RODRX_NOVA ↗</a> · <a href="{_LI}" rel="me noopener">LinkedIn ↗</a></p>
<h2>{h_how}</h2><ol>{"".join(f"<li>{x}</li>" for x in how)}</ol>
<h2>{h_not}</h2><ul>{"".join(f"<li>{x}</li>" for x in nots)}</ul>
<h2>{h_c}</h2><p>{contact} <a href="mailto:{MAIL}">{MAIL}</a>.</p><p><a class="btn a" href="{B}{scan}">{cta}</a></p>"""
ABOUT = {
"es": ("Sobre LaunchLatam", "Quién está detrás de LaunchLatam y cómo trabajamos: agentes de IA con revisión y aprobación antes de aplicar cualquier cambio en tu app, para lanzar y cobrar apps hechas con IA en Latinoamérica.", "Sobre nosotros",
 _about("Sobre nosotros", "Una aduana chica, <em>con tu OK al final de la fila.</em>",
  "LaunchLatam deja apps hechas con Lovable, Bolt, Cursor o Replit listas para lanzar y cobrar en Latinoamérica: seguridad, pagos locales y lo básico de protección de datos.",
  "Quién está detrás", "LaunchLatam nace en Bolivia, de Rodrigo Pantoja Navajas, data scientist manager que construye con agentes de IA todos los días. Todavía no tenemos clientes que mostrar: preferimos decírtelo a inventarlos.",
  "Cómo trabajamos", ["Los agentes de IA escanean tu repo y preparan el primer borrador de cada corrección.", "Con revisión y aprobación antes de aplicar cualquier cambio en tu app.", "Todo llega como pull request: vos decidís si lo aplicás."],
  "Lo que no hacemos", ["No te pedimos contraseñas ni la clave service_role.", "No usamos cookies de seguimiento ni publicidad.", "No inventamos testimonios ni clientes."],
  "Contacto", "Escribinos a", "Escaneo gratis →", "/escaneo/")),
"pt": ("Sobre a LaunchLatam", "Quem está por trás da LaunchLatam e como trabalhamos: agentes de IA com revisão e aprovação antes de aplicar qualquer mudança no seu app, para lançar e cobrar apps feitos com IA na América Latina.", "Sobre nós",
 _about("Sobre nós", "Uma alfândega pequena, <em>com o seu OK no fim da fila.</em>",
  "A LaunchLatam deixa apps feitos com Lovable, Bolt, Cursor ou Replit prontos para lançar e cobrar na América Latina: segurança, pagamentos locais e o básico da LGPD.",
  "Quem está por trás", "A LaunchLatam nasceu na Bolívia, criada por Rodrigo Pantoja Navajas, gerente de ciência de dados que constrói com agentes de IA todos os dias. Ainda não temos clientes para mostrar, e preferimos dizer isso a inventá-los.",
  "Como trabalhamos", ["Agentes de IA escaneiam seu repo e preparam o primeiro rascunho de cada correção.", "Com revisão e aprovação antes de aplicar qualquer mudança no seu app.", "Tudo chega como pull request: você decide se aplica."],
  "O que não fazemos", ["Não pedimos senhas nem a chave service_role.", "Não usamos cookies de rastreamento nem publicidade.", "Não inventamos depoimentos nem clientes."],
  "Contato", "Escreva para", "Scan grátis →", "/pt/#escaneo")),
"en": ("About LaunchLatam", "Who is behind LaunchLatam and how we work: AI agents, with review and approval before any change is applied to your app, to launch and get paid with AI-built apps in Latin America.", "About",
 _about("About", "A small customs office, <em>with your OK at the end of the line.</em>",
  "LaunchLatam makes apps built with Lovable, Bolt, Cursor or Replit ready to launch and get paid in Latin America: security, local payments and data-protection basics.",
  "Who's behind it", "LaunchLatam was started in Bolivia by Rodrigo Pantoja Navajas, a data science manager who builds with AI agents every day. We don't have customers to show yet, and we'd rather say so than invent them.",
  "How we work", ["AI agents scan your repo and draft each fix.", "With review and approval before any change is applied to your app.", "Everything arrives as a pull request: you decide whether to merge."],
  "What we don't do", ["We never ask for passwords or your service_role key.", "No tracking or advertising cookies.", "No made-up testimonials or customers."],
  "Contact", "Email us at", "Free scan →", "/en/#escaneo")),
}
