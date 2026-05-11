"""Add diagnostic_completed_at column to profiles.

Revision ID: c2d3e4f5g6h7
Revises: 720b33690c58
Create Date: 2026-05-11 04:00:00.000000
"""
import sqlalchemy as sa
from alembic import op

revision = "c2d3e4f5g6h7"
down_revision = "720b33690c58"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "profiles",
        sa.Column("diagnostic_completed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("profiles", "diagnostic_completed_at")
