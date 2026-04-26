"""api keys

Revision ID: 0002_api_keys
Revises: 0001_init
Create Date: 2026-04-26
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_api_keys"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "api_keys",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("prefix", sa.String(16), nullable=False),
        sa.Column("key_hash", sa.String(128), nullable=False, unique=True),
        sa.Column("rate_limit_per_min", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_used_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_api_keys_user", "api_keys", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_api_keys_user", table_name="api_keys")
    op.drop_table("api_keys")
