"""rename is_superadmin to is_admin

Revision ID: 644f2887df07
Revises: 4e115bcdb4d2
Create Date: 2018-08-01 16:40:34.114828+02:00

"""
from alembic import op


revision = '644f2887df07'
down_revision = '4e115bcdb4d2'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('longitude_permission_role', 'is_superadmin', new_column_name='is_admin')


def downgrade():
    op.alter_column('longitude_permission_role', 'is_admin', new_column_name='is_superadmin')
