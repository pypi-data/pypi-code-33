"""
Custom fields for storing RDF primitives.

Based on http://blog.elsdoerfer.name/2008/01/08/fuzzydates-or-one-django-model-field-multiple-database-columns/
"""  # noqa: E501
from django.db import models
from rdflib.graph import Graph
from rdflib.term import BNode, URIRef, Literal


class LiteralField(models.TextField):
    """
    Custom field for storing literals.
    """

    description = "Field for storing Literals, including their type and language"  # noqa: 501

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value

        parts = value.split('^^')
        if len(parts) != 3:
            raise ValueError("Wrong value: {}".format(value))
        return Literal(parts[0], parts[1] or None, parts[2] or None)

    def to_python(self, value):
        if isinstance(value, Literal):
            return value

        if value is None:
            return value

        parts = value.split('^^')
        if len(parts) != 3:
            raise ValueError("Wrong value: {0}".format(value))
        return Literal(parts[0], parts[1] or None, parts[2] or None)

    def get_prep_value(self, value):
        if not isinstance(value, Literal):
            raise TypeError("Value {} has the wrong type: {}".format(
                value, value.__class__)
            )

        return (
            str(value) +
            "^^" +
            str(value.language or '') +
            "^^" +
            str(value.datatype or '')
        )


def deserialize_uri(value):
    """
    Deserialize a representation of a BNode or URIRef.
    """
    if isinstance(value, BNode):
        return value
    if isinstance(value, URIRef):
        return value
    if not value:
        return None
    if not isinstance(value, str):
        raise ValueError("Cannot create URI from {} of type {}".format(
            value, value.__class__)
        )
    if value.startswith("_:"):
        return BNode(value[2:])
    return URIRef(value)


def serialize_uri(value):
    """
    Serialize a BNode or URIRef.
    """
    if isinstance(value, BNode):
        return value.n3()
    if isinstance(value, URIRef):
        return str(value)
    # neccessary for migrations in some db backends (e.g. postgres)
    if value is None:
        return None
    raise ValueError("Cannot get prepvalue for {} of type {}".format(
        value, value.__class__)
    )


class URIField(models.CharField):
    """
    Custom field for storing URIRefs and BNodes.

    URIRefs are stored as themselves; BNodes are stored in their Notation3 serialization.
    """  # noqa: E501

    description = "Field for storing URIRefs and BNodes."

    def __init__(self, *args, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 500
        super(URIField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        return deserialize_uri(value)

    def to_python(self, value):
        return deserialize_uri(value)

    def get_prep_value(self, value):
        return serialize_uri(value)


class GraphReferenceField(models.CharField):
    """
    Custom field for storing graph references.
    """

    description = "Field for storing references to Graphs"

    def from_db_value(self, value, expression, connection):
        if isinstance(value, Graph):
            return value.identifier

        return deserialize_uri(value)

    def to_python(self, value):
        if isinstance(value, Graph):
            return value.identifier

        return deserialize_uri(value)

    def get_prep_value(self, value):
        if isinstance(value, Graph):
            return serialize_uri(value.identifier)

        return serialize_uri(value)
