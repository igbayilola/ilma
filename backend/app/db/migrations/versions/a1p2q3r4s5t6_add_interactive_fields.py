"""Add media_references, interactive_config columns and new question types.

Revision ID: a1p2q3r4s5t6
Revises: z7q8r9s0t1u2
Create Date: 2026-04-04 00:00:00.000000
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "a1p2q3r4s5t6"
down_revision = "z7q8r9s0t1u2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("questions", sa.Column("media_references", JSONB, nullable=True))
    op.add_column("questions", sa.Column("interactive_config", JSONB, nullable=True))

    # Add new enum values for interactive question types
    op.execute("ALTER TYPE questiontype ADD VALUE IF NOT EXISTS 'DRAG_DROP'")
    op.execute("ALTER TYPE questiontype ADD VALUE IF NOT EXISTS 'INTERACTIVE_DRAW'")
    op.execute("ALTER TYPE questiontype ADD VALUE IF NOT EXISTS 'CHART_INPUT'")
    op.execute("ALTER TYPE questiontype ADD VALUE IF NOT EXISTS 'AUDIO_COMPREHENSION'")


def downgrade() -> None:
    op.drop_column("questions", "interactive_config")
    op.drop_column("questions", "media_references")
