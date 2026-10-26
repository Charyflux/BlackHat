// Proxy HTTP com Basic Auth na frente do ambiente de staging (teste.minghat.com.br).
// Sem dependencias externas (so http/net do Node), inclui suporte a WebSocket
// (upgrade), necessario para o streaming do chat via socket.io.
//
// Uso: node staging-basic-auth-proxy.cjs
// Configuracao via variaveis de ambiente:
//   STAGING_PROXY_PORT   porta publica do proxy (default 8822)
//   STAGING_TARGET_PORT  porta do vite do ambiente de staging (default 8821)
//   STAGING_AUTH_USER    usuario exigido (default "minghat")
//   STAGING_AUTH_PASS    senha exigida (obrigatoria - sem default por seguranca)

const http = require('http');
const net = require('net');

const PROXY_PORT = parseInt(process.env.STAGING_PROXY_PORT || '8822', 10);
const TARGET_PORT = parseInt(process.env.STAGING_TARGET_PORT || '8821', 10);
const AUTH_USER = process.env.STAGING_AUTH_USER || 'minghat';
const AUTH_PASS = process.env.STAGING_AUTH_PASS;

if (!AUTH_PASS) {
	console.error('STAGING_AUTH_PASS nao definido. Defina uma senha antes de iniciar o proxy.');
	process.exit(1);
}

const expected = 'Basic ' + Buffer.from(`${AUTH_USER}:${AUTH_PASS}`).toString('base64');

function isAuthorized(headers) {
	const auth = headers['authorization'];
	return typeof auth === 'string' && auth === expected;
}

function sendUnauthorized(res) {
	res.writeHead(401, {
		'WWW-Authenticate': 'Basic realm="MingHat Staging"',
		'Content-Type': 'text/plain; charset=utf-8'
	});
	res.end('401 - autenticacao necessaria para o ambiente de staging da MingHat.');
}

const server = http.createServer((req, res) => {
	if (!isAuthorized(req.headers)) {
		sendUnauthorized(res);
		return;
	}

	const proxyReq = http.request(
		{
			host: '127.0.0.1',
			port: TARGET_PORT,
			path: req.url,
			method: req.method,
			headers: req.headers
		},
		(proxyRes) => {
			res.writeHead(proxyRes.statusCode || 502, proxyRes.headers);
			proxyRes.pipe(res, { end: true });
		}
	);

	proxyReq.on('error', (err) => {
		console.error('Erro ao encaminhar requisicao:', err.message);
		if (!res.headersSent) {
			res.writeHead(502, { 'Content-Type': 'text/plain; charset=utf-8' });
		}
		res.end('502 - staging indisponivel.');
	});

	req.pipe(proxyReq, { end: true });
});

// WebSocket (socket.io) - proxy bruto de socket TCP apos validar o Basic Auth
// no handshake HTTP inicial do upgrade.
server.on('upgrade', (req, clientSocket, head) => {
	if (!isAuthorized(req.headers)) {
		clientSocket.write(
			'HTTP/1.1 401 Unauthorized\r\n' +
				'WWW-Authenticate: Basic realm="MingHat Staging"\r\n' +
				'Connection: close\r\n\r\n'
		);
		clientSocket.destroy();
		return;
	}

	const targetSocket = net.connect(TARGET_PORT, '127.0.0.1', () => {
		let rawHeaders = `${req.method} ${req.url} HTTP/${req.httpVersion}\r\n`;
		for (let i = 0; i < req.rawHeaders.length; i += 2) {
			rawHeaders += `${req.rawHeaders[i]}: ${req.rawHeaders[i + 1]}\r\n`;
		}
		rawHeaders += '\r\n';

		targetSocket.write(rawHeaders);
		if (head && head.length) targetSocket.write(head);

		targetSocket.pipe(clientSocket);
		clientSocket.pipe(targetSocket);
	});

	targetSocket.on('error', (err) => {
		console.error('Erro no upgrade (WS) para staging:', err.message);
		clientSocket.destroy();
	});
	clientSocket.on('error', () => targetSocket.destroy());
});

server.listen(PROXY_PORT, '127.0.0.1', () => {
	console.log(
		`Proxy de staging com Basic Auth ouvindo em 127.0.0.1:${PROXY_PORT} -> 127.0.0.1:${TARGET_PORT}`
	);
});
