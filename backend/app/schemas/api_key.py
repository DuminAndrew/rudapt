from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApiKeyCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    rate_limit_per_min: int = Field(default=60, ge=1, le=1000)


class ApiKeyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    prefix: str
    rate_limit_per_min: int
    created_at: datetime
    last_used_at: datetime | None = None
    revoked_at: datetime | None = None


class ApiKeyCreated(ApiKeyOut):
    """Возвращается один раз при создании — содержит plaintext ключ."""
    plaintext: str
