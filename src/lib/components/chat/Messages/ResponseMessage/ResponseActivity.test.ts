import { describe, expect, it } from 'vitest';
import { render } from 'svelte/server';
import { writable } from 'svelte/store';
import ResponseActivity from './ResponseActivity.svelte';

const renderActivity = (responding = false) =>
	render(ResponseActivity, {
		props: { responding },
		context: new Map([
			[
				'i18n',
				writable({ t: (key: string) => (key === 'Thinking...' ? 'Pensando...' : 'Gerando...') })
			]
		])
	}).body;

describe('response activity', () => {
	it('shows a translated waiting state before the answer arrives', () => {
		expect(renderActivity()).toContain('Pensando...');
	});

	it('shows a translated generating state while text is streaming', () => {
		const html = renderActivity(true);
		expect(html).toContain('Gerando...');
		expect(html).not.toContain('Pensando...');
	});

	it('announces the state without exposing decorative dots', () => {
		const html = renderActivity();
		expect(html).toContain('role="status"');
		expect(html).toContain('aria-live="polite"');
		expect(html).toContain('aria-atomic="true"');
		expect(html).toContain('aria-hidden="true"');
	});
});
