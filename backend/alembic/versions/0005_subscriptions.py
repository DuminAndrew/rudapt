"""subscriptions

Revision ID: 0005_subscriptions
Revises: 0004_telegram
Create Date: 2026-04-26
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_subscriptions"
down_revision = "0004_telegram"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan", sa.String(32), nullable=False, server_default="pro"),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("provider", sa.String(32), nullable=False, server_default="platega"),
        sa.Column("provider_order_id", sa.String(64), nullable=False, unique=True),
        sa.Column("provider_payment_id", sa.String(128)),
        sa.Column("amount_minor", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(8), nullable=False, server_default="RUB"),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("raw", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_subs_user_status", "subscriptions", ["user_id", "status"])


def downgrade() -> None:
    op.drop_index("ix_subs_user_status", table_name="subscriptions")
    op.drop_table("subscriptions")
