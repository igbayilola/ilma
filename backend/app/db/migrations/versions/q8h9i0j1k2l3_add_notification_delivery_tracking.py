"""Add notification delivery tracking columns.

Revision ID: q8h9i0j1k2l3
Revises: p7g8h9i0j1k2
Create Date: 2026-03-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = "q8h9i0j1k2l3"
down_revision = "p7g8h9i0j1k2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("notifications", sa.Column("status", sa.String(20), nullable=False, server_default="pending"))
    op.add_column("notifications", sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("notifications", sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("notifications", sa.Column("error_message", sa.Text(), nullable=True))
    op.create_index("ix_notifications_status", "notifications", ["status"])


def downgrade() -> None:
    op.drop_index("ix_notifications_status", table_name="notifications")
    op.drop_column("notifications", "error_message")
    op.drop_column("notifications", "delivered_at")
    op.drop_column("notifications", "sent_at")
    op.drop_column("notifications", "status")
