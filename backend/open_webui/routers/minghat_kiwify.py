"""Webhook da Kiwify para a MingHat.

Recebe eventos de pagamento/assinatura, valida o token e mantém uma allowlist de
e-mails autorizados a criar conta (compra aprovada) / revogados (reembolso,
chargeback, cancelamento, atraso). O cadastro no MingHat é liberado só para
e-mails ativos nesta allowlist.
"""

import json
import logging
import os
import time
from pathlib import Path

from fastapi import APIRouter, Request

from open_webui.utils.minghat_mail import send_welcome_email

log = logging.getLogger(__name__)
router = APIRouter()

# Respeita DATA_DIR (isola dev/staging/producao) quando definido; cai para o
# diretorio padrao do Open WebUI (backend/open_webui/data) caso contrario.
_DATA_DIR = Path(os.getenv("DATA_DIR", Path(__file__).resolve().parents[1] / "data"))
SUBS_FILE = _DATA_DIR / "minghat_subscribers.json"
EXPECTED_TOKEN = os.getenv("MINGHAT_KIWIFY_TOKEN", "")

# Marcadores de status vindos da Kiwify (defensivo: cobre variações).
ACTIVATE_MARKERS = (
    "paid",
    "approved",
    "aprovada",
    "aprovado",
    "renov",
    "active",
    "ativa",
)
DEACTIVATE_MARKERS = (
    "refund",
    "reembol",
    "chargeback",
    "recus",
    "cancel",
    "atras",
    "overdue",
    "expired",
)


def _load() -> dict:
    if SUBS_FILE.exists():
        try:
            return json.loads(SUBS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save(data: dict) -> None:
    SUBS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUBS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _deep_find_email(obj) -> str | None:
    """Procura o primeiro valor que pareça um e-mail em qualquer nível do payload."""
    if isinstance(obj, str):
        if "@" in obj and "." in obj.split("@")[-1]:
            return obj.strip().lower()
        return None
    if isinstance(obj, dict):
        # prioriza chaves de e-mail
        for key in ("email", "customer_email", "buyer_email", "Email"):
            v = obj.get(key)
            if isinstance(v, str) and "@" in v:
                return v.strip().lower()
        for v in obj.values():
            found = _deep_find_email(v)
            if found:
                return found
    if isinstance(obj, list):
        for v in obj:
            found = _deep_find_email(v)
            if found:
                return found
    return None


def _status_text(payload: dict) -> str:
    parts = []
    for key in (
        "order_status",
        "webhook_event_type",
        "event",
        "status",
        "subscription_status",
        "type",
    ):
        v = payload.get(key) if isinstance(payload, dict) else None
        if isinstance(v, str):
            parts.append(v.lower())
    return " ".join(parts)


def is_subscriber_active(email: str) -> bool:
    if not email:
        return False
    entry = _load().get(email.strip().lower())
    return bool(entry and entry.get("status") == "active")


@router.post("/webhook")
async def kiwify_webhook(request: Request):
    token = request.query_params.get("token", "")
    # Falha fechada: sem token configurado (env) OU token errado -> recusa.
    if not EXPECTED_TOKEN or token != EXPECTED_TOKEN:
        log.warning("Kiwify webhook: token invalido ou nao configurado")
        return {"ok": False, "error": "invalid token"}

    try:
        payload = await request.json()
    except Exception:
        try:
            payload = json.loads((await request.body()) or b"{}")
        except Exception:
            payload = {}

    log.info("Kiwify webhook payload: %s", json.dumps(payload, ensure_ascii=False)[:2000])

    email = _deep_find_email(payload)
    status = _status_text(payload)
    activate = any(m in status for m in ACTIVATE_MARKERS)
    deactivate = any(m in status for m in DEACTIVATE_MARKERS)

    if email:
        subs = _load()
        was_active = subs.get(email, {}).get("status") == "active"

        if deactivate and not activate:
            subs[email] = {"status": "inactive", "event": status, "ts": int(time.time())}
        else:
            # compra aprovada / assinatura ativa / renovada (ou status desconhecido
            # de compra) -> autoriza o e-mail a criar conta.
            subs[email] = {"status": "active", "event": status, "ts": int(time.time())}
        _save(subs)
        log.info("Kiwify webhook: %s -> %s (%s)", email, subs[email]["status"], status)

        # So dispara o e-mail de boas-vindas na TRANSICAO para ativo, para nao
        # reenviar a cada disparo repetido de webhook (renovacao, retry, etc.).
        if subs[email]["status"] == "active" and not was_active:
            send_welcome_email(email)

    return {"ok": True, "email": email, "status": status}
