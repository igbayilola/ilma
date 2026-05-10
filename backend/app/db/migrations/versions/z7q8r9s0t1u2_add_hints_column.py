"""Add hints JSONB column to questions and migrate existing hint data.

Revision ID: z7q8r9s0t1u2
Revises: y6p7q8r9s0t1
Create Date: 2026-04-03 00:00:02.000000
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "z7q8r9s0t1u2"
down_revision = "y6p7q8r9s0t1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("questions", sa.Column("hints", JSONB, nullable=True))

    # Migrate existing hint (string) → hints (array with single element)
    op.execute("""
        UPDATE questions
        SET hints = jsonb_build_array(hint)
        WHERE hint IS NOT NULL AND hint != '' AND hints IS NULL
    """)


def downgrade() -> None:
    op.drop_column("questions", "hints")
