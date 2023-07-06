"""create email table

Revision ID: 833d8b36fd0c
Create Date: 2023-07-06 23:18:59.020912

"""
import sqlalchemy as sa
from alembic import op

revision = "833d8b36fd0c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "email",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(), unique=True, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("email")
