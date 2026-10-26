<script lang="ts">
	import { showPaywall } from '$lib/stores';
	import { goto } from '$app/navigation';

	// Troque pela URL real do checkout.
	const CHECKOUT_URL = 'https://pay.cakto.com.br/p9uf5nc_1132723';
	const CHECKOUT_URL_INTL = 'https://buy.stripe.com/14AfZg8n27ru3kCcBX3wQ0d';

	const close = () => showPaywall.set(false);
	const login = () => {
		showPaywall.set(false);
		goto('/auth');
	};
</script>

{#if $showPaywall}
	<div class="mh-paywall-backdrop" role="presentation" on:click={close}>
		<div
			class="mh-paywall"
			role="dialog"
			aria-modal="true"
			aria-labelledby="mh-paywall-title"
			on:click|stopPropagation
		>
			<button class="mh-paywall-close" type="button" aria-label="Fechar" on:click={close}>×</button>

			<img class="mh-paywall-logo" src="/static/minghat-mark.png" alt="BlackHat" />

			<h2 id="mh-paywall-title">Desbloqueie a BlackHat</h2>
			<p class="mh-paywall-sub">
				Para usar nossa IA <strong>sem filtro</strong> e o modo <strong>Pentesting</strong>, você
				precisa estar logado.
			</p>

			<div class="mh-paywall-price">
				<span class="mh-old">de R$ 89,90/mês</span>
				<div class="mh-amt"><span class="mh-cur">R$</span><span class="mh-val">40<span class="mh-cents">,90</span></span></div>
				<span class="mh-per">por mês · cancele quando quiser</span>
			</div>

			<a class="mh-paywall-cta" href={CHECKOUT_URL}>🇧🇷 Pagar em Real (Pix/Cartão) 🎩</a>
			<a class="mh-paywall-cta mh-paywall-cta-alt" href={CHECKOUT_URL_INTL}>💳 Pagamento internacional</a>
			<button class="mh-paywall-login" type="button" on:click={login}>
				Já sou assinante? Entrar
			</button>

			<p class="mh-paywall-foot">🔒 Pagamento 100% seguro</p>
		</div>
	</div>
{/if}

<style>
	.mh-paywall-backdrop {
		position: fixed;
		inset: 0;
		z-index: 9999;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 20px;
		background: rgba(6, 5, 10, 0.72);
		backdrop-filter: blur(6px);
	}
	.mh-paywall {
		position: relative;
		width: 100%;
		max-width: 400px;
		padding: 30px 26px 24px;
		border-radius: 20px;
		border: 1px solid rgba(194, 154, 255, 0.3);
		background: linear-gradient(180deg, #1a1622, #100d18);
		box-shadow: 0 30px 90px -30px rgba(139, 92, 246, 0.55);
		text-align: center;
		color: #f4f1fa;
		font-family: 'Segoe UI Variable Display', 'Segoe UI', 'Inter', sans-serif;
	}
	.mh-paywall-close {
		position: absolute;
		top: 10px;
		right: 12px;
		width: 30px;
		height: 30px;
		border: none;
		background: transparent;
		color: #aaa8b7;
		font-size: 22px;
		line-height: 1;
		cursor: pointer;
		border-radius: 8px;
	}
	.mh-paywall-close:hover {
		background: rgba(255, 255, 255, 0.06);
		color: #fff;
	}
	.mh-paywall-logo {
		width: 60px;
		height: 60px;
		object-fit: contain;
		margin: 0 auto 12px;
		filter: drop-shadow(0 6px 18px rgba(139, 92, 246, 0.6));
	}
	.mh-paywall h2 {
		margin: 0 0 8px;
		font-size: 24px;
		font-weight: 800;
	}
	.mh-paywall-sub {
		margin: 0 0 18px;
		font-size: 14.5px;
		color: #c9c5d6;
		line-height: 1.5;
	}
	.mh-paywall-sub strong {
		color: #c29aff;
	}
	.mh-paywall-price {
		margin-bottom: 18px;
	}
	.mh-old {
		display: block;
		color: #726e80;
		text-decoration: line-through;
		font-size: 14px;
	}
	.mh-amt {
		font-weight: 800;
		line-height: 1;
		letter-spacing: -0.03em;
	}
	.mh-cur {
		font-size: 22px;
		vertical-align: top;
		color: #aaa8b7;
	}
	.mh-val {
		font-size: 56px;
		background: linear-gradient(120deg, #e9d8ff, #c29aff);
		-webkit-background-clip: text;
		background-clip: text;
		color: transparent;
	}
	.mh-cents {
		font-size: 28px;
	}
	.mh-per {
		display: block;
		margin-top: 4px;
		font-size: 13px;
		color: #aaa8b7;
	}
	.mh-paywall-cta {
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
	.mh-paywall-cta:hover {
		transform: translateY(-1px);
		filter: brightness(1.05);
	}
	.mh-paywall-cta-alt {
		margin-top: 10px;
		color: #f4f1fa;
		background: transparent;
		border: 1px solid rgba(194, 154, 255, 0.45);
		box-shadow: none;
	}
	.mh-paywall-cta-alt:hover {
		border-color: #c29aff;
		background: rgba(194, 154, 255, 0.08);
	}
	.mh-paywall-login {
		display: block;
		width: 100%;
		margin-top: 12px;
		padding: 10px;
		border: 1px solid #2a2634;
		border-radius: 999px;
		background: transparent;
		color: #f4f1fa;
		font-size: 14px;
		cursor: pointer;
		transition: border-color 0.15s ease, color 0.15s ease;
	}
	.mh-paywall-login:hover {
		border-color: #c29aff;
		color: #c29aff;
	}
	.mh-paywall-foot {
		margin: 16px 0 0;
		font-size: 12px;
		color: #726e80;
	}
</style>
