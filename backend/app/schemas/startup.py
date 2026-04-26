from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class StartupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    source: str
    name: str
    tagline: str | None = None
    description: str | None = None
    url: str | None = None
    logo_url: str | None = None
    categories: list[str] | None = None
    votes: int | None = None
    launched_at: datetime | None = None


class StartupListOut(BaseModel):
    items: list[StartupOut]
    total: int
    limit: int
    offset: int
