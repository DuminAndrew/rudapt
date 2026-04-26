from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, JSON, ForeignKey, Uuid, Index, BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class TelegramLink(Base):
    """Одноразовый код для привязки Telegram chat_id к пользователю."""
    __tablename__ = "telegram_links"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class TelegramSubscription(Base):
    """Привязанный chat_id с подпиской на категории стартапов."""
    __tablename__ = "telegram_subscriptions"
    __table_args__ = (Index("ix_tg_subs_user", "user_id"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(64))
    categories: Mapped[list[str] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_digest_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
