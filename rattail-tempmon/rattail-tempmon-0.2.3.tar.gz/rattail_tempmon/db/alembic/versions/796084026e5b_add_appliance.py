# -*- coding: utf-8; -*-
"""add appliance

Revision ID: 796084026e5b
Revises: b02c531caca5
Create Date: 2018-10-19 17:28:34.146307

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '796084026e5b'
down_revision = u'b02c531caca5'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # appliance
    op.create_table('appliance',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=False),
                    sa.Column('location', sa.String(length=255), nullable=True),
                    sa.PrimaryKeyConstraint('uuid'),
                    sa.UniqueConstraint('name', name=u'appliance_uq_name')
    )

    # probe
    op.add_column(u'probe', sa.Column('appliance_uuid', sa.String(length=32), nullable=True))
    op.add_column(u'probe', sa.Column('location', sa.String(length=255), nullable=True))
    op.create_foreign_key(u'probe_fk_appliance', 'probe', 'appliance', ['appliance_uuid'], ['uuid'])


def downgrade():

    # probe
    op.drop_constraint(u'probe_fk_appliance', 'probe', type_='foreignkey')
    op.drop_column(u'probe', 'location')
    op.drop_column(u'probe', 'appliance_uuid')

    # appliance
    op.drop_table('appliance')
