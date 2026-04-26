"""Универсальный раннер: тянет стартапы из всех источников и UPSERT-ит в БД."""
from __future__ import annotations

import logging

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Startup
from app.services.scraper import producthunt, yc
from app.services.scraper.base import StartupRecord

log = logging.getLogger(__name__)


async def upsert_records(db: AsyncSession, records: list[StartupRecord]) -> int:
    if not records:
        return 0
    rows = [r.__dict__ for r in records]
    stmt = insert(Startup).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["source", "external_id"],
        set_={
            "name": stmt.excluded.name,
            "tagline": stmt.excluded.tagline,
            "description": stmt.excluded.description,
            "url": stmt.excluded.url,
            "logo_url": stmt.excluded.logo_url,
            "categories": stmt.excluded.categories,
            "votes": stmt.excluded.votes,
            "launched_at": stmt.excluded.launched_at,
            "raw": stmt.excluded.raw,
        },
    )
    await db.execute(stmt)
    await db.commit()
    return len(records)


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
