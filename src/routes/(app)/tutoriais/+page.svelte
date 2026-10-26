<script>
	import { showSidebar } from '$lib/stores';
</script>

<svelte:head>
	<title>Tutoriais | BlackHat</title>
</svelte:head>

<div
	class="flex flex-col w-full h-screen max-h-[100dvh] transition-width duration-200 ease-in-out {$showSidebar
		? 'md:max-w-[calc(100%-var(--sidebar-width))]'
		: ''} max-w-full"
>
	<div class="flex-1 max-h-full overflow-y-auto">
		<div class="mx-auto w-full max-w-3xl px-4 py-6 text-gray-800 dark:text-gray-100">
			<header class="mb-6">
				<h1 class="text-2xl font-semibold">Tutoriais</h1>
				<p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
					Como escrever boas perguntas de Pentest &amp; Recon para ter respostas mais profundas e
					úteis.
				</p>
			</header>

			<div
				class="mb-6 rounded-xl border border-amber-300/40 bg-amber-50 dark:border-amber-500/20 dark:bg-amber-500/10 px-4 py-3 text-sm"
			>
				<strong>Regra de ouro:</strong> só teste alvos que você está <em>autorizado</em> a testar
				(bug bounty com escopo, laboratório, CTF, ou ambiente próprio). Prefira testes
				não-destrutivos e sempre baseie afirmações em evidência.
			</div>

			<section class="mb-7">
				<h2 class="text-lg font-semibold mb-2">1. Declare escopo e autorização</h2>
				<p class="text-sm mb-3 text-gray-600 dark:text-gray-300">
					O modelo responde com muito mais profundidade quando o contexto está claro.
				</p>
				<div class="space-y-2">
					<p class="text-sm text-rose-600 dark:text-rose-400">❌ "invade o site X"</p>
					<p class="text-sm text-emerald-600 dark:text-emerald-400">
						✅ "Tenho autorização de bug bounty no escopo <code>*.exemplo.com</code>. Quero um plano
						de recon passivo priorizando a superfície de ataque web."
					</p>
				</div>
			</section>

			<section class="mb-7">
				<h2 class="text-lg font-semibold mb-2">2. Peça metodologia, não só comando</h2>
				<p class="text-sm text-emerald-600 dark:text-emerald-400">
					✅ "Explique a metodologia para enumerar subdomínios e priorizar quais valem análise
					manual, e por quê."
				</p>
			</section>

			<section class="mb-7">
				<h2 class="text-lg font-semibold mb-2">3. Dê o contexto técnico que você já tem</h2>
				<p class="text-sm text-emerald-600 dark:text-emerald-400">
					✅ "Encontrei <code>api-dev.exemplo.com</code> com 401 e header <code>Server: Kong</code>.
					Quais hipóteses de teste seguro fazem sentido e como validar cada uma sem causar impacto?"
				</p>
			</section>

			<section class="mb-7">
				<h2 class="text-lg font-semibold mb-2">4. Peça saída estruturada</h2>
				<p class="text-sm text-emerald-600 dark:text-emerald-400">
					✅ "Organize por: fato observado → hipótese → teste seguro → evidência esperada →
					severidade (CVSS)."
				</p>
			</section>

			<section class="mb-7">
				<h2 class="text-lg font-semibold mb-2">5. Recon na BlackHat — como pedir</h2>
				<p class="text-sm text-emerald-600 dark:text-emerald-400">
					✅ "Rode recon em <code>exemplo.com</code> e me diga: subdomínios vivos, serviços web com
					status/tecnologia, e endpoints interessantes (admin, api, swagger, graphql). Destaque o
					que merece análise manual."
				</p>
			</section>

			<section class="mb-7">
				<h2 class="text-lg font-semibold mb-2">6. Foque no impacto e na mitigação</h2>
				<p class="text-sm mb-3 text-gray-600 dark:text-gray-300">
					É o que transforma um achado em um relatório de valor.
				</p>
				<p class="text-sm text-emerald-600 dark:text-emerald-400">
					✅ "Se o <code>.git</code> estiver exposto, qual o impacto real, como confirmar com
					segurança e qual a recomendação de correção?"
				</p>
			</section>

			<section class="mb-2">
				<h2 class="text-lg font-semibold mb-2">Princípios</h2>
				<ul class="list-disc pl-5 text-sm space-y-1 text-gray-700 dark:text-gray-300">
					<li>Alvo autorizado</li>
					<li>Teste não-destrutivo</li>
					<li>Evidência antes de afirmação</li>
					<li>Foco em impacto + correção</li>
				</ul>
			</section>
		</div>
	</div>
</div>

<style>
	code {
		background: rgba(127, 127, 127, 0.18);
		padding: 0.05rem 0.3rem;
		border-radius: 0.3rem;
		font-size: 0.8em;
	}
</style>
