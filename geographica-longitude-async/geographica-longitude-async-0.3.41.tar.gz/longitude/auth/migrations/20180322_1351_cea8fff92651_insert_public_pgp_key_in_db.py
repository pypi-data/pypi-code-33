"""insert public pgp key in db

Revision ID: cea8fff92651
Revises: e93ef06edae1
Create Date: 2018-03-22 13:51:41.493558+01:00

"""
from alembic import op
from longitude import config


revision = 'cea8fff92651'
down_revision = 'e93ef06edae1'
branch_labels = None
depends_on = None


def get_pgp_public_key__create_function():
    if config.PGP_PRIVATE_KEY:
        return '''
            CREATE OR REPLACE FUNCTION get_pgp_pubkey()
            RETURNS text AS 
            $$ BEGIN
                RETURN '{}';
            END $$ 
            LANGUAGE plpgsql SECURITY DEFINER;
        '''.format(str(config.PGP_PRIVATE_KEY[0].pubkey))

    return None


def get_pgp_public_key__drop_function():
    if config.PGP_PRIVATE_KEY:
        return 'DROP FUNCTION IF EXISTS get_pgp_pubkey()'

    return None


def upgrade():
    sql = get_pgp_public_key__create_function()

    if sql:
        conn = op.get_bind()
        conn.execute(sql)


def downgrade():
    sql = get_pgp_public_key__drop_function()

    if sql:
        conn = op.get_bind()
        conn.execute(sql)
