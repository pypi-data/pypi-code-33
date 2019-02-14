"""
A module to collect fields from Avro schemas to generate Python classes.
"""

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2019, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"

import json
from collections import OrderedDict
from typing import List

from avro_preprocessor.avro_domain import Avro
from avro_preprocessor.preprocessor_module import PreprocessorModule

from pyavro_gen.codewriters.core import ClassWriter, Attribute, Method, EnumValueWriter, Comment, \
    Docstring, SimpleTypeClassWriter
from pyavro_gen.codewriters.containers import UnionClassWriter, ListClassWriter, MapClassWriter
from pyavro_gen.codewriters.logicaltypes import DatetimeClassWriter, DateClassWriter, \
    UUIDClassWriter
from pyavro_gen.codewriters.utils import namespace_name
from pyavro_gen.generation_classes import GENERATION_CLASSES, GenerationClassesType
from pyavro_gen.modules.avsc_schema_dependency_checker import AvscSchemaDependenciesChecker
from pyavro_gen.schema_and_classes_container import SchemaAndClassesContainer


class FieldsCollector(PreprocessorModule):  # type: ignore
    """
    Collects fields to construct classes in all schemas.
    """

    def __init__(self, schemas: SchemaAndClassesContainer) -> None:
        super().__init__(schemas)

        self.writers = schemas.output_writers

        self.prefix = schemas.output_prefix

    def process(self) -> None:
        """Process all schemas."""

        for _, schema in self.processed_schemas_iter():
            self.traverse_schema(self.fill_fields_of_node, schema)

    def fill_fields_of_node(self, node: Avro.Node) -> None:
        """
        Find fields in an Avro Node.
        :param node: The node
        """
        if not isinstance(node, OrderedDict):
            return

        if Avro.Protocol in node:
            self.fill_fields_of_protocol_record(node)

        elif Avro.Name in node and (Avro.Fields in node or Avro.Symbols in node):
            self.fill_fields_of_standard_record(node)

    # pylint: disable=R0914,R0912
    def fill_fields_of_protocol_record(self, node: Avro.Node) -> None:
        """
        Fills attributes, methods, and documentation of a ClassWriter for Avro protocol records.
        :param node: The Avro node
        """
        writer = self.get_class_writer_from_name(
            self.current_schema_name, GenerationClassesType.RPC_CLASS
        )

        if Avro.Doc in node:
            writer.doc = Docstring(node[Avro.Doc])

        for message_name, message in node[Avro.Messages].items():
            request_fields: List[Attribute] = []
            for field in message[Avro.Request]:
                avro_type = field[Avro.Type]
                field_type = self.get_class_writer_for_node(avro_type)
                field_type.prefix = self.prefix
                request_field = Attribute(field[Avro.Name], field_type)
                if Avro.Doc in field:
                    request_field.doc = Docstring(field[Avro.Doc])
                request_fields.append(request_field)

            doc = message.get(Avro.Doc, None)

            response = message[Avro.Response]
            if isinstance(response, OrderedDict):
                if Avro.Namespace in response:
                    response_fully_qualified_name = \
                        response[Avro.Namespace] + '.' + response[Avro.Name]
                else:
                    response_fully_qualified_name = \
                        namespace_name(self.current_schema_name) + '.' + response[Avro.Name]

            else:
                # response is string
                if response == 'null' or Avro.OneWay:
                    response_fully_qualified_name = 'None'
                elif '.' in response[Avro.Name]:
                    response_fully_qualified_name = response[Avro.Name]
                else:
                    raise TypeError(f'Type unsupported: {response}')

            errors = message.get(Avro.Errors)
            if errors:
                errors_writers = []
                for error in errors:
                    if '.' in error:
                        err = self.get_class_writer_from_name(error)
                    else:
                        err = self.get_class_writer_from_name(
                            f'{namespace_name(self.current_schema_name)}.{error}')
                    errors_writers.append(err)
            else:
                errors_writers = []

            writer.methods.append(Method(
                name=message_name,
                parameters=request_fields,
                return_type=self.get_class_writer_from_name(response_fully_qualified_name),
                doc=Docstring(doc),
                errors=errors_writers
            ))

    def fill_fields_of_standard_record(self, node: Avro.Node) -> None:
        """
        Fills attributes and documentation of a ClassWriter for Avro records.
        :param node: The Avro node
        """
        if Avro.Namespace in node:
            fully_qualified_name = node[Avro.Namespace] + '.' + node[Avro.Name]
        elif '.' in node[Avro.Name]:
            fully_qualified_name = node[Avro.Name]
        else:
            fully_qualified_name = \
                namespace_name(self.current_schema_name) + '.' + node[Avro.Name]

        writer = self.get_class_writer_from_name(fully_qualified_name)

        if not writer.attributes:
            if Avro.Fields in node:
                for field in node[Avro.Fields]:
                    avro_type = field[Avro.Type]
                    field_type = self.get_class_writer_for_node(avro_type)
                    field_type.prefix = self.prefix
                    attribute = Attribute(field[Avro.Name], field_type)
                    if Avro.Doc in field:
                        attribute.doc = Docstring(field[Avro.Doc])
                    writer.attributes.append(attribute)
            else:
                fully_qualified_name = writer.namespace + '.' + writer.name
                writer = self.get_class_writer_from_name(
                    fully_qualified_name, GenerationClassesType.ENUM_CLASS)

                for field in node[Avro.Symbols]:
                    writer.attributes.append(Attribute(field, EnumValueWriter(field)))

            writer.attributes.append(
                Attribute(
                    name='_schema',
                    type=GENERATION_CLASSES[GenerationClassesType.CLASS_VARIABLE_CLASS](
                        SimpleTypeClassWriter('str')),
                    doc=Docstring('The Avro Schema associated to this class'),
                    default_value=f'"""{json.dumps(node, indent=4)}"""'
                )
            )

        if Avro.Doc in node:
            writer.doc = Docstring(node[Avro.Doc])

    def get_class_writer_from_name(
            self,
            fully_qualified_name: str,
            writer_type: GenerationClassesType = GenerationClassesType.RECORD_CLASS
    ) -> ClassWriter:
        """
        Returns a Class writer for the record in input. If it not exists, this method creates one.

        :param fully_qualified_name: The fully qualified name of the record
        :param writer_type: The type of writer
        """
        schemas: SchemaAndClassesContainer = self.schemas
        record_dependencies: 'OrderedDict[str, List[str]]' = \
            schemas.modules[AvscSchemaDependenciesChecker.__name__].record_dependencies

        if fully_qualified_name in record_dependencies:
            if fully_qualified_name in self.writers:
                if isinstance(self.writers[fully_qualified_name], GENERATION_CLASSES[writer_type]):
                    return self.writers[fully_qualified_name]
                # if it is not, we create and store a new one of the requested type

            writer: ClassWriter = GENERATION_CLASSES[writer_type](
                fully_qualified_name,
                prefix=schemas.output_prefix
            )

            writer.external_dependencies = record_dependencies[fully_qualified_name]
            self.writers[fully_qualified_name] = writer
            return writer

        return SimpleTypeClassWriter(fully_qualified_name)

    # pylint: disable=R0915,R0912
    def get_class_writer_for_node(self, avro_type: Avro.Node) -> ClassWriter:
        """
        Recursively returns an appropriate class writer given an Avro node
        :param avro_type: An Avro Node
        """

        # to make mypy happy
        field_type: ClassWriter

        if avro_type == 'boolean':
            field_type = SimpleTypeClassWriter('bool')
        elif avro_type == 'string':
            field_type = SimpleTypeClassWriter('str')
        elif avro_type == 'int':
            field_type = SimpleTypeClassWriter('int')
        elif avro_type == 'long':
            field_type = SimpleTypeClassWriter('int')
        elif avro_type == 'float':
            field_type = SimpleTypeClassWriter('float')
        elif avro_type == 'double':
            field_type = SimpleTypeClassWriter('float')
        elif avro_type == 'null':
            field_type = SimpleTypeClassWriter('None')
        elif isinstance(avro_type, str):
            if '.' in avro_type:
                field_type = self.get_class_writer_from_name(avro_type)
            else:
                raise ValueError(f'Type unsupported: {str(avro_type)}')

        elif isinstance(avro_type, list):
            field_type = UnionClassWriter([self.get_class_writer_for_node(t) for t in avro_type])
        elif isinstance(avro_type, OrderedDict):
            if Avro.Type in avro_type:
                if avro_type[Avro.Type] in [Avro.Record, Avro.Enum]:
                    if Avro.Namespace in avro_type:
                        name = avro_type[Avro.Namespace] + '.' + avro_type[Avro.Name]
                    else:
                        if '.' in avro_type[Avro.Name]:
                            name = avro_type[Avro.Name]
                        else:
                            name = namespace_name(self.current_schema_name) \
                                   + '.' + avro_type[Avro.Name]
                    field_type = self.get_class_writer_from_name(name)
                elif avro_type[Avro.Type] == Avro.Array:
                    field_type = ListClassWriter(
                        self.get_class_writer_for_node(avro_type[Avro.Items]))
                elif avro_type[Avro.Type] == Avro.Map:
                    field_type = MapClassWriter(
                        self.get_class_writer_for_node(avro_type[Avro.Values]))
                elif Avro.LogicalType in avro_type:
                    if avro_type[Avro.LogicalType] == 'timestamp-micros':
                        field_type = DatetimeClassWriter()
                    elif avro_type[Avro.LogicalType] == 'timestamp-millis':
                        field_type = DatetimeClassWriter('milliseconds')
                    elif avro_type[Avro.LogicalType] == 'date':
                        field_type = DateClassWriter()
                    elif avro_type[Avro.LogicalType] == 'uuid':
                        field_type = UUIDClassWriter()
                    else:
                        field_type = self.get_class_writer_for_node(avro_type[Avro.Type])
                    field_type.comment = Comment(f"logicalType: {avro_type[Avro.LogicalType]}")

                else:
                    raise TypeError(f'Type unsupported: {str(avro_type)}')
            else:
                raise TypeError(f'Type unsupported: {str(avro_type)}')
        else:
            raise TypeError(f'Type unsupported: {str(avro_type)}')

        return field_type
