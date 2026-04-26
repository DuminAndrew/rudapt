"""telegram tables

Revision ID: 0004_telegram
Revises: 0003_report_regions
Create Date: 2026-04-26
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_telegram"
down_revision = "0003_report_regions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "telegram_links",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(16), unique=True, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "telegram_subscriptions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("username", sa.String(64)),
        sa.Column("categories", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_digest_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_tg_subs_user", "telegram_subscriptions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_tg_subs_user", table_name="telegram_subscriptions")
    op.drop_table("telegram_subscriptions")
    op.drop_table("telegram_links")
