<script lang="ts">
	// Menu lateral "vitrine" da pagina publica (/preview). E so visual: mostra a
	// cara do produto (nova conversa, historico) mas qualquer clique manda para
	// o login, porque so quem tem sessao ve o historico de verdade.
	import { goto } from '$app/navigation';

	const gate = () => goto('/auth');

	const fakeHistory = [
		'Ideias para um post no Instagram',
		'Revisar contrato em PDF',
		'Script de automação em Python',
		'Plano de treino da semana'
	];
</script>

<nav class="minghat-preview-sidebar" aria-label="Menu lateral (visitante)">
	<div class="minghat-preview-sidebar-top">
		<button type="button" class="minghat-preview-sidebar-brand" on:click={gate}>
			<img src="/static/minghat-mark.png" alt="BlackHat" class="minghat-preview-sidebar-logo" />
			<span>BlackHat</span>
		</button>

		<button type="button" class="minghat-preview-new-chat" on:click={gate}>
			<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
				<path d="M12 5v14M5 12h14" />
			</svg>
			<span>Nova conversa</span>
		</button>
	</div>

	<div class="minghat-preview-history">
		<span class="minghat-preview-history-label">Histórico</span>
		<ul class="minghat-preview-history-list" aria-hidden="true">
			{#each fakeHistory as item}
				<li>{item}</li>
			{/each}
		</ul>
		<div class="minghat-preview-history-lock">
			<span aria-hidden="true">🔒</span>
			<p>Faça login para ver e salvar seu histórico de conversas</p>
			<button type="button" class="minghat-preview-history-cta" on:click={gate}>Entrar</button>
		</div>
	</div>

	<button type="button" class="minghat-preview-account" on:click={gate}>
		<span class="minghat-preview-account-avatar" aria-hidden="true">?</span>
		<span class="minghat-preview-account-text">
			<span class="minghat-preview-account-title">Entrar na conta</span>
			<span class="minghat-preview-account-sub">Assinantes BlackHat</span>
		</span>
	</button>
</nav>

<style>
	.minghat-preview-sidebar {
		flex: none;
		width: 260px;
		height: 100%;
		display: flex;
		flex-direction: column;
		gap: 10px;
		padding: 14px 10px;
		background: rgba(10, 8, 15, 0.55);
		border-right: 1px solid rgba(194, 154, 255, 0.14);
		overflow-y: auto;
		box-sizing: border-box;
	}
	.minghat-preview-sidebar-top {
		display: flex;
		flex-direction: column;
		gap: 10px;
	}
	.minghat-preview-sidebar-brand {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 6px 4px;
		background: transparent;
		border: none;
		color: #f4f1fa;
		font-weight: 800;
		font-size: 15px;
		cursor: pointer;
		border-radius: 10px;
		text-align: left;
	}
	.minghat-preview-sidebar-brand:hover {
		background: rgba(255, 255, 255, 0.05);
	}
	.minghat-preview-sidebar-logo {
		width: 26px;
		height: 26px;
		object-fit: contain;
		filter: drop-shadow(0 0 8px rgba(139, 92, 246, 0.5));
	}
	.minghat-preview-new-chat {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 9px 12px;
		border-radius: 10px;
		border: 1px solid rgba(194, 154, 255, 0.25);
		background: rgba(139, 92, 246, 0.08);
		color: #e8e2f5;
		font-size: 13.5px;
		cursor: pointer;
		transition: border-color 150ms ease, background 150ms ease;
	}
	.minghat-preview-new-chat:hover {
		border-color: #aa78e7;
		background: rgba(139, 92, 246, 0.16);
	}

	.minghat-preview-history {
		flex: 1 1 auto;
		position: relative;
		display: flex;
		flex-direction: column;
		min-height: 0;
		margin-top: 4px;
		padding-top: 8px;
		border-top: 1px solid rgba(255, 255, 255, 0.06);
	}
	.minghat-preview-history-label {
		font-size: 11px;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: #726e80;
		padding: 0 4px 6px;
	}
	.minghat-preview-history-list {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: 4px;
		filter: blur(3px);
		opacity: 0.45;
		user-select: none;
	}
	.minghat-preview-history-list li {
		padding: 8px 10px;
		border-radius: 8px;
		background: rgba(255, 255, 255, 0.04);
		font-size: 12.5px;
		color: #cfc9dd;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.minghat-preview-history-lock {
		position: absolute;
		inset: 0;
		top: 22px;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 8px;
		text-align: center;
		padding: 0 14px;
	}
	.minghat-preview-history-lock span {
		font-size: 20px;
	}
	.minghat-preview-history-lock p {
		margin: 0;
		font-size: 12px;
		line-height: 1.4;
		color: #a9a4b8;
	}
	.minghat-preview-history-cta {
		margin-top: 2px;
		padding: 7px 18px;
		border-radius: 999px;
		border: none;
		font-weight: 700;
		font-size: 12.5px;
		color: #150c22;
		background: linear-gradient(180deg, #d9bcff, #c29aff);
		cursor: pointer;
	}

	.minghat-preview-account {
		display: flex;
		align-items: center;
		gap: 10px;
		padding: 8px;
		border-radius: 10px;
		border: 1px solid rgba(255, 255, 255, 0.08);
		background: rgba(255, 255, 255, 0.03);
		color: #f4f1fa;
		cursor: pointer;
		text-align: left;
	}
	.minghat-preview-account:hover {
		border-color: rgba(194, 154, 255, 0.3);
	}
	.minghat-preview-account-avatar {
		flex: none;
		width: 30px;
		height: 30px;
		border-radius: 999px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, #7735d0, #ab4bc7);
		font-weight: 700;
		font-size: 13px;
	}
	.minghat-preview-account-text {
		display: flex;
		flex-direction: column;
		line-height: 1.25;
	}
	.minghat-preview-account-title {
		font-size: 13px;
		font-weight: 700;
	}
	.minghat-preview-account-sub {
		font-size: 11px;
		color: #8b8798;
	}

	@media (max-width: 768px) {
		.minghat-preview-sidebar {
			display: none;
		}
	}
</style>
