"""Add answer table

Revision ID: d6a225b36d22
Revises: 73b29c114eb1
Create Date: 2023-07-08 21:50:51.357000

"""
import sqlalchemy as sa
from alembic import op

revision = "d6a225b36d22"
down_revision = "73b29c114eb1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "answer",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("answer")
