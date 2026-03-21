"""Add social tables, editorial workflow columns, notification prefs.

New tables:
- weekly_leaderboard (classement hebdomadaire)
- challenges (défis entre élèves)
- content_transitions (audit trail éditorial)

New columns:
- questions.status (ContentStatus enum, default PUBLISHED)
- questions.reviewer_notes (text)
- micro_lessons.status (ContentStatus enum, default PUBLISHED)
- micro_lessons.reviewer_notes (text)
- users.notification_prefs (JSONB)

Revision ID: o6f7g8h9i0j1
Revises: n5e6f7g8h9i0
Create Date: 2026-03-11 18:00:00.000000

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "o6f7g8h9i0j1"
down_revision = "n5e6f7g8h9i0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Create enums ────────────────────────────────────────
    contentstatus = postgresql.ENUM(
        "DRAFT", "IN_REVIEW", "PUBLISHED", "ARCHIVED",
        name="contentstatus", create_type=False,
    )
    challengestatus = postgresql.ENUM(
        "PENDING", "ACCEPTED", "COMPLETED", "EXPIRED", "DECLINED",
        name="challengestatus", create_type=False,
    )
    # Create the enum types in the database
    contentstatus.create(op.get_bind(), checkfirst=True)
    challengestatus.create(op.get_bind(), checkfirst=True)

    # ── weekly_leaderboard ──────────────────────────────────
    op.create_table(
        "weekly_leaderboard",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("week_iso", sa.String(10), nullable=False),
        sa.Column("xp_earned", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pseudonym", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_weekly_leaderboard_profile_id", "weekly_leaderboard", ["profile_id"])
    op.create_index("ix_weekly_leaderboard_week_iso", "weekly_leaderboard", ["week_iso"])
    op.create_index(
        "uq_weekly_leaderboard_profile_week",
        "weekly_leaderboard",
        ["profile_id", "week_iso"],
        unique=True,
    )

    # ── challenges ──────────────────────────────────────────
    op.create_table(
        "challenges",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("challenger_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("challenged_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("skill_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", postgresql.ENUM("PENDING", "ACCEPTED", "COMPLETED", "EXPIRED", "DECLINED", name="challengestatus", create_type=False), nullable=False),
        sa.Column("challenger_score", sa.Float(), nullable=True),
        sa.Column("challenged_score", sa.Float(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["challenger_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["challenged_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_challenges_challenger_id", "challenges", ["challenger_id"])
    op.create_index("ix_challenges_challenged_id", "challenges", ["challenged_id"])
    op.create_index("ix_challenges_status", "challenges", ["status"])

    # ── content_transitions ─────────────────────────────────
    op.create_table(
        "content_transitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content_type", sa.String(20), nullable=False),
        sa.Column("content_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("from_status", sa.String(20), nullable=False),
        sa.Column("to_status", sa.String(20), nullable=False),
        sa.Column("transitioned_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["transitioned_by"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_content_transitions_content_type", "content_transitions", ["content_type"])
    op.create_index("ix_content_transitions_content_id", "content_transitions", ["content_id"])
    op.create_index("ix_content_transitions_transitioned_by", "content_transitions", ["transitioned_by"])

    # ── Add status + reviewer_notes to questions ────────────
    op.add_column(
        "questions",
        sa.Column(
            "status",
            postgresql.ENUM("DRAFT", "IN_REVIEW", "PUBLISHED", "ARCHIVED", name="contentstatus", create_type=False),
            nullable=False,
            server_default="PUBLISHED",
        ),
    )
    op.add_column(
        "questions",
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_questions_status", "questions", ["status"])

    # ── Add status + reviewer_notes to micro_lessons ────────
    op.add_column(
        "micro_lessons",
        sa.Column(
            "status",
            postgresql.ENUM("DRAFT", "IN_REVIEW", "PUBLISHED", "ARCHIVED", name="contentstatus", create_type=False),
            nullable=False,
            server_default="PUBLISHED",
        ),
    )
    op.add_column(
        "micro_lessons",
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_micro_lessons_status", "micro_lessons", ["status"])

    # ── Add notification_prefs JSONB to users ───────────────
    op.add_column(
        "users",
        sa.Column(
            "notification_prefs",
            postgresql.JSONB(),
            nullable=True,
            server_default='{"sms_digest": true, "push_enabled": true, "inactivity_alerts": true}',
        ),
    )


def downgrade() -> None:
    # ── Drop columns ────────────────────────────────────────
    op.drop_column("users", "notification_prefs")

    op.drop_index("ix_micro_lessons_status", table_name="micro_lessons")
    op.drop_column("micro_lessons", "reviewer_notes")
    op.drop_column("micro_lessons", "status")

    op.drop_index("ix_questions_status", table_name="questions")
    op.drop_column("questions", "reviewer_notes")
    op.drop_column("questions", "status")

    # ── Drop tables ─────────────────────────────────────────
    op.drop_table("content_transitions")
    op.drop_table("challenges")
    op.drop_table("weekly_leaderboard")

    # ── Drop enums ──────────────────────────────────────────
    sa.Enum(name="challengestatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="contentstatus").drop(op.get_bind(), checkfirst=True)
