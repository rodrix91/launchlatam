# Long-form content for LaunchLatam (blog bodies + legal pages)
B = "https://rodrix91.github.io/launchlatam"
MAIL = "rodrixlabs@mail.grokbot.com"
SYM = "https://www.symbioticsec.ai/blog/we-scanned-1-072-vibe-coded-apps-98-had-security-flaws"
CVE = "https://mattpalmer.io/posts/2025/05/statement-on-CVE-2025-48757/"

POST_BODIES = {
"service-role-expuesta-supabase": """
<div class="report" style="margin:1.5rem 0"><p><strong>Respuesta corta:</strong> si tu clave <code>service_role</code> (o una clave secreta <code>sb_secret_</code>) apareció en el frontend, en un repositorio o en un commit, dala por comprometida. Esa clave elude Row Level Security y da acceso completo a tu proyecto. Primero cortá la vía de filtración, después creá una clave secreta nueva en <em>Settings → API Keys</em>, actualizá el servidor y retirá la clave vieja. Si era una <code>service_role</code> heredada, también tenés que reemplazar la <code>anon</code> en el cliente: al desactivar las claves legacy se apagan las dos.</p></div>
<p>En una app hecha con Lovable, Bolt, Cursor o Replit, la clave que va al navegador tiene que ser solo la pública (<code>anon</code> o, en proyectos nuevos, <code>sb_publishable_</code>). La de servicio es otra: según la <a href="https://supabase.com/docs/guides/getting-started/api-keys" rel="noopener">documentación de claves de Supabase</a>, elude Row Level Security y no debe salir de un servidor que controles. Si llegó al frontend o a un repo, no alcanza con borrarla del archivo. Hay que rotarla.</p>
<h2>Qué está en juego</h2>
<p>Supabase está dejando de usar las claves <code>anon</code> y <code>service_role</code> para finales de 2026, a favor de las claves <code>sb_publishable_</code> y <code>sb_secret_</code> (<a href="https://supabase.com/docs/guides/getting-started/api-keys" rel="noopener">fuente</a>). Mientras tanto, muchas apps hechas con IA siguen usando las claves legacy. La <code>service_role</code> es un JWT: si está en el cliente, cualquiera puede copiarla y hablarle a tu API con privilegios de servidor. Las claves secretas nuevas no funcionan en el navegador (Supabase responde <code>401</code> según el encabezado <code>User-Agent</code>), pero igual no van en el código ni en el frontend.</p>
<p>Este control es el punto 5 de nuestra <a href="https://rodrix91.github.io/launchlatam/blog/checklist-seguridad-apps-vibe-coding/">checklist de seguridad</a>. Después de rotar, conviene revisar que las tablas tengan RLS, porque la clave pública va a seguir en el cliente: <a href="https://rodrix91.github.io/launchlatam/blog/rls-supabase-lovable/">cómo saber si tu base está abierta y cerrarla</a>.</p>
<h2>Minutos 0 a 10: confirmá la filtración y cortá la vía</h2>
<p>La <a href="https://supabase.com/docs/guides/security/rotate-leaked-api-keys" rel="noopener">guía oficial para rotar una clave filtrada</a> pide corregir la causa raíz <strong>antes</strong> de rotar. Si no, la clave nueva se vuelve a filtrar igual.</p>
<ol>
<li>Buscá en el repo (y en el historial de git) textos como <code>service_role</code>, <code>sb_secret_</code>, <code>SUPABASE_SERVICE_ROLE</code> o variables públicas de frontend (<code>VITE_</code>, <code>NEXT_PUBLIC_</code>, <code>PUBLIC_</code>) que estén cargando la clave de servicio.</li>
<li>Si el repositorio es o fue público, o la clave quedó en un commit aunque después la hayas sacado del archivo, dala por comprometida.</li>
<li>Sacala del código del cliente, de los <code>.env</code> que se hayan subido y de cualquier secreto de Lovable o Bolt que se esté inyectando al navegador. Agregá <code>.env</code> a <code>.gitignore</code> si no estaba.</li>
</ol>
<p>Si tenés indicios de que alguien ya está usando la clave, la misma guía dice que la retires de inmediato, aunque los componentes que todavía la usen dejen de funcionar hasta que la reemplaces.</p>
<h2>Minutos 10 a 45: rotá según la documentación de Supabase</h2>
<p>El procedimiento oficial es: crear una clave secreta nueva, reemplazar la comprometida en toda la aplicación y recién entonces retirar la vieja (<a href="https://supabase.com/docs/guides/security/rotate-leaked-api-keys" rel="noopener">fuente</a>).</p>
<ol>
<li><strong>Creá una clave secreta nueva</strong> en <em>Settings → API Keys</em> del Dashboard (empieza con <code>sb_secret_</code>). No la pegues en el chat del agente ni en un issue.</li>
<li><strong>Reemplazala en todos los lugares del servidor:</strong> secretos de Edge Functions, cron, workers y cualquier webhook de base de datos que la estuviera enviando. Confirmá que ningún componente sigue usando la clave vieja.</li>
<li><strong>Si la filtrada era una <code>service_role</code> legacy, cambiá también la <code>anon</code> del cliente por una clave <code>sb_publishable_</code>.</strong> Al retirar la clave comprometida se desactivan las dos claves legacy, la de servicio y la anónima (<a href="https://supabase.com/docs/guides/security/rotate-leaked-api-keys" rel="noopener">fuente</a>).</li>
<li><strong>Retirá la clave comprometida.</strong> Si es una clave secreta nueva, eliminala (esa acción no se puede deshacer). Si es una <code>anon</code> o <code>service_role</code> legacy, desactivá las claves legacy en la misma pantalla. No las vuelvas a activar: reactivarlas restaura la clave comprometida.</li>
<li><strong>Si era una <code>service_role</code> legacy, revocá también el secreto JWT legacy.</strong> Esas claves son JWTs firmados con ese secreto, y cualquier sistema que todavía lo acepte puede seguir validando la clave filtrada. El detalle está en la <a href="https://supabase.com/docs/guides/auth/signing-keys" rel="noopener">guía de JWT signing keys</a>, enlazada desde el procedimiento de rotación.</li>
</ol>
<h2>Minutos 45 a 60: revisá el daño y el RLS</h2>
<p>Quien tuvo la clave de servicio pudo leer o cambiar datos, aunque después la hayas rotado. Revisá en el Dashboard si hubo actividad que no reconocés y confirmá que cada tabla del esquema <code>public</code> tenga RLS con políticas filtradas por <code>auth.uid()</code>. Si todavía no lo hiciste, seguí el <a href="https://rodrix91.github.io/launchlatam/blog/rls-supabase-lovable/">paso a paso de RLS para apps de Lovable</a>.</p>
<p>Volvé a mirar el repo para comprobar que la clave nueva no haya quedado en el código. Podés usar nuestro <a href="https://rodrix91.github.io/launchlatam/#escaneo">escaneo gratis</a> en un repositorio público: corre en tu navegador y busca secretos expuestos, tablas sin RLS y páginas legales que falten. No reemplaza una revisión del historial de git ni una auditoría completa.</p>
<h2>Después de la primera hora</h2>
<p>Si tu app todavía usa <code>anon</code> y <code>service_role</code>, planificá la migración a las claves nuevas: Supabase las depreca para finales de 2026 (<a href="https://supabase.com/docs/guides/getting-started/migrating-to-new-api-keys" rel="noopener">guía de migración</a>). Un secreto por componente del backend permite rotar uno sin tocar los demás.</p>
<p>Si querés que te avisemos cuando salga la próxima guía, el <a href="https://whop.com/checkout/plan_rO1ouDQJcQy2D" rel="noopener">boletín de LaunchLatam es gratis</a>.</p>
""",
"webhooks-mercado-pago-supabase": """
<div class="report" style="margin:1.5rem 0"><p><strong>Respuesta corta:</strong> un webhook de Mercado Pago es solo un aviso. Antes de activar un plan, validá el encabezado <code>x-signature</code> con un HMAC-SHA256 de tu secreto y después consultá el pago en la API. Si la firma no coincide, respondé 401. Si coincide, liberá el acceso solo cuando el <code>status</code> sea <code>approved</code>. No confíes en la URL de “gracias” ni en el cuerpo de la notificación sin esa verificación.</p></div>
<p>En la <a href="https://rodrix91.github.io/launchlatam/blog/mercado-pago-en-apps-lovable/">guía de Checkout Pro en Lovable</a> ya decimos que el plan se activa por webhook, no cuando el comprador vuelve a tu sitio. Esta guía se concentra en el paso que más se salta en las apps hechas con IA: <strong>verificar la firma</strong>. Sin eso, cualquiera que conozca la URL de tu función puede mandar un aviso falso y entrar como si hubiera pagado. El mismo criterio vale si cobrás con Pix: lo detallamos en <a href="https://rodrix91.github.io/launchlatam/pt/blog/pix-no-lovable/" hreflang="pt-BR">Como receber Pix em um app feito no Lovable</a>.</p>
<h2>Paso 1: configurá la URL y guardá el secreto</h2>
<p>En <em>Tus integraciones</em>, elegí la aplicación, entrá a <em>Webhooks → Configurar notificación</em> y cargá la URL de una Edge Function, por ejemplo <code>https://TU-PROYECTO.supabase.co/functions/v1/webhook-mp</code>. Revelá la clave secreta que genera Mercado Pago y guardala como secreto de Supabase (<code>MP_WEBHOOK_SECRET</code>), junto con el access token (<code>MP_ACCESS_TOKEN</code>) que vas a usar para consultar el pago. El access token no va al frontend: esa regla está en la guía de Checkout Pro.</p>
<p>Por defecto, las Edge Functions de Supabase exigen un JWT válido en el encabezado de autorización. Mercado Pago no envía un JWT de Supabase, así que esta función tiene que publicarse con <code>verify_jwt = false</code> en <code>supabase/config.toml</code>. Es el mismo patrón que Supabase documenta para webhooks de Stripe (<a href="https://supabase.com/docs/guides/functions/function-configuration" rel="noopener">configuración de funciones</a>). La autenticidad la vas a comprobar vos, con la firma de Mercado Pago, no con un JWT.</p>
<pre><code>[functions.webhook-mp]
verify_jwt = false</code></pre>
<p>Las URLs que configures al crear un pago o una preferencia tienen prioridad sobre las de <em>Tus integraciones</em> (<a href="https://www.mercadopago.com.ar/developers/es/docs/checkout-pro-orders/resources/notifications/webhooks" rel="noopener">documentación de webhooks de Mercado Pago</a>). Las notificaciones de Código QR no llevan firma y no deben validarse con este procedimiento.</p>
<h2>Paso 2: validá el encabezado x-signature</h2>
<p>Cada notificación llega con un encabezado <code>x-signature</code> con este formato (<a href="https://www.mercadopago.com.ar/developers/es/docs/checkout-pro-orders/resources/notifications/webhooks" rel="noopener">fuente</a>):</p>
<pre><code>x-signature: ts=1704908010,v1=618c85345248dd820d5fd456117c2ab2ef8eda45a0282ff693eac24131a5e839</code></pre>
<p>También necesitás el encabezado <code>x-request-id</code> y el parámetro <code>data.id</code> de la query de la URL. Con esos valores armás el manifiesto y calculás un HMAC-SHA256 en hexadecimal, usando tu secreto como clave:</p>
<pre><code>id:&lt;data.id&gt;;request-id:&lt;x-request-id&gt;;ts:&lt;ts&gt;;</code></pre>
<p>Si <code>data.id</code> viene con letras mayúsculas (pasa con algunos ids de órdenes), la documentación pide pasarlo a minúsculas antes de usarlo. Si falta <code>data.id</code> o <code>x-request-id</code>, esos tramos se sacan del manifiesto. El resultado tiene que coincidir exactamente con <code>v1</code>. Si no coincide, respondé <code>401</code> y no actives nada.</p>
<p>Los SDK oficiales traen un <code>WebhookSignatureValidator</code>. En una Edge Function de Supabase, que corre en Deno, lo habitual es calcularlo con la Web Crypto API:</p>
<pre><code>// supabase/functions/webhook-mp/index.ts
async function hmacHex(secret, message) {
  const key = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(message));
  return [...new Uint8Array(sig)].map(b =&gt; b.toString(16).padStart(2, "0")).join("");
}

function part(header, name) {
  for (const p of header.split(",")) {
    const [k, ...rest] = p.trim().split("=");
    if (k === name) return rest.join("=");
  }
  return "";
}

Deno.serve(async (req) =&gt; {
  const secret = Deno.env.get("MP_WEBHOOK_SECRET") ?? "";
  const xSignature = req.headers.get("x-signature") ?? "";
  const xRequestId = req.headers.get("x-request-id") ?? "";
  let dataId = new URL(req.url).searchParams.get("data.id") ?? "";
  if (/[A-Z]/.test(dataId)) dataId = dataId.toLowerCase();
  const ts = part(xSignature, "ts");
  const v1 = part(xSignature, "v1");
  let manifest = "";
  if (dataId) manifest += `id:${dataId};`;
  if (xRequestId) manifest += `request-id:${xRequestId};`;
  manifest += `ts:${ts};`;
  const expected = await hmacHex(secret, manifest);
  if (!secret || !v1 || expected !== v1) {
    return new Response("unauthorized", { status: 401 });
  }
  // Firma válida: consultar el pago en la API y recién entonces activar el plan.
  return new Response("ok", { status: 200 });
});</code></pre>
<h2>Paso 3: respondé 200 o 201 en menos de 22 segundos</h2>
<p>Cuando la notificación llega, Mercado Pago espera un <code>200</code> o un <code>201</code> en un plazo de <strong>22 segundos</strong>. Si no lo recibe, reintenta cada 15 minutos; después del tercer intento el plazo se prorroga, pero los envíos siguen (<a href="https://www.mercadopago.com.ar/developers/es/docs/checkout-pro-orders/resources/notifications/webhooks" rel="noopener">fuente</a>). Por eso tu función tiene que ser <strong>idempotente</strong>: la misma notificación puede llegar más de una vez y también fuera de orden. El <a href="https://github.com/mercadopago/sdk-nodejs/blob/master/docs/webhooks.md" rel="noopener">guía de webhooks del SDK oficial</a> recomienda tratar el aviso como una señal, no como la verdad, y consultar el recurso en la API.</p>
<h2>Paso 4: consultá el pago en la API y activá el plan solo si está approved</h2>
<p>Con la firma ya validada, pedí el recurso con tu access token. Para un pago de Checkout Pro o de la Payments API:</p>
<pre><code>GET https://api.mercadopago.com/v1/payments/{id}
Authorization: Bearer &lt;MP_ACCESS_TOKEN&gt;</code></pre>
<p>Activá el plan del usuario solo si <code>status</code> es <code>approved</code>. Guardá el id del pago en tu base y no lo proceses dos veces. El precio y el plan tienen que estar definidos en el servidor, nunca tomados del cuerpo de la notificación ni del navegador.</p>
<h2>Paso 5: protegé la tabla de pedidos con RLS</h2>
<p>La Edge Function, con la clave secreta del servidor, es quien escribe el estado del pago. El usuario autenticado puede leer el suyo, no marcarse a sí mismo como “pro”. El patrón está en la <a href="https://rodrix91.github.io/launchlatam/blog/mercado-pago-en-apps-lovable/">guía de Checkout Pro</a> y el detalle de las políticas, en el artículo de <a href="https://rodrix91.github.io/launchlatam/blog/rls-supabase-lovable/">RLS para apps de Lovable</a>.</p>
<h2>Paso 6: probá antes de ir a producción</h2>
<p>En la misma pantalla de Webhooks, Mercado Pago documenta cómo <strong>simular el recibimiento de una notificación</strong>. Hacé una compra de prueba con credenciales de test, confirmá que una firma inválida responde 401, que una válida consulta la API y que un reintento no activa el plan dos veces.</p>
<h2>El MCP oficial de Mercado Pago</h2>
<p>Mercado Pago publica un servidor MCP oficial para agentes de IA. Sirve para buscar la documentación sin salir del editor, configurar y monitorear webhooks, crear usuarios de prueba y medir la calidad de la integración. Está documentado para Cursor, VS Code, Windsurf, Cline, Claude y ChatGPT (<a href="https://www.mercadopago.com.ar/developers/es/docs/mcp-server/overview" rel="noopener">resumen del MCP Server</a>). La conexión remota usa el endpoint <code>https://mcp.mercadopago.com/mcp</code> (<a href="https://www.mercadopago.com.ar/developers/es/docs/mcp-server/connection" rel="noopener">guía de conexión</a>). El access token de tu cuenta es secreto: no lo pegues en un chat ni en un archivo del frontend.</p>
<h2>Si pensabas usar solo Stripe</h2>
<p>En Latinoamérica, Stripe abre cuentas locales solo en México y Brasil, según la <a href="https://stripe.com/global" rel="noopener">página de disponibilidad global de Stripe</a> (consultada el 15 de noviembre de 2026). Si tu cuenta no está en esos países, Mercado Pago con el webhook verificado es el camino habitual; comparamos opciones en <a href="https://rodrix91.github.io/launchlatam/blog/stripe-no-funciona-en-mi-pais/">¿Stripe no está disponible en tu país?</a>.</p>
<p>Antes de cobrar el primer pago, conviene escanear el repo: <a href="https://rodrix91.github.io/launchlatam/#escaneo">escaneo gratis</a>, en el navegador, sin crear cuenta. Si querés que te avisemos cuando salga la próxima guía, el <a href="https://whop.com/checkout/plan_rO1ouDQJcQy2D" rel="noopener">boletín de LaunchLatam es gratis</a>.</p>
""",
"app-feito-com-ia-e-seguro": """
<div class="report" style="margin:1.5rem 0"><p><strong>Resposta curta:</strong> um app feito com IA (Lovable, Bolt, Cursor, Replit) pode ser seguro, mas não é seguro por padrão. Antes de lançar no Brasil, confira pelo menos 10 pontos: RLS ativado em todas as tabelas do Supabase, nenhuma chave <code>service_role</code>/<code>sb_secret_</code> no frontend ou no repositório, segredos fora do código, webhooks do Mercado Pago com <code>x-signature</code> validado, autenticação e limites de taxa, CORS e cabeçalhos HTTP, dependências atualizadas, o mínimo da LGPD e backups com logs.</p></div>
<h2>Por que a pergunta faz sentido: os dados</h2>
<ul>
<li>A Sentris escaneou 2.144 repositórios públicos de Supabase feitos com ferramentas de IA (agosto de 2026): 40,6% tinham uma exposição crítica confirmada, contra 24,9% de um grupo de controle sem IA. Nos repositórios do Lovable, a cifra foi 57,9% (<a href="https://sentris.dev/blog/we-scanned-2000-ai-built-supabase-apps" rel="noopener">fonte</a>).</li>
<li>Em 2025, Matt Palmer encontrou 170 de 1.645 apps do Lovable com dados expostos por falta de RLS, o caso registrado como CVE-2025-48757 (<a href="https://mattpalmer.io/posts/2025/05/statement-on-CVE-2025-48757/" rel="noopener">fonte</a>).</li>
</ul>
<p>O problema raramente é a ferramenta em si. É a configuração que ninguém revisou antes de colocar o app no ar. As 10 verificações abaixo são as que mais pesam num app com Supabase e pagamentos via Pix ou Mercado Pago.</p>
<h2>1. RLS ativado em todas as tabelas do Supabase</h2>
<p>A documentação do Supabase é direta: uma tabela num esquema exposto sem Row Level Security pode ser lida e alterada por qualquer papel que tenha permissão sobre ela, e a recomendação é ativar RLS em todas as tabelas expostas (<a href="https://supabase.com/docs/guides/database/postgres/row-level-security" rel="noopener">documentação de RLS</a>). Com RLS ativado e sem políticas, nada fica acessível pela API com a chave pública até você criar as políticas. O <em>Security Advisor</em> do Supabase aponta tabelas do esquema <code>public</code> sem RLS (lint <code>0013_rls_disabled_in_public</code>) (<a href="https://supabase.com/docs/guides/database/database-advisors" rel="noopener">Advisors</a>). Passo a passo no nosso <a href="https://rodrix91.github.io/launchlatam/blog/rls-supabase-lovable/" hreflang="es-419">guia de RLS no Supabase para apps do Lovable</a> (em espanhol).</p>
<h2>2. Chaves anon e service_role no lugar certo</h2>
<p>A chave pública (<code>anon</code> ou <code>sb_publishable_</code>) pode ir no navegador: ela só alcança o que o RLS permitir. A chave secreta (<code>service_role</code> ou <code>sb_secret_</code>) contorna todas as políticas de RLS, e o Supabase diz para nunca colocá-la num navegador, num app distribuído nem no controle de versão (<a href="https://supabase.com/docs/guides/api/api-keys" rel="noopener">documentação de chaves de API</a>). As chaves <code>sb_secret_</code> respondem 401 quando usadas de um navegador, mas um atacante ainda pode usá-las de outras ferramentas. Se a sua já vazou, veja <a href="https://rodrix91.github.io/launchlatam/blog/service-role-expuesta-supabase/" hreflang="es-419">o que fazer na primeira hora</a> (em espanhol).</p>
<h2>3. Segredos fora do frontend e do repositório</h2>
<p>O access token do Mercado Pago, chaves de APIs de IA e senhas de e-mail são segredos: vão como segredos do Supabase e são lidos só dentro de Edge Functions. Variáveis com prefixo público do bundler (<code>VITE_</code>, <code>NEXT_PUBLIC_</code>) acabam no JavaScript que qualquer visitante baixa. Em repositórios públicos, o GitHub roda o <em>secret scanning</em> automaticamente e de graça (<a href="https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning" rel="noopener">documentação do GitHub</a>); o guia de gestão de segredos da OWASP explica como guardar e rotacionar (<a href="https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html" rel="noopener">OWASP</a>). Um segredo que já foi para um commit precisa ser rotacionado, não só apagado.</p>
<h2>4. Webhooks do Mercado Pago e do Pix com x-signature validado</h2>
<p>Não libere acesso na tela de “obrigado”. Em cada notificação, valide o cabeçalho <code>x-signature</code>: monte <code>id:&lt;data.id&gt;;request-id:&lt;x-request-id&gt;;ts:&lt;ts&gt;;</code>, calcule o HMAC-SHA256 com a sua assinatura secreta e compare com <code>v1</code>; se não bater, responda 401 (<a href="https://www.mercadopago.com.br/developers/pt/docs/checkout-pro-orders/resources/notifications/webhooks" rel="noopener">documentação de webhooks do Mercado Pago</a>). Depois, consulte o pagamento na API e só ative o plano com status <code>approved</code>, de forma idempotente. Detalhes em <a href="https://rodrix91.github.io/launchlatam/pt/blog/pix-no-lovable/">Como receber Pix em um app feito no Lovable</a> e no guia de <a href="https://rodrix91.github.io/launchlatam/blog/webhooks-mercado-pago-supabase/" hreflang="es-419">webhooks do Mercado Pago com Supabase</a> (em espanhol).</p>
<h2>5. Autenticação: quem é quem, no servidor</h2>
<p>Esconder um botão no frontend não protege nada. Cada leitura ou escrita sensível precisa ser filtrada no banco (políticas com <code>auth.uid()</code>) ou checada dentro da Edge Function. Para os formulários de cadastro e login, o Supabase oferece proteção com CAPTCHA (<a href="https://supabase.com/docs/guides/auth/auth-captcha" rel="noopener">documentação de CAPTCHA</a>). Teste com dois usuários: o usuário A não pode ver nem editar os dados do usuário B.</p>
<h2>6. Limites de taxa (rate limit)</h2>
<p>O Supabase Auth aplica limites de taxa nos endpoints de autenticação, e alguns podem ser ajustados em <em>Authentication → Rate Limits</em> (<a href="https://supabase.com/docs/guides/auth/rate-limits" rel="noopener">documentação de rate limits</a>). As suas Edge Functions, principalmente as que chamam APIs pagas de IA ou enviam e-mails, precisam do próprio limite: a OWASP classifica o consumo irrestrito de recursos como o risco API4:2023 (<a href="https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/" rel="noopener">OWASP API Security</a>).</p>
<h2>7. CORS e cabeçalhos HTTP</h2>
<p>Para chamar uma Edge Function do navegador é preciso tratar as requisições CORS de preflight (<a href="https://supabase.com/docs/guides/functions/cors" rel="noopener">documentação de CORS do Supabase</a>). A OWASP recomenda, se você usa <code>Access-Control-Allow-Origin</code>, definir origens específicas em vez de <code>*</code>, e também descreve <code>Content-Security-Policy</code> e <code>Strict-Transport-Security</code> (<a href="https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html" rel="noopener">OWASP HTTP Headers Cheat Sheet</a>).</p>
<h2>8. Dependências</h2>
<p>Agentes de IA instalam pacotes com facilidade, e cada um é código de terceiros no seu app. A OWASP Top 10:2025 tem uma categoria inteira para isso, “Software Supply Chain Failures” (A03:2025) (<a href="https://owasp.org/Top10/2025/A03_2025-Software_Supply_Chain_Failures/" rel="noopener">OWASP</a>). Antes de lançar, remova o que não usa, confira se cada pacote existe e é o esperado, e rode <code>npm audit</code> no projeto.</p>
<h2>9. LGPD: o mínimo para lançar</h2>
<ul>
<li><strong>Segurança.</strong> A LGPD exige medidas de segurança técnicas e administrativas para proteger os dados pessoais de acessos não autorizados (art. 46). Os itens 1 a 8 desta lista são parte disso.</li>
<li><strong>Transparência.</strong> O titular tem direito a informações claras sobre a finalidade e a forma do tratamento (art. 9º): publique uma política de privacidade que diga o que você coleta e por quê.</li>
<li><strong>Direitos do titular.</strong> O titular pode pedir confirmação, acesso e correção dos seus dados, entre outros direitos (art. 18): tenha um canal de contato que funcione.</li>
<li><strong>Incidentes.</strong> Incidentes que possam causar risco ou dano relevante devem ser comunicados à ANPD e aos titulares (art. 48); pela Resolução CD/ANPD nº 15/2024, o prazo é de 3 dias úteis (<a href="https://www.gov.br/anpd/pt-br/canais_atendimento/agente-de-tratamento/comunicado-de-incidente-de-seguranca-cis" rel="noopener">ANPD</a>).</li>
</ul>
<p>Texto da lei: <a href="https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm" rel="noopener">Lei nº 13.709/2018 (LGPD), no Planalto</a>. Isto é um resumo técnico, não aconselhamento jurídico.</p>
<h2>10. Backups e logs</h2>
<p>O Supabase faz backup diário automático dos projetos Pro, Team e Enterprise; no plano Pro ficam disponíveis os últimos 7 dias. Para projetos do plano gratuito, o Supabase recomenda exportar os dados regularmente com o comando <code>db dump</code> da CLI e guardar backups fora da plataforma (<a href="https://supabase.com/docs/guides/platform/backups" rel="noopener">documentação de backups</a>). Saiba também onde consultar os logs do projeto (<a href="https://supabase.com/docs/guides/telemetry/logs" rel="noopener">documentação de logs</a>): sem eles, não dá para saber o que aconteceu num incidente, nem cumprir o prazo de comunicação do item 9.</p>
<h2>Como verificar em poucos minutos</h2>
<p>Comece pelo que é automático: o <a href="https://rodrix91.github.io/launchlatam/pt/#escaneo">escaneamento grátis da LaunchLatam</a> verifica um repositório público ou a URL do seu app no navegador, sem criar conta (também em <a href="https://rodrix91.github.io/launchlatam/escaneo/">/escaneo/</a>). Depois, siga o <a href="https://rodrix91.github.io/launchlatam/blog/checklist-seguridad-apps-vibe-coding/" hreflang="es-419">checklist de segurança para apps feitos com IA</a> (em espanhol). Se quiser receber o próximo guia, o <a href="https://whop.com/checkout/plan_rO1ouDQJcQy2D" rel="noopener">boletim da LaunchLatam é grátis</a>.</p>
""",
"pix-no-lovable": """
<div class="report" style="margin:1.5rem 0"><p><strong>Resposta curta:</strong> para receber Pix num app feito no Lovable, crie o pagamento no servidor (uma Edge Function do Supabase) chamando <code>POST /v1/payments</code> do Mercado Pago com <code>payment_method_id: "pix"</code>, mostre ao comprador o QR Code e o Pix Copia e Cola que voltam na resposta e libere o acesso só quando o webhook, com assinatura validada, confirmar o status <code>approved</code>. O access token nunca vai para o frontend.</p></div>
<p>O Lovable tem pagamentos integrados com Stripe ou Paddle e também aceita a sua própria conta Stripe (<a href="https://docs.lovable.dev/integrations/stripe" rel="noopener">documentação do Lovable</a>). Para Pix, o caminho mais direto para quem vende no Brasil costuma ser o Mercado Pago. Abaixo está o passo a passo, com as alternativas no final.</p>
<h2>O que você precisa antes</h2>
<ul>
<li>Uma conta de vendedor no Mercado Pago com <strong>chaves Pix cadastradas</strong>. Sem chave Pix, a opção não aparece (<a href="https://www.mercadopago.com.br/developers/pt/docs/checkout-api-orders/overview" rel="noopener">pré-requisitos do Mercado Pago</a>).</li>
<li>Uma aplicação criada em <em>Suas integrações</em>, com a <em>public key</em> e o <em>access token</em> de teste.</li>
<li>Um backend: o Supabase conectado ao seu projeto do Lovable, onde vão a Edge Function e os segredos.</li>
</ul>
<h2>Passo 1: guarde o access token como segredo</h2>
<p>O access token cria cobranças e lê pagamentos da sua conta. Salve-o como segredo do Supabase (por exemplo <code>MP_ACCESS_TOKEN</code>) e use-o só dentro de Edge Functions. No navegador vai, no máximo, a <em>public key</em>. Se o token já apareceu no código ou no repositório, gere outro no painel do Mercado Pago antes de seguir.</p>
<h2>Passo 2: crie o pagamento Pix numa Edge Function</h2>
<p>A documentação do Mercado Pago mostra o pagamento Pix como um <code>POST</code> em <code>/v1/payments</code> com <code>payment_method_id: "pix"</code>, o e-mail do comprador e o cabeçalho obrigatório <code>X-Idempotency-Key</code>, que evita cobrança duplicada se a requisição for repetida (<a href="https://www.mercadopago.com.br/developers/pt/docs/checkout-api-payments/integration-configuration/integrate-pix" rel="noopener">documentação Pix do Mercado Pago</a>).</p>
<pre><code>// supabase/functions/criar-pix/index.ts
Deno.serve(async (req) =&gt; {
  const { email, pedidoId } = await req.json();
  const PRECO = 49.90; // o preço é definido aqui, nunca no navegador
  const r = await fetch("https://api.mercadopago.com/v1/payments", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${Deno.env.get("MP_ACCESS_TOKEN")}`,
      "Content-Type": "application/json",
      "X-Idempotency-Key": crypto.randomUUID(),
    },
    body: JSON.stringify({
      transaction_amount: PRECO,
      description: "Plano Pro",
      payment_method_id: "pix",
      external_reference: pedidoId,
      payer: { email },
    }),
  });
  const p = await r.json();
  const t = p.point_of_interaction?.transaction_data;
  return Response.json({ id: p.id, status: p.status,
    qr_code: t?.qr_code, qr_code_base64: t?.qr_code_base64, ticket_url: t?.ticket_url });
});</code></pre>
<p>Por padrão o código Pix vence em <strong>24 horas</strong>. Você pode mudar isso com <code>date_of_expiration</code>, entre 30 minutos e 30 dias a partir da emissão (<a href="https://www.mercadopago.com.br/developers/pt/docs/checkout-api-payments/integration-configuration/integrate-pix" rel="noopener">fonte</a>). Para um app com assinatura ou acesso imediato, um prazo curto evita pedidos “pendentes” acumulados.</p>
<p>O Mercado Pago também documenta o Pix na Orders API, mais nova, com <code>payment_method.type = "bank_transfer"</code> (<a href="https://www.mercadopago.com.br/developers/pt/docs/checkout-api-orders/payment-integration/pix" rel="noopener">documentação da Orders API</a>). A lógica é a mesma: criar no servidor, exibir o QR e confirmar pelo webhook.</p>
<h2>Passo 3: mostre o QR Code e o Copia e Cola</h2>
<p>A resposta do pagamento chega com status <code>pending</code> e <code>status_detail</code> <code>pending_waiting_transfer</code>, e traz três coisas em <code>point_of_interaction.transaction_data</code>: <code>qr_code_base64</code> (a imagem), <code>qr_code</code> (o texto do Pix Copia e Cola) e <code>ticket_url</code> (uma página do Mercado Pago com tudo pronto). No Lovable, peça na conversa um componente que receba esses campos:</p>
<pre><code>&lt;img src={`data:image/jpeg;base64,${qr_code_base64}`} alt="QR Code Pix" /&gt;
&lt;input readOnly value={qr_code} /&gt; &lt;button&gt;Copiar código Pix&lt;/button&gt;</code></pre>
<p>Quem paga pelo celular normalmente prefere o Copia e Cola; quem está no computador escaneia o QR.</p>
<h2>Passo 4: confirme o pagamento pelo webhook, não pela tela</h2>
<p>O Pix é pago fora do seu app, no banco do comprador. Por isso a confirmação tem que vir do servidor:</p>
<ol>
<li>Configure em <em>Suas integrações → Webhooks</em> uma URL que aponte para outra Edge Function e copie a assinatura secreta.</li>
<li>Em cada notificação, valide o cabeçalho <code>x-signature</code> (formato <code>ts=...,v1=...</code>): monte <code>id:&lt;data.id&gt;;request-id:&lt;x-request-id&gt;;ts:&lt;ts&gt;;</code>, calcule o HMAC-SHA256 com a sua chave secreta e compare com <code>v1</code>. Se não bater, responda 401 (<a href="https://www.mercadopago.com.br/developers/pt/docs/checkout-pro-orders/resources/notifications/webhooks" rel="noopener">documentação de webhooks</a>).</li>
<li>Com a assinatura válida, consulte <code>GET /v1/payments/{id}</code> e só libere o acesso se o status for <code>approved</code>. Trate a notificação como um aviso, e a consulta à API como a verdade.</li>
<li>Seja idempotente: a mesma notificação pode chegar mais de uma vez. Guarde o id do pagamento e não ative o plano duas vezes (<a href="https://github.com/mercadopago/sdk-nodejs/blob/master/docs/webhooks.md" rel="noopener">guia do SDK oficial</a>).</li>
</ol>
<p>Guarde o pagamento numa tabela do Supabase com <strong>RLS ativado</strong>, para que cada usuário veja só os próprios pedidos. Se você ainda não revisou isso, veja o nosso <a href="https://rodrix91.github.io/launchlatam/blog/rls-supabase-lovable/" hreflang="es-419">guia de RLS no Supabase para apps do Lovable</a> (em espanhol).</p>
<h2>Passo 5: teste antes de ir para produção</h2>
<p>Use as credenciais e contas de teste do Mercado Pago e faça uma compra de teste com Pix antes de trocar para as credenciais de produção. O Mercado Pago tem uma seção específica para isso (“Realizar uma compra teste com Pix”) na <a href="https://www.mercadopago.com.br/developers/pt/docs/checkout-api-orders/overview" rel="noopener">documentação do Checkout Transparente</a>.</p>
<h2>Alternativas ao Checkout Transparente</h2>
<ul>
<li><strong>Checkout Pro do Mercado Pago.</strong> O comprador é levado ao ambiente do Mercado Pago, que já oferece Pix, cartão e boleto. Dá menos trabalho de interface; você ainda precisa do webhook para confirmar o pagamento. Temos um <a href="https://rodrix91.github.io/launchlatam/blog/mercado-pago-en-apps-lovable/" hreflang="es-419">guia de Checkout Pro no Lovable</a> (em espanhol).</li>
<li><strong>Stripe com Pix.</strong> Contas Stripe no Brasil aceitam Pix avulso com liquidação em BRL; empresas fora do Brasil (por exemplo EUA ou países da Europa) também podem receber Pix de clientes brasileiros. Nesse caso o cliente paga IOF de 3,5% por padrão, e o Pix Automático (recorrente) não está disponível para empresas sediadas no Brasil (<a href="https://docs.stripe.com/payments/pix" rel="noopener">documentação da Stripe</a>). Como o Lovable conecta a sua própria conta Stripe, essa é uma opção se você já tem Stripe.</li>
<li><strong>Atenção se você não está no Brasil.</strong> A lista de países com conta Stripe que aceita Pix não inclui Bolívia, Paraguai nem Argentina (<a href="https://docs.stripe.com/payments/pix" rel="noopener">fonte</a>). Para vender para o Brasil a partir desses países, compare as opções no nosso artigo <a href="https://rodrix91.github.io/launchlatam/blog/stripe-no-funciona-en-mi-pais/" hreflang="es-419">sobre cobrar sem Stripe</a> (em espanhol).</li>
</ul>
<h2>Erros que mais vemos</h2>
<ol>
<li><strong>Access token no frontend.</strong> Qualquer pessoa que abrir o código do site consegue usá-lo.</li>
<li><strong>Preço enviado pelo navegador.</strong> O valor tem que ser definido na Edge Function.</li>
<li><strong>Liberar o acesso na tela de “obrigado”.</strong> Sem webhook validado, qualquer um chega nessa tela sem pagar.</li>
<li><strong>Webhook sem validar <code>x-signature</code>.</strong> Abre a porta para notificações falsas.</li>
<li><strong>Sem <code>X-Idempotency-Key</code>.</strong> Um clique duplo pode gerar dois pagamentos.</li>
</ol>
""",
"rls-supabase-lovable": f"""
<div class="report" style="margin:1.5rem 0"><p><strong>Respuesta corta:</strong> en una app de Lovable con Supabase, la clave pública que va en el navegador (<code>anon</code> o, en proyectos nuevos, <code>sb_publishable_</code>) es pública por diseño. Lo único que impide que cualquiera lea o modifique tus tablas es Row Level Security (RLS). Revisá que cada tabla del esquema <code>public</code> tenga RLS activado, una política por operación filtrada por <code>auth.uid()</code> y ninguna política <code>using (true)</code> sobre datos privados.</p></div>
<h2>Por qué importa: los datos</h2>
<ul>
<li>Sentris escaneó 2.144 repositorios públicos de Supabase hechos con herramientas de IA (agosto de 2026): el 40,6% tenía una exposición crítica confirmada, contra el 24,9% de un grupo de control sin IA. En los repos de Lovable la cifra fue 57,9% (<a href="https://sentris.dev/blog/we-scanned-2000-ai-built-supabase-apps" rel="noopener">fuente</a>).</li>
<li>En 2025, Matt Palmer encontró 170 de 1.645 apps de Lovable con datos expuestos por falta de RLS, el caso registrado como CVE-2025-48757 (<a href="{CVE}" rel="noopener">fuente</a>).</li>
<li>UpGuard explica la causa: Supabase activa RLS por defecto en las tablas creadas desde el Table Editor, pero no en las que se crean por API o SQL, que es como trabajan los agentes de código (<a href="https://www.upguard.com/blog/everything-everywhere-systemic-data-exposure-in-supabase-apps" rel="noopener">fuente</a>).</li>
</ul>
<p>La documentación oficial de Supabase lo dice sin vueltas: una tabla de un esquema expuesto sin RLS se puede leer y escribir con cualquier rol que tenga permisos sobre ella (<a href="https://supabase.com/docs/guides/database/postgres/row-level-security" rel="noopener">fuente</a>).</p>
<h2>Paso 1: mirá el escaneo de seguridad de Lovable</h2>
<p>Lovable corre un <em>Quick scan</em> cada vez que abrís el diálogo de publicar. Entre otras cosas, marca tablas sin RLS y políticas que dejan pasar a todos. También podés lanzarlo cuando quieras desde la vista <em>Security</em> del proyecto, y las políticas se revisan en <em>More → Database → Manage → Policies</em> (<a href="https://docs.lovable.dev/features/security" rel="noopener">documentación de Lovable</a>). Es un buen primer filtro, pero la propia Lovable aclara que no garantiza seguridad completa.</p>
<h2>Paso 2: listá las tablas sin RLS con SQL</h2>
<p>En Supabase, abrí el <em>SQL Editor</em> y ejecutá:</p>
<pre><code>select tablename, rowsecurity
from pg_tables
where schemaname = 'public'
order by rowsecurity, tablename;</code></pre>
<p>Cada fila con <code>rowsecurity = false</code> es una tabla abierta. Después mirá qué políticas tenés y para quién:</p>
<pre><code>select tablename, policyname, cmd, roles, qual, with_check
from pg_policies
where schemaname = 'public';</code></pre>
<p>Buscá políticas con <code>qual = true</code> dirigidas a <code>anon</code> o <code>public</code>: equivalen a no tener RLS, salvo que esa tabla sea realmente pública.</p>
<h2>Paso 3: probá desde afuera, como lo haría un atacante</h2>
<p>Solo en tu propio proyecto: con la URL y la clave <code>anon</code> que ya están en el frontend de tu app, pedí una fila de una tabla privada.</p>
<pre><code>curl "https://TU-PROYECTO.supabase.co/rest/v1/perfiles?select=*&amp;limit=1" \\
  -H "apikey: TU_CLAVE_ANON"</code></pre>
<p>Si devuelve datos sin haber iniciado sesión, esa tabla está expuesta. Una respuesta vacía (<code>[]</code>) o un error de permisos es lo que querés ver.</p>
<h2>Paso 4: activá RLS y ajustá los permisos</h2>
<p>Supabase recomienda tres cosas juntas: activar RLS, quitar los permisos por defecto a <code>anon</code> y <code>authenticated</code>, y devolver solo los que tu app usa.</p>
<pre><code>alter table public.perfiles enable row level security;
revoke all on table public.perfiles from anon, authenticated;
grant select, insert, update, delete on table public.perfiles to authenticated;</code></pre>
<p>Con RLS activado y sin políticas, nadie lee nada con la clave pública. Ahora agregá una política por operación:</p>
<pre><code>create policy "ver mi perfil" on public.perfiles
  for select to authenticated
  using ( (select auth.uid()) = user_id );

create policy "crear mi perfil" on public.perfiles
  for insert to authenticated
  with check ( (select auth.uid()) = user_id );

create policy "editar mi perfil" on public.perfiles
  for update to authenticated
  using ( (select auth.uid()) = user_id )
  with check ( (select auth.uid()) = user_id );

create policy "borrar mi perfil" on public.perfiles
  for delete to authenticated
  using ( (select auth.uid()) = user_id );</code></pre>
<p>El <code>with check</code> del update evita que alguien se “regale” una fila cambiando el <code>user_id</code>. Agregá un índice en <code>user_id</code> para que las consultas no se vuelvan lentas.</p>
<h2>Paso 5: los cinco errores que vemos más seguido</h2>
<ol>
<li><strong><code>using (true)</code> en datos privados.</strong> Deja pasar a cualquiera. Usalo solo para contenido público, como un catálogo.</li>
<li><strong>Vistas que saltan RLS.</strong> En Postgres las vistas se crean como <code>security definer</code> y devuelven todo. Crealas con <code>with (security_invoker = true)</code>.</li>
<li><strong>Funciones <code>security definer</code> en el esquema <code>public</code>.</strong> Se pueden llamar desde la API con los privilegios de su dueño. Ponelas en un esquema privado y fijá <code>search_path = ''</code>.</li>
<li><strong>Políticas basadas en <code>user_metadata</code>.</strong> El usuario puede modificar ese campo. Para roles y permisos usá <code>app_metadata</code>.</li>
<li><strong>La clave <code>service_role</code> o <code>sb_secret_</code> en el frontend.</strong> Salta todo RLS. Si alguna vez estuvo en tu repo, rotala en Supabase.</li>
</ol>
<h2>Paso 6: comprobalo con tests</h2>
<p>Supabase propone un archivo de test por tabla en <code>supabase/tests/</code> (pgTAP) que verifique qué puede y qué no puede hacer cada rol, y correrlo con <code>supabase test db</code>. Hasta que el test pasa, no sabés si la política hace lo que creés.</p>
<h2>Si preferís pedírselo a Lovable</h2>
<p>Podés escribir en el chat del proyecto algo como: <em>“Activá Row Level Security en todas las tablas de public, quitá los permisos de anon que no hagan falta y creá políticas separadas de select, insert, update y delete filtradas por auth.uid() = user_id. No uses using (true) en tablas con datos de usuarios.”</em> Después volvé a correr el escaneo y repetí la prueba del paso 3.</p>
<h2>Revisalo gratis en tu repo</h2>
<p>Nuestro <a href="{B}/escaneo/">escaneo gratis</a> lee las migraciones SQL de cualquier repo público de GitHub desde tu navegador y marca tablas creadas sin RLS, políticas <code>using (true)</code> y claves <code>service_role</code> en el código. No crea cuenta ni guarda tu código. Para la lista completa de controles, mirá la <a href="{B}/blog/checklist-seguridad-apps-vibe-coding/">checklist de seguridad para apps hechas con IA</a>.</p>
<p>¿Querés una guía así cada semana? <a href="https://whop.com/checkout/plan_rO1ouDQJcQy2D" rel="noopener">Suscribite gratis al boletín</a>.</p>
<h2>Fuentes</h2>
<ul>
<li><a href="https://supabase.com/docs/guides/database/postgres/row-level-security" rel="noopener">Supabase: Row Level Security</a></li>
<li><a href="https://docs.lovable.dev/features/security" rel="noopener">Lovable: Security overview</a></li>
<li><a href="https://sentris.dev/blog/we-scanned-2000-ai-built-supabase-apps" rel="noopener">Sentris: We scanned 2,144 AI-built Supabase repos</a></li>
<li><a href="https://www.upguard.com/blog/everything-everywhere-systemic-data-exposure-in-supabase-apps" rel="noopener">UpGuard: systemic data exposure in Supabase apps</a></li>
<li><a href="{CVE}" rel="noopener">Matt Palmer: statement on CVE-2025-48757</a></li>
</ul>
""",
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
<ol><li>Leé el <code>id</code> del pago que llega en la notificación.</li><li>Consultá <code>GET https://api.mercadopago.com/v1/payments/{{id}}</code> con tu access token.</li><li>Si <code>status</code> es <code>approved</code>, activá el plan del usuario en tu tabla.</li><li>Validá la firma del encabezado <code>x-signature</code> con la clave secreta de webhooks que te da Mercado Pago, para descartar notificaciones falsas. El paso a paso está en la guía de <a href="https://rodrix91.github.io/launchlatam/blog/webhooks-mercado-pago-supabase/">webhooks de Mercado Pago con Edge Functions</a>.</li></ol>
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
<ol><li><strong>Row Level Security en todas las tablas.</strong> La clave <code>anon</code> de Supabase es pública por diseño: lo que protege tus datos es RLS. Sin RLS, cualquiera con esa clave lee y escribe todo. Guía paso a paso: <a href="{B}/blog/rls-supabase-lovable/">cómo revisar y activar RLS en una app de Lovable</a>.</li>
<li><strong>Nada de <code>using (true)</code>.</strong> Una política que deja pasar a todos equivale a no tener RLS. Filtrá por <code>auth.uid()</code>.</li>
<li><strong>Columnas sensibles fuera de la API.</strong> Emails, teléfonos o tokens no deberían poder consultarse desde el navegador si no hace falta.</li>
<li><strong>Funciones RPC revisadas.</strong> Una función <code>security definer</code> ignora RLS; asegurate de que valide al usuario.</li></ol>
<h2>Claves y secretos</h2>
<ol start="5"><li><strong>La clave <code>service_role</code> nunca en el frontend.</strong> Salta toda la seguridad. Si alguna vez estuvo en tu repo, rotala: <a href="https://rodrix91.github.io/launchlatam/blog/service-role-expuesta-supabase/">qué hacer en la próxima hora</a>.</li>
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

# Legal pages are generated from /workspace/quiposa/legal/*.md (see build.py LEGAL_DOCS).

# Per-article FAQ (rendered visibly on the article and as FAQPage JSON-LD). Key = slug.
POST_FAQ = {
"app-feito-com-ia-e-seguro": [
 ("Um app feito com IA é seguro?", "Pode ser, mas não por padrão. A Sentris encontrou exposição crítica em 40,6% de 2.144 repositórios públicos de Supabase feitos com IA (57,9% nos do Lovable). Antes de lançar, confira RLS, chaves service_role fora do frontend, segredos fora do repositório, webhooks com x-signature validado, autenticação, rate limit, CORS, dependências, LGPD e backups."),
 ("A chave anon do Supabase pode ficar no frontend?", "Sim. A chave anon ou sb_publishable_ é pública por design e só alcança o que o Row Level Security permitir. A service_role ou sb_secret_ contorna o RLS e nunca deve ir para o navegador, para um app distribuído nem para o repositório."),
 ("O que a LGPD exige no mínimo de um app recém-lançado?", "Medidas de segurança técnicas e administrativas (art. 46), informações claras sobre o tratamento (art. 9º), atendimento aos direitos do titular (art. 18) e comunicação de incidentes relevantes à ANPD e aos titulares (art. 48), em 3 dias úteis segundo a Resolução CD/ANPD nº 15/2024."),
],
"service-role-expuesta-supabase": [
 ("¿Qué puede hacer alguien con mi clave service_role?", "Eludir Row Level Security y acceder a los datos de tu proyecto con privilegios de servidor. No debe salir de un backend que controles: ni al frontend, ni a un repositorio, ni a un commit. Supabase documenta que la clave secreta es la llave maestra del proyecto."),
 ("Roté la clave en el Dashboard, pero el código viejo sigue en GitHub. ¿Alcanza?", "No. La guía oficial pide corregir la causa de la filtración antes de rotar, reemplazar la clave en todos los componentes y recién entonces retirar la comprometida. Si era una service_role legacy, al desactivarla también se apaga la clave anon: hay que poner una sb_publishable_ en el cliente."),
 ("¿Es lo mismo service_role que sb_secret_?", "sb_secret_ es la clave secreta nueva que reemplaza a service_role, que Supabase depreca para finales de 2026. Las dos eluden RLS. Las claves secretas nuevas responden 401 si se usan en un navegador, pero igual no van en el código ni en el frontend."),
],
"webhooks-mercado-pago-supabase": [
 ("¿Puedo activar el plan cuando el usuario vuelve a /gracias?", "No. Cualquiera puede abrir esa URL. La fuente de verdad es el webhook con la firma x-signature validada y, después, la consulta a la API de Mercado Pago: el plan se activa solo si el status es approved."),
 ("¿Cómo valido x-signature en una Edge Function, sin el SDK?", "Extraé ts y v1 del encabezado, armá el manifiesto id:<data.id>;request-id:<x-request-id>;ts:<ts>;, calculá un HMAC-SHA256 en hexadecimal con tu secreto y comparalo con v1. Si no coinciden, respondé 401. Si data.id o x-request-id no vienen, esos tramos se omiten."),
 ("¿Qué pasa si no respondo 200 a tiempo?", "Mercado Pago espera 22 segundos. Si no recibe 200 o 201, reintenta cada 15 minutos; después del tercer intento el plazo se prorroga, pero los envíos siguen. Tu función tiene que ser idempotente para no activar el plan dos veces."),
],
"pix-no-lovable": [
 ('Como recebo Pix num app feito no Lovable?', 'Crie o pagamento numa Edge Function do Supabase com POST /v1/payments do Mercado Pago e payment_method_id pix, mostre o qr_code_base64 e o qr_code (Copia e Cola) que voltam na resposta e libere o acesso só quando o webhook, com a assinatura x-signature validada, confirmar o status approved.'),
 ('Quanto tempo vale um código Pix do Mercado Pago?', 'Por padrão, 24 horas. Dá para mudar com o campo date_of_expiration, entre 30 minutos e 30 dias a partir da emissão do pagamento.'),
 ('Posso usar Stripe para receber Pix?', 'Sim, se a sua conta Stripe for de um país suportado (Brasil, EUA, Canadá, vários da Europa, Austrália ou Singapura). Fora do Brasil, o cliente brasileiro paga IOF de 3,5% por padrão. Bolívia, Paraguai e Argentina não estão na lista.'),
],
"rls-supabase-lovable": [
 ("¿Cómo sé si mi app de Lovable tiene la base de datos abierta?", "Ejecutá en el SQL Editor de Supabase: select tablename, rowsecurity from pg_tables where schemaname = 'public'. Toda tabla con rowsecurity = false está abierta para cualquiera que tenga la clave anon, que es pública. También podés probar con curl usando la clave anon contra una tabla privada."),
 ("¿Supabase activa RLS automáticamente?", "En las tablas creadas desde el Table Editor, sí. En las creadas por SQL o por API, que es como trabajan los agentes de IA, no: hay que ejecutar alter table ... enable row level security en cada una."),
 ("¿Alcanza con activar RLS?", "No. Con RLS activado y sin políticas nadie accede; después necesitás una política por operación filtrada por auth.uid(), quitar los permisos de anon que no uses y evitar using (true) en datos privados."),
],
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


# HowTo JSON-LD for genuine step-by-step articles (schema.org HowTo).
# Google no longer shows HowTo rich results (deprecated 2023-09-13) but the type
# remains valid at schema.org and is useful for AEO. Only pages with ordered steps.
POST_HOWTO = {
"service-role-expuesta-supabase": {
  "name": "Qué hacer en la próxima hora si filtraste la clave service_role de Supabase",
  "description": "Cortar la vía de filtración, rotar a una clave secreta nueva, retirar la clave comprometida y revisar RLS.",
  "steps": [
    ("Confirmá la filtración y cortá la vía", "Buscá service_role, sb_secret_ y variables públicas de frontend en el repo y en el historial. Sacá la clave del cliente y de los .env subidos antes de rotar, como pide la guía oficial de Supabase."),
    ("Creá una clave secreta nueva", "En Settings → API Keys del Dashboard de Supabase creá una clave sb_secret_ y no la pegues en el chat ni en el frontend."),
    ("Reemplazala en todo el servidor", "Actualizá secretos de Edge Functions, cron y workers. Si la filtrada era una service_role legacy, cambiá también la anon del cliente por una sb_publishable_."),
    ("Retirá la clave comprometida", "Eliminá la clave secreta o desactivá las claves legacy. No las reactives: eso restaura la clave filtrada. Si era legacy, revocá también el secreto JWT legacy."),
    ("Revisá el daño y el RLS", "Confirmá que las tablas public tengan RLS con políticas filtradas por auth.uid() y volvé a revisar que la clave nueva no haya quedado en el código."),
  ],
},
"webhooks-mercado-pago-supabase": {
  "name": "Verificar la firma de un webhook de Mercado Pago en una Edge Function de Supabase",
  "description": "Configurar la URL, validar x-signature con HMAC-SHA256, consultar el pago en la API y activar el plan solo si está approved.",
  "steps": [
    ("Configurá la URL y guardá el secreto", "En Tus integraciones cargá la URL de la Edge Function, guardá MP_WEBHOOK_SECRET y MP_ACCESS_TOKEN como secretos de Supabase y publicá la función con verify_jwt = false."),
    ("Validá el encabezado x-signature", "Armá el manifiesto id:<data.id>;request-id:<x-request-id>;ts:<ts>;, calculá un HMAC-SHA256 en hexadecimal con tu secreto y comparalo con v1. Si no coincide, respondé 401."),
    ("Respondé 200 o 201 en menos de 22 segundos", "Si Mercado Pago no recibe esa respuesta, reintenta cada 15 minutos. La función tiene que ser idempotente."),
    ("Consultá el pago en la API", "Con la firma válida, pedí GET /v1/payments/{id} y activá el plan solo si el status es approved. No confíes en el cuerpo de la notificación ni en la URL de gracias."),
    ("Protegé la tabla de pedidos y probá", "Escribí el estado solo desde la Edge Function, con RLS para que el usuario no se marque a sí mismo como pro, y simulá una notificación de prueba antes de producción."),
  ],
},
"rls-supabase-lovable": {
  "name": "Activar RLS en Supabase para una app de Lovable",
  "description": "Comprobar si las tablas están expuestas, activar Row Level Security y dejar políticas filtradas por auth.uid().",
  "steps": [
    ("Mirá el escaneo de seguridad de Lovable", "Revisá el reporte de seguridad del proyecto para ver tablas sin RLS o políticas abiertas."),
    ("Listá las tablas sin RLS con SQL", "En el SQL Editor ejecutá la consulta a pg_tables del esquema public y anotá las que tienen rowsecurity = false."),
    ("Probá desde afuera", "Con la clave anon, que es pública, intentá leer una tabla privada para confirmar la exposición."),
    ("Activá RLS y ajustá los permisos", "Ejecutá alter table ... enable row level security y creá una política por operación filtrada por auth.uid()."),
    ("Evité los errores más comunes y comprobalo con tests", "Quitá using (true) en datos privados y verificá que un usuario no vea las filas de otro."),
  ],
},
"pix-no-lovable": {
  "name": "Receber Pix em um app feito no Lovable com Mercado Pago",
  "description": "Criar o pagamento Pix numa Edge Function, mostrar o QR e o Copia e Cola, e liberar o acesso só com o webhook assinado e o status approved.",
  "steps": [
    ("Guarde o access token como segredo", "Salve o access token do Mercado Pago em segredos do Supabase e use-o só em Edge Functions."),
    ("Crie o pagamento Pix no servidor", "Chame POST /v1/payments com payment_method_id pix, X-Idempotency-Key e o preço definido na Edge Function."),
    ("Mostre o QR Code e o Copia e Cola", "Use qr_code_base64, qr_code e ticket_url que voltam na resposta do pagamento."),
    ("Confirme pelo webhook, não pela tela", "Valide x-signature, consulte GET /v1/payments/{id} e libere o acesso só se o status for approved."),
    ("Teste antes de ir para produção", "Faça uma compra de teste com credenciais de teste do Mercado Pago."),
  ],
},
"mercado-pago-en-apps-lovable": {
  "name": "Cobrar con Mercado Pago Checkout Pro en una app de Lovable",
  "description": "Guardar el access token en el servidor, crear la preferencia en una Edge Function, confirmar el pago con un webhook firmado y proteger la tabla con RLS.",
  "steps": [
    ("Guardá el access token como secreto", "Creá MP_ACCESS_TOKEN en los secretos de Supabase. En el frontend solo va la public key."),
    ("Creá la preferencia en una Edge Function", "Definí el precio en el servidor, creá la preferencia en la API de Mercado Pago y redirigí al init_point."),
    ("Confirmá el pago con el webhook", "Validá x-signature, consultá el pago en la API y activá el plan solo si el status es approved."),
    ("Protegé la tabla de suscripciones", "Activá RLS y dejá que solo la Edge Function escriba el plan del usuario."),
  ],
},
}

# Portuguese citable answers for Spanish-only articles (PT blog lists them as ES).
POST_FAQ_PT = {
"service-role-expuesta-supabase": [
 ("O que alguém pode fazer com a minha chave service_role?", "Contornar o Row Level Security e acessar os dados do projeto com privilégios de servidor. Não deve sair de um backend que você controla: nem para o frontend, nem para um repositório, nem para um commit."),
 ("Troquei a chave no Dashboard, mas o código antigo continua no GitHub. Isso basta?", "Não. O guia oficial pede corrigir a causa da exposição antes de rotacionar, substituir a chave em todos os componentes e só então retirar a comprometida. Se era uma service_role legacy, ao desativá-la a chave anon também é desligada: é preciso colocar uma sb_publishable_ no cliente."),
 ("service_role e sb_secret_ são a mesma coisa?", "sb_secret_ é a chave secreta nova que substitui a service_role, que a Supabase depreca até o fim de 2026. As duas contornam o RLS. As chaves secretas novas respondem 401 se usadas no navegador, mas mesmo assim não vão no código nem no frontend."),
],
"webhooks-mercado-pago-supabase": [
 ("Posso ativar o plano quando o usuário volta para /gracias?", "Não. Qualquer pessoa pode abrir essa URL. A fonte da verdade é o webhook com a assinatura x-signature validada e, depois, a consulta à API do Mercado Pago: o plano só é ativado se o status for approved."),
 ("Como valido o x-signature numa Edge Function, sem o SDK?", "Extraia ts e v1 do cabeçalho, monte o manifesto id:<data.id>;request-id:<x-request-id>;ts:<ts>;, calcule um HMAC-SHA256 em hexadecimal com o seu segredo e compare com v1. Se não coincidirem, responda 401."),
 ("O que acontece se eu não responder 200 a tempo?", "O Mercado Pago espera 22 segundos. Se não receber 200 ou 201, tenta de novo a cada 15 minutos; depois da terceira tentativa o prazo é prorrogado, mas os envios continuam. A função precisa ser idempotente."),
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
