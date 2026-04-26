from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.startup import StartupOut


class GeneratePlanIn(BaseModel):
    startup_id: UUID
    region: str = Field(min_length=2, max_length=128)


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    startup_id: UUID
    region: str
    status: str
    model: str | None = None
    content: dict[str, Any] | None = None
    content_md: str | None = None
    error: str | None = None
    created_at: datetime
    finished_at: datetime | None = None


class ReportWithStartup(ReportOut):
    startup: StartupOut | None = None


class ReportListOut(BaseModel):
    items: list[ReportOut]
    total: int
