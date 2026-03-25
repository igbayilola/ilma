"""Add editor role to userrole enum.

Revision ID: w4n5o6p7q8r9
Revises: v3m4n5o6p7q8
Create Date: 2026-03-25 00:00:00.000000
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "w4n5o6p7q8r9"
down_revision = "v3m4n5o6p7q8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'EDITOR'")


def downgrade() -> None:
    # PostgreSQL does not support removing values from an enum type directly.
    # A full migration to a new enum would be needed; leaving as no-op.
    pass
