"""Webhook da Stripe para a MingHat.

Ativa/revoga assinantes a partir dos eventos da Stripe (checkout, assinatura,
fatura). Verificacao da assinatura feita na mao (HMAC-SHA256, stdlib) — sem
depender da lib `stripe`. Compartilha a MESMA allowlist da Cakto/Kiwify, entao
`is_subscriber_active` continua valendo para todos os provedores.

Configure STRIPE_WEBHOOK_SECRET (o "Signing secret" whsec_... do endpoint no
painel da Stripe).
"""

import hashlib
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

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
# Tolerancia do timestamp (anti-replay), em segundos.
SIGNATURE_TOLERANCE = int(os.getenv("STRIPE_SIGNATURE_TOLERANCE", "300"))

# Eventos que LIBERAM acesso (pagamento aprovado / assinatura ativa ou renovada).
ACTIVATE_EVENTS = {
    "checkout.session.completed",
    "checkout.session.async_payment_succeeded",
    "customer.subscription.created",
    "invoice.paid",
    "invoice.payment_succeeded",
}
# Eventos que REVOGAM acesso.
DEACTIVATE_EVENTS = {
    "customer.subscription.deleted",
    "customer.subscription.paused",
    "invoice.payment_failed",
    "charge.refunded",
    "charge.dispute.created",
}


def _verify_signature(raw: bytes, sig_header: str) -> bool:
    """Valida o header Stripe-Signature (t=...,v1=...) via HMAC-SHA256."""
    if not STRIPE_WEBHOOK_SECRET or not sig_header:
        return False
    try:
        parts = {}
        for item in sig_header.split(","):
            k, _, v = item.partition("=")
            parts.setdefault(k.strip(), v.strip())
        ts = parts.get("t")
        v1 = parts.get("v1")
        if not ts or not v1:
            return False
        # Anti-replay: rejeita timestamps muito antigos.
        try:
            if SIGNATURE_TOLERANCE and abs(int(time.time()) - int(ts)) > SIGNATURE_TOLERANCE:
                log.warning("Stripe webhook: timestamp fora da tolerancia")
                return False
        except ValueError:
            return False
        signed_payload = ts.encode() + b"." + raw
        expected = hmac.new(STRIPE_WEBHOOK_SECRET.encode(), signed_payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, v1)
    except Exception:
        log.exception("Stripe webhook: erro ao validar assinatura")
        return False


@router.post("/webhook")
async def stripe_webhook(request: Request):
    raw = await request.body()
    sig = request.headers.get("stripe-signature", "")
    if not _verify_signature(raw, sig):
        log.warning("Stripe webhook: assinatura invalida")
        return {"ok": False, "error": "invalid signature"}

    try:
        payload = json.loads(raw or b"{}")
    except Exception:
        payload = {}

    event = payload.get("type", "") if isinstance(payload, dict) else ""
    log.info("Stripe webhook: evento %s", event)

    email = _deep_find_email(payload)
    result_status = "ignored"
    if email:
        subs = _load()
        was_active = subs.get(email, {}).get("status") == "active"

        if event in ACTIVATE_EVENTS:
            subs[email] = {
                "status": "active",
                "event": event,
                "provider": "stripe",
                "ts": int(time.time()),
            }
            _save(subs)
            result_status = "active"
            if not was_active:
                send_welcome_email(email)
        elif event in DEACTIVATE_EVENTS:
            subs[email] = {
                "status": "inactive",
                "event": event,
                "provider": "stripe",
                "ts": int(time.time()),
            }
            _save(subs)
            result_status = "inactive"
        else:
            log.info("Stripe webhook: evento sem acao (%s) para %s", event, email)
    else:
        # Eventos sem e-mail no payload (ex.: subscription.deleted so traz o
        # customer id) nao dao pra mapear sem a API. Registramos e ignoramos.
        log.info("Stripe webhook: evento %s sem e-mail no payload", event)

    log.info("Stripe webhook: %s -> %s (%s)", email or "?", result_status, event)
    return {"ok": True, "email": email, "status": result_status, "event": event}
