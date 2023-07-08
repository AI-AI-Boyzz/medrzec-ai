"""create remote_work_score table

Revision ID: 5026e71b8f4d
Revises: a633f8c52875
Create Date: 2023-07-06 23:36:02.050738

"""
import sqlalchemy as sa
from alembic import op

revision = "5026e71b8f4d"
down_revision = "a633f8c52875"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "remote_work_score",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("type", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("remote_work_score")
