<script lang="ts">
	import { goto } from '$app/navigation';
	import MingHatWelcome from './chat/Placeholder/MingHatWelcome.svelte';
	import MingHatPrompts from './chat/Placeholder/MingHatPrompts.svelte';
	import MingHatCapabilitiesCard from './MingHatCapabilitiesCard.svelte';

	// Ao tentar usar a IA sem login, vai para a tela de login.
	const gate = () => goto('/auth');
</script>

<div class="minghat-preview">
	<div class="minghat-home mx-auto w-full flex flex-col items-center">
		<MingHatWelcome />

		<div class="minghat-preview-input-wrap">
			<button
				id="message-input-container"
				type="button"
				class="minghat-preview-input"
				on:click={gate}
				aria-label="Enviar uma mensagem"
			>
				<span class="minghat-preview-placeholder">Como posso ajudar você hoje?</span>
				<span class="minghat-preview-send" aria-hidden="true">
					<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M22 2 11 13" />
						<path d="M22 2 15 22l-4-9-9-4 20-7z" />
					</svg>
				</span>
			</button>
		</div>

		<MingHatPrompts onChoose={gate} />

		<MingHatCapabilitiesCard />
	</div>
</div>

<style>
	.minghat-preview {
		width: 100%;
		flex: 1 1 auto;
		min-height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		overflow-y: auto;
	}
	.minghat-preview-input-wrap {
		width: 100%;
		max-width: 48rem;
		padding: 0 16px;
		margin: 6px auto 0;
	}
	.minghat-preview-input {
		width: 100%;
		min-height: 118px;
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 12px;
		padding: 18px 16px;
		border-radius: 16px;
		border: 1px solid var(--neon-border, #4a365f);
		background: linear-gradient(125deg, #1e1629, #15131c 65%, #18131f);
		box-shadow: 0 6px 32px #00000025, inset 0 1px 0 #e0baff0a;
		cursor: pointer;
		text-align: left;
		transition: border-color 160ms ease, box-shadow 160ms ease;
	}
	.minghat-preview-input:hover {
		border-color: #aa78e7;
		box-shadow: 0 0 0 1px #aa78e71c, 0 8px 38px #9250d51c;
	}
	.minghat-preview-placeholder {
		color: #8b8798;
		font-size: 15px;
	}
	.minghat-preview-send {
		flex: none;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 36px;
		height: 36px;
		border-radius: 999px;
		color: #fff;
		background: var(--neon-gradient, linear-gradient(120deg, #7735d0, #9145de 70%, #ab4bc7));
		box-shadow: 0 0 14px #a855f73d;
		align-self: flex-end;
	}
</style>
