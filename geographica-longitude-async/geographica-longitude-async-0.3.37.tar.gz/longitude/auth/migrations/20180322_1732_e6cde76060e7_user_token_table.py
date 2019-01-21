"""user token table

Revision ID: e6cde76060e7
Revises: cea8fff92651
Create Date: 2018-03-22 17:32:17.067021+01:00

"""
from alembic import op
import sqlalchemy as sa


revision = 'e6cde76060e7'
down_revision = 'cea8fff92651'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('auth_user_tokens',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('auth_user_id', sa.Integer(), sa.ForeignKey('auth_user.id'), nullable=False, unique=True),
        sa.Column('token', sa.Text(), nullable=False)
    )


def downgrade():
    op.drop_table('auth_user_tokens')
