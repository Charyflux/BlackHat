<script lang="ts">
	import PencilSquare from '$lib/components/icons/PencilSquare.svelte';
	import CodeBracket from '$lib/components/icons/CodeBracket.svelte';
	import LightBulb from '$lib/components/icons/LightBulb.svelte';
	import TaskList from '$lib/components/icons/TaskList.svelte';
	import Search from '$lib/components/icons/Search.svelte';

	export let onChoose: (text: string) => void;

	const prompts = [
		{
			title: 'Escrever',
			detail: 'Um texto do zero',
			text: 'Escreva um texto claro e bem estruturado (com título, introdução, desenvolvimento e conclusão) sobre: ',
			icon: PencilSquare,
			color: 'violet'
		},
		{
			title: 'Programar',
			detail: 'Da ideia ao código',
			text: 'Como programador sênior, escreva o código comentado e explique as decisões e cuidados de segurança para: ',
			icon: CodeBracket,
			color: 'blue'
		},
		{
			title: 'Explorar',
			detail: 'Uma nova perspectiva',
			text: 'Explique de forma didática, do básico ao avançado, com exemplos e analogias, o assunto: ',
			icon: LightBulb,
			color: 'mint'
		},
		{
			title: 'Planejar',
			detail: 'O próximo passo',
			text: 'Crie um plano de ação com etapas numeradas, prazos sugeridos e o primeiro passo para começar hoje, para: ',
			icon: TaskList,
			color: 'amber'
		},
		{
			title: 'Recon',
			detail: 'Exemplo de pergunta de recon',
			text: 'Faça um recon completo do alvo autorizado abaixo e liste: subdomínios vivos, serviços web (status e tecnologia) e endpoints interessantes (admin, api, swagger, graphql). Destaque o que merece análise manual. Alvo: ',
			icon: Search,
			color: 'rose',
			full: true
		}
	];
</script>

<div class="minghat-prompts" aria-label="Ideias para começar">
	{#each prompts as prompt}
		<button
			type="button"
			class="minghat-prompt minghat-accent-{prompt.color} {prompt.full ? 'minghat-prompt-recon' : ''}"
			on:click={() => onChoose(prompt.text)}
		>
			<span class="minghat-prompt-icon" aria-hidden="true"
				><svelte:component this={prompt.icon} className="size-5" /></span
			>
			<span class="minghat-prompt-title">{prompt.title}</span>
			<span class="minghat-prompt-detail">{prompt.detail}</span>
		</button>
	{/each}
</div>
