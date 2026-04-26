"""Сбор свежих компаний из Y Combinator (публичный JSON каталога компаний).

YC отдаёт компании пакетами; здесь берём свежий батч и фильтруем по `launched_at`.
"""
from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.services.scraper.base import StartupRecord

YC_API = "https://api.ycombinator.com/v0.1/companies"


async def fetch_recent(limit: int = 30, batch: str | None = None) -> list[StartupRecord]:
    params: dict = {}
    if batch:
        params["batch"] = batch
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        r = await client.get(YC_API, params=params, headers={"User-Agent": "RuDapt/0.1"})
        r.raise_for_status()
        data = r.json()

    companies = data.get("companies") if isinstance(data, dict) else data
    if not companies:
        return []

    companies = sorted(
        companies,
        key=lambda c: c.get("launched_at") or c.get("year_founded") or 0,
        reverse=True,
    )[:limit]

    out: list[StartupRecord] = []
    for c in companies:
        out.append(
            StartupRecord(
                external_id=str(c.get("id") or c.get("slug") or c.get("name")),
                source="yc",
                name=c.get("name", "—"),
                tagline=c.get("one_liner"),
                description=c.get("long_description") or c.get("one_liner"),
                url=c.get("website") or c.get("url"),
                logo_url=c.get("small_logo_thumb_url") or c.get("logo"),
                categories=c.get("tags") or [],
                launched_at=_to_dt(c.get("launched_at")),
                raw=c,
            )
        )
    return out


def _to_dt(v) -> datetime | None:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        try:
            return datetime.fromtimestamp(int(v), tz=timezone.utc)
        except Exception:
            return None
    if isinstance(v, str):
        try:
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        except Exception:
            return None
    return None
