import logging
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.deps import get_current_user
from app.models import Subscription, User
from app.services import platega

router = APIRouter(prefix="/api/billing", tags=["billing"])
log = logging.getLogger(__name__)


class CheckoutOut(BaseModel):
    payment_url: str
    order_id: str


class StatusOut(BaseModel):
    plan: str
    is_pro: bool
    expires_at: datetime | None = None
    provider_configured: bool


class SubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    plan: str
    status: str
    started_at: datetime | None
    expires_at: datetime | None
    amount_minor: int
    currency: str
    created_at: datetime


async def _active(db: AsyncSession, user_id) -> Subscription | None:
    now = datetime.now(timezone.utc)
    rows = (
        await db.scalars(
            select(Subscription)
            .where(Subscription.user_id == user_id, Subscription.status == "active")
            .order_by(Subscription.expires_at.desc())
        )
    ).all()
    for s in rows:
        if s.expires_at and s.expires_at > now:
            return s
    return None


@router.get("/status", response_model=StatusOut)
async def status(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> StatusOut:
    sub = await _active(db, user.id)
    return StatusOut(
        plan="pro" if sub else user.plan,
        is_pro=bool(sub),
        expires_at=sub.expires_at if sub else None,
        provider_configured=platega.is_configured(),
    )


@router.post("/checkout", response_model=CheckoutOut)
async def checkout(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CheckoutOut:
    if not platega.is_configured():
        raise HTTPException(503, "payment provider is not configured")

    order_id = f"rudapt-{secrets.token_hex(8)}"
    sub = Subscription(
        user_id=user.id,
        plan="pro",
        status="pending",
        provider="platega",
        provider_order_id=order_id,
        amount_minor=settings.PRO_PRICE_RUB * 100,
        currency="RUB",
    )
    db.add(sub)
    await db.commit()

    try:
        session = await platega.create_payment(
            order_id=order_id,
            amount_minor=sub.amount_minor,
            currency=sub.currency,
            description=f"RuDapt Pro · {settings.PRO_PERIOD_DAYS} дней",
            customer_email=user.email,
        )
    except Exception as e:
        sub.status = "failed"
        sub.raw = {"error": str(e)}
        await db.commit()
        raise HTTPException(502, f"platega: {e}") from e

    sub.provider_payment_id = session.payment_id
    sub.raw = session.raw
    await db.commit()
    return CheckoutOut(payment_url=session.payment_url, order_id=order_id)


@router.post("/webhook", status_code=200)
async def webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_signature: str | None = Header(default=None, alias="X-Signature"),
) -> dict:
    body = await request.json()

    if not platega.verify_webhook(body, x_signature):
        raise HTTPException(401, "invalid signature")

    order_id = body.get("order_id")
    status_value = (body.get("status") or "").lower()
    if not order_id:
        raise HTTPException(400, "order_id missing")

    sub = await db.scalar(
        select(Subscription).where(Subscription.provider_order_id == order_id)
    )
    if sub is None:
        raise HTTPException(404, "subscription not found")

    if status_value in ("success", "succeeded", "paid", "completed"):
        now = datetime.now(timezone.utc)
        sub.status = "active"
        sub.started_at = sub.started_at or now
        sub.expires_at = now + timedelta(days=settings.PRO_PERIOD_DAYS)
        sub.user.plan = "pro" if hasattr(sub, "user") and sub.user else sub.user_id and "pro"
    elif status_value in ("failed", "cancelled", "expired"):
        sub.status = "failed"
    sub.raw = body
    await db.commit()
    return {"ok": True}


@router.get("/history", response_model=list[SubscriptionOut])
async def history(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Subscription]:
    rows = (
        await db.scalars(
            select(Subscription)
            .where(Subscription.user_id == user.id)
            .order_by(Subscription.created_at.desc())
        )
    ).all()
    return list(rows)
