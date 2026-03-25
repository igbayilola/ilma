"""Add teacher role and classroom/assignment tables.

Revision ID: u2l3m4n5o6p7
Revises: t1k2l3m4n5o6
Create Date: 2026-03-25 20:00:00.000000

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "u2l3m4n5o6p7"
down_revision = "t1k2l3m4n5o6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add 'teacher' to userrole enum
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'teacher'")

    # Create classrooms table
    op.create_table(
        "classrooms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("invite_code", sa.String(8), unique=True, nullable=False, index=True),
        sa.Column("grade_level_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("grade_levels.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("max_students", sa.Integer(), default=30, nullable=False),
    )

    # Create classroom_students table
    op.create_table(
        "classroom_students",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("classroom_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("classroom_id", "profile_id", name="uq_classroom_profile"),
    )

    # Create assignments table
    op.create_table(
        "assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("classroom_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("skill_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("question_count", sa.Integer(), default=10, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("assignments")
    op.drop_table("classroom_students")
    op.drop_table("classrooms")
    # Note: PostgreSQL does not support removing values from enums easily.
    # The 'teacher' value will remain in the userrole enum after downgrade.
