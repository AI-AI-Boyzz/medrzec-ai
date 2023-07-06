"""add created_at columns

Revision ID: 73b29c114eb1
Revises: 5026e71b8f4d
Create Date: 2023-07-06 23:47:26.464156

"""
import sqlalchemy as sa
from alembic import op

revision = "73b29c114eb1"
down_revision = "5026e71b8f4d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user", sa.Column("created_at", sa.DateTime(), nullable=False))
    op.add_column(
        "remote_work_score", sa.Column("created_at", sa.DateTime(), nullable=False)
    )


def downgrade() -> None:
    op.drop_column("user", "created_at")
    op.drop_column("remote_work_score", "created_at")
