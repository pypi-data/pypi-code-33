"""Role support

Revision ID: 3f4ec3873142
Revises: b3ce11d1b919
Create Date: 2018-06-19 14:21:51.842624+02:00

"""
from alembic import op
import sqlalchemy as sa


revision = '3f4ec3873142'
down_revision = 'a84311174ef7'
branch_labels = ('longitude.permissions',)
depends_on = None


def upgrade():

    op.create_table('longitude_permission_role',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True, primary_key=True),
        sa.Column('name', sa.String(32), nullable=True, server_default=None),
        sa.Column('is_superadmin', sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.add_column('longitude_auth_user',
      sa.Column('role_id', sa.Integer(), sa.ForeignKey('longitude_permission_role.id'), nullable=True, server_default=None)
    )


def downgrade():
    op.drop_column('longitude_auth_user', 'role_id')
    op.drop_table('longitude_permission_role')
