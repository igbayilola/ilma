"""add micro_skills table and FK columns on questions/micro_lessons

Revision ID: c4f8e2a91d05
Revises: bd33d5c64307
Create Date: 2026-02-17 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c4f8e2a91d05"
down_revision: Union[str, Sequence[str], None] = "bd33d5c64307"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "micro_skills",
        sa.Column("skill_id", sa.UUID(), nullable=False),
        sa.Column("external_id", sa.String(length=100), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("difficulty_index", sa.Integer(), nullable=True),
        sa.Column("estimated_time_minutes", sa.Integer(), nullable=True),
        sa.Column("bloom_taxonomy_level", sa.String(length=50), nullable=True),
        sa.Column("mastery_threshold", sa.String(length=100), nullable=True),
        sa.Column("cep_frequency", sa.Integer(), nullable=True),
        sa.Column("prerequisites", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("recommended_exercise_types", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_micro_skills_skill_id"), "micro_skills", ["skill_id"], unique=False)
    op.create_index(op.f("ix_micro_skills_external_id"), "micro_skills", ["external_id"], unique=True)

    # Add optional micro_skill_id to questions
    op.add_column("questions", sa.Column("micro_skill_id", sa.UUID(), nullable=True))
    op.create_index(op.f("ix_questions_micro_skill_id"), "questions", ["micro_skill_id"], unique=False)
    op.create_foreign_key(
        "fk_questions_micro_skill_id",
        "questions", "micro_skills",
        ["micro_skill_id"], ["id"],
        ondelete="SET NULL",
    )

    # Add optional micro_skill_id to micro_lessons
    op.add_column("micro_lessons", sa.Column("micro_skill_id", sa.UUID(), nullable=True))
    op.create_index(op.f("ix_micro_lessons_micro_skill_id"), "micro_lessons", ["micro_skill_id"], unique=False)
    op.create_foreign_key(
        "fk_micro_lessons_micro_skill_id",
        "micro_lessons", "micro_skills",
        ["micro_skill_id"], ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_micro_lessons_micro_skill_id", "micro_lessons", type_="foreignkey")
    op.drop_index(op.f("ix_micro_lessons_micro_skill_id"), table_name="micro_lessons")
    op.drop_column("micro_lessons", "micro_skill_id")

    op.drop_constraint("fk_questions_micro_skill_id", "questions", type_="foreignkey")
    op.drop_index(op.f("ix_questions_micro_skill_id"), table_name="questions")
    op.drop_column("questions", "micro_skill_id")

    op.drop_index(op.f("ix_micro_skills_external_id"), table_name="micro_skills")
    op.drop_index(op.f("ix_micro_skills_skill_id"), table_name="micro_skills")
    op.drop_table("micro_skills")
