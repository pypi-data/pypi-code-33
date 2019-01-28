# -*- coding: utf-8; -*-
"""add client.archived

Revision ID: e9eb7fc0a451
Revises: 75c09e11543c
Create Date: 2018-09-28 12:12:19.813042

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'e9eb7fc0a451'
down_revision = u'75c09e11543c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # client
    op.add_column('client', sa.Column('archived', sa.Boolean(), nullable=True))
    client = sa.sql.table('client', sa.sql.column('archived'))
    op.execute(client.update().values({'archived': False}))
    op.alter_column('client', 'archived', nullable=False)


def downgrade():

    # client
    op.drop_column('client', 'archived')
