"""Add question_comments table for inline editorial comments.

Revision ID: p7g8h9i0j1k2
Revises: o6f7g8h9i0j1
Create Date: 2026-03-18 10:00:00.000000

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "p7g8h9i0j1k2"
down_revision = "o6f7g8h9i0j1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "question_comments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_question_comments_question_id", "question_comments", ["question_id"])
    op.create_index("ix_question_comments_author_id", "question_comments", ["author_id"])


def downgrade() -> None:
    op.drop_index("ix_question_comments_author_id", table_name="question_comments")
    op.drop_index("ix_question_comments_question_id", table_name="question_comments")
    op.drop_table("question_comments")
