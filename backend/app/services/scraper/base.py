from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class StartupRecord:
    external_id: str
    source: str
    name: str
    tagline: str | None = None
    description: str | None = None
    url: str | None = None
    logo_url: str | None = None
    categories: list[str] = field(default_factory=list)
    votes: int | None = None
    launched_at: datetime | None = None
    raw: dict | None = None
