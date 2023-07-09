"""create purchase table

Revision ID: 3b13b47de6c3
Revises: 8a40210ceabf
Create Date: 2023-07-09 16:50:29.749363

"""
import sqlalchemy as sa
from alembic import op

revision = '3b13b47de6c3'
down_revision = '8a40210ceabf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('purchase',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('purchase')
