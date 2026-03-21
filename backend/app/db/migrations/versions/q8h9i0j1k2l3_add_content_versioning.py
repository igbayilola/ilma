"""Add content versioning: version column on questions/lessons + content_versions table.

Revision ID: q8h9i0j1k2l3
Revises: p7g8h9i0j1k2
Create Date: 2026-03-18 12:00:00.000000

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "q8h9i0j1k2l3"
down_revision = "p7g8h9i0j1k2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add version column to questions
    op.add_column("questions", sa.Column("version", sa.Integer(), nullable=False, server_default="1"))
    # Add version column to micro_lessons
    op.add_column("micro_lessons", sa.Column("version", sa.Integer(), nullable=False, server_default="1"))

    # Create content_versions table
    op.create_table(
        "content_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content_type", sa.String(20), nullable=False),
        sa.Column("content_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("data_json", postgresql.JSONB(), nullable=False),
        sa.Column("modified_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("modified_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["modified_by"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_content_versions_content_id", "content_versions", ["content_id"])
    op.create_index("ix_content_versions_content_type_content_id", "content_versions", ["content_type", "content_id"])


def downgrade() -> None:
    op.drop_index("ix_content_versions_content_type_content_id", table_name="content_versions")
    op.drop_index("ix_content_versions_content_id", table_name="content_versions")
    op.drop_table("content_versions")
    op.drop_column("micro_lessons", "version")
    op.drop_column("questions", "version")
