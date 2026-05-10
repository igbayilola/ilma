"""Add mock_exams and exam_sessions tables for Examen Blanc feature.

Revision ID: t1k2l3m4n5o6
Revises: s0j1k2l3m4n5
Create Date: 2026-03-25 20:00:00.000000

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "t1k2l3m4n5o6"
down_revision = "s0j1k2l3m4n5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mock_exams",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("grade_level_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("total_questions", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("question_distribution", postgresql.JSONB(), nullable=True),
        sa.Column("is_free", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_national", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("national_date", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["grade_level_id"], ["grade_levels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_mock_exams_grade_level_id", "mock_exams", ["grade_level_id"])
    op.create_index("ix_mock_exams_subject_id", "mock_exams", ["subject_id"])

    op.create_table(
        "exam_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mock_exam_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("time_spent_seconds", sa.Integer(), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("total_correct", sa.Integer(), nullable=True),
        sa.Column("total_questions", sa.Integer(), nullable=False),
        sa.Column("predicted_cep_score", sa.Float(), nullable=True),
        sa.Column("answers", postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="in_progress"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["mock_exam_id"], ["mock_exams.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_exam_sessions_profile_id", "exam_sessions", ["profile_id"])
    op.create_index("ix_exam_sessions_mock_exam_id", "exam_sessions", ["mock_exam_id"])


def downgrade() -> None:
    op.drop_index("ix_exam_sessions_mock_exam_id", table_name="exam_sessions")
    op.drop_index("ix_exam_sessions_profile_id", table_name="exam_sessions")
    op.drop_table("exam_sessions")
    op.drop_index("ix_mock_exams_subject_id", table_name="mock_exams")
    op.drop_index("ix_mock_exams_grade_level_id", table_name="mock_exams")
    op.drop_table("mock_exams")
