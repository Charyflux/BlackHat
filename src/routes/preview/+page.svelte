<script lang="ts">
	import MingHatPreview from '$lib/components/MingHatPreview.svelte';
	import MingHatPreviewSidebar from '$lib/components/MingHatPreviewSidebar.svelte';
	import MingHatPaywall from '$lib/components/MingHatPaywall.svelte';
</script>

<svelte:head>
	<title>BlackHat</title>
</svelte:head>

<div class="minghat-preview-page">
	<MingHatPreviewSidebar />
	<div class="minghat-preview-main">
		<MingHatPreview />
	</div>
	<MingHatPaywall />
</div>

<style>
	.minghat-preview-page {
		position: fixed;
		inset: 0;
		display: flex;
		flex-direction: row;
		background: linear-gradient(160deg, #140f1f 0%, #0b0b10 55%, #120d1b 100%);
		overflow: hidden;
	}
	.minghat-preview-main {
		flex: 1 1 auto;
		display: flex;
		align-items: center;
		justify-content: center;
		overflow: auto;
		min-width: 0;
	}

	/* ===== MingHat: piscantes neon roxo no fundo da vitrine publica ===== */
	.minghat-preview-page::before,
	.minghat-preview-page::after {
		content: '';
		position: fixed;
		inset: 0;
		z-index: -1;
		pointer-events: none;
		background-repeat: no-repeat;
		will-change: opacity, transform;
	}
	.minghat-preview-page::before {
		background-image:
			radial-gradient(circle 4.8px at 6% 14%, rgba(216, 188, 255, 1) 0%, rgba(139, 92, 246, 0.6) 40%, transparent 80%),
			radial-gradient(circle 1.9px at 15% 60%, rgba(206, 170, 255, 0.9), transparent 70%),
			radial-gradient(circle 2.8px at 24% 30%, rgba(206, 170, 255, 0.96), rgba(139, 92, 246, 0.3) 45%, transparent 76%),
			radial-gradient(circle 4.2px at 33% 78%, rgba(216, 188, 255, 1) 0%, rgba(139, 92, 246, 0.6) 40%, transparent 80%),
			radial-gradient(circle 1.8px at 41% 12%, rgba(206, 170, 255, 0.9), transparent 70%),
			radial-gradient(circle 2.8px at 48% 52%, rgba(206, 170, 255, 0.96), rgba(139, 92, 246, 0.3) 45%, transparent 76%),
			radial-gradient(circle 5px at 63% 26%, rgba(216, 188, 255, 1) 0%, rgba(139, 92, 246, 0.6) 40%, transparent 80%),
			radial-gradient(circle 2px at 72% 66%, rgba(206, 170, 255, 0.9), transparent 70%),
			radial-gradient(circle 2.8px at 80% 10%, rgba(206, 170, 255, 0.96), rgba(139, 92, 246, 0.3) 45%, transparent 76%),
			radial-gradient(circle 4.4px at 86% 44%, rgba(216, 188, 255, 1) 0%, rgba(139, 92, 246, 0.6) 40%, transparent 80%),
			radial-gradient(circle 1.8px at 92% 78%, rgba(206, 170, 255, 0.9), transparent 70%),
			radial-gradient(circle 2.8px at 97% 32%, rgba(206, 170, 255, 0.96), rgba(139, 92, 246, 0.3) 45%, transparent 76%),
			radial-gradient(circle 1.9px at 19% 45%, rgba(206, 170, 255, 0.9), transparent 70%),
			radial-gradient(circle 3px at 55% 40%, rgba(206, 170, 255, 0.96), rgba(139, 92, 246, 0.3) 45%, transparent 76%),
			radial-gradient(circle 4px at 69% 84%, rgba(216, 188, 255, 1) 0%, rgba(139, 92, 246, 0.6) 40%, transparent 80%),
			radial-gradient(circle 1.8px at 35% 20%, rgba(206, 170, 255, 0.9), transparent 70%);
		animation: preview-twinkle-a 10s ease-in-out infinite;
	}
	.minghat-preview-page::after {
		background-image:
			radial-gradient(circle 2px at 11% 34%, rgba(206, 170, 255, 0.9), transparent 70%),
			radial-gradient(circle 4.8px at 21% 82%, rgba(216, 188, 255, 1) 0%, rgba(139, 92, 246, 0.6) 40%, transparent 80%),
			radial-gradient(circle 2.8px at 30% 50%, rgba(206, 170, 255, 0.96), rgba(139, 92, 246, 0.3) 45%, transparent 76%),
			radial-gradient(circle 1.9px at 45% 84%, rgba(206, 170, 255, 0.9), transparent 70%),
			radial-gradient(circle 4.4px at 52% 38%, rgba(216, 188, 255, 1) 0%, rgba(139, 92, 246, 0.6) 40%, transparent 80%),
			radial-gradient(circle 2.8px at 66% 14%, rgba(206, 170, 255, 0.96), rgba(139, 92, 246, 0.3) 45%, transparent 76%),
			radial-gradient(circle 5px at 75% 82%, rgba(216, 188, 255, 1) 0%, rgba(139, 92, 246, 0.6) 40%, transparent 80%),
			radial-gradient(circle 1.8px at 83% 58%, rgba(206, 170, 255, 0.9), transparent 70%),
			radial-gradient(circle 2.8px at 89% 24%, rgba(206, 170, 255, 0.96), rgba(139, 92, 246, 0.3) 45%, transparent 76%),
			radial-gradient(circle 2px at 58% 62%, rgba(206, 170, 255, 0.9), transparent 70%),
			radial-gradient(circle 4.4px at 38% 20%, rgba(216, 188, 255, 1) 0%, rgba(139, 92, 246, 0.6) 40%, transparent 80%),
			radial-gradient(circle 2.8px at 95% 90%, rgba(206, 170, 255, 0.96), rgba(139, 92, 246, 0.3) 45%, transparent 76%),
			radial-gradient(circle 1.8px at 14% 22%, rgba(206, 170, 255, 0.9), transparent 70%),
			radial-gradient(circle 3px at 48% 66%, rgba(206, 170, 255, 0.96), rgba(139, 92, 246, 0.3) 45%, transparent 76%),
			radial-gradient(circle 4.2px at 78% 40%, rgba(216, 188, 255, 1) 0%, rgba(139, 92, 246, 0.6) 40%, transparent 80%),
			radial-gradient(circle 1.9px at 28% 8%, rgba(206, 170, 255, 0.9), transparent 70%);
		animation: preview-twinkle-b 12s ease-in-out infinite;
	}
	@keyframes preview-twinkle-a {
		0%,
		100% {
			opacity: 0.28;
			transform: translate3d(0, 0, 0);
		}
		50% {
			opacity: 0.8;
			transform: translate3d(20px, -16px, 0);
		}
	}
	@keyframes preview-twinkle-b {
		0%,
		100% {
			opacity: 1;
			transform: translate3d(0, 0, 0);
		}
		50% {
			opacity: 0.35;
			transform: translate3d(-20px, 16px, 0);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.minghat-preview-page::before,
		.minghat-preview-page::after {
			animation: none;
			transform: none;
			opacity: 0.4;
		}
	}
</style>
