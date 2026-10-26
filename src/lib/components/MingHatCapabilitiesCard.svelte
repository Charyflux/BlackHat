<script lang="ts">
	// Card + popup de marketing: mostra tudo que a BlackHat pode fazer.
	// Usado na vitrine pública (/preview) para converter visitante em assinante.
	const CHECKOUT_URL = 'https://pay.cakto.com.br/p9uf5nc_1132723';
	const CHECKOUT_URL_INTL = 'https://buy.stripe.com/14AfZg8n27ru3kCcBX3wQ0d';

	let open = false;
	const show = () => (open = true);
	const close = () => (open = false);

	const capabilities = [
		{
			icon: '🪙',
			title: 'Livre de tokens',
			text: 'Sem contador de tokens, sem "créditos" acabando no meio da conversa e sem resposta cortada pela metade. Uma assinatura, uso à vontade — sem essa ansiedade de ficar de olho no medidor.'
		},
		{
			icon: '✍️',
			title: 'Criação de conteúdo sem travas',
			text: 'Textos, roteiros, posts, e-mails, redações e copys prontas — do jeito que você pedir, sem enrolação e sem a IA "recusar" o pedido.'
		},
		{
			icon: '💻',
			title: 'Programação nível sênior',
			text: 'Código comentado, debugging, arquitetura de sistemas e explicações técnicas em qualquer linguagem, como um dev sênior ao seu lado 24h.'
		},
		{
			icon: '🕵️',
			title: 'Modo PENTESTING exclusivo',
			text: 'Um modo dedicado para testes de segurança, reconhecimento e análise de vulnerabilidades — algo que nenhuma IA "de prateleira" te entrega.'
		},
		{
			icon: '🔓',
			title: 'Sem censura, sem sermão',
			text: 'Respostas diretas ao ponto. Você faz a pergunta, a BlackHat responde — sem enrolar, sem fugir do assunto e sem te tratar como criança.'
		},
		{
			icon: '🇧🇷',
			title: 'Português impecável',
			text: 'Treinada para não errar gramática, acentuação e concordância — textos com qualidade de revisor profissional.'
		},
		{
			icon: '🧠',
			title: 'Explica qualquer assunto',
			text: 'Do básico ao avançado, com exemplos e analogias — didática de verdade, não resposta de robô genérico.'
		},
		{
			icon: '🗂️',
			title: 'Planejamento e estratégia',
			text: 'Planos de ação, cronogramas e o próximo passo prático para qualquer projeto, pessoal ou profissional.'
		},
		{
			icon: '⚡',
			title: 'Disponível 24 horas por dia',
			text: 'Sem fila, sem horário comercial. A BlackHat está online sempre que você precisar, todos os dias.'
		},
		{
			icon: '🔒',
			title: 'Privacidade em primeiro lugar',
			text: 'Suas conversas são suas. Infraestrutura própria, sem depender de gigantes de tecnologia espionando seus dados.'
		}
	];
</script>

<button type="button" class="mh-cap-card" on:click={show}>
	<span class="mh-cap-card-text">
		<span class="mh-cap-card-title">Veja tudo que a BlackHat pode fazer por você</span>
		<span class="mh-cap-card-sub">e muito mais — clique e descubra</span>
	</span>
	<span class="mh-cap-card-arrow" aria-hidden="true">→</span>
</button>

{#if open}
	<div class="mh-cap-backdrop" role="presentation" on:click={close}>
		<div
			class="mh-cap-modal"
			role="dialog"
			aria-modal="true"
			aria-labelledby="mh-cap-title"
			on:click|stopPropagation
		>
			<button class="mh-cap-close" type="button" aria-label="Fechar" on:click={close}>×</button>

			<div class="mh-cap-header">
				<span class="mh-cap-emoji">🎩</span>
				<h2 id="mh-cap-title">Tudo que a BlackHat pode fazer por você</h2>
				<p class="mh-cap-lead">
					Uma IA <strong>sem censura</strong>, criada por desenvolvedores sênior e hackers da
					União Europeia — pensada para quem quer respostas de verdade, sem filtro e sem enrolação.
				</p>
			</div>

			<div class="mh-cap-grid">
				{#each capabilities as cap}
					<div class="mh-cap-item">
						<span class="mh-cap-item-icon" aria-hidden="true">{cap.icon}</span>
						<div>
							<h3>{cap.title}</h3>
							<p>{cap.text}</p>
						</div>
					</div>
				{/each}
			</div>

			<div class="mh-cap-footer">
				<p class="mh-cap-footer-text">
					🔥 Vagas de assinatura limitadas para manter a qualidade e a velocidade das respostas.
				</p>
				<a class="mh-cap-cta" href={CHECKOUT_URL}>🇧🇷 Pagar em Real (Pix/Cartão) 🎩</a>
				<a class="mh-cap-cta mh-cap-cta-alt" href={CHECKOUT_URL_INTL}>💳 Pagamento internacional</a>
				<p class="mh-cap-foot-small">🔒 Pagamento 100% seguro · cancele quando quiser</p>
			</div>
		</div>
	</div>
{/if}

<style>
	.mh-cap-card {
		width: 100%;
		max-width: 48rem;
		margin: 18px auto 0;
		display: flex;
		align-items: center;
		gap: 14px;
		padding: 16px 18px;
		border-radius: 16px;
		border: 1px solid rgba(194, 154, 255, 0.28);
		background: linear-gradient(120deg, rgba(119, 53, 208, 0.16), rgba(21, 17, 30, 0.4) 60%);
		box-shadow: 0 6px 28px #00000025, inset 0 1px 0 #e0baff0a;
		color: #f4f1fa;
		text-align: left;
		cursor: pointer;
		transition: border-color 160ms ease, box-shadow 160ms ease, transform 160ms ease;
	}
	.mh-cap-card:hover {
		border-color: #aa78e7;
		box-shadow: 0 0 0 1px #aa78e71c, 0 8px 38px #9250d51c;
		transform: translateY(-1px);
	}
	.mh-cap-card-text {
		flex: 1 1 auto;
		display: flex;
		flex-direction: column;
		gap: 2px;
		min-width: 0;
	}
	.mh-cap-card-title {
		font-weight: 700;
		font-size: 15px;
	}
	.mh-cap-card-sub {
		font-size: 13px;
		color: #a9a4b8;
	}
	.mh-cap-card-arrow {
		flex: none;
		font-size: 18px;
		color: #c29aff;
	}

	.mh-cap-backdrop {
		position: fixed;
		inset: 0;
		z-index: 9999;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 20px;
		background: rgba(6, 5, 10, 0.75);
		backdrop-filter: blur(6px);
	}
	.mh-cap-modal {
		position: relative;
		width: 100%;
		max-width: 640px;
		max-height: 86vh;
		overflow-y: auto;
		padding: 32px 28px 26px;
		border-radius: 22px;
		border: 1px solid rgba(194, 154, 255, 0.3);
		background: linear-gradient(180deg, #1a1622, #100d18);
		box-shadow: 0 30px 90px -30px rgba(139, 92, 246, 0.55);
		color: #f4f1fa;
		font-family: 'Segoe UI Variable Display', 'Segoe UI', 'Inter', sans-serif;
	}
	.mh-cap-close {
		position: absolute;
		top: 12px;
		right: 14px;
		width: 32px;
		height: 32px;
		border: none;
		background: transparent;
		color: #aaa8b7;
		font-size: 24px;
		line-height: 1;
		cursor: pointer;
		border-radius: 8px;
	}
	.mh-cap-close:hover {
		background: rgba(255, 255, 255, 0.06);
		color: #fff;
	}
	.mh-cap-header {
		text-align: center;
		margin-bottom: 22px;
	}
	.mh-cap-emoji {
		font-size: 34px;
		display: block;
		margin-bottom: 6px;
		filter: drop-shadow(0 6px 18px rgba(139, 92, 246, 0.6));
	}
	.mh-cap-header h2 {
		margin: 0 0 10px;
		font-size: 24px;
		font-weight: 800;
	}
	.mh-cap-lead {
		margin: 0 auto;
		max-width: 480px;
		font-size: 14.5px;
		color: #c9c5d6;
		line-height: 1.55;
	}
	.mh-cap-lead strong {
		color: #c29aff;
	}
	.mh-cap-grid {
		display: grid;
		grid-template-columns: 1fr;
		gap: 14px;
		margin-bottom: 22px;
	}
	.mh-cap-item {
		display: flex;
		gap: 12px;
		padding: 12px 14px;
		border-radius: 14px;
		background: rgba(255, 255, 255, 0.03);
		border: 1px solid rgba(255, 255, 255, 0.06);
	}
	.mh-cap-item-icon {
		flex: none;
		font-size: 20px;
		line-height: 1.3;
	}
	.mh-cap-item h3 {
		margin: 0 0 3px;
		font-size: 14.5px;
		font-weight: 700;
		color: #f4f1fa;
	}
	.mh-cap-item p {
		margin: 0;
		font-size: 13px;
		color: #a9a4b8;
		line-height: 1.5;
	}
	.mh-cap-footer {
		text-align: center;
		padding-top: 6px;
		border-top: 1px solid rgba(255, 255, 255, 0.06);
	}
	.mh-cap-footer-text {
		margin: 14px 0 14px;
		font-size: 13.5px;
		color: #c9c5d6;
	}
	.mh-cap-cta {
		display: block;
		width: 100%;
		padding: 14px;
		border-radius: 999px;
		font-weight: 700;
		font-size: 16px;
		text-decoration: none;
		color: #150c22;
		background: linear-gradient(180deg, #d9bcff, #c29aff);
		box-shadow: 0 12px 30px -12px rgba(139, 92, 246, 0.6);
		transition: transform 0.15s ease, filter 0.15s ease;
	}
	.mh-cap-cta:hover {
		transform: translateY(-1px);
		filter: brightness(1.05);
	}
	.mh-cap-cta-alt {
		margin-top: 10px;
		color: #f4f1fa;
		background: transparent;
		border: 1px solid rgba(194, 154, 255, 0.45);
		box-shadow: none;
	}
	.mh-cap-cta-alt:hover {
		border-color: #c29aff;
		background: rgba(194, 154, 255, 0.08);
	}
	.mh-cap-foot-small {
		margin: 12px 0 0;
		font-size: 12px;
		color: #726e80;
	}

	@media (min-width: 560px) {
		.mh-cap-grid {
			grid-template-columns: 1fr 1fr;
		}
	}
</style>
