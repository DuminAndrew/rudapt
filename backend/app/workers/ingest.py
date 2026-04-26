"""ARQ-воркер: периодический парсинг свежих стартапов."""
from __future__ import annotations

import logging

from app.db import SessionLocal
from app.services.scraper.runner import ingest_all

log = logging.getLogger(__name__)


async def ingest_startups(ctx, limit: int = 30) -> dict:
    async with SessionLocal() as db:
        result = await ingest_all(db, limit=limit)
        log.info("ingest finished: %s", result)
        return result
