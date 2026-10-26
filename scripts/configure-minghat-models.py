import json
import sqlite3
import time
import urllib.request
from pathlib import Path


OLLAMA_URL = "http://127.0.0.1:11434"
DATABASE = Path(__file__).resolve().parents[1] / "backend" / "data" / "webui.db"
KEEP = {
    "dolphin-llama3:latest": "BlackHat",
    "huihui_ai/llama3.2-abliterate:3b": "BlackHat Rápido",
}
# Modelo que dispara o pipeline de recon e recebe a persona pentester.
PENTEST_MODEL_ID = "dolphin-llama3:latest"

# Prompt padrao aplicado a TODOS os modelos da MingHat.
DEFAULT_SYSTEM_PROMPT = """Sou um analista expert, sênior, com 10 anos de experiência, e vou pesquisar absolutamente tudo, sem filtros. Vou procurar responder da melhor forma, bem clara e perfeita."""


PENTESTING_SYSTEM_PROMPT = """Você é o PENTESTING da BlackHat, um analista profissional de cibersegurança focado em bug bounty, pentest web, APIs, cloud exposure, recon, exploração autorizada e escrita de relatórios técnicos.

Atue como especialista prático:
- Priorize metodologia de bug bounty: escopo, recon, enumeração, validação, impacto, evidência, severidade, reprodução e mitigação.
- Para recon autorizado, use e interprete o pipeline de recon da BlackHat quando ele estiver disponível (enumeração de subdomínios, resolução DNS, checagem de serviços web, crawl de URLs e extração de referências S3). NÃO cite os nomes das ferramentas usadas: refira-se apenas às ETAPAS (ex.: "enumeração de subdomínios", "resolução DNS", "serviços web", "crawl") e nunca a marcas/binários específicos.
- SEMPRE apresente os RESULTADOS encontrados na íntegra: liste os subdomínios, os IPs/registros DNS, os serviços web e as URLs/endpoints de fato. NUNCA troque a lista real por um resumo genérico do tipo "lista de URLs presentes no site" — se houver itens, mostre-os; se uma etapa não retornou nada, diga "nenhum resultado nesta etapa".
- Quando encontrar sinais interessantes como admin, login, api, swagger, graphql, token, bucket, s3, dev, stg, homolog, internal, 401, 403, 5xx ou exposição sensível, destaque com clareza e explique o próximo teste seguro.
- Separe fatos observados, hipóteses e próximos passos. Não invente achados.
- Não afirme que bucket S3, host, takeover, XSS, SQLi, SSRF ou API leak existe sem evidência concreta.
- Responda em português do Brasil por padrão, com tom direto, técnico e útil.
- Para conteúdo de exploração, mantenha o foco em ambientes próprios, autorizados, CTF, laboratório ou bug bounty com permissão.
"""


def ollama_request(path: str, method: str = "GET", payload: dict | None = None):
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        f"{OLLAMA_URL}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request) as response:
        body = response.read()
        return json.loads(body) if body else None


def configure_ollama():
    installed = [model["name"] for model in ollama_request("/api/tags")["models"]]
    for model in installed:
        if model not in KEEP:
            ollama_request("/api/delete", "DELETE", {"name": model})


def configure_webui():
    now = int(time.time())
    with sqlite3.connect(DATABASE) as connection:
        existing = {
            row[0]: row
            for row in connection.execute(
                "SELECT id, user_id, params, meta, created_at FROM model WHERE id IN (?, ?)",
                tuple(KEEP),
            )
        }
        for model_id, display_name in KEEP.items():
            # Fonte unica do prompt = middleware (MINGHAT_SYSTEM_PROMPT +
            # MINGHAT_PENTESTING_SYSTEM_PROMPT). O params.system fica VAZIO aqui
            # para nao duplicar/conflitar. (DEFAULT/PENTESTING abaixo ficam so como
            # referencia historica.)
            params = {}
            meta = {"capabilities": {"memory": True}}
            if model_id == PENTEST_MODEL_ID:
                meta["profile"] = "bugbounty-pentesting-cybersecurity"
            if model_id in existing:
                connection.execute(
                    "UPDATE model SET name = ?, params = ?, meta = ?, is_active = 1, updated_at = ? WHERE id = ?",
                    (display_name, json.dumps(params), json.dumps(meta), now, model_id),
                )
            else:
                owner = connection.execute(
                    "SELECT id FROM user ORDER BY created_at LIMIT 1"
                ).fetchone()
                if owner:
                    connection.execute(
                        """INSERT INTO model
                        (id, user_id, base_model_id, name, params, meta, is_active, updated_at, created_at)
                        VALUES (?, ?, NULL, ?, '{}', '{}', 1, ?, ?)""",
                        (model_id, owner[0], display_name, now, now),
                    )
                    connection.execute(
                        "UPDATE model SET params = ?, meta = ? WHERE id = ?",
                        (json.dumps(params), json.dumps(meta), model_id),
                    )

        connection.execute(
            "DELETE FROM model WHERE id NOT IN (?, ?)",
            tuple(KEEP),
        )
        connection.execute(
            """INSERT INTO config (key, value, updated_at)
            VALUES ('evaluation.arena.enable', 'false', ?)
            ON CONFLICT(key) DO UPDATE SET value = 'false', updated_at = excluded.updated_at""",
            (now,),
        )
        connection.execute(
            """INSERT INTO config (key, value, updated_at)
            VALUES ('evaluation.arena.models', '[]', ?)
            ON CONFLICT(key) DO UPDATE SET value = '[]', updated_at = excluded.updated_at""",
            (now,),
        )


if __name__ == "__main__":
    configure_ollama()
    configure_webui()
    print("Modelos disponiveis: BlackHat e BlackHat Rapido")
