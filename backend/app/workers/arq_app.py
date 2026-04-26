"""ARQ настройки воркера: задачи и cron."""
from __future__ import annotations

from arq.connections import RedisSettings
from arq.cron import cron

from app.config import settings
from app.workers.generate import generate_report
from app.workers.ingest import ingest_startups


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    functions = [generate_report, ingest_startups]
    cron_jobs = [
        cron(ingest_startups, hour={9, 15, 21}, minute=0, run_at_startup=True),
    ]
    keep_result = 3600
    max_jobs = 8
    job_timeout = 180
