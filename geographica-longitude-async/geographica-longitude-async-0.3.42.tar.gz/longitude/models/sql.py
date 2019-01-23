import itertools

from copy import deepcopy

from shapely.geometry import shape

import pgpy
import json
import re

from collections import OrderedDict

from geojson import GeoJSON
from marshmallow import ValidationError
from sanic.log import logger
from longitude.utils import is_list_or_tuple, allow_sync, dict_recursive_mapper
from longitude import config
from longitude.exceptions import NotFound


class SQLFetchable:
    def fetch(self, *args, **kwargs):
        raise RuntimeError('not implemented')

    def get_conn(self):
        raise RuntimeError('not implemented')


class SQLCRUDModelMetaclass(type):

    ALIAS_REGEX = re.compile(r'^[a-zA-Z_][a-zA-Z_0-9]*$')

    _TO_COPY_FIELDS = {
        'encoded_columns',
        'select_columns',
        'filters',
        'having_filters',
        'joins',
        'group_by',
        'order_by'
    }

    _ALIASED_COMPULSORY_FIELDS = {
        'select_columns',
        'filters',
        'having_filters',
        'joins',
        'group_by',
        'order_by'
    }

    _NEED_SORTING_FIELDS = {
        'joins',
        'order_by'
    }

    _TO_CHECK_SQL_FIELDS = frozenset(
        _TO_COPY_FIELDS |
        _ALIASED_COMPULSORY_FIELDS |
        _NEED_SORTING_FIELDS
    )

    @classmethod
    def check_and_unify_sql_fields(mcs, name, bases, fields):

        from_alias = fields.get(
            'from_alias',
            next(
                (
                    getattr(base, 'from_alias', None)
                    for base in bases
                    if hasattr(base, 'from_alias')
                ),
                None
            )
        )

        # Perform checks
        for field_name in mcs._TO_CHECK_SQL_FIELDS:

            if field_name not in fields:
               fields[field_name] = next(
                    getattr(base, field_name)
                    for base in bases
                    if hasattr(base, field_name)
                )

            if isinstance(fields[field_name], property):
                continue

            field_value = fields[field_name]

            if field_name in mcs._TO_COPY_FIELDS:
                field_value = deepcopy(field_value)

            if field_name in mcs._ALIASED_COMPULSORY_FIELDS:

                # String literals can be provided without having to provide
                # its alias. The value itself is used as alias.
                if isinstance(field_value, dict):
                    field_value = field_value.items()

                field_value = tuple(
                    (x, '{}.{}'.format(from_alias, x)) if isinstance(x, str) and field_name != 'filters' else
                    (x, '{}.{}=%'.format(from_alias, x)) if isinstance(x, str) and field_name == 'filters'
                    else x
                    for x
                    in field_value
                )

                is_valid_tuple = isinstance(field_value, tuple) and (
                    # The collection must be a list of collections ...
                    next((x for x in field_value if not isinstance(x, (tuple, list))), None) is None and
                    # ... where all elements have len=2 ...
                    next((x for x in field_value if len(x) != 2), None) is None and
                    # ..., aliases must be strings...
                    next((x for x in field_value if not isinstance(x[0], str)), None) is None and
                    # ..., values must be strings...
                    next((x for x in field_value if not isinstance(x[1], str)), None) is None
                )

                if is_valid_tuple:
                    field_value = OrderedDict(field_value)
                else:
                    a = 0

                # If everything is ok, the field value must be a dict by now,
                # either because the user directly provided a dictionary or
                # because it was converted from a correct tuple of pairs
                if not isinstance(field_value, dict):
                    raise ValidationError(
                        '{}.{}.{} must be an iterable of pairs(p.e. [(alias, value), ...]) or a dictionary, '.format(
                            fields['__module__'], name, field_name
                        )
                    )

                wrong_alias = next(
                    (
                        x
                        for x
                        in field_value.keys()
                        if not mcs.ALIAS_REGEX.match(x)
                    ),
                    None
                )

                if wrong_alias is not None:
                    raise ValidationError(
                        '{}.{}.{} defines an alias that does not matches "{}": {}'.format(
                            fields['__module__'],
                            name,
                            field_name,
                            mcs.ALIAS_REGEX.pattern,
                            wrong_alias
                        )
                    )

            if field_name in mcs._NEED_SORTING_FIELDS and \
               not isinstance(field_value, OrderedDict):
                raise ValueError(
                    '{}.{}.{} must be sorted, either as a list of pairs (p.e. [(alias, value), ...]) or an OrderedDict.'.format(
                        fields['__module__'], name, field_name
                    )
                )

            fields[field_name] = field_value

    def __new__(mcs, name, bases, fields):

        mcs.check_and_unify_sql_fields(name, bases, fields)

        return type.__new__(mcs, name, bases, fields)


class SQLCRUDModel(metaclass=SQLCRUDModelMetaclass):

    ALIAS_REGEX = SQLCRUDModelMetaclass.ALIAS_REGEX

    table_name = None
    encoded_columns = tuple()
    select_columns = tuple()
    joins = tuple()
    filters = tuple()
    having_filters = tuple()
    group_by = tuple()
    order_by = tuple()

    from_alias = '_t'

    formats = {
        'geojson': ('format_geojson_featurecollection', 'format_geojson_feature')
    }

    db_model = None
    db_conn = None

    def __init__(self, db_model: SQLFetchable, conn=None):
        self.db_model = db_model
        self.db_conn = conn

    @allow_sync
    async def list(self, format=None, flat=False, **kwargs):

        if flat == True:
            format = None

        res = await self.list_unformatted(format=format, **kwargs)

        res = await self.transform_objects(res, format=format)

        if flat == True:
            flattened_obj = []
            dict_recursive_mapper(res, lambda x: flattened_obj.append(x), copy=False)
            res = flattened_obj

        return res

    async def list_unformatted(self, **kwargs):
        select_sql = self.select_sql(
            joins=kwargs.pop('joins', None),
            joins_append=kwargs.pop('joins_append', None),
            group_by=kwargs.pop('group_by', None),
            order_by=kwargs.pop('order_by', None),
            **kwargs
        )
        sql, params = self.placeholder_to_ordinal(*select_sql)

        if config.DEBUG:
            logger.debug(sql)

        return await self._fetch(sql, *params)

    @allow_sync
    async def count(self, **filters):
        res = (await self.list_unformatted(
            columns=(('count', 'count(DISTINCT {}.id)'.format(self.from_alias)),),
            order_by=[],
            group_by=[],
            **filters
        ))

        return res[0]['count']

    @allow_sync
    async def exists(self, **filters):
        return (await self.count(**filters)) > 0

    @allow_sync
    async def get(self, *args, format=None, **kwargs):

        if len(args) == 1:
            kwargs['oid'] = args[0]
        elif len(args) > 1:
            raise TypeError('get() expected at most 1 arguments, got ' + len(args))

        kwargs['order_by'] = []

        ret = await self.list_unformatted(**kwargs)

        if len(ret) == 0:
            raise NotFound('Object not found')
        elif len(ret) > 1:
            raise AssertionError(
                'SQLCRUDModel.get can only return 0 or 1 '
                'elements.'
            )

        return await self.transform_object(ret[0], format=format)

    @allow_sync
    async def upsert(self, values, **filters):

        pk = values.get('id', values.pop('oid', None))
        if not filters and pk:
            filters['oid'] = pk

        params = {}

        values = self.patch_insert_columns_encoded(values)
        values = self.patch_insert_columns(values)

        insert_columns_snippet = []
        set_snippet = []
        values_snippet = []

        for key, val in values.items():

            if is_list_or_tuple(val, length=2):
                val, right_side_tpl = val
            else:
                right_side_tpl = '${}'

            param_name = self.add_param_name(key, val, params)
            insert_columns_snippet.append(key)
            set_snippet.append(('{}=' + right_side_tpl).format(key, param_name))
            values_snippet.append(right_side_tpl.format(param_name))

        missing_filters = set(filters.keys()).difference(
            set(self.filters.keys()) | {'id', 'oid', 'oid__in'}
        )

        if missing_filters:
            raise ValueError('Trying upsert with undefined filters: {}'.format(missing_filters))

        do_update = filters and (await self.exists(**filters))

        if not do_update:
            sql = '''
                INSERT INTO {schema}{table} (
                  {columns}
                ) VALUES (
                  {values}
                )
                RETURNING id
            '''.format(
                schema=self.schema,
                table=self.table_name,
                columns=','.join(insert_columns_snippet),
                values=','.join(values_snippet),
                conflict=','.join(set_snippet)
            )
        else:
            where_sql, params = self.where_sql(params, **filters)

            sql = '''
                UPDATE {schema}{table} {from_alias} 
                SET
                  {set_expr}
                WHERE {where_sql}
                RETURNING id
            '''.format(
                schema=self.schema,
                table=self.table_name,
                set_expr=','.join(set_snippet),
                where_sql=where_sql,
                from_alias=self.from_alias
            )

        sql, params = self.placeholder_to_ordinal(sql, params)

        res = (await self._fetch(sql, *params))

        return res[0]['id']

    @allow_sync
    async def delete(self, oid=None, **filters):

        if oid is not None:
            filters['oid'] = oid

        sql, params = self.placeholder_to_ordinal(*self.delete_sql(**filters))

        ret = await self._fetch(sql, *params)

        if len(ret) == 0:
            raise NotFound('Object not found')

        return {
            'results': ret
        }

    def select_sql(self, params=None, columns=None, joins=None,
                   joins_append=None, group_by=None, order_by=None,
                   page=None, page_size=None, **filters):

        if columns is None:
            columns = self.select_columns

        if params is None:
            params = {}

        where_clause, params = self.where_sql(params, **filters)
        columns_sql = self.columns_sql(columns)

        if joins is None:
            all_joins = dict(self.joins.items())
            all_joins.update(joins or {})
        else:
            all_joins = dict(joins)

        if joins_append:
            all_joins.update(joins_append)

        if group_by is None:
            group_by = self.group_by

        if group_by is not None and group_by:
            group_by = 'GROUP BY ' + ','.join(
                group_by.values() if isinstance(group_by, dict)
                else group_by
            )
            having_clause, params = self.having_sql(params, **filters)
        else:
            group_by = ''
            having_clause = ''

        if having_clause:
            having_clause = 'HAVING ' + having_clause

        if order_by is None:
            order_by = self.order_by

        if order_by:
            order_by_sql = 'ORDER BY ' + ','.join(
                order_by.values() if isinstance(order_by, dict)
                else order_by
            )
        else:
            order_by_sql = ''

        if page is not None and page <= 0:
            return (
                'SELECT WHERE False',
                params
            )
        elif page:
            page_size = min(
                page_size or config.PAGINATION_PAGE_SIZE,
                config.PAGINATION_MAX_PAGE_SIZE
            )
            page = f'LIMIT {page_size} OFFSET {(page - 1)*page_size}'

            # Try to obtain stable ordering for pagination
            if not order_by_sql:
                if 'id' in columns:
                    order_by_sql = 'ORDER BY id'
                else:
                    order_by_sql = 'ORDER BY ' + ','.join(str(x) for x in columns_sql)

            if 'id' in columns:
                order_by_sql += ',id'
        else:
            page = ''

        return (
            '''
                SELECT 
                    {columns}
                FROM {schema}{table} {from_alias}
                {joins}
                WHERE {where_clause}
                {group_by}
                {having_clause}
                {order_by}
                {page}
            '''.format(
                from_alias=self.from_alias,
                schema=self.schema,
                table=self.table_name,
                where_clause=where_clause,
                having_clause=having_clause,
                columns=','.join(str(x) for x in columns_sql),
                joins='\n'.join(all_joins.values()),
                group_by=group_by,
                order_by=order_by_sql,
                page=page
            ),
            params
        )

    def columns_sql(self, columns):
        return [
            '{} AS {}'.format(column, alias) if alias != column
                else column
            for alias, column
            in self.columns_parse(columns)
        ]

    def columns_parse(self, columns):
        return (
            columns.items() if isinstance(columns, dict)
            else (
                (x, '{}.{}'.format(self.from_alias, x)) if isinstance(x, str)
                    else x
                for x
                in columns
            )
        )

    def delete_sql(self, params=None, force=False, **filters):

        if params is None:
            params = {}

        if filters is None and not force:
            raise ValueError(
                'Cannot wildly delete entries without set delimiting filters. '
                'If you are sure that you want to delete entries without filtering, '
                'please use param force=True'
            )

        where_clause, params = self.where_sql(params, **filters)

        return (
            '''
                DELETE FROM {schema}{table} {from_alias}
                WHERE {where_clause}
                RETURNING id
            '''.format(
                from_alias=self.from_alias,
                schema=self.schema,
                table=self.table_name,
                where_clause=where_clause
            ),
            params
        )

    def where_sql(self, params, **filters):

        declared_filters = []

        if 'oid' not in self.filters.keys():
            declared_filters.append(('oid', self.from_alias + '.id=%'))

        if 'oid__in' not in self.filters.keys():
            declared_filters.append(('oid__in', self.from_alias + '.id = any(%::int[])'))

        declared_filters.extend(self.filters.items())

        return self._filter_expression(declared_filters, params, **filters)

    def having_sql(self, params, **filters):

        res = self._filter_expression(
            self.having_filters.items(),
            params,
            **filters
        )

        return res if res != 'TRUE' \
            else ''

    def _filter_expression(self, declared_filters, params, **filters):

        snippet = []

        for opts in declared_filters:

            filter_name,\
            expr        = opts

            if filter_name in filters:
                filter_value = filters[filter_name]
                param_name = self.add_param_name(filter_name, filter_value, params)

                snippet.append(expr.replace('%', '${}'.format(param_name)))

        if not snippet:
            snippet = 'TRUE'
        else:
            snippet = ' AND '.join(snippet)

        return snippet, params

    async def query(self, sql, params={}):

        if isinstance(params, dict):
            sql, params = self.placeholder_to_ordinal(sql, params)

        return await self._fetch(sql, *params)

    async def _fetch(self, *args, **kwargs):

        ret = await self.db_model.fetch(*args, conn=self.db_conn, **kwargs)
        ret = self.decode_objects(ret)
        return ret

    async def transform_objects(self, data, format=None):
        is_single = isinstance(data, dict)

        if is_single:
            data = [data]

        transformed_objects = []
        for obj in data:
            transformed_objects.append(await self.transform_object(obj, format=format))

        if is_single:
            transformed_objects = transformed_objects[0]

        if format and format != 'json' and format not in self.formats:
            raise RuntimeError('Format does not exists, allowed values: json,' + ','.join(self.formats.keys()))
        elif format and format != 'json'  and isinstance(self.formats[format], tuple):
            transformed_objects = getattr(self, self.formats[format][0])(transformed_objects)
        else:
            transformed_objects = {
                'results': transformed_objects
            }

        return transformed_objects

    async def transform_object(self, data, format=None):

        if format and format != 'json' and format not in self.formats:
            raise RuntimeError('Format does not exists, allowed values: json' + ','.join(self.formats.keys()))
        elif format and format != 'json' and isinstance(self.formats[format], tuple) and len(self.formats[format])>1:
            data = getattr(self, self.formats[format][1])(data)

        return data

    def format_geojson_featurecollection(self, data):
        return {
            'type': 'FeatureCollection',
            'features': data,
            'properties': {}
        }

    def format_geojson_feature(self, data):
        return {
            'type': 'Feature',
            'geometry': data.get('geom', None),
            'properties': OrderedDict(
                (k, v)
                for k, v
                in data.items()
                if k != 'geom'
            )
        }

    @property
    def schema(self):
        return config.DB_SCHEMA + '.' if config.DB_SCHEMA \
            else ''

    @classmethod
    def add_param_name(cls, name, value, params):

        if name in params:
            for i in itertools.count(1):
                name = name + str(i)
                if name not in params:
                    break

        params[name] = cls.prepare_value(value)

        return name

    @staticmethod
    def prepare_value(val):
        if isinstance(val, dict):
            val = json.dumps(val)

        return val

    def to_python(self, obj:dict):
        return obj

    @staticmethod
    def placeholder_to_ordinal(sql, params):
        ordinal_params = []

        named_params = list(sorted(params.keys(), key=lambda x: -len(x)))

        for named_param in named_params:
            if ('$' + named_param) in sql:
                sql = sql.replace('$' + named_param, '$' + str(len(ordinal_params) + 1))
                ordinal_params.append(params[named_param])

        return sql, ordinal_params

    def patch_insert_columns_encoded(self, data):
        for attr_name in self.encoded_columns:
            if attr_name in data and not is_list_or_tuple(data[attr_name], length=2):
                data[attr_name] = (data[attr_name], 'pgp_pub_encrypt(${}, dearmor(get_pgp_pubkey()))')

        return data

    def patch_insert_columns(self, values):

        values.pop('created_at', None)

        if any(re.match(r'^(' + self.from_alias + '\.)?updated_at$', x) for x in self.select_columns.values()):
            values['updated_at'] = ('', 'CURRENT_TIMESTAMP')

        for attr, value in values.items():
            if isinstance(value, GeoJSON):
                values[attr] = shape(value).wkb_hex

        return values

    def decode_objects(self, data):

        if not config.PGP_PRIVATE_KEY:
            return data

        is_single = isinstance(data, dict)

        if is_single:
            data = [data]

        for obj in data:
            for encoded_attr in set(self.encoded_columns).intersection(obj.keys()):
                if obj[encoded_attr] is not None:
                    try:
                        db_crypted_attr = pgpy.PGPMessage.from_blob(obj[encoded_attr])
                        obj[encoded_attr] = config.PGP_PRIVATE_KEY[0].decrypt(db_crypted_attr).message
                    except ValueError as e:
                        obj[encoded_attr] = None
                        logger.warning(
                            "Couldn't decode attribute attribute %s of object with %s.%s: %s",
                            encoded_attr,
                            self.__class__.__name__,
                            str(obj.get('id', 'UNKNOWN')),
                            str(e)
                        )

        if is_single:
            data = data[0]

        return data

