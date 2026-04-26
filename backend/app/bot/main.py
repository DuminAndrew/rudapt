"""Telegram-бот RuDapt: привязка пользователя по коду из ЛК, управление подписками,
выдача дайджеста свежих стартапов в выбранных категориях.

Запуск:
    python -m app.bot.main

Требуется TELEGRAM_BOT_TOKEN в env.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message
from sqlalchemy import select

from app.config import settings
from app.db import SessionLocal
from app.models import Startup, TelegramLink, TelegramSubscription

log = logging.getLogger("rudapt.bot")
router = Router()


def _format_startup(s: Startup) -> str:
    cats = ", ".join((s.categories or [])[:3])
    parts = [f"<b>{_e(s.name)}</b>"]
    if s.tagline:
        parts.append(_e(s.tagline[:200]))
    if cats:
        parts.append(f"<i>{_e(cats)}</i>")
    if s.url:
        parts.append(f'<a href="{_e(s.url)}">источник</a>')
    return "\n".join(parts)


def _e(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


@router.message(CommandStart(deep_link=True))
async def start_with_code(message: Message, command: CommandObject):
    code = (command.args or "").strip().upper()
    if not code:
        await message.answer("Привет! Зайди в ЛК RuDapt → раздел Telegram → получи код привязки.")
        return
    async with SessionLocal() as db:
        link = (
            await db.scalars(select(TelegramLink).where(TelegramLink.code == code))
        ).first()
        now = datetime.now(timezone.utc)
        if link is None or link.used_at is not None or link.expires_at < now:
            await message.answer("❌ Код недействителен или истёк. Запроси новый в ЛК.")
            return

        existing = (
            await db.scalars(
                select(TelegramSubscription).where(
                    TelegramSubscription.chat_id == message.chat.id
                )
            )
        ).first()
        if existing:
            existing.user_id = link.user_id
            existing.username = message.from_user.username if message.from_user else None
        else:
            db.add(
                TelegramSubscription(
                    user_id=link.user_id,
                    chat_id=message.chat.id,
                    username=message.from_user.username if message.from_user else None,
                    categories=[],
                )
            )
        link.used_at = now
        await db.commit()

    await message.answer(
        "✅ Аккаунт привязан.\n\n"
        "Команды:\n"
        "• <code>/subscribe ai, fintech</code> — категории через запятую\n"
        "• <code>/list</code> — мои категории\n"
        "• <code>/digest</code> — свежие стартапы\n"
        "• <code>/unsubscribe</code> — отвязать чат",
        parse_mode="HTML",
    )


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет! Я RuDapt-бот.\n"
        "Чтобы привязать аккаунт — открой ЛК на сайте, перейди в раздел Telegram и нажми «Получить код привязки»."
    )


@router.message(Command("subscribe"))
async def subscribe(message: Message):
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: <code>/subscribe ai, fintech, b2b</code>", parse_mode="HTML")
        return
    cats = [c.strip().lower() for c in parts[1].split(",") if c.strip()]
    async with SessionLocal() as db:
        sub = (
            await db.scalars(
                select(TelegramSubscription).where(TelegramSubscription.chat_id == message.chat.id)
            )
        ).first()
        if sub is None:
            await message.answer("Сначала привяжи аккаунт через /start <код>.")
            return
        sub.categories = cats
        await db.commit()
    await message.answer(f"✅ Подписка обновлена: {', '.join(cats)}")


@router.message(Command("list"))
async def list_cats(message: Message):
    async with SessionLocal() as db:
        sub = (
            await db.scalars(
                select(TelegramSubscription).where(TelegramSubscription.chat_id == message.chat.id)
            )
        ).first()
    if sub is None:
        await message.answer("Чат не привязан. /start <код>")
        return
    cats = sub.categories or []
    await message.answer("Категории: " + (", ".join(cats) if cats else "— (пусто)"))


@router.message(Command("digest"))
async def digest(message: Message):
    async with SessionLocal() as db:
        sub = (
            await db.scalars(
                select(TelegramSubscription).where(TelegramSubscription.chat_id == message.chat.id)
            )
        ).first()
        if sub is None:
            await message.answer("Чат не привязан. /start <код>")
            return
        rows = (
            await db.scalars(
                select(Startup).order_by(Startup.launched_at.desc().nulls_last()).limit(20)
            )
        ).all()
    cats = set((sub.categories or []))
    if cats:
        rows = [
            r for r in rows
            if any(c.lower() in cats for c in (r.categories or []))
        ][:5]
    else:
        rows = list(rows)[:5]
    if not rows:
        await message.answer("Свежих стартапов под твои категории пока нет.")
        return
    body = "\n\n".join(_format_startup(r) for r in rows)
    await message.answer(f"<b>Свежие стартапы</b>\n\n{body}", parse_mode="HTML", disable_web_page_preview=True)


@router.message(Command("unsubscribe"))
async def unsubscribe(message: Message):
    async with SessionLocal() as db:
        sub = (
            await db.scalars(
                select(TelegramSubscription).where(TelegramSubscription.chat_id == message.chat.id)
            )
        ).first()
        if sub is not None:
            await db.delete(sub)
            await db.commit()
    await message.answer("Чат отвязан. Спасибо!")


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if not settings.TELEGRAM_BOT_TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set")
    bot = Bot(settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    log.info("starting RuDapt bot polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
