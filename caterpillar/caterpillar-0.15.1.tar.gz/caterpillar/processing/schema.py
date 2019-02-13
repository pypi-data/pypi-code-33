# Copyright (c) 2012-2014 Kapiche Limited
# Author: Kris Rogers <kris@kapiche.com>, Ryan Stuart <ryan@kapiche.com>
"""
Indexes (see :mod:`caterpillar.processing.index`) in caterpillar must have a :class:`.Schema`. This module defines that
schema and also provides a bunch of utility functions for working with schemas and csv.

"""
from __future__ import absolute_import, division

import re
import sys

from caterpillar.processing.analysis.analyse import EverythingAnalyser, DefaultAnalyser, DateTimeAnalyser
from caterpillar.processing.analysis.tokenize import Token


class FieldConfigurationError(Exception):
    pass


class FieldType(object):
    """
    Represents a field configuration. :class:`.Schema`s are built out of fields.

    The FieldType object controls how a field is analysed via the ``analyser``
    (:class:`caterpillar.processing.analysis.Analyser`) attribute.

    If you don't provide an analyser for your field, it will default to a
    :class:``caterpillar.processing.analysis.EverythingAnalyser``.

    """
    # Convenience hash of operators -> methods
    FIELD_OPS = {'<': 'lt', '<=': 'lte', '>': 'gt', '>=': 'gte', '*=': 'equals_wildcard', '=': 'equals'}

    def __init__(self, analyser=EverythingAnalyser(), indexed=False, categorical=False, stored=True):
        """
        Create a new field.

        ``analyser`` (:class:`caterpillar.processing.analysis.Analyser`) is the analyser used for this field.
        ``indexed`` (bool) indicates if this field should be indexed or not. ``categorical`` (bool) indicates if this
        field is categorical or not. Categorical fields only support indexing for the purpose of searching and do not
        collect full statistics such as positions and associations. ``stored`` (bool) says if this field should be
        stored or not.

        """
        self._analyser = analyser
        self._indexed = indexed
        self._categorical = categorical
        self._stored = stored

    def analyse(self, value):
        """Analyse ``value``, returning a :class:`caterpillar.processing.analysis.tokenize.Token` generator."""
        for token in self._analyser.analyse(value):
            yield token

    @property
    def categorical(self):
        return self._categorical

    @property
    def indexed(self):
        return self._indexed

    @property
    def stored(self):
        return self._stored

    def evaluate_op(self, operator, value1, value2):
        """
        Evaluate ``operator`` (str from :const:`FieldType.FIELD_OPS`) on operands ``value1`` and ``value2``.

        """
        op_method = getattr(self, FieldType.FIELD_OPS[operator])
        return op_method(value1, value2)

    def equals(self, value1, value2):
        """Returns whether ``value1`` is equal to ``value2``."""
        raise NotImplementedError('Equality operator not supported for field type {}.'.format(self.__class__.__name__))

    def equals_wildcard(self, value, wildcard_value):
        """Returns whether ``value`` matches regex ``wildcard_value``."""
        raise NotImplementedError('Wildcard equality operator not supported for field type {}.'
                                  .format(self.__class__.__name__))

    def gt(self, value1, value2):
        """Returns whether ``value1`` is greater than ``value2``."""
        raise NotImplementedError('Greater-than operator not supported for field type {}.'
                                  .format(self.__class__.__name__))

    def gte(self, value1, value2):
        """Returns whether ``value1`` is greater than or equal to ``value2``."""
        raise NotImplementedError('Greater-than-or-equals operator not supported for field type {}.'
                                  .format(self.__class__.__name__))

    def lt(self, value1, value2):
        """Returns whether ``value1`` is less than ``value2``."""
        raise NotImplementedError('Less-than operator not supported for field type {}.'
                                  .format(self.__class__.__name__))

    def lte(self, value1, value2):
        """Returns whether ``value1`` is less than or equal to ``value2``."""
        raise NotImplementedError('Less-than-or-equals operator not supported for field type {}.'
                                  .format(self.__class__.__name__))


class CategoricalFieldType(FieldType):
    """Represents a categorical field type. Categorical fields can extend this class for convenience."""
    def __init__(self, analyser=EverythingAnalyser(), indexed=False, stored=True):
        super(CategoricalFieldType, self).__init__(analyser=analyser, indexed=indexed, categorical=True, stored=stored)

    def value_of(self, raw_value):
        """Return the value of ``raw_value`` after being processed by this field type's analyse method."""
        return list(self.analyse(raw_value))[0].value

    def equals(self, value1, value2):
        return self.value_of(value1) == self.value_of(value2)


class ID(CategoricalFieldType):
    """
    Configured field type that indexes the entire value of the field as one token. This is useful for data you don't
    want to tokenize, such as the path of a file.

    """
    def __init__(self, indexed=False, stored=True):
        super(ID, self).__init__(indexed=indexed, stored=stored)


class NUMERIC(CategoricalFieldType):
    """Special field type that lets you index ints or floats."""
    TYPES = (int, float)

    def __init__(self, indexed=False, stored=True, num_type=int, default_value=None):
        """Create new NUMERIC instance with type ``num_type`` (float or int) and default_value (float or int)."""
        if num_type not in NUMERIC.TYPES:
            raise ValueError("Invalid num_type '{}'".format(num_type))
        self._num_type = num_type
        self._default_value = default_value
        super(NUMERIC, self).__init__(analyser=None, indexed=indexed, stored=stored)

    def analyse(self, value):
        try:
            yield Token(self._num_type(value))
        except (TypeError, ValueError) as e:
            if value is None or len(value) == 0:
                yield Token(self._default_value)
            else:
                raise e

    def gt(self, value1, value2):
        return self.value_of(value1) > self.value_of(value2)

    def gte(self, value1, value2):
        return self.value_of(value1) >= self.value_of(value2)

    def lt(self, value1, value2):
        return self.value_of(value1) < self.value_of(value2)

    def lte(self, value1, value2):
        return self.value_of(value1) <= self.value_of(value2)


class BOOLEAN(CategoricalFieldType):
    """
    bool field type that lets you index boolean values (True and False).

    The field converts the bool values to text for you before indexing.

    """
    def __init__(self, indexed=False, stored=True):
        super(BOOLEAN, self).__init__(analyser=None, indexed=indexed, stored=stored)

    def analyse(self, value):
        # First try converting value to an integer, to handle the '0' string as Falsey
        try:
            yield Token(bool(int(value)))
        except ValueError:
            yield Token(bool(value))


class TEXT(FieldType):
    """Configured field type for text fields."""
    def __init__(self, analyser=DefaultAnalyser(), indexed=True, stored=True):
        """
        Create a text field with ``analyser`` (:class:`caterpillar.processing.analysis.Analyser`) default to
        :class:`caterpillar.processing.analysis.DefaultAnalyzer`.

        """
        super(TEXT, self).__init__(analyser=analyser, indexed=indexed, categorical=False, stored=stored)


class CATEGORICAL_TEXT(CategoricalFieldType):
    """Configured field type for categorical text fields."""
    def __init__(self, indexed=False, stored=True):
        super(CATEGORICAL_TEXT, self).__init__(indexed=indexed, stored=stored)

    def analyse(self, value):
        yield Token(value.strip())

    def equals_wildcard(self, value, wildcard_value):
        return re.match(wildcard_value, value) is not None


class DATETIME(FieldType):
    """Field type for datetimes.

    Datetimes are stored as ISO8601 strings down to a resolution of 1 second. All datetimes are either datetime
    unaware (no UTC offset) or datetime aware and stored as UTC (explicit offset +00:00). This means all datetimes
    are lexicographically comparable.

    """

    def __init__(self, analyser=DateTimeAnalyser(), indexed=False, stored=True):
        super(DATETIME, self).__init__(analyser=analyser, indexed=indexed, stored=stored, categorical=True)

    def value_of(self, raw_value):
        """Return the value of ``raw_value`` after being processed by this field type's analyse method."""
        return list(self.analyse(raw_value))[0].value

    def gt(self, value1, value2):
        return self.value_of(value1) > self.value_of(value2)

    def gte(self, value1, value2):
        return self.value_of(value1) >= self.value_of(value2)

    def lt(self, value1, value2):
        return self.value_of(value1) < self.value_of(value2)

    def lte(self, value1, value2):
        return self.value_of(value1) <= self.value_of(value2)

    def equals(self, value1, value2):
        return self.value_of(value1) == self.value_of(value2)


class Schema(object):
    """
    Represents the collection of fields in an index. Maps field names to FieldType objects which define the behavior of
    each field.

    Low-level parts of the index use field numbers instead of field names for compactness. This class has several
    methods for converting between the field name, field number, and field object itself.

    """
    def __init__(self, **fields):
        """
        All keyword arguments to the constructor are treated as ``fieldname = fieldtype`` pairs. The fieldtype can be an
        instantiated FieldType object, or a FieldType sub-class (in which case the Schema will instantiate it with the
        default constructor before adding it).

        For example::

            s = Schema(content = TEXT, title = TEXT(stored = True), tags = KEYWORD(stored = True))

        """

        self._fields = {}

        for name in sorted(fields.keys()):
            self.add(name, fields[name])

    def __iter__(self):
        """Returns the field objects in this schema."""
        return iter(self._fields.values())

    def __getitem__(self, name):
        """Returns the field associated with the given field name."""
        if name in self._fields:
            return self._fields[name]

        raise KeyError("No field named {}".format(name))

    def __len__(self):
        """Returns the number of fields in this schema."""
        return len(self._fields)

    def __contains__(self, field_name):
        """Returns True if a field by the given name is in this schema."""
        # Defined in terms of __getitem__ so that there's only one method to override to provide dynamic fields
        try:
            field = self[field_name]
            return field is not None
        except KeyError:
            return False

    def items(self):
        """Returns a list of ``("field_name", field_object)`` pairs for the fields in this schema."""
        return sorted(self._fields.items())

    def names(self):
        """Returns a list of the names of the fields in this schema."""
        return sorted(self._fields.keys())

    def get_indexed_text_fields(self):
        """Returns a list of the indexed text fields."""
        return [name for name, field in self._fields.items() if field.indexed and type(field) == TEXT]

    def get_indexed_structured_fields(self):
        """Returns a list of the indexed structured (non-text) fields."""
        return [name for name, field in self._fields.items() if field.indexed and type(field) != TEXT]

    def add(self, name, field_type):
        """
        Adds a field to this schema.

        ``name`` (str) is the name of the field. ``fieldtype`` (:class:`FieldType`) is either
        instantiated FieldType object, or a FieldType subclass. If you pass an instantiated object, the schema will use
        that as the field configuration for this field. If you pass a FieldType subclass, the schema will automatically
        instantiate it with the default constructor.

        """
        # Check field name
        if name.startswith("_"):
            raise FieldConfigurationError("Field names cannot start with an underscore")
        if name in self._fields:
            raise FieldConfigurationError("Schema already has a field {}".format(name))

        # If the user passed a type rather than an instantiated field object,
        # instantiate it automatically
        if type(field_type) is type:
            try:
                field_type = field_type()
            except Exception:
                e = sys.exc_info()[1]
                raise FieldConfigurationError("Error: {} instantiating field {}: {}".format(e, name, field_type))

        if not isinstance(field_type, FieldType):
            raise FieldConfigurationError("{} is not a FieldType object".format(field_type))

        self._fields[name] = field_type
