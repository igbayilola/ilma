"""add grade levels

Revision ID: f7a9b1c2d3e4
Revises: a1b2c3d4e5f6
Create Date: 2026-02-22 18:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f7a9b1c2d3e4"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create grade_levels table
    op.create_table(
        "grade_levels",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_grade_levels_slug"), "grade_levels", ["slug"], unique=True)

    # 2. Add grade_level_id FK on subjects
    op.add_column("subjects", sa.Column("grade_level_id", sa.UUID(), nullable=True))
    op.create_index(op.f("ix_subjects_grade_level_id"), "subjects", ["grade_level_id"], unique=False)
    op.create_foreign_key(
        "fk_subjects_grade_level_id",
        "subjects",
        "grade_levels",
        ["grade_level_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # 3. Drop old unique index on subjects.slug, create composite unique
    op.drop_index("ix_subjects_slug", table_name="subjects")
    op.create_unique_constraint("uq_subject_slug_grade", "subjects", ["slug", "grade_level_id"])

    # 4. Add grade_level_id FK on users
    op.add_column("users", sa.Column("grade_level_id", sa.UUID(), nullable=True))
    op.create_index(op.f("ix_users_grade_level_id"), "users", ["grade_level_id"], unique=False)
    op.create_foreign_key(
        "fk_users_grade_level_id",
        "users",
        "grade_levels",
        ["grade_level_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    # Users
    op.drop_constraint("fk_users_grade_level_id", "users", type_="foreignkey")
    op.drop_index(op.f("ix_users_grade_level_id"), table_name="users")
    op.drop_column("users", "grade_level_id")

    # Subjects: restore original unique index on slug
    op.drop_constraint("uq_subject_slug_grade", "subjects", type_="unique")
    op.create_index("ix_subjects_slug", "subjects", ["slug"], unique=True)

    op.drop_constraint("fk_subjects_grade_level_id", "subjects", type_="foreignkey")
    op.drop_index(op.f("ix_subjects_grade_level_id"), table_name="subjects")
    op.drop_column("subjects", "grade_level_id")

    # Grade levels table
    op.drop_index(op.f("ix_grade_levels_slug"), table_name="grade_levels")
    op.drop_table("grade_levels")
