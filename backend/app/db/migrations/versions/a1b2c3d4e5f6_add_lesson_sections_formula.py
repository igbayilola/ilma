"""Add sections, formula, external_id to micro_lessons; make content_html nullable.

Revision ID: a1b2c3d4e5f6
Revises: z7q8r9s0t1u2
Create Date: 2026-04-13 00:00:00.000000
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "a1b2c3d4e5f6"
down_revision = "z7q8r9s0t1u2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("micro_lessons", sa.Column("sections", JSONB, nullable=True))
    op.add_column("micro_lessons", sa.Column("formula", sa.Text(), nullable=True))
    op.add_column("micro_lessons", sa.Column("external_id", sa.String(100), nullable=True))

    # Make content_html nullable (new structured lessons may not have it)
    op.alter_column("micro_lessons", "content_html", existing_type=sa.Text(), nullable=True)

    # Unique index on external_id for upsert imports
    op.create_index("ix_micro_lessons_external_id", "micro_lessons", ["external_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_micro_lessons_external_id", table_name="micro_lessons")
    op.drop_column("micro_lessons", "external_id")
    op.drop_column("micro_lessons", "formula")
    op.drop_column("micro_lessons", "sections")
    op.alter_column("micro_lessons", "content_html", existing_type=sa.Text(), nullable=False)
