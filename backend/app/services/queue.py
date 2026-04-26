"""Очередь с fallback: ARQ (если есть Redis), иначе FastAPI BackgroundTasks."""
from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Callable

from app.config import settings

log = logging.getLogger(__name__)


async def _redis_available() -> bool:
    if not settings.REDIS_URL:
        return False
    try:
        from arq import create_pool
        from arq.connections import RedisSettings

        pool = await asyncio.wait_for(
            create_pool(RedisSettings.from_dsn(settings.REDIS_URL)), timeout=2
        )
        await pool.close()
        return True
    except Exception as e:
        log.debug("Redis unavailable: %s", e)
        return False


async def enqueue_or_run(
    job_name: str, *args, fallback_fn: Callable[..., Awaitable] | None = None
) -> str:
    """Отправить job в ARQ. Если Redis недоступен — запустить fallback_fn в фоне."""
    if await _redis_available():
        from arq import create_pool
        from arq.connections import RedisSettings

        pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
        try:
            await pool.enqueue_job(job_name, *args)
            return "queued"
        finally:
            await pool.close()
    if fallback_fn is not None:
        asyncio.create_task(fallback_fn(*args))
        return "running-inproc"
    return "skipped"
