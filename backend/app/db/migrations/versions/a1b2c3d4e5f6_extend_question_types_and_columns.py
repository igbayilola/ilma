"""extend question types and add metadata columns

Revision ID: a1b2c3d4e5f6
Revises: c4f8e2a91d05
Create Date: 2026-02-21 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "c4f8e2a91d05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# New enum values to add to questiontype
NEW_QUESTION_TYPES = [
    "numeric_input",
    "short_answer",
    "error_correction",
    "contextual_problem",
    "guided_steps",
    "justification",
    "tracing",
]


def upgrade() -> None:
    # -- 1. Extend the PostgreSQL enum with new values -------------------------
    # ALTER TYPE ... ADD VALUE cannot run inside a transaction in PostgreSQL,
    # so we commit the current transaction first.
    op.execute("COMMIT")
    for val in NEW_QUESTION_TYPES:
        op.execute(f"ALTER TYPE questiontype ADD VALUE IF NOT EXISTS '{val}'")

    # -- 2. Add new columns to questions table ---------------------------------
    op.add_column("questions", sa.Column("external_id", sa.String(length=150), nullable=True))
    op.add_column("questions", sa.Column("hint", sa.Text(), nullable=True))
    op.add_column("questions", sa.Column("bloom_level", sa.String(length=50), nullable=True))
    op.add_column("questions", sa.Column("ilma_level", sa.String(length=50), nullable=True))
    op.add_column("questions", sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("questions", sa.Column("common_mistake_targeted", sa.Text(), nullable=True))

    # -- 3. Create unique index on external_id ---------------------------------
    op.create_index(op.f("ix_questions_external_id"), "questions", ["external_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_questions_external_id"), table_name="questions")
    op.drop_column("questions", "common_mistake_targeted")
    op.drop_column("questions", "tags")
    op.drop_column("questions", "ilma_level")
    op.drop_column("questions", "bloom_level")
    op.drop_column("questions", "hint")
    op.drop_column("questions", "external_id")
    # Note: PostgreSQL does not support removing values from enums.
    # To fully downgrade, recreate the enum type (not done here for safety).
