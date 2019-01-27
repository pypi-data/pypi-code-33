# -*- coding: utf-8 -*-

import pprint
from datetime import datetime


class BaseResponse(dict):

    class assertRaises:

        def __init__(self, expected, expected_regexp=None):
            self.expected = expected
            self.failureException = AssertionError
            self.expected_regexp = expected_regexp

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, tb):  # pragma: no cover
            if exc_type is None:
                try:
                    exc_name = self.expected.__name__
                except AttributeError:
                    exc_name = str(self.expected)
                raise self.failureException(
                    "{0} not raised".format(exc_name))
            if not issubclass(exc_type, self.expected):
                # let unexpected exceptions pass through
                return False
            self.exception = exc_value  # store for later retrieval
            if self.expected_regexp is None:
                return True

            expected_regexp = self.expected_regexp
            if not expected_regexp.search(str(exc_value)):
                raise self.failureException('"%s" does not match "%s"' %
                                            (expected_regexp.pattern, str(exc_value)))
            return True

    def __init__(self, data):
        if data is None:
            self.update({})
        elif data.get('data'):
            self.update(data['data'])
        else:
            self.update(data)
        if data is not None and data.get('included'):
            self['included'] = data['included']

    @property
    def id(self):
        assert 'id' in self
        try:
            return int(self['id'])
        except AssertionError:  # pragma: no cover
            raise AttributeError("Object id not found in response.")

    @property
    def created_on_datetime(self):
        return self._format_datetime(self.get_attribute('created-on-datetime'))

    def _format_datetime(self, date_time):
        return datetime.strptime(date_time, '%Y-%m-%dT%H:%M:%S')

    def get_attribute(self, attribute):
        attribute = attribute.replace('_', '-')
        assert 'attributes' in self
        assert attribute in self['attributes'], attribute
        try:
            return self['attributes'][attribute]
        except AssertionError:  # pragma: no cover
            raise AttributeError("Attribute '%s' not found in response." % attribute)

    def _get_relationships(self, relationships):
        relationships = relationships.replace('_', '-')
        assert 'relationships' in self
        assert relationships in self['relationships'], relationships
        return self['relationships'][relationships]

    def assertDataIsNone(self):
        """Assert the data attribute is None
        """
        assert 'data' in self
        assert self['data'] is None, self['data']

    def assertHasId(self, value):
        """Assert the ID has value
        """
        assert str(self.id) == str(value), "Expected id to be '{}' but was '{}'".format(value, self.id)
        return self

    def assertHasRelationshipRelated(self, relation_type, link):
        """Assert an error response has a specific pointer
        """
        relation_type = relation_type.replace('_', '-')
        assert 'relationships' in self
        assert relation_type in self['relationships']
        assert 'links' in self['relationships'][relation_type]
        assert 'related' in self['relationships'][relation_type]['links']
        try:
            assert link in self['relationships'][relation_type]['links']['related']
        except AssertionError:  # pragma: no cover
            raise AttributeError(
                "assert '%s' in self['relationships']['%s']['links']['related']" % (link, relation_type))
        return self

    def assertHasRelationshipSelf(self, relation_type, link):
        """Assert an error response has a specific pointer
        """
        relation_type = relation_type.replace('_', '-')
        assert 'relationships' in self
        assert relation_type in self['relationships'], relation_type
        assert 'links' in self['relationships'][relation_type], relation_type
        assert 'self' in self['relationships'][relation_type]['links'], relation_type
        assert link in self['relationships'][relation_type]['links']['self'], link
        return self

    def assertHasAttribute(self, attribute, value):
        """Assert a response attribute has a specific value
        """
        try:
            assert self.get_attribute(attribute) == value
        except AssertionError:  # pragma: no cover
            raise AttributeError("Attribute '%s' value '%s' not the expected one (%s)." %
                                 (attribute, self.get_attribute(attribute), value))
        return self

    def assertAttributeNotPresent(self, attribute):
        """Assert a response doesn't contains an attribute
        """
        try:
            self.get_attribute(attribute)
            raise AttributeError("Attribute '{}' was not found in response but we don't expect it.".format(attribute))  # pragma: no cover
        except AssertionError:
            pass
        return self

    def assertNotHasAttribute(self, attribute, value):
        """Assert a response attribute equals a specific value
        """
        try:
            assert self.get_attribute(attribute) != value
        except AssertionError:  # pragma: no cover
            raise AttributeError("Attribute '%s' value '%s' is expected to be different then '%s'." %
                                 (attribute, self.get_attribute(attribute), value))
        return self

    def assertHasRelationshipData(self, relationships, value, obj_type):
        """Assert a response relation has a specific value
        """
        rel = self._get_relationships(relationships)
        if value is None:  # pragma: no cover
            assert rel['data'] is None
        assert rel['data'] is not None
        try:
            assert 'id' in rel['data']
            assert rel['data']['id'] == str(value)
        except AssertionError:  # pragma: no cover
            raise AttributeError("Relationships '%s' value should be '%s' but was '%s'." %
                                 (relationships, value, rel['data']['id']))
        try:
            assert 'type' in rel['data']
            assert rel['data']['type'] == obj_type
        except AssertionError:  # pragma: no cover
            raise AttributeError("Relationships '%s' should be '%s' but was '%s'." %
                                 (relationships, obj_type, rel['data']['type']))
        return self

    def assertHasRelationshipDatas(self, relationships, values, obj_type):
        """Assert a response relation has specific values
        """
        rel = self._get_relationships(relationships)
        if values is None:  # pragma: no cover
            assert rel['data'] is None, rel
        assert rel['data'] is not None, rel

        str_values = [str(value.id) for value in values]
        found_ids = []
        try:
            # returned data in expected list
            for data in rel['data']:
                assert 'id' in data
                assert data['id'] in str_values, data['id']
                assert 'type' in data
                assert data['type'] == obj_type
                found_ids.append(data['id'])
            # expect to find all expected values in response
            for value in str_values:
                assert value in found_ids
        except AssertionError:  # pragma: no cover
            raise AttributeError("Included relationships '%s' not found in response, expected %s, found %s." % (
                relationships, str_values, rel['data']))
        return self

    def assertHasData(self, obj_type, value):
        """Assert a response has a specific data value
        """
        assert 'type' in self, "'type' key not found in 'data'"
        assert 'id' in self, "'id' key not found in 'data'"
        assert self['type'] == obj_type, "type '{}' expected but found '{}'".format(obj_type, self['type'])
        assert self['id'] == value, "id '{}' expected but found '{}'".format(value, self['id'])
        return self

    def assertCreationDateTime(self):
        self.assertDateTimePresent('created-on-datetime')
        return self

    def assertUpdatedDateTime(self):
        self.assertDateTimePresent('updated-on-datetime')
        return self

    def assertHasAttributeDateTimeOrNone(self, attribute, date_time):
        if date_time is None:
            return
        self.assertHasAttributeDateTime(attribute, date_time)
        return self

    def assertHasAttributeDateTime(self, attribute, date_time):
        self.assertDateTimePresent(attribute)
        if isinstance(date_time, datetime):
            date_time = date_time.strftime("%Y-%m-%dT%H:%M:%S")
        assert self.get_attribute(attribute)[:-1] == date_time[:-1]
        return self

    def assertDateTimePresent(self, attribute):
        datetime = self.get_attribute(attribute)
        self.assertIsDateTime(datetime)
        return self

    def assertIsDateTime(self, date_time):
        if isinstance(date_time, datetime):  # pragma: no cover
            return self

        try:
            datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S")
        except ValueError:  # pragma: no cover
            assert False, 'Date is not parsable (%s)' % date_time
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

    def assertJsonApiErrorCount(self, count):
        """Assert an error response has a specific number of entries
        """
        assert 'errors' in self, "No error found but we expect to see {}".format(count)
        assert len(self['errors']) == count, "Expected to find {} errors, but was {}" \
            .format(count, self.count)
        return self

    def assertDateTimeAlmostEqual(self, first, second, delta=1):
        """ Compare two datetime attributes, accept maximum difference
        of `delta` seconds.
        """
        first_attribute = datetime.strptime(self.get_attribute(first), "%Y-%m-%dT%H:%M:%S")
        second_attribute = datetime.strptime(self.get_attribute(second), "%Y-%m-%dT%H:%M:%S")
        computed_delta = (first_attribute - second_attribute).seconds
        assert computed_delta == 0 or computed_delta == 1

    def pprint(self):  # pragma: no cover
        pprint.pprint(self)
        return self
