"""Migrate existing STUDENT users to PARENT role.

Standalone student accounts are no longer supported.
All users register as PARENT and manage child profiles.

Revision ID: l3c4d5e6f7g8
Revises: k2b3c4d5e6f7
Create Date: 2026-03-08 12:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "l3c4d5e6f7g8"
down_revision = "k2b3c4d5e6f7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE users SET role = 'PARENT' WHERE role = 'STUDENT'")


def downgrade() -> None:
    # Cannot reliably revert — we don't know which parents were originally students
    pass
