"""Add profiles table and profile_id to student-facing tables.

Revision ID: j1a2b3c4d5e6
Revises: i0d4e5f6g7h8
Create Date: 2026-03-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "j1a2b3c4d5e6"
down_revision = "i0d4e5f6g7h8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create profiles table
    op.create_table(
        "profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("pin_hash", sa.String(255), nullable=True),
        sa.Column("grade_level_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("grade_levels.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("weekly_goal_minutes", sa.Integer(), nullable=False, server_default=sa.text("120")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Add profile_id to exercise_sessions
    op.add_column("exercise_sessions", sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True))
    op.create_index("ix_exercise_sessions_profile_id", "exercise_sessions", ["profile_id"])

    # Add profile_id to attempts
    op.add_column("attempts", sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True))
    op.create_index("ix_attempts_profile_id", "attempts", ["profile_id"])

    # Add profile_id to progress
    op.add_column("progress", sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True))
    op.create_index("ix_progress_profile_id", "progress", ["profile_id"])

    # Add profile_id to micro_skill_progress
    op.add_column("micro_skill_progress", sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True))
    op.create_index("ix_micro_skill_progress_profile_id", "micro_skill_progress", ["profile_id"])

    # Add profile_id to student_badges
    op.add_column("student_badges", sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True))
    op.create_index("ix_student_badges_profile_id", "student_badges", ["profile_id"])

    # Add profile_id to subscriptions
    op.add_column("subscriptions", sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True))
    op.create_index("ix_subscriptions_profile_id", "subscriptions", ["profile_id"])

    # Add profile_id to payments
    op.add_column("payments", sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True))
    op.create_index("ix_payments_profile_id", "payments", ["profile_id"])

    # Make student_id nullable on tables that now use profile_id
    op.alter_column("exercise_sessions", "student_id", nullable=True)
    op.alter_column("attempts", "student_id", nullable=True)
    op.alter_column("progress", "student_id", nullable=True)
    op.alter_column("micro_skill_progress", "student_id", nullable=True)
    op.alter_column("student_badges", "student_id", nullable=True)


def downgrade() -> None:
    # Drop profile_id columns
    op.drop_index("ix_payments_profile_id", "payments")
    op.drop_column("payments", "profile_id")

    op.drop_index("ix_subscriptions_profile_id", "subscriptions")
    op.drop_column("subscriptions", "profile_id")

    op.drop_index("ix_student_badges_profile_id", "student_badges")
    op.drop_column("student_badges", "profile_id")

    op.drop_index("ix_micro_skill_progress_profile_id", "micro_skill_progress")
    op.drop_column("micro_skill_progress", "profile_id")

    op.drop_index("ix_progress_profile_id", "progress")
    op.drop_column("progress", "profile_id")

    op.drop_index("ix_attempts_profile_id", "attempts")
    op.drop_column("attempts", "profile_id")

    op.drop_index("ix_exercise_sessions_profile_id", "exercise_sessions")
    op.drop_column("exercise_sessions", "profile_id")

    op.drop_table("profiles")

    # Restore NOT NULL on student_id columns
    op.alter_column("exercise_sessions", "student_id", nullable=False)
    op.alter_column("attempts", "student_id", nullable=False)
    op.alter_column("progress", "student_id", nullable=False)
    op.alter_column("micro_skill_progress", "student_id", nullable=False)
    op.alter_column("student_badges", "student_id", nullable=False)
