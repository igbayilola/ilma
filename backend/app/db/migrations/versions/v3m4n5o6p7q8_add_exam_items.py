"""Add exam_items and exam_sub_questions tables for CEP format.

Revision ID: v3m4n5o6p7q8
Revises: u2l3m4n5o6p7
Create Date: 2026-03-25 21:00:00.000000

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "v3m4n5o6p7q8"
down_revision = "u2l3m4n5o6p7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to mock_exams
    op.add_column("mock_exams", sa.Column("context_text", sa.Text(), nullable=True))
    op.add_column("mock_exams", sa.Column("exam_type", sa.String(20), nullable=False, server_default="qcm"))

    # Create exam_items table
    op.create_table(
        "exam_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mock_exam_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("item_number", sa.Integer(), nullable=False),
        sa.Column("domain", sa.String(50), nullable=False),
        sa.Column("context_text", sa.Text(), nullable=True),
        sa.Column("points", sa.Float(), nullable=True, server_default="6.67"),
        sa.Column("order", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["mock_exam_id"], ["mock_exams.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_exam_items_mock_exam_id", "exam_items", ["mock_exam_id"])

    # Create exam_sub_questions table
    op.create_table(
        "exam_sub_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exam_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sub_label", sa.String(5), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(30), nullable=False),
        sa.Column("correct_answer", sa.Text(), nullable=False),
        sa.Column("choices", postgresql.JSONB(), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("hint", sa.Text(), nullable=True),
        sa.Column("points", sa.Float(), nullable=True, server_default="2.22"),
        sa.Column("depends_on_previous", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("order", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("skill_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["exam_item_id"], ["exam_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_exam_sub_questions_exam_item_id", "exam_sub_questions", ["exam_item_id"])


def downgrade() -> None:
    op.drop_index("ix_exam_sub_questions_exam_item_id", table_name="exam_sub_questions")
    op.drop_table("exam_sub_questions")
    op.drop_index("ix_exam_items_mock_exam_id", table_name="exam_items")
    op.drop_table("exam_items")
    op.drop_column("mock_exams", "exam_type")
    op.drop_column("mock_exams", "context_text")
