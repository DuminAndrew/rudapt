from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, Integer, JSON, Uuid, UniqueConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Startup(Base):
    __tablename__ = "startups"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_startups_source_extid"),
        Index("ix_startups_launched_at", "launched_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tagline: Mapped[str | None] = mapped_column(String(512))
    description: Mapped[str | None] = mapped_column(String(8000))
    url: Mapped[str | None] = mapped_column(String(1024))
    logo_url: Mapped[str | None] = mapped_column(String(1024))
    categories: Mapped[list[str] | None] = mapped_column(JSON)
    votes: Mapped[int | None] = mapped_column(Integer)
    launched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    raw: Mapped[dict | None] = mapped_column(JSON)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
