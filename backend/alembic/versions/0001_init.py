"""init schema

Revision ID: 0001_init
Revises:
Create Date: 2026-04-25
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255)),
        sa.Column("plan", sa.String(32), nullable=False, server_default="free"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "startups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("tagline", sa.String(512)),
        sa.Column("description", sa.String(8000)),
        sa.Column("url", sa.String(1024)),
        sa.Column("logo_url", sa.String(1024)),
        sa.Column("categories", postgresql.ARRAY(sa.String())),
        sa.Column("votes", sa.Integer()),
        sa.Column("launched_at", sa.DateTime(timezone=True)),
        sa.Column("raw", postgresql.JSONB()),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("source", "external_id", name="uq_startups_source_extid"),
    )
    op.create_index("ix_startups_launched_at", "startups", ["launched_at"])
    op.create_index(
        "ix_startups_categories", "startups", ["categories"], postgresql_using="gin"
    )

    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "startup_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("startups.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("region", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("model", sa.String(64)),
        sa.Column("content", postgresql.JSONB()),
        sa.Column("content_md", sa.Text()),
        sa.Column("prompt_tokens", sa.Integer()),
        sa.Column("completion_tokens", sa.Integer()),
        sa.Column("error", sa.String(2000)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_reports_user_created", "reports", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_reports_user_created", table_name="reports")
    op.drop_table("reports")
    op.drop_index("ix_startups_categories", table_name="startups")
    op.drop_index("ix_startups_launched_at", table_name="startups")
    op.drop_table("startups")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
