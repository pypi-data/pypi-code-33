"""rename auth columns

Revision ID: a84311174ef7
Revises: e6cde76060e7
Create Date: 2018-03-23 14:20:53.540905+01:00

"""
from alembic import op


revision = 'a84311174ef7'
down_revision = 'e6cde76060e7'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('auth_user', 'longitude_auth_user')
    op.rename_table('auth_user_tokens', 'longitude_auth_user_refresh_token')


def downgrade():
    op.rename_table('longitude_auth_user', 'auth_user')
    op.rename_table('longitude_auth_user_refresh_token', 'auth_user_tokens')
