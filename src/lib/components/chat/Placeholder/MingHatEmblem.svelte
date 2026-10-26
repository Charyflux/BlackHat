<script lang="ts">
	import { onMount } from 'svelte';

	let canvas: HTMLCanvasElement;
	let stage: HTMLDivElement;
	let ready = false;

	onMount(() => {
		let disposed = false;
		const cleanups: (() => void)[] = [];
		const cleanup = () => {
			disposed = true;
			cleanups
				.splice(0)
				.reverse()
				.forEach((dispose) => dispose());
		};

		const initialize = async () => {
			const THREE = await import('three');
			if (disposed) return;

			const renderer = new THREE.WebGLRenderer({
				canvas,
				alpha: true,
				antialias: true,
				powerPreference: 'low-power',
				preserveDrawingBuffer: true
			});
			cleanups.push(() => renderer.dispose());
			// Supersampling: renderiza em resolução bem maior que a exibida (nitidez 4K).
			renderer.setPixelRatio(Math.min(window.devicePixelRatio * 2, 4));
			renderer.setClearColor(0x000000, 0);
			renderer.outputColorSpace = THREE.SRGBColorSpace;

			const texture = await new THREE.TextureLoader().loadAsync('/static/minghat-mark.png');
			if (disposed) {
				texture.dispose();
				return;
			}
			cleanups.push(() => texture.dispose());
			texture.colorSpace = THREE.SRGBColorSpace;
			// Nitidez: filtro anisotrópico máximo + mipmaps para bordas limpas em qualquer ângulo.
			texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
			texture.magFilter = THREE.LinearFilter;
			texture.minFilter = THREE.LinearMipmapLinearFilter;
			texture.generateMipmaps = true;
			texture.needsUpdate = true;

			const scene = new THREE.Scene();
			const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 20);
			camera.position.z = 4.6;
			const hat = new THREE.Group();
			scene.add(hat);

			// A shallow curved relief preserves the original artwork while adding real perspective.
			const geometry = new THREE.PlaneGeometry(3.2, 3.2, 32, 32);
			const positions = geometry.attributes.position;
			for (let i = 0; i < positions.count; i++) {
				const x = positions.getX(i) / 1.6;
				const y = positions.getY(i) / 1.6;
				positions.setZ(i, 0.24 * (1 - x * x) + 0.06 * (1 - y * y));
			}
			geometry.computeVertexNormals();
			const material = new THREE.MeshBasicMaterial({
				map: texture,
				transparent: true,
				opacity: 1,
				depthWrite: false
			});
			hat.add(new THREE.Mesh(geometry, material));
			cleanups.push(
				() => geometry.dispose(),
				() => material.dispose()
			);

			const shadowGeometry = new THREE.PlaneGeometry(3.2, 3.2);
			const shadowMaterial = new THREE.MeshBasicMaterial({
				map: texture,
				color: 0x08030e,
				transparent: true,
				opacity: 0.12,
				depthWrite: false
			});
			const shadow = new THREE.Mesh(shadowGeometry, shadowMaterial);
			shadow.position.set(0, -0.2, -0.4);
			scene.add(shadow);
			cleanups.push(
				() => shadowGeometry.dispose(),
				() => shadowMaterial.dispose()
			);

			const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
			let targetX = 0;
			let targetY = 0;
			let inView = true;
			let previousTime = 0;
			const render = (time = previousTime) => {
				const delta = Math.max(0, Math.min((time - previousTime) / 1000, 0.05));
				previousTime = time;
				const blend = 1 - Math.exp(-6 * delta);
				const t = time / 1000;
				const still = motion.matches;
				hat.rotation.x = still ? 0 : THREE.MathUtils.lerp(hat.rotation.x, targetX, blend);
				hat.rotation.y = still
					? 0
					: THREE.MathUtils.lerp(hat.rotation.y, targetY + Math.sin(t * 0.65) * 0.045, blend);
				hat.position.y = still ? 0 : Math.sin(t * 1.15) * 0.07;
				hat.position.z = still ? 0.12 : 0.12 + Math.sin(t * 0.8) * 0.06;
				shadowMaterial.opacity = still ? 0.1 : 0.1 - hat.position.y * 0.18;
				renderer.render(scene, camera);
			};
			const updateAnimation = () => {
				renderer.setAnimationLoop(!motion.matches && !document.hidden && inView ? render : null);
				render();
			};
			const resize = () => {
				const { width, height } = stage.getBoundingClientRect();
				if (!width || !height) return;
				renderer.setSize(width, height, false);
				camera.aspect = width / height;
				camera.updateProjectionMatrix();
				render();
			};
			const move = (event: PointerEvent) => {
				if (motion.matches || event.pointerType !== 'mouse') return;
				// Aponta o chapéu para o cursor em relação ao centro do próprio emblema,
				// com amplitude bem visível (efeito de "olhar para o mouse").
				const rect = stage.getBoundingClientRect();
				const cx = rect.left + rect.width / 2;
				const cy = rect.top + rect.height / 2;
				const dx = (event.clientX - cx) / window.innerWidth;
				const dy = (event.clientY - cy) / window.innerHeight;
				targetY = THREE.MathUtils.clamp(dx * 1.1, -0.42, 0.42);
				targetX = THREE.MathUtils.clamp(dy * 0.75, -0.28, 0.28);
			};
			const reset = () => {
				targetX = 0;
				targetY = 0;
			};
			const contextLost = (event: Event) => {
				event.preventDefault();
				ready = false;
				cleanup();
			};
			const observer = new ResizeObserver(resize);
			observer.observe(stage);
			const visibility = new IntersectionObserver(([entry]) => {
				inView = entry.isIntersecting;
				updateAnimation();
			});
			visibility.observe(stage);
			window.addEventListener('pointermove', move, { passive: true });
			window.addEventListener('blur', reset);
			document.addEventListener('visibilitychange', updateAnimation);
			motion.addEventListener('change', updateAnimation);
			canvas.addEventListener('webglcontextlost', contextLost);
			cleanups.push(() => {
				renderer.setAnimationLoop(null);
				observer.disconnect();
				visibility.disconnect();
				window.removeEventListener('pointermove', move);
				window.removeEventListener('blur', reset);
				document.removeEventListener('visibilitychange', updateAnimation);
				motion.removeEventListener('change', updateAnimation);
				canvas.removeEventListener('webglcontextlost', contextLost);
			});
			resize();
			updateAnimation();
			ready = true;
		};

		initialize().catch(() => {
			ready = false;
			cleanup();
		});
		return cleanup;
	});
</script>

<div bind:this={stage} class="minghat-emblem-stage" class:ready aria-hidden="true">
	<img src="/static/minghat-mark.png" alt="" width="132" height="132" />
	<canvas bind:this={canvas}></canvas>
</div>

<style>
	.minghat-emblem-stage {
		position: relative;
		width: 200px;
		max-width: 100%;
		height: 132px;
		margin: -22px auto 9px;
		pointer-events: none;
		perspective: 700px;
		transform-origin: 50% 70%;
		animation: minghat-emerge 900ms cubic-bezier(0.16, 1, 0.3, 1) both;
	}
	img,
	canvas {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		object-fit: contain;
		filter: drop-shadow(0 12px 10px #00000060) drop-shadow(0 0 8px #a562ef30);
	}
	canvas {
		opacity: 0;
		transition: opacity 220ms ease-out;
	}
	.ready canvas {
		opacity: 1;
	}
	.ready img {
		opacity: 0;
	}
	img {
		transition: opacity 220ms ease-out;
	}
	@keyframes minghat-emerge {
		0% {
			opacity: 0;
			transform: translateY(34px) translateZ(-240px) rotateX(24deg) scale(0.45);
			filter: blur(8px);
		}
		58% {
			opacity: 1;
			transform: translateY(-7px) translateZ(34px) rotateX(-4deg) scale(1.08);
			filter: blur(0);
		}
		100% {
			opacity: 1;
			transform: translateY(0) translateZ(0) rotateX(0) scale(1);
			filter: blur(0);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.minghat-emblem-stage {
			animation: none;
		}
		canvas,
		img {
			transition: none;
		}
	}
	@media (max-width: 640px) {
		.minghat-emblem-stage {
			width: 180px;
			height: 116px;
			margin-top: -20px;
		}
	}
</style>
