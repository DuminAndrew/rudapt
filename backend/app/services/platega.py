"""Интеграция с Platega — российским платёжным шлюзом.

Настройки:
- PLATEGA_API_URL          — base URL API (по умолчанию https://app.platega.io/api)
- PLATEGA_MERCHANT_ID      — ID мерчанта
- PLATEGA_SECRET           — секретный ключ для подписи
- PLATEGA_RETURN_URL       — куда возвращать пользователя после оплаты
- PLATEGA_WEBHOOK_URL      — публичный URL backend для webhook (опц.)

Если ключи не заданы — `is_configured()` вернёт False и UI покажет
тарифы в режиме "coming soon" вместо чекаута.

⚠️ Точная схема payload Platega может отличаться по версии — методы
`create_payment` и `verify_signature` инкапсулируют интеграцию.
Если у вас другой набор полей, меняется только этот файл.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
from dataclasses import dataclass

import httpx

from app.config import settings

log = logging.getLogger(__name__)


@dataclass
class CheckoutSession:
    payment_id: str
    payment_url: str
    raw: dict


def is_configured() -> bool:
    return bool(settings.PLATEGA_MERCHANT_ID and settings.PLATEGA_SECRET)


def _sign(payload: dict) -> str:
    """sha256 hmac по канонической JSON-репрезентации (sorted keys)."""
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hmac.new(
        settings.PLATEGA_SECRET.encode("utf-8"),
        canonical.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


async def create_payment(
    *,
    order_id: str,
    amount_minor: int,
    currency: str,
    description: str,
    customer_email: str,
) -> CheckoutSession:
    if not is_configured():
        raise RuntimeError("Platega is not configured")

    payload = {
        "merchant_id": settings.PLATEGA_MERCHANT_ID,
        "order_id": order_id,
        "amount": amount_minor,
        "currency": currency,
        "description": description,
        "customer_email": customer_email,
        "success_url": settings.PLATEGA_RETURN_URL or "",
        "fail_url": settings.PLATEGA_RETURN_URL or "",
        "callback_url": settings.PLATEGA_WEBHOOK_URL or "",
    }
    payload["signature"] = _sign({k: v for k, v in payload.items() if k != "signature"})

    url = f"{settings.PLATEGA_API_URL.rstrip('/')}/payments"
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        data = r.json()

    pid = str(data.get("id") or data.get("payment_id") or "")
    purl = data.get("payment_url") or data.get("url") or ""
    if not pid or not purl:
        raise RuntimeError(f"Platega returned unexpected payload: {data}")
    return CheckoutSession(payment_id=pid, payment_url=purl, raw=data)


def verify_webhook(body: dict, signature: str | None) -> bool:
    """Проверить HMAC подпись из webhook (заголовок X-Signature или поле в body)."""
    if not signature:
        signature = body.get("signature")
    if not signature:
        return False
    body_for_check = {k: v for k, v in body.items() if k != "signature"}
    expected = _sign(body_for_check)
    return hmac.compare_digest(expected, signature)
