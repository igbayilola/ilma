"""add micro_skill_progress table and exercise_sessions.micro_skill_id

Revision ID: i0d4e5f6g7h8
Revises: h9c3d4e5f6b7
Create Date: 2026-02-26 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "i0d4e5f6g7h8"
down_revision: Union[str, Sequence[str], None] = "h9c3d4e5f6b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "micro_skill_progress",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("student_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("micro_skill_id", UUID(as_uuid=True), sa.ForeignKey("micro_skills.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("smart_score", sa.Float, default=0.0, nullable=False, server_default="0.0"),
        sa.Column("total_attempts", sa.Integer, default=0, nullable=False, server_default="0"),
        sa.Column("correct_attempts", sa.Integer, default=0, nullable=False, server_default="0"),
        sa.Column("streak", sa.Integer, default=0, nullable=False, server_default="0"),
        sa.Column("best_streak", sa.Integer, default=0, nullable=False, server_default="0"),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_decay_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("student_id", "micro_skill_id", name="uq_student_micro_skill"),
    )

    op.add_column(
        "exercise_sessions",
        sa.Column("micro_skill_id", UUID(as_uuid=True), sa.ForeignKey("micro_skills.id", ondelete="SET NULL"), nullable=True, index=True),
    )


def downgrade() -> None:
    op.drop_column("exercise_sessions", "micro_skill_id")
    op.drop_table("micro_skill_progress")
