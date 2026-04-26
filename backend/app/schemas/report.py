from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.startup import StartupOut


class GeneratePlanIn(BaseModel):
    startup_id: UUID
    region: str | None = Field(default=None, max_length=128)
    regions: list[str] | None = Field(default=None, max_length=5)

    def normalized_regions(self) -> list[str]:
        out: list[str] = []
        if self.regions:
            out.extend(r.strip() for r in self.regions if r and r.strip())
        if self.region and self.region.strip() and self.region.strip() not in out:
            out.append(self.region.strip())
        seen: set[str] = set()
        result: list[str] = []
        for r in out:
            if r not in seen:
                seen.add(r)
                result.append(r)
        return result


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    startup_id: UUID
    region: str
    regions: list[str] | None = None
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
