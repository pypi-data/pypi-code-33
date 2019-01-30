from guillotina.catalog.utils import get_index_fields
from guillotina.component import getUtilitiesFor
from guillotina.content import IResourceFactory


class BasicJsonIndex(object):

    def __init__(self, name):
        self.name = name

    @property
    def idx_name(self):
        return 'idx_{}'.format(self.name)

    @property
    def index_sql(self):
        return '''CREATE INDEX {} ON objects ((json->>'{}'));'''.format(
            self.idx_name,
            self.name
        )

    def where(self, value, operator='=', arg_idx=1):
        return """json->>'{}' {} ${}::text """.format(
            self.name, operator, arg_idx)

    def order_by(self, arg_idx=1, reversed=False):
        type_ = 'ASC'
        if reversed:
            type_ = 'DESC'
        return "order by json->>'{}' {}".format(self.name, type_)

    def select(self, arg_idx=1):
        return []


class BooleanIndex(BasicJsonIndex):
    @property
    def index_sql(self):
        return '''CREATE INDEX {} ON objects (((json->>'{}')::boolean));'''.format(  # noqa
            self.idx_name,
            self.name
        )

    def where(self, value, operator='=', arg_idx=1):
        return """(json->>'{}')::boolean {} ${}::boolean """.format(
            self.name, operator, arg_idx)


class KeywordIndex(BasicJsonIndex):
    @property
    def index_sql(self):
        return '''CREATE INDEX {} ON objects USING gin ((json->'{}'))'''.format(  # noqa
            self.idx_name,
            self.name
        )

    def where(self, value, operator='?', arg_idx=1):
        return """json->'{}' {} ${}::text """.format(
            self.name, operator, arg_idx)


class PathIndex(BasicJsonIndex):

    def where(self, value, operator='=', arg_idx=1):
        return """substring(json->>'{}', 0, {}) {} ${}::text """.format(
            self.name, len(value) + 1, operator, arg_idx)


class CastIntIndex(BasicJsonIndex):
    cast_type = 'integer'

    @property
    def index_sql(self):
        return '''CREATE INDEX {} ON objects
                  using btree(CAST(json->>'{}' AS {}))'''.format(
            self.idx_name,
            self.name,
            self.cast_type
        )

    def where(self, value, operator='>', arg_idx=1):
        """
        where CAST(json->>'favorite_count' AS integer) > 5;
        """
        return """CAST(json->>'{}' AS {}) {} ${}::{}""".format(
            self.name, self.cast_type,
            operator,
            arg_idx,
            self.cast_type)


class CastFloatIndex(BasicJsonIndex):
    cast_type = 'float'


class FullTextIndex(BasicJsonIndex):

    @property
    def index_sql(self):
        return '''CREATE INDEX {} ON objects
                  using gin(to_tsvector('english', json->>'{}'));'''.format(
            self.idx_name,
            self.name
        )

    def where(self, value, operator='', arg_idx=1):
        """
        to_tsvector('english', json->>'text') @@ to_tsquery('python & ruby')
        """
        return """to_tsvector('english', json->>'{}') @@ plainto_tsquery(${}::text)""".format(  # noqa
            self.name, arg_idx)

    def order_by(self, arg_idx=1, reversed=False):
        type_ = 'ASC'
        if reversed:
            type_ = 'DESC'
        return 'order by {}_score {}'.format(self.name, type_)

    def select(self, arg_idx=1):
        return [
            '''ts_rank_cd(to_tsvector('english', json->>'{}'),
                          plainto_tsquery(${}::text)) AS {}_score'''.format(
                self.name,
                arg_idx,
                self.name)
        ]


index_mappings = {
    '*': BasicJsonIndex,
    'keyword': KeywordIndex,
    'textkeyword': KeywordIndex,
    'path': PathIndex,
    'int': CastIntIndex,
    'float': CastFloatIndex,
    'searchabletext': FullTextIndex,
    'boolean': BooleanIndex
}


_cached_indexes = {}


def get_indexes(invalidate=False):
    """
{
    "access_users": ["root"],
    "uuid":"a037df9fa3624b5fb09dbda1480f8210",
    "contributors":null,
    "created":"2017-03-16T08:46:00.633690-05:00",
    "portal_type":"Folder",
    "title":"Posts",
    "modified":"2017-03-16T08:46:00.633690-05:00",
    "depth":2,
    "subjects":null,
    "path":"/site/posts",
    "creators":null,
    "access_roles":["guillotina.SiteAdmin"],
    "parent_uuid":"8406d8b94d0e47bfa6cb0a82e531216b"
}
    """
    if invalidate:
        _cached_indexes.clear()
    if len(_cached_indexes) > 0:
        return _cached_indexes

    for type_name, schema in getUtilitiesFor(IResourceFactory):
        for field_name, catalog_info in get_index_fields(type_name).items():
            catalog_type = catalog_info.get('type', 'text')
            if catalog_type not in index_mappings:
                index = index_mappings['*'](field_name)
            else:
                index = index_mappings[catalog_type](field_name)
            _cached_indexes[field_name] = index
    return _cached_indexes


def get_index(name):
    indexes = get_indexes()
    if name in indexes:
        return indexes[name]
