"""
A module to create a map fully_qualified_class_name -> topic name.
"""
import json
from collections import OrderedDict
from typing import Dict, List

from avro_preprocessor.avro_domain import Avro
from avro_preprocessor.avro_naming import AvroNaming
from avro_preprocessor.colored_json import ColoredJson
from avro_preprocessor.preprocessor_module import PreprocessorModule
from avro_preprocessor.schemas_container import SchemasContainer

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"


class SchemaMappingGenerator(PreprocessorModule):
    """
    Generates and saves the schema mapping.
    """

    def __init__(self, schemas: SchemasContainer):
        super().__init__(schemas)
        self.current_schema_name: str = ""
        self.schema_mapping: Dict = {}

    def process(self) -> None:
        """Process all schemas."""

        for name, schema in self.processed_schemas_iter():
            if self.schemas.paths.is_event_resource(name):
                self.schema_mapping[name] = OrderedDict((
                    ('topic', AvroNaming.get_topic(self.schemas.paths.base_namespace, name)),
                    ('value-subject', AvroNaming.get_subject_name_for_value(
                        self.schemas.paths.base_namespace, name)),
                    ('key-subject', AvroNaming.get_subject_name_for_key(
                        self.schemas.paths.base_namespace,
                        AvroNaming.get_key_fully_qualified_name(name))),
                    ('key-fqcn', AvroNaming.get_key_fully_qualified_name(name)),
                    ('partition-fields', []),
                    ('user-id-fields', [])
                ))

                self.current_schema_name = name

                self.traverse_schema(self.find_partition_keys, schema)
                self.schema_mapping[name]['partition-fields'] = \
                    sorted(self.schema_mapping[name]['partition-fields'])

                self.traverse_schema(self.find_logical_types, schema)
                self.schema_mapping[name]['user-id-fields'] = \
                    sorted(self.schema_mapping[name]['user-id-fields'])

        sorted_schema_mapping = OrderedDict(sorted(self.schema_mapping.items()))
        sorted_schema_mapping_text = \
            json.dumps(sorted_schema_mapping, indent=ColoredJson.json_indent)
        if self.schemas.verbose:
            print('Schema Mapping:')
            print(sorted_schema_mapping_text)
            print()

        self.schemas.paths.schema_mapping_path.parent.mkdir(parents=True, exist_ok=True)
        self.schemas.paths.schema_mapping_path.write_text(sorted_schema_mapping_text)

        # we now check if schemas inside the same topic have the same key
        last_key_list: List[str] = []
        last_topic = ""
        for name, mapping in sorted_schema_mapping.items():
            self.current_schema_name = name
            topic = AvroNaming.get_topic(self.schemas.paths.base_namespace, name)
            key_list = mapping['partition-fields']
            if topic == last_topic:
                if key_list != last_key_list:
                    raise ValueError(
                        "Key list must be the same inside a topic:\n"
                        "\tcurrent schema: {}, key list: {}\n"
                        "\tlast seen key list in the same topic {}:"
                        .format(name, key_list, last_key_list)
                    )

            last_topic = topic
            last_key_list = key_list

    def find_partition_keys(self, node: Avro.Node) -> None:
        """
        Finds property 'partition-field' inside schemas and saves them in the schema mapping.
        :param node: The node
        """
        if isinstance(node, OrderedDict) and Avro.PartitionKey in node:
            if node[Avro.PartitionKey]:
                self.schema_mapping[self.current_schema_name]['partition-fields'] \
                    .append(node[Avro.Name])

            # property 'partition-field' is removed from the schema anyway
            node.pop(Avro.PartitionKey)

    def find_logical_types(self, node: Avro.Node) -> None:
        """
        Finds logicalType 'user-id-fields' inside schemas and saves them in the schema mapping.
        :param node: The node
        """
        if self.ancestors and isinstance(node, OrderedDict):
            if Avro.LogicalType in node and node[Avro.LogicalType] == 'user_id':
                for ancestor in reversed(self.ancestors):
                    if Avro.Name in ancestor.node and isinstance(ancestor.node, OrderedDict):
                        field_name = ancestor.node[Avro.Name]
                        user_id_fields = \
                            self.schema_mapping[self.current_schema_name]['user-id-fields']
                        if field_name not in user_id_fields:
                            user_id_fields.append(field_name)
                        break
