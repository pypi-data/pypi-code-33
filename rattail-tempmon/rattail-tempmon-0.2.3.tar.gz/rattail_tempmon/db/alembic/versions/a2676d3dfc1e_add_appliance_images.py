# -*- coding: utf-8; -*-
"""add appliance images

Revision ID: a2676d3dfc1e
Revises: 796084026e5b
Create Date: 2018-10-19 18:27:01.700943

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'a2676d3dfc1e'
down_revision = u'796084026e5b'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # appliance
    op.add_column('appliance', sa.Column('appliance_type', sa.Integer(), nullable=True))
    op.add_column('appliance', sa.Column('image_normal', sa.LargeBinary(), nullable=True))
    op.add_column('appliance', sa.Column('image_raw', sa.LargeBinary(), nullable=True))
    op.add_column('appliance', sa.Column('image_thumbnail', sa.LargeBinary(), nullable=True))


def downgrade():

    # appliance
    op.drop_column('appliance', 'image_thumbnail')
    op.drop_column('appliance', 'image_raw')
    op.drop_column('appliance', 'image_normal')
    op.drop_column('appliance', 'appliance_type')
