# -*- coding: utf-8; -*-
"""add client.disk_type

Revision ID: 5f2b87474433
Revises: 34041e1032a2
Create Date: 2018-09-28 19:08:02.743343

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '5f2b87474433'
down_revision = u'34041e1032a2'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # client
    op.add_column('client', sa.Column('disk_type', sa.Integer(), nullable=True))


def downgrade():

    # client
    op.drop_column('client', 'disk_type')
