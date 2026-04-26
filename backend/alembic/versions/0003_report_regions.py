"""report.regions for multi-region plans

Revision ID: 0003_report_regions
Revises: 0002_api_keys
Create Date: 2026-04-26
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_report_regions"
down_revision = "0002_api_keys"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("reports") as batch:
        batch.add_column(sa.Column("regions", sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("reports") as batch:
        batch.drop_column("regions")
