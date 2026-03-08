"""add skill metadata and micro_skill external_prerequisites

Revision ID: h9c3d4e5f6b7
Revises: g8b2d3e4f5a6
Create Date: 2026-02-24 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from alembic import op

revision: str = "h9c3d4e5f6b7"
down_revision: Union[str, Sequence[str], None] = "g8b2d3e4f5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Skill metadata columns
    op.add_column("skills", sa.Column("prerequisites", JSONB(), nullable=True))
    op.add_column("skills", sa.Column("common_mistakes", JSONB(), nullable=True))
    op.add_column("skills", sa.Column("exercise_types", JSONB(), nullable=True))
    op.add_column("skills", sa.Column("mastery_threshold", sa.String(length=100), nullable=True))

    # MicroSkill external_prerequisites
    op.add_column("micro_skills", sa.Column("external_prerequisites", JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column("micro_skills", "external_prerequisites")
    op.drop_column("skills", "mastery_threshold")
    op.drop_column("skills", "exercise_types")
    op.drop_column("skills", "common_mistakes")
    op.drop_column("skills", "prerequisites")
