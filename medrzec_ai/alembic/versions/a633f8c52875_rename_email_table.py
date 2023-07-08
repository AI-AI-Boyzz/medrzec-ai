"""rename email table

Revision ID: a633f8c52875
Revises: 833d8b36fd0c
Create Date: 2023-07-06 23:33:21.296166

"""
from alembic import op

revision = "a633f8c52875"
down_revision = "833d8b36fd0c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("email", "user")


def downgrade() -> None:
    op.rename_table("user", "email")
