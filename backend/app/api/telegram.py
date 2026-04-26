import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.deps import get_current_user
from app.models import TelegramLink, TelegramSubscription, User

router = APIRouter(prefix="/api/telegram", tags=["telegram"])


class LinkOut(BaseModel):
    code: str
    expires_at: datetime
    bot_username: str | None = None
    deep_link: str | None = None


class SubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    chat_id: int
    username: str | None
    categories: list[str] | None
    created_at: datetime


class SubscriptionUpdate(BaseModel):
    categories: list[str]


@router.post("/link-code", response_model=LinkOut)
async def create_link_code(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> LinkOut:
    code = secrets.token_hex(4).upper()  # 8-char hex
    expires = datetime.now(timezone.utc) + timedelta(minutes=10)
    link = TelegramLink(user_id=user.id, code=code, expires_at=expires)
    db.add(link)
    await db.commit()
    deep = (
        f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={code}"
        if settings.TELEGRAM_BOT_USERNAME
        else None
    )
    return LinkOut(
        code=code,
        expires_at=expires,
        bot_username=settings.TELEGRAM_BOT_USERNAME or None,
        deep_link=deep,
    )


@router.get("/subscriptions", response_model=list[SubscriptionOut])
async def list_subs(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[TelegramSubscription]:
    rows = (
        await db.scalars(
            select(TelegramSubscription)
            .where(TelegramSubscription.user_id == user.id)
            .order_by(TelegramSubscription.created_at.desc())
        )
    ).all()
    return list(rows)


@router.patch("/subscriptions/{sub_id}", response_model=SubscriptionOut)
async def update_sub(
    sub_id: UUID,
    payload: SubscriptionUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TelegramSubscription:
    sub = await db.get(TelegramSubscription, sub_id)
    if sub is None or sub.user_id != user.id:
        raise HTTPException(404, "subscription not found")
    sub.categories = [c.strip() for c in payload.categories if c.strip()]
    await db.commit()
    await db.refresh(sub)
    return sub


@router.delete("/subscriptions/{sub_id}", status_code=204)
async def delete_sub(
    sub_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    sub = await db.get(TelegramSubscription, sub_id)
    if sub is None or sub.user_id != user.id:
        raise HTTPException(404, "subscription not found")
    await db.delete(sub)
    await db.commit()
