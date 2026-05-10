"""Add pg_trgm GIN indexes for full-text search.

Revision ID: y6p7q8r9s0t1
Revises: x5o6p7q8r9s0
Create Date: 2026-04-03 00:00:01.000000
"""
from alembic import op

revision = "y6p7q8r9s0t1"
down_revision = "x5o6p7q8r9s0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pg_trgm extension (idempotent)
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # GIN trigram indexes for fuzzy search
    op.execute("CREATE INDEX IF NOT EXISTS ix_skills_name_trgm ON skills USING gin (name gin_trgm_ops)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_questions_text_trgm ON questions USING gin (text gin_trgm_ops)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_domains_name_trgm ON domains USING gin (name gin_trgm_ops)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_micro_lessons_title_trgm ON micro_lessons USING gin (title gin_trgm_ops)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_micro_lessons_title_trgm")
    op.execute("DROP INDEX IF EXISTS ix_domains_name_trgm")
    op.execute("DROP INDEX IF EXISTS ix_questions_text_trgm")
    op.execute("DROP INDEX IF EXISTS ix_skills_name_trgm")
