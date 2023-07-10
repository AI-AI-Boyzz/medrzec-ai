"""add magnitude to answer model

Revision ID: 813581af98ec
Revises: eaa1c071a28a
Create Date: 2023-07-09 13:34:14.510013

"""
import sqlalchemy as sa
from alembic import op

revision = "813581af98ec"
down_revision = "eaa1c071a28a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("answer", sa.Column("magnitude", sa.Float(), nullable=False))


def downgrade() -> None:
    op.drop_column("answer", "magnitude")
