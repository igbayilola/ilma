"""Recover iter5 WIP — micro_lessons.sections/formula/external_id + SessionMode.CALCUL_MENTAL.

Cette migration récupère deux pans d'iter 5 WIP qui n'avaient jamais atteint
la DB à cause d'un id de révision dupliqué et d'un down_revision invalide
sur l'enum case :

- `micro_lessons.sections` (JSONB), `formula` (Text), `external_id` (String 100
  unique) — référencés par le modèle SQLAlchemy `MicroLesson` depuis iter 5+.
  Sans ces colonnes, toute requête chargeant un lesson avec sections échoue.
  `content_html` passe nullable (fallback pour les nouvelles leçons
  structurées sans HTML legacy).
- `sessionmode.CALCUL_MENTAL` — valeur enum requise par
  `SessionMode.CALCUL_MENTAL` côté Python. Stockage uppercase (`.name`) pour
  cohérence avec les autres valeurs PRACTICE / DAILY_CHALLENGE / REVISION /
  EXAM. L'ancienne migration dangling l'ajoutait en lowercase, ce qui aurait
  cassé l'ORM au runtime.

Les 3 fichiers dangling supprimés en parallèle :
- a1b2c3d4e5f6_extend_question_types_and_columns.py — obsolète, colonnes
  déjà en DB par autre chemin, 7 enum lowercase contradictoires
- a1b2c3d4e5f6_add_lesson_sections_formula.py — remplacé ici
- b2c3d4e5f6g7_add_calcul_mental_mode.py — remplacé ici avec case correcte

Revision ID: e4f5a6b7c8d9
Revises: d3e4f5a6b7c8
Create Date: 2026-05-11 15:50:00.000000
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "e4f5a6b7c8d9"
down_revision = "d3e4f5a6b7c8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── micro_lessons : structured sections + formula + external_id ─────────
    op.add_column("micro_lessons", sa.Column("sections", JSONB, nullable=True))
    op.add_column("micro_lessons", sa.Column("formula", sa.Text(), nullable=True))
    op.add_column("micro_lessons", sa.Column("external_id", sa.String(100), nullable=True))
    op.alter_column("micro_lessons", "content_html", existing_type=sa.Text(), nullable=True)
    op.create_index(
        "ix_micro_lessons_external_id",
        "micro_lessons",
        ["external_id"],
        unique=True,
    )

    # ── sessionmode : CALCUL_MENTAL (uppercase, matches Python enum .name) ──
    # ALTER TYPE ... ADD VALUE cannot run inside a transaction in PostgreSQL.
    op.execute("COMMIT")
    op.execute("ALTER TYPE sessionmode ADD VALUE IF NOT EXISTS 'CALCUL_MENTAL'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values — CALCUL_MENTAL stays.
    op.drop_index("ix_micro_lessons_external_id", table_name="micro_lessons")
    op.drop_column("micro_lessons", "external_id")
    op.drop_column("micro_lessons", "formula")
    op.drop_column("micro_lessons", "sections")
    # content_html : on ne re-NOT-NULL pas en downgrade — du contenu nullable
    # peut déjà exister depuis l'upgrade.
