"""Add calcul_mental value to sessionmode enum.

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-13 00:00:01.000000
"""
from alembic import op

revision = "b2c3d4e5f6g7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new enum value to the existing PostgreSQL enum type
    op.execute("ALTER TYPE sessionmode ADD VALUE IF NOT EXISTS 'calcul_mental'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values; this is a no-op.
    # The value will remain but be unused after downgrade.
    pass
