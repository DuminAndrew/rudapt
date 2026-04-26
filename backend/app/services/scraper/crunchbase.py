"""Crunchbase интеграция.

Crunchbase Basic REST API требует API-ключ (или RapidAPI прокси).
Через `CRUNCHBASE_API_KEY` (или `RAPIDAPI_KEY` + `RAPIDAPI_HOST`) можно
дёрнуть свежие организации с фильтром по дате founded.

Без ключа — фолбэк на публичный RSS feed news.crunchbase.com (анонсы свежих
проектов; парсим как стартапы с базовой инфой).
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.services.scraper.base import StartupRecord

log = logging.getLogger(__name__)

CB_API = "https://api.crunchbase.com/api/v4/searches/organizations"
CB_RSS = "https://news.crunchbase.com/feed/"


async def _fetch_via_api(limit: int) -> list[StartupRecord]:
    api_key = settings.CRUNCHBASE_API_KEY
    if not api_key:
        return []
    headers = {"X-cb-user-key": api_key, "Content-Type": "application/json"}
    body = {
        "field_ids": [
            "identifier",
            "name",
            "short_description",
            "website_url",
            "image_url",
            "categories",
            "founded_on",
        ],
        "order": [{"field_id": "founded_on", "sort": "desc"}],
        "limit": limit,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(CB_API, headers=headers, json=body)
        r.raise_for_status()
        data = r.json()

    out: list[StartupRecord] = []
    for entity in data.get("entities", []):
        p = entity.get("properties", {})
        out.append(
            StartupRecord(
                external_id=str(entity.get("uuid") or p.get("identifier", {}).get("uuid")),
                source="crunchbase",
                name=p.get("name", "—"),
                tagline=p.get("short_description"),
                description=p.get("short_description"),
                url=p.get("website_url"),
                logo_url=p.get("image_url"),
                categories=[c.get("value") for c in (p.get("categories") or []) if c.get("value")],
                launched_at=_parse_date(p.get("founded_on")),
                raw=entity,
            )
        )
    return out


async def _fetch_via_rss(limit: int) -> list[StartupRecord]:
    import feedparser

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        r = await client.get(CB_RSS, headers={"User-Agent": "RuDapt/0.1"})
        r.raise_for_status()
        text = r.text

    feed = feedparser.parse(text)
    out: list[StartupRecord] = []
    for entry in feed.entries[:limit]:
        out.append(
            StartupRecord(
                external_id=entry.get("id") or entry.get("link", ""),
                source="crunchbase",
                name=(entry.get("title") or "").split(":")[0].strip()[:255] or "Crunchbase post",
                tagline=(entry.get("summary") or "")[:500] or None,
                description=entry.get("summary"),
                url=entry.get("link"),
                launched_at=_parse_struct(entry.get("published_parsed")),
                raw=dict(entry),
            )
        )
    return out


async def fetch_recent(limit: int = 30) -> list[StartupRecord]:
    if settings.CRUNCHBASE_API_KEY:
        try:
            return await _fetch_via_api(limit)
        except Exception:
            log.exception("crunchbase api failed, falling back to rss")
    return await _fetch_via_rss(limit)


def _parse_date(s):
    if not s:
        return None
    if isinstance(s, dict):
        s = s.get("value")
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception:
        return None


def _parse_struct(t):
    if not t:
        return None
    try:
        return datetime(*t[:6], tzinfo=timezone.utc)
    except Exception:
        return None
