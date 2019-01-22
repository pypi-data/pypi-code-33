"""generate user model

Revision ID: e93ef06edae1
Revises: 00bfffcc2ee6
Create Date: 2018-03-22 13:13:08.018173+01:00

"""
from alembic import op
import sqlalchemy as sa


revision = 'e93ef06edae1'
down_revision = None
branch_labels = ('longitude.auth',)
depends_on = None


def upgrade():
    conn = op.get_bind()

    op.create_table('auth_user',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True, primary_key=True),

        sa.Column('name', sa.String(128), nullable=True, server_default=None),

        sa.Column('username', sa.String(128), nullable=False, unique=True),
        sa.Column('email', sa.String(128), nullable=True, unique=True, server_default=None),
        sa.Column('password', sa.Binary(), nullable=False),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_onupdate=sa.func.current_timestamp()),
    )

    conn.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")


def downgrade():
    op.drop_table('auth_user')
