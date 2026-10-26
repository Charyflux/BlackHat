<script lang="ts">
	import { getContext } from 'svelte';
	import type { Writable } from 'svelte/store';
	import type { i18n as i18nType } from 'i18next';

	const i18n = getContext<Writable<i18nType>>('i18n');
	export let responding = false;
</script>

<div class="minghat-response-activity" role="status" aria-live="polite" aria-atomic="true">
	<span class="activity-dots" aria-hidden="true">
		<span></span>
		<span></span>
		<span></span>
	</span>
	<span>{$i18n.t(responding ? 'Generating...' : 'Thinking...')}</span>
</div>

<style>
	.minghat-response-activity {
		display: flex;
		align-items: center;
		gap: 10px;
		min-height: 32px;
		padding-block: 6px;
		color: #7735c1;
		font-size: 13px;
		line-height: 20px;
	}

	:global(.dark) .minghat-response-activity {
		color: var(--neon-purple, #c29aff);
	}

	.activity-dots {
		display: flex;
		align-items: center;
		gap: 4px;
		width: 26px;
		height: 16px;
		flex-shrink: 0;
	}

	.activity-dots span {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: currentColor;
		animation: minghat-thinking 1.4s ease-in-out infinite;
	}

	.activity-dots span:nth-child(2) {
		animation-delay: 0.16s;
	}

	.activity-dots span:nth-child(3) {
		animation-delay: 0.32s;
	}

	@keyframes minghat-thinking {
		0%,
		70%,
		100% {
			transform: translateY(0);
			opacity: 0.45;
		}
		35% {
			transform: translateY(-3px);
			opacity: 1;
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.activity-dots span {
			animation: none;
			opacity: 1;
		}
	}
</style>
