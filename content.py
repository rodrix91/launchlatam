# Long-form content for LaunchLatam (blog bodies + legal pages)
B = "https://rodrix91.github.io/launchlatam"
MAIL = "rodrixlabs@mail.grokbot.com"
SYM = "https://www.symbioticsec.ai/blog/we-scanned-1-072-vibe-coded-apps-98-had-security-flaws"
CVE = "https://mattpalmer.io/posts/2025/05/statement-on-CVE-2025-48757/"

POST_BODIES = {
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
<li>Em cada notificação, valide o cabeçalho <code>x-signature</code> (formato <code>ts=...,v1=...</code>): monte <code>id:&lt;data.id&gt;;request-id:&lt;x-request-id&gt;;ts:&lt;ts&gt;;</code>, calcule o HMAC-SHA256 com a sua chave secreta e compare com <code>v1</code>. Se não bater, responda 401 (<a href="https://www.mercadopago.com.br/developers/pt/docs/your-integrations/notifications/webhooks" rel="noopener">documentação de webhooks</a>).</li>
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
<ol><li><strong>Row Level Security en todas las tablas.</strong> La clave <code>anon</code> de Supabase es pública por diseño: lo que protege tus datos es RLS. Sin RLS, cualquiera con esa clave lee y escribe todo. Guía paso a paso: <a href="{B}/blog/rls-supabase-lovable/">cómo revisar y activar RLS en una app de Lovable</a>.</li>
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
