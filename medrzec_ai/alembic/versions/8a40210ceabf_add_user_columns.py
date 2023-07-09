"""add user columns

Revision ID: 8a40210ceabf
Revises: 73b29c114eb1
Create Date: 2023-07-08 19:36:38.498211

"""
import sqlalchemy as sa
from alembic import op

revision = "8a40210ceabf"
down_revision = "73b29c114eb1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user", sa.Column("country", sa.String(), nullable=False))
    op.add_column("user", sa.Column("industry", sa.String(), nullable=False))
    op.add_column("user", sa.Column("profession", sa.String(), nullable=False))


def downgrade() -> None:
    op.drop_column("user", "country")
    op.drop_column("user", "industry")
    op.drop_column("user", "profession")
