# coding: utf-8
"""
This module provides a :class:`JsonbTable` class which allows to flatten JSONB
fields data in generated scalar fields.

To achieves this, for each JSONB field to be flattened, it parses a JSON data
description (a sort of json-schema) to build a sqlalchemy selectable
expression.
This expression can be used as an actual table, where each JSONB field has been
replaced by multiple typed fields which names are the path of the data with a
double-underscore separator.
This path is composed of the name of the JSONB field plus the path of the data
in the JSON structure.

In example, considering a JSON `data` field which contains a `prop` property,
the `prop` data will be available in the `data__prop` field of the generated
sqlalchemy expression.
"""

from operator import attrgetter

from sqlalchemy import (cast, false as sa_false, select, true as sa_true,
                        Column)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import sqltypes
from sqlalchemy.sql.base import _generative
from sqlalchemy.sql.functions import FunctionElement


class _OrdinableFunctionElement(FunctionElement):
    """
    This is a base class for functions which can be used with the `WITH
    ORDINALITY` Postgresql feature.
    It is not supposed to be instantiated as is but should rather be inherited
    by former usable classes providing an actual `name` class attribute.
    """
    name = None
    alias = None
    alias_columns = None
    ordinality = None

    @_generative
    def alias(self, name, columns=None):
        """
        Sets attributes needed to compile with an alias clause

        """
        self.alias = name
        self.alias_columns = columns or []

    @_generative
    def with_ordinality(self, name="idx"):
        """
        Sets attribute needed to compile with an ordinality clause

        """
        self.ordinality = name


class _JsonbArrayElements(_OrdinableFunctionElement):
    """
    This class allows to use an "ordinable" version of the Postgresql
    'jsonb_array_elements' function with sqlalchemy.
    """
    name = 'jsonb_array_elements'


class _JsonbArrayElementsText(_OrdinableFunctionElement):
    """
    This class allows to use an "ordinable" version of the Postgresql
    'jsonb_array_elements_text' function with sqlalchemy.
    """
    name = 'jsonb_array_elements_text'


@compiles(_OrdinableFunctionElement)
def _compile_orinable_function_element(element, compiler, **kw):
    """
    This function is used by sqlalchemy to compile `OrdinableFunctionElement`
    instances.
    """
    statement = '%s(%s)' % (element.name, compiler.process(element.clauses))

    if element.ordinality is not None:
        statement = '{} WITH ORDINALITY'.format(statement)

    if element.alias is not None:
        alias = element.alias
        if element.alias_columns is not None:
            alias = '{}({})'.format(alias, ', '.join(element.alias_columns))
        statement = '{} AS {}'.format(statement, alias)

    return statement


class _Fragment(object):
    """
    This class represents a chunk of a JSON data description and is intended
    to be inherited by more functional classes.
    """
    def __init__(self, name, fragment, parent, parent_array=None):
        """
        Args:
            name: the name of the fragment
            fragment: the JSON description
            parent: the direct parent of the fragment
            parent_array: the nearest parent array of the fragment
        """
        assert fragment.get('type'), (
            'fragment has no "type" attribute: {}'.format(fragment))
        self.name = name
        self.fragment = fragment
        self.parent = parent
        self.parent_array = (parent_array
                             or getattr(parent, 'parent_array', None))

    @property
    def root(self):
        """
        _JsonbField: The root of the JSON data structure

        """
        return self.parent.root

    @property
    def path(self):
        """
        tuple (str): The list of the instance's parents.

        """
        parent_path = getattr(self.parent, 'path', tuple())
        return parent_path + (self.name, )

    @property
    def full_name(self):
        """
        str: The full name of the instance with all its ancestor separated by
             a double underscore.

        """
        return '__'.join(self.path)

    def parse(self):
        """
        This function should be overriden by subclasses to parse the JSON
        description and extract required information.

        """
        raise NotImplementedError

    def expression(self):
        """
        This function should be overriden by subclasses to generate the
        sqlalchemy expression allowing to access the data represented by the
        JSON description.

        .. todo:: check that the return type is correct

        Returns: sqlalchemy.sql.ColumnElement
        """
        raise NotImplementedError

    @property
    def parent_expression(self):
        """
        Computes and returns the parent expression.
        This parent expression is the first available among this list:

        * The parent array expression
        * The direct parent expression
        * The column containing the JSON data

        .. todo:: check that the return type is correct

        Returns: sqlalchemy.sql.ClauseElement

        """
        expressable_parent = self.parent_array or self.parent
        if isinstance(expressable_parent.parent, _Fragment):
            return expressable_parent.expression()
        else:
            return self.root.column

    def __str__(self):
        return '{} {}'.format(self.__class__.__name__, self.full_name)


class _Array(_Fragment):
    """
    This class represents an array chunk of JSON data description.
    """
    PG_TYPE = JSONB
    INDEX_SUFFIX = 'index'
    ITEM_SUFFIX = 'item'

    def __init__(self, name, fragment, parent, parent_array=None):
        """
        Args:
            name: the name of the fragment
            fragment: the JSON description
            parent: the direct parent of the fragment
            parent_array: the nearest parent array of the fragment
        """
        super(_Array, self).__init__(name, fragment, parent, parent_array)
        assert fragment['type'] == 'array'
        assert fragment.get('items'), (
            'array has no "items" attribute: {}'.format(fragment))
        self.items = None
        self.child_arrays = []
        self.preserved = False
        self.root.register_array(self)
        if self.parent_array:
            self.parent_array.register_child_array(self)
        self.parse()

    @property
    def item_name(self):
        """
        str: The name of the instance's item column.

        """
        return '__'.join((self.full_name, self.ITEM_SUFFIX))

    @property
    def index_name(self):
        """
        str: The name of the instance's index column.

        """
        return '__'.join((self.item_name, self.INDEX_SUFFIX))

    @property
    def index(self):
        """
        ~sqlalchemy.schema.Column: The instance's index column

        """
        return None if self.preserved else Column(self.index_name)

    def register_child_array(self, array):
        """
        This function registers a child array to the instance. It is used by
        children arrays to register themselves to their parent array.

        Args:
            array (_Array): The child array to be registered

        """
        self.child_arrays.append(array)

    def parse(self):
        """
        This function parses the array JSON data description to extract needed
        data.

        """
        self.items = _fragment_factory(
            self.ITEM_SUFFIX, self.fragment['items'], self, parent_array=self)

    def expression(self):
        """
        This function computes the sqlalchemy expression representing the
        instance's data according to its preservation status.

        .. todo:: check that the return type is correct

        Returns: sqlalchemy.sql.ColumnElement

        """
        if self.preserved:
            return _JsonbArrayElementsText(
                self.parent_expression.op('->')(self.name))
        else:
            return Column(self.item_name)

    def from_expression(self):
        """
        This function computes the sqlalchemy expression to be used in FROM
        clause.

        .. todo:: check that the return type is correct

        Returns: sqlalchemy.sql.ClauseElement

        """
        func_class = (_JsonbArrayElements if self.child_arrays
                      else _JsonbArrayElementsText)

        if self.parent is self.parent_array:
            base_from = func_class(self.parent_expression)
        else:
            base_from = func_class(self.parent_expression.op('->')(self.name))

        from_ = (base_from
                 .with_ordinality(self.index_name)
                 .alias(self.full_name, columns=(self.item_name,
                                                 self.index_name)))

        non_preserved_children = [child for child in self.child_arrays
                                  if not child.preserved]

        if non_preserved_children:
            sub_join = non_preserved_children[0].from_expression()
            for child in non_preserved_children[1:]:
                sub_join = sub_join.join(child.from_expression(),
                                         onclause=sa_false(), full=True)
            from_ = from_.join(select(['*']).select_from(sub_join).lateral(),
                               onclause=sa_true(), isouter=True)

        return from_


class _Object(_Fragment):
    """
    This class represents an object chunk of JSON data description.
    """
    def __init__(self, name, fragment, parent, parent_array=None):
        """
        Args:
            name: the name of the fragment
            fragment: the JSON description
            parent: the direct parent of the fragment
            parent_array: the nearest parent array of the fragment
        """
        super(_Object, self).__init__(name, fragment, parent, parent_array)
        assert fragment['type'] == 'object'
        assert fragment.get('properties'), (
            'object has no "properties" attribute: {}'.format(fragment))
        self.properties = []
        self.parse()

    def parse(self):
        """
        This function parses the array JSON data description to extract needed
        data.
        """
        for name, property_fragment in self.fragment['properties'].items():
            self.properties.append(
                _fragment_factory(name, property_fragment, self,
                                  parent_array=self.parent_array))

    def expression(self):
        """
        This function computes the sqlalchemy expression representing the
        instance's data.

        .. todo:: check that the return type is correct

        Returns: sqlalchemy.sql.ColumnElement
        """
        return self.parent_expression.op('->')(self.name)


class _Integer(_Fragment):
    """
    This class represents an integer chunk of JSON data description.
    """
    PG_TYPE = sqltypes.Integer

    def __init__(self, name, fragment, parent, parent_array=None):
        """
        Args:
            name: the name of the fragment
            fragment: the JSON description
            parent: the direct parent of the fragment
            parent_array: the nearest parent array of the fragment
        """
        super(_Integer, self).__init__(name, fragment, parent, parent_array)
        assert fragment['type'] == 'integer'
        self.root.register_leaf(self)

    # TODO: factoriser cette fonction pour tous les "leaf"
    def expression(self):
        """
        This function computes the sqlalchemy expression representing the
        instance's data.

        .. todo:: check that the return type is correct

        Returns: sqlalchemy.sql.ColumnElement
        """
        if self.parent is self.parent_array:
            return cast(
                self.parent_expression, self.PG_TYPE
            ).label(self.full_name)
        else:
            return cast(
                cast(self.parent_expression, JSONB).op('->>')(self.name),
                self.PG_TYPE
            ).label(self.full_name)


class _Number(_Fragment):
    """
    This class represents a number chunk of JSON data description.
    """
    PG_TYPE = sqltypes.Numeric

    def __init__(self, name, fragment, parent, parent_array=None):
        """
        Args:
            name: the name of the fragment
            fragment: the JSON description
            parent: the direct parent of the fragment
            parent_array: the nearest parent array of the fragment
        """
        super(_Number, self).__init__(name, fragment, parent, parent_array)
        assert fragment['type'] == 'number'
        self.root.register_leaf(self)

    def expression(self):
        """
        This function computes the sqlalchemy expression representing the
        instance's data.

        .. todo:: check that the return type is correct

        Returns: sqlalchemy.sql.ColumnElement
        """
        if self.parent is self.parent_array:
            return cast(
                self.parent_expression, self.PG_TYPE
            ).label(self.full_name)
        else:
            return cast(
                cast(self.parent_expression, JSONB).op('->>')(self.name),
                self.PG_TYPE
            ).label(self.full_name)


class _String(_Fragment):
    """
    This class represents a string chunk of JSON data description.
    """
    PG_TYPE = sqltypes.Text

    def __init__(self, name, fragment, parent, parent_array=None):
        """
        Args:
            name: the name of the fragment
            fragment: the JSON description
            parent: the direct parent of the fragment
            parent_array: the nearest parent array of the fragment
        """
        super(_String, self).__init__(name, fragment, parent, parent_array)
        assert fragment['type'] == 'string'
        self.root.register_leaf(self)

    def expression(self):
        """
        This function computes the sqlalchemy expression representing the
        instance's data.

        .. todo:: check that the return type is correct

        Returns: sqlalchemy.sql.ColumnElement
        """
        if self.parent is self.parent_array:
            return cast(
                self.parent_expression, self.PG_TYPE
            ).label(self.full_name)
        else:
            return cast(
                cast(self.parent_expression, JSONB).op('->>')(self.name),
                self.PG_TYPE
            ).label(self.full_name)


class _JsonbField(object):
    """
    This class represents a JSONB field to be flattened.
    """
    def __init__(self, column, schema):
        """
        Args:
            column (~sqlalchemy.schema.Column): The field to flatten
            schema (dict): The JSON data description
        """
        self.column = column
        self.schema = schema
        self.parsed = None
        self._arrays = []
        self._leaves = []
        self.parse()

    @property
    def root(self):
        """
        _JsonbField: The instance itself.

        """
        return self

    @property
    def fields(self):
        """
        list (~sqlalchemy.schema.Column):
            The list of generated flat data fields

        """
        fields = [leaf.expression() for leaf in self._leaves]
        fields.extend([array.index for array in self._arrays
                       if not array.preserved])
        return fields

    @property
    def select_clause(self):
        """
        .. todo:: check this return type

        ~sqlalchemy.sql.expression.Select: The select clause of the field (to
            be joined in final query)

        """
        clause = None
        root_arrays = [array for array in self._arrays
                       if not array.parent_array]

        if root_arrays:
            sub_join = root_arrays[0].from_expression()
            for array in root_arrays[1:]:
                sub_join = sub_join.join(array.from_expression(),
                                         onclause=sa_false(), full=True)

            clause = select(['*']).select_from(sub_join).lateral()

        return clause

    def register_leaf(self, leaf):
        """
        This function is used by :class:`_Fragment` instances to register JSON
        data leaves.

        Args:
            leaf (~sqlalchemy.schema.Column): The leaf to be registered

        """
        self._leaves.append(leaf)

    def register_array(self, array):
        """
        This function is used by :class:`_Fragment` instances to register JSON
        data arrays.

        Args:
            array (_Array): The array to be registered
        """
        self._arrays.append(array)

    def parse(self):
        """
        This function parses the JSON data description to extract needed data.

        """
        self.parsed = _fragment_factory(self.column.name, self.schema, self)


class JsonbTable(object):
    """
    This class is the only entry-point to benefit from the feature provided
    by the module.

    It have to be provided with a :class:`~sqlalchemy.schema.Table` and a
    list of named arguements where the argument name is the name of a JSONB
    field to be flattened and the argument value is the JSON data description.
    """

    def __init__(self, table, **field_schemas):
        """
        Args:
            table (~sqlalchemy.schema.Table):
                a table whose some fields have to be flattened
            **field_schemas (dict):
                JSON data descriptions associated to JSONB field names
        """
        self.table = table
        self.field_schemas = {
            field: _JsonbField(getattr(self.table.c, field), schema)
            for field, schema in field_schemas.items()}

    # TODO: docstring: améliorer la description du type des données de la liste
    @property
    def columns(self):
        """
        Provides a list of the columns made available by the instance.

        """
        columns = list(self.table.c)
        flat_fields = []
        for jsonb, flat in self.field_schemas.items():
            columns.remove(getattr(self.table.c, jsonb))
            flat_fields.extend(flat.fields)
        return columns + sorted(flat_fields, key=attrgetter('name'))

    def get_query(self):
        """
        This function computes a selectable :mod:`sqlalchemy` expression which
        provides flattened data.

        Returns:
            ~sqlalchemy.sql.expression.Select: the selectable expression

        """
        from_ = self.table

        clauses_to_join = filter(
            lambda clause: clause is not None,
            [field.select_clause for field in self.field_schemas.values()]
        )

        for clause in clauses_to_join:
            from_ = from_.join(clause, onclause=sa_true(), isouter=True)

        flattened = (
            select(self.columns)
            .select_from(from_)
        )

        return flattened


_TYPE_MAPPING = {
    'array': _Array,
    'object': _Object,
    'string': _String,
    'number': _Number,
    'integer': _Integer,
}


def _fragment_factory(name, fragment, parent, parent_array=None):
    """
    This function aims at Instantiating the correct :class:`Fragment` sub-class
    according to the type attribute of a JSON description chunk.

    Args:
        name (str): The name of the fragment
        fragment (dict): The fragment's JSON description
        parent (_Fragment):
            The parent of the :class:`_Fragment` to be instantiated
        parent_array (_Array):
            The closest :class:`_Array` parent of the :class:`_Fragment` to be
            instantiated

    Returns:
        _Fragment: The instantiated :class:`_Fragment`

    """
    assert fragment.get('type'), (
        'fragment has no "type" attribute: {}'.format(fragment))
    return _TYPE_MAPPING[fragment['type']](
        name, fragment, parent, parent_array)
