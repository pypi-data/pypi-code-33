# -*- coding: utf-8; -*-
"""make enabled datetime

Revision ID: fd1df160539a
Revises: a2676d3dfc1e
Create Date: 2019-01-25 18:41:01.652823

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'fd1df160539a'
down_revision = 'a2676d3dfc1e'
branch_labels = None
depends_on = None

import datetime
from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    now = datetime.datetime.utcnow()

    # client
    op.add_column('client', sa.Column('new_enabled', sa.DateTime(), nullable=True))
    client = sa.sql.table('client',
                          sa.sql.column('enabled'),
                          sa.sql.column('new_enabled'))
    op.execute(client.update()\
               .where(client.c.enabled == True)\
               .values({'new_enabled': now}))
    op.drop_column('client', 'enabled')
    op.alter_column('client', 'new_enabled', new_column_name='enabled')

    # probe
    op.add_column('probe', sa.Column('new_enabled', sa.DateTime(), nullable=True))
    probe = sa.sql.table('probe',
                         sa.sql.column('enabled'),
                         sa.sql.column('new_enabled'))
    op.execute(probe.update()\
               .where(probe.c.enabled == True)\
               .values({'new_enabled': now}))
    op.drop_column('probe', 'enabled')
    op.alter_column('probe', 'new_enabled', new_column_name='enabled')


def downgrade():

    # probe
    op.add_column('probe', sa.Column('old_enabled', sa.Boolean(), nullable=True))
    probe = sa.sql.table('probe',
                         sa.sql.column('enabled'),
                         sa.sql.column('old_enabled'))
    op.execute(probe.update()\
               .where(probe.c.enabled != None)\
               .values({'old_enabled': True}))
    op.execute(probe.update()\
               .where(probe.c.enabled == None)\
               .values({'old_enabled': False}))
    op.drop_column('probe', 'enabled')
    op.alter_column('probe', 'old_enabled', new_column_name='enabled', nullable=False)

    # client
    op.add_column('client', sa.Column('old_enabled', sa.Boolean(), nullable=True))
    client = sa.sql.table('client',
                          sa.sql.column('enabled'),
                          sa.sql.column('old_enabled'))
    op.execute(client.update()\
               .where(client.c.enabled != None)\
               .values({'old_enabled': True}))
    op.execute(client.update()\
               .where(client.c.enabled == None)\
               .values({'old_enabled': False}))
    op.drop_column('client', 'enabled')
    op.alter_column('client', 'old_enabled', new_column_name='enabled', nullable=False)
