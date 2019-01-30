# -*- coding: utf-8 -*-
from guillotina import configure
from guillotina.catalog.catalog import DefaultSearchUtility
from guillotina.interfaces import ICatalogUtility
from guillotina.interfaces import IInteraction
from guillotina.transactions import get_transaction
from guillotina.utils import get_content_path
from guillotina.utils import get_current_request
from guillotina_pgcatalog import schema

import json
import logging


logger = logging.getLogger('guillotina')


@configure.utility(provides=ICatalogUtility)
class PGSearchUtility(DefaultSearchUtility):
    """
    Indexes are transparently maintained in the database so all indexing
    operations can be ignored
    """

    async def get_data(self, content):
        # we can override and ignore this request since data is already
        # stored in db...
        return {}

    async def search(self, site, query):
        """
        XXX transform into el query
        """
        pass

    def get_access_where_clauses(self):
        users = []
        roles = []
        request = get_current_request()
        interaction = IInteraction(request)

        for user in interaction.participations:
            users.append(user.principal.id)
            users.extend(user.principal.groups)
            roles_dict = interaction.global_principal_roles(
                user.principal.id,
                user.principal.groups)
            roles.extend([key for key, value in roles_dict.items()
                          if value])

        clauses = []
        if len(users) > 0:
            clauses.append("json->'access_users' ?| array['{}']".format(
                "','".join(users)
            ))
        if len(roles) > 0:
            clauses.append("json->'access_roles' ?| array['{}']".format(
                "','".join(roles)
            ))
        return '({})'.format(
            ' OR '.join(clauses)
        )

    async def query(self, site, query, request=None):
        """
        transform into query...
        right now, it's just passing through into elasticsearch
        """

        # this data needs to be careful verified because we can't use prepared
        # placeholders for it.
        try:
            limit = int(query.pop('limit', 20))
        except Exception:
            limit = 20
        limit = min(limit, 100)
        page = query.pop('page', 1)
        # need some ordering to ensure paging works
        order_by = query.pop('order_by', 'zoid')
        sort_reversed = query.pop('reversed', False)
        if order_by not in [k for k in schema.get_indexes().keys()] + ['zoid']:
            order_by = 'zoid'
        try:
            skip = (int(page) - 1) * limit
        except Exception:
            skip = 0

        order_by_index = (
            schema.get_index(order_by) or schema.BasicJsonIndex(order_by))
        order_by_arg_index = 1

        sql_arguments = []
        sql_wheres = []
        select_fields = ['id', 'zoid', 'json']
        for field_name, value in query.items():
            index = schema.get_index(field_name)
            kwargs = {}
            if isinstance(value, dict):
                kwargs['operator'] = value.get('operator', None)
                value = value.get('value', None)
            sql_arguments.append(value)
            sql_wheres.append(index.where(
                value, arg_idx=len(sql_arguments), **kwargs))
            select_fields.extend(index.select(arg_idx=len(sql_arguments)))

            if field_name == index.name:
                order_by_arg_index = len(sql_arguments)

        # ensure we only query this site
        site_path = get_content_path(site)
        sql_wheres.append("""substring(json->>'path', 0, {}) = '{}'""".format(
            len(site_path) + 1,
            site_path
        ))

        access_wheres = self.get_access_where_clauses()

        sql = '''select {}
                 from objects
                 where {}
                    AND {}
                 {}
                 limit {} offset {}'''.format(
                    ','.join(select_fields),
                    ' AND '.join(sql_wheres),
                    access_wheres,
                    order_by_index.order_by(order_by_arg_index, sort_reversed),
                    limit,
                    skip)

        logger.debug('Running search:\n{}'.format(sql))
        txn = get_transaction()
        conn = await txn.get_connection()

        results = []
        for record in await conn.fetch(sql, *sql_arguments):
            data = json.loads(record['json'])
            data['id'] = record['id']
            results.append(data)
        return {
            'member': results,
            'page': page,
            'limit': limit
        }

    async def index(self, site, datas):
        pass

    async def remove(self, site, uids):
        pass

    async def initialize_catalog(self, site):
        txn = get_transaction()
        conn = await txn.get_connection()
        if conn is not None:
            for name, index in schema.get_indexes().items():
                await conn.execute('''DROP INDEX IF EXISTS {}'''.format(
                    index.idx_name))
                await conn.execute(index.index_sql)
