# -*- coding: utf-8 -*-


class BaseCollectionResponse(dict):

    def __init__(self, data):
        self.update(data)

    @property
    def data(self):
        return self.get('data', [])

    @property
    def count(self):
        return self['meta']['count']

    def assertCount(self, count):
        assert self.count == count, "Expected to find {} results, but was {}" \
            .format(count, self.count)
        return self

    def assertRaiseJsonApiError(self, pointer):
        """Assert an error response has a specific pointer
        """
        assert 'errors' in self
        for error in self['errors']:
            assert 'source' in error
            assert 'pointer' in error['source']
            if pointer in error['source']['pointer']:
                return self
        assert False, "JsonApiError pointer '{}' not raised".format(pointer)  # pragma: no cover

    def assertHasDatas(self, obj_type, values):
        """Assert a response has specific data values
        """
        assert 'data' in self, "'data' key not fount in response"

        for idx, entry in enumerate(self['data']):
            assert 'type' in entry, "'type' key not found in 'data[%s]'" % idx
            assert 'id' in entry, "'id' key not found in 'data[%s]'" % idx
            assert entry['type'] == obj_type, "Item {}: type '{}' expected but found '{}'".format(
                idx, obj_type, entry['type'])
            assert entry['id'] == values[idx], "Item {}: id '{}' expected but found '{}'".format(
                idx, values[idx], entry['id'])
        return self

    def assertHasPaginationLinks(self):
        """ Assert pagination links are present in links.
        """
        assert 'links' in self, "'links' key not present"
        assert set(['first', 'last', 'self']).issubset(self['links'])
        return self
