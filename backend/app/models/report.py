from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, Index, JSON, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (Index("ix_reports_user_created", "user_id", "created_at"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    startup_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("startups.id", ondelete="RESTRICT"), nullable=False
    )
    region: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    model: Mapped[str | None] = mapped_column(String(64))
    content: Mapped[dict | None] = mapped_column(JSON)
    content_md: Mapped[str | None] = mapped_column(Text)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer)
    completion_tokens: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="reports")  # noqa: F821
    startup: Mapped["Startup"] = relationship()  # noqa: F821
