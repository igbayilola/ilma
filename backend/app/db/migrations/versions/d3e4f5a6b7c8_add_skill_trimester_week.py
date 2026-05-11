"""Add trimester and week_order to skills for curriculum sequencing.

Granularité au niveau Skill (et non Domain) pour permettre "Cette semaine :
la division euclidienne" plutôt que "Cette semaine : Opérations" trop vague.
Nullable + sans default : pas de backfill obligatoire, la donnée sera remplie
au fur et à mesure côté contenu pour aligner sur le programme officiel MEMP
Bénin (T1 sept-déc, T2 jan-avr, T3 avr-juin).

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5g6h7
Create Date: 2026-05-11 14:00:00.000000
"""
import sqlalchemy as sa
from alembic import op

revision = "d3e4f5a6b7c8"
down_revision = "c2d3e4f5g6h7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "skills",
        sa.Column("trimester", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "skills",
        sa.Column("week_order", sa.SmallInteger(), nullable=True),
    )
    op.create_index(
        "ix_skills_trimester_week",
        "skills",
        ["trimester", "week_order"],
    )


def downgrade() -> None:
    op.drop_index("ix_skills_trimester_week", table_name="skills")
    op.drop_column("skills", "week_order")
    op.drop_column("skills", "trimester")
