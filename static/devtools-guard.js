(() => {
	const host = window.location.hostname;
	const isLocal = host === 'localhost' || host === '127.0.0.1' || host === '::1';
	const disabled = localStorage.getItem('minghatDevtoolsGuard') === 'off';

	if (isLocal || disabled) {
		return;
	}

	const block = (event) => {
		event.preventDefault();
		event.stopPropagation();
		return false;
	};

	document.addEventListener('contextmenu', block, { capture: true });
	document.addEventListener(
		'keydown',
		(event) => {
			const key = String(event.key || '').toLowerCase();
			const blocked =
				key === 'f12' ||
				(event.ctrlKey && event.shiftKey && ['i', 'j', 'c'].includes(key)) ||
				(event.ctrlKey && ['u', 's'].includes(key)) ||
				(event.metaKey && event.altKey && ['i', 'j', 'c'].includes(key));

			if (blocked) {
				block(event);
			}
		},
		{ capture: true }
	);
})();
