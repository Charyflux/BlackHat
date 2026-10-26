"""Servidor estatico minimo para a landing page da MingHat.

Entrega static/landing/home.html em qualquer caminho (ex.: /home), na porta
127.0.0.1:8815. O Cloudflare Tunnel roteia www.minghat.com.br/home para ca.
"""

import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANDING = os.path.join(ROOT, "static", "landing", "home.html")
HOST = os.getenv("MINGHAT_LANDING_HOST", "127.0.0.1")
PORT = int(os.getenv("MINGHAT_LANDING_PORT", "8815"))


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "public, max-age=300")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_GET(self) -> None:
        try:
            with open(LANDING, "rb") as f:
                body = f.read()
        except OSError:
            self._send(404, b"landing indisponivel", "text/plain; charset=utf-8")
            return
        self._send(200, body, "text/html; charset=utf-8")

    def do_HEAD(self) -> None:
        self.do_GET()

    def log_message(self, *args) -> None:
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"landing em http://{HOST}:{PORT} -> {LANDING}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
