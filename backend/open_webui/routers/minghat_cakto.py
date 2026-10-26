"""Webhook da Cakto para a MingHat.

Formato do payload (Cakto):
    { "event": "purchase_approved", "secret": "<segredo>", "data": { "customer": { "email": ... } } }

O `secret` vem no CORPO (nao em header). Compartilha a MESMA allowlist do webhook
da Kiwify (arquivo minghat_subscribers.json), entao `is_subscriber_active` continua
valendo para os dois provedores.

Regra importante: eventos de pagamento NAO concluido (ex.: "Pix gerado") NAO liberam
acesso — so libera em compra aprovada / assinatura ativa ou renovada.
"""

import hmac
import json
import logging
import os
import time

from fastapi import APIRouter, Request

from open_webui.utils.minghat_mail import send_welcome_email
from open_webui.routers.minghat_kiwify import _deep_find_email, _load, _save

log = logging.getLogger(__name__)
router = APIRouter()

EXPECTED_SECRET = os.getenv("CAKTO_WEBHOOK_SECRET", "")

# Libera acesso: compra aprovada / assinatura ativa ou renovada.
ACTIVATE_MARKERS = (
    "purchase_approved",
    "approved",
    "aprovad",
    "paid",
    "subscription_renewed",
    "subscription_renew",
    "renov",
    "subscription_active",
)
# Revoga acesso: recusa, reembolso, chargeback, cancelamento, pausa, atraso.
DEACTIVATE_MARKERS = (
    "refused",
    "recus",
    "refund",
    "reembol",
    "chargeback",
    "cancel",
    "paused",
    "pausada",
    "expired",
    "overdue",
    "atras",
    "declined",
)
# Pagamento ainda NAO concluido -> nao libera (ex.: Pix/boleto gerado, pendente).
PENDING_MARKERS = (
    "pix_generated",
    "pix",
    "waiting_payment",
    "waiting",
    "generated",
    "gerado",
    "pending",
    "aguardando",
    "boleto",
)


def _extract_secret(payload, request: Request) -> str:
    """Cakto envia o secret no corpo; aceitamos header/query como fallback."""
    if isinstance(payload, dict):
        s = payload.get("secret")
        if isinstance(s, str) and s:
            return s
    return (
        request.headers.get("x-cakto-signature")
        or request.headers.get("x-webhook-secret")
        or request.headers.get("authorization")
        or request.query_params.get("secret")
        or ""
    )


def _event_text(payload) -> str:
    """Concatena os campos que indicam o tipo/estado do evento, em minusculas."""
    parts = []
    if isinstance(payload, dict):
        for key in ("event", "type", "status"):
            v = payload.get(key)
            if isinstance(v, str):
                parts.append(v.lower())
        data = payload.get("data")
        if isinstance(data, dict):
            for key in ("status", "event", "type"):
                v = data.get(key)
                if isinstance(v, str):
                    parts.append(v.lower())
    return " ".join(parts)


def _extract_customer(payload) -> tuple[str, str]:
    """Extrai (nome, telefone) de data.customer (ou variantes) do payload Cakto."""
    name = ""
    phone = ""
    data = payload.get("data") if isinstance(payload, dict) else None
    customer = data.get("customer") if isinstance(data, dict) else None
    sources = [c for c in (customer, data, payload) if isinstance(c, dict)]
    for src in sources:
        for k in ("name", "full_name", "nome", "customer_name"):
            if not name and isinstance(src.get(k), str) and src.get(k).strip():
                name = src[k].strip()
        for k in ("phone", "phone_number", "telefone", "celular", "mobile", "whatsapp"):
            if not phone and isinstance(src.get(k), (str, int)) and str(src.get(k)).strip():
                phone = str(src[k]).strip()
    return name, phone


@router.post("/webhook")
async def cakto_webhook(request: Request):
    try:
        payload = await request.json()
    except Exception:
        try:
            payload = json.loads((await request.body()) or b"{}")
        except Exception:
            payload = {}

    secret = _extract_secret(payload, request)
    if EXPECTED_SECRET and not hmac.compare_digest(str(secret), EXPECTED_SECRET):
        log.warning("Cakto webhook: secret invalido")
        return {"ok": False, "error": "invalid secret"}

    log.info("Cakto webhook payload: %s", json.dumps(payload, ensure_ascii=False)[:2000])

    email = _deep_find_email(payload)
    name, phone = _extract_customer(payload)
    text = _event_text(payload)
    activate = any(m in text for m in ACTIVATE_MARKERS)
    deactivate = any(m in text for m in DEACTIVATE_MARKERS)
    pending = any(m in text for m in PENDING_MARKERS)

    result_status = "ignored"
    if email:
        subs = _load()
        was_active = subs.get(email, {}).get("status") == "active"

        prev = subs.get(email, {})
        if activate and not deactivate:
            subs[email] = {
                "status": "active",
                "event": text,
                "provider": "cakto",
                "name": name or prev.get("name", ""),
                "phone": phone or prev.get("phone", ""),
                "ts": int(time.time()),
            }
            _save(subs)
            result_status = "active"
            # Envia o e-mail de boas-vindas só na TRANSICAO para ativo.
            if not was_active:
                send_welcome_email(email)
        elif deactivate:
            subs[email] = {
                "status": "inactive",
                "event": text,
                "provider": "cakto",
                "name": name or prev.get("name", ""),
                "phone": phone or prev.get("phone", ""),
                "ts": int(time.time()),
            }
            _save(subs)
            result_status = "inactive"
        else:
            # Pix/boleto gerado, pendente ou evento desconhecido -> NAO libera acesso.
            result_status = "pending" if pending else "ignored"
            log.info("Cakto webhook: sem ativacao (%s) para %s", text or "?", email)

    log.info("Cakto webhook: %s -> %s (%s)", email or "?", result_status, text or "?")
    return {"ok": True, "email": email, "status": result_status, "event": text}
