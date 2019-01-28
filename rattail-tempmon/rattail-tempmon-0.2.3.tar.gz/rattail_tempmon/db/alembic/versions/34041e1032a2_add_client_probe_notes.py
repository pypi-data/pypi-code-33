# -*- coding: utf-8; -*-
"""add client, probe notes

Revision ID: 34041e1032a2
Revises: e9eb7fc0a451
Create Date: 2018-09-28 12:24:11.348627

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '34041e1032a2'
down_revision = u'e9eb7fc0a451'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # client
    op.add_column('client', sa.Column('notes', sa.Text(), nullable=True))

    # probe
    op.add_column('probe', sa.Column('notes', sa.Text(), nullable=True))


def downgrade():

    # probe
    op.drop_column('probe', 'notes')

    # client
    op.drop_column('client', 'notes')
