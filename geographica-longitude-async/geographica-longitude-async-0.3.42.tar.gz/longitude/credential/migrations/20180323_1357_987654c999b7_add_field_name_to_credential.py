"""add field name to credential

Revision ID: 987654c999b7
Revises: e6cde76060e7
Create Date: 2018-03-23 13:57:18.812048+01:00

"""
from alembic import op
import sqlalchemy as sa


revision = '987654c999b7'
down_revision = 'c6a61e3cc7ec'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'longitude_credentials',
        sa.Column(
            'name',
            sa.String(32),
            nullable=False,
            unique=True
        )
    )

    op.add_column(
        'longitude_credentials',
        sa.Column(
            'description',
            sa.Text(),
            nullable=False,
            server_default=''
        )
    )


def downgrade():
    op.drop_column('longitude_credentials', 'name')
    op.drop_column('longitude_credentials', 'description')
