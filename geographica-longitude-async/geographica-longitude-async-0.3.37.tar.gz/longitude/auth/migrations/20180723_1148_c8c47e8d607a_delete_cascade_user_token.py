"""delete cascade user token 

Revision ID: c8c47e8d607a
Revises: a1a01d456ce2
Create Date: 2018-07-23 11:48:18.277671+02:00

"""
from alembic import op
import sqlalchemy as sa


revision = 'c8c47e8d607a'
down_revision = 'a84311174ef7'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('auth_user_tokens_auth_user_id_fkey',
                       'longitude_auth_user_refresh_token', type_='foreignkey')
    op.create_foreign_key(
        'auth_user_tokens_auth_user_id_fkey',
        'longitude_auth_user_refresh_token', 'longitude_auth_user',
        ['auth_user_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    op.drop_constraint('auth_user_tokens_auth_user_id_fkey',
                       'longitude_auth_user_refresh_token', type_='foreignkey')
    op.create_foreign_key(
        'auth_user_tokens_auth_user_id_fkey',
        'longitude_auth_user_refresh_token', 'longitude_auth_user',
        ['auth_user_id'], ['id']
    )
