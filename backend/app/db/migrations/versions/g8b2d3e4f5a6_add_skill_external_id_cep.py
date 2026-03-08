"""add external_id and cep_frequency to skills

Revision ID: g8b2d3e4f5a6
Revises: f7a9b1c2d3e4
Create Date: 2026-02-24 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "g8b2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "f7a9b1c2d3e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("skills", sa.Column("external_id", sa.String(length=100), nullable=True))
    op.add_column("skills", sa.Column("cep_frequency", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_skills_external_id"), "skills", ["external_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_skills_external_id"), table_name="skills")
    op.drop_column("skills", "cep_frequency")
    op.drop_column("skills", "external_id")
