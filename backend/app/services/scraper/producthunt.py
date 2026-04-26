"""Сбор свежих стартапов с Product Hunt.

Если задан PRODUCTHUNT_TOKEN — используем GraphQL API,
иначе фолбэк на публичный RSS-фид (без апвоутов и категорий).
"""
from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.config import settings
from app.services.scraper.base import StartupRecord

PH_API = "https://api.producthunt.com/v2/api/graphql"
PH_RSS = "https://www.producthunt.com/feed"

GRAPHQL_QUERY = """
query LatestPosts($first: Int!) {
  posts(first: $first, order: NEWEST) {
    edges {
      node {
        id
        name
        tagline
        description
        url
        votesCount
        createdAt
        thumbnail { url }
        topics(first: 5) { edges { node { name } } }
      }
    }
  }
}
"""


async def fetch_via_api(limit: int = 30) -> list[StartupRecord]:
    headers = {
        "Authorization": f"Bearer {settings.PRODUCTHUNT_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            PH_API,
            headers=headers,
            json={"query": GRAPHQL_QUERY, "variables": {"first": limit}},
        )
        r.raise_for_status()
        data = r.json()["data"]["posts"]["edges"]

    out: list[StartupRecord] = []
    for edge in data:
        n = edge["node"]
        out.append(
            StartupRecord(
                external_id=str(n["id"]),
                source="producthunt",
                name=n["name"],
                tagline=n.get("tagline"),
                description=n.get("description"),
                url=n.get("url"),
                logo_url=(n.get("thumbnail") or {}).get("url"),
                categories=[t["node"]["name"] for t in (n.get("topics", {}) or {}).get("edges", [])],
                votes=n.get("votesCount"),
                launched_at=_parse_iso(n.get("createdAt")),
                raw=n,
            )
        )
    return out


async def fetch_via_rss(limit: int = 30) -> list[StartupRecord]:
    import feedparser

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        r = await client.get(PH_RSS, headers={"User-Agent": "RuDapt/0.1"})
        r.raise_for_status()
        text = r.text

    feed = feedparser.parse(text)
    out: list[StartupRecord] = []
    for entry in feed.entries[:limit]:
        out.append(
            StartupRecord(
                external_id=entry.get("id") or entry.get("link"),
                source="producthunt",
                name=entry.get("title", "").split(" - ")[0].strip(),
                tagline=entry.get("summary", "")[:500] if entry.get("summary") else None,
                description=entry.get("summary"),
                url=entry.get("link"),
                launched_at=_parse_struct(entry.get("published_parsed")),
                raw=dict(entry),
            )
        )
    return out


async def fetch_recent(limit: int = 30) -> list[StartupRecord]:
    if settings.PRODUCTHUNT_TOKEN:
        try:
            return await fetch_via_api(limit)
        except Exception:
            pass
    return await fetch_via_rss(limit)


def _parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def _parse_struct(t) -> datetime | None:
    if not t:
        return None
    try:
        return datetime(*t[:6], tzinfo=timezone.utc)
    except Exception:
        return None
