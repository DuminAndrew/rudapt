"""Универсальный раннер: тянет стартапы из всех источников и UPSERT-ит в БД."""
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Startup
from app.services.scraper import producthunt, yc
from app.services.scraper.base import StartupRecord

log = logging.getLogger(__name__)

_FIELDS = (
    "name", "tagline", "description", "url", "logo_url",
    "categories", "votes", "launched_at", "raw",
)


async def upsert_records(db: AsyncSession, records: list[StartupRecord]) -> int:
    if not records:
        return 0
    n = 0
    for r in records:
        existing = (
            await db.scalars(
                select(Startup).where(
                    Startup.source == r.source, Startup.external_id == r.external_id
                )
            )
        ).first()
        if existing:
            for f in _FIELDS:
                setattr(existing, f, getattr(r, f))
        else:
            db.add(Startup(**r.__dict__))
        n += 1
    await db.commit()
    return n


async def ingest_all(db: AsyncSession, limit: int = 30) -> dict:
    out: dict = {}
    for name, fn in (("producthunt", producthunt.fetch_recent), ("yc", yc.fetch_recent)):
        try:
            records = await fn(limit=limit)
            out[name] = await upsert_records(db, records)
        except Exception as e:
            log.exception("scraper %s failed", name)
            out[name] = f"error: {e}"
    return out
