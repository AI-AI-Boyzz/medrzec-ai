"""Add answer table

Revision ID: c8f917d8ea45
Revises: d6a225b36d22
Create Date: 2023-07-08 22:34:54.587770

"""
import sqlalchemy as sa
from alembic import op

revision = "c8f917d8ea45"
down_revision = "d6a225b36d22"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("answer", sa.Column("question", sa.String(), nullable=False))
    op.add_column("answer", sa.Column("response", sa.String(), nullable=False))
    op.drop_column("answer", "text")


def downgrade() -> None:
    op.add_column("answer", sa.Column("text", sa.VARCHAR(), nullable=False))
    op.drop_column("answer", "response")
    op.drop_column("answer", "question")
