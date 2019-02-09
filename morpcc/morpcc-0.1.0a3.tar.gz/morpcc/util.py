import colander
from morpfw.crud.util import dataclass_get_type, dataclass_check_type
import dataclasses
from datetime import datetime, date
from morpfw.interfaces import ISchema


def dataclass_field_to_colander_schemanode(
        prop: dataclasses.Field, oid_prefix='deformField') -> colander.SchemaNode:

    t = dataclass_get_type(prop)
    if t['type'] == date:
        return colander.SchemaNode(typ=colander.Date(),
                                   name=prop.name,
                                   oid='%s-%s' % (oid_prefix, prop.name),
                                   missing=colander.required if t['required'] else colander.drop)
    if t['type'] == datetime:
        return colander.SchemaNode(typ=colander.DateTime(),
                                   name=prop.name,
                                   oid='%s-%s' % (oid_prefix, prop.name),
                                   missing=colander.required if t['required'] else colander.drop)
    if t['type'] == str:
        return colander.SchemaNode(typ=colander.String(),
                                   name=prop.name,
                                   oid='%s-%s' % (oid_prefix, prop.name),
                                   missing=colander.required if t['required'] else colander.drop)
    if t['type'] == int:
        return colander.SchemaNode(typ=colander.Integer(),
                                   name=prop.name,
                                   oid='%s-%s' % (oid_prefix, prop.name),
                                   missing=colander.required if t['required'] else colander.drop)
    if t['type'] == float:
        return colander.SchemaNode(typ=colander.Float(),
                                   name=prop.name,
                                   oid='%s-%s' % (oid_prefix, prop.name),
                                   missing=colander.required if t['required'] else colander.drop)
    if t['type'] == bool:
        return colander.SchemaNode(typ=colander.Boolean(),
                                   name=prop.name,
                                   oid='%s-%s' % (oid_prefix, prop.name),
                                   missing=colander.required if t['required'] else colander.drop)

    if dataclass_check_type(prop, ISchema):
        subtype = dataclass_to_colander(
            t['type'], colander_schema_type=colander.MappingSchema)

        return subtype()
    if t['type'] == dict:
        return colander.SchemaNode(typ=colander.Mapping(),
                                   name=prop.name,
                                   oid='%s-%s' % (oid_prefix, prop.name),
                                   missing=colander.required if t['required'] else colander.drop)

    if t['type'] == list:
        return colander.SchemaNode(
            typ=colander.List(),
            name=prop.name,
            oid='%s-%s' % (oid_prefix, prop.name),
            missing=colander.required if t['required'] else colander.drop)

    raise KeyError(prop)


def dataclass_to_colander(schema,
                          include_fields=None,
                          exclude_fields=None,
                          colander_schema_type=colander.MappingSchema,
                          oid_prefix='deformField'):
    # output colander schema from dataclass schema
    attrs = {}

    include_fields = include_fields or []
    exclude_fields = exclude_fields or []

    if include_fields:
        for attr, prop in schema.__dataclass_fields__.items():
            if prop.name in include_fields and prop.name not in exclude_fields:
                prop = dataclass_field_to_colander_schemanode(
                    prop, oid_prefix=oid_prefix)
                attrs[attr] = prop
    else:
        for attr, prop in schema.__dataclass_fields__.items():
            if prop.name not in exclude_fields:
                prop = dataclass_field_to_colander_schemanode(
                    prop, oid_prefix=oid_prefix)
                attrs[attr] = prop

    Schema = type("Schema", (colander_schema_type, ), attrs)

    return Schema
