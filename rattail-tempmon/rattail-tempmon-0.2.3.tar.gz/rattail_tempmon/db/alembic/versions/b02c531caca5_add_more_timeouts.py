# -*- coding: utf-8; -*-
"""add more timeouts

Revision ID: b02c531caca5
Revises: 5f2b87474433
Create Date: 2018-10-19 13:51:54.422490

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'b02c531caca5'
down_revision = u'5f2b87474433'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # probe
    op.add_column('probe', sa.Column('critical_max_started', sa.DateTime(), nullable=True))
    op.add_column('probe', sa.Column('critical_max_timeout', sa.Integer(), nullable=True))
    op.add_column('probe', sa.Column('critical_min_started', sa.DateTime(), nullable=True))
    op.add_column('probe', sa.Column('critical_min_timeout', sa.Integer(), nullable=True))
    op.add_column('probe', sa.Column('error_started', sa.DateTime(), nullable=True))
    op.add_column('probe', sa.Column('error_timeout', sa.Integer(), nullable=True))
    op.add_column('probe', sa.Column('good_max_started', sa.DateTime(), nullable=True))
    op.add_column('probe', sa.Column('good_max_timeout', sa.Integer(), nullable=True))
    op.add_column('probe', sa.Column('good_min_started', sa.DateTime(), nullable=True))
    op.add_column('probe', sa.Column('good_min_timeout', sa.Integer(), nullable=True))


def downgrade():

    # probe
    op.drop_column('probe', 'good_min_timeout')
    op.drop_column('probe', 'good_min_started')
    op.drop_column('probe', 'good_max_timeout')
    op.drop_column('probe', 'good_max_started')
    op.drop_column('probe', 'error_timeout')
    op.drop_column('probe', 'error_started')
    op.drop_column('probe', 'critical_min_timeout')
    op.drop_column('probe', 'critical_min_started')
    op.drop_column('probe', 'critical_max_timeout')
    op.drop_column('probe', 'critical_max_started')
