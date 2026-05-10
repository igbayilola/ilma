"""Add analytics_events table.

Revision ID: x5o6p7q8r9s0
Revises: w4n5o6p7q8r9
Create Date: 2026-04-03 00:00:00.000000
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "x5o6p7q8r9s0"
down_revision = "w4n5o6p7q8r9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "analytics_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("profile_id", UUID(as_uuid=True), sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True),
        sa.Column("session_id", UUID(as_uuid=True), nullable=True),
        sa.Column("data", JSONB, nullable=True),
        sa.Column("client_ts", sa.DateTime(timezone=True), nullable=True),
        sa.Column("server_ts", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_analytics_event_type", "analytics_events", ["event_type"])
    op.create_index("ix_analytics_profile_created", "analytics_events", ["profile_id", "created_at"])
    op.create_index("ix_analytics_session_id", "analytics_events", ["session_id"])


def downgrade() -> None:
    op.drop_table("analytics_events")
