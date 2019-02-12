#!python

"""
Command line entrypoint for avro preprocessor
"""

import argparse
from pathlib import Path

from avro_preprocessor.avro_paths import AvroPaths
from avro_preprocessor.preprocessor import AvroPreprocessor

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        description='Pre-processor for extended Avro schemata.')

    PARSER.add_argument('-a', '--avro-tools', dest='avro_tools', type=str, default=None)

    PARSER.add_argument('-i', '--input-path', dest='input_path', type=str, required=True)
    PARSER.add_argument('-o', '--output-path', dest='output_path', type=str, required=True)

    PARSER.add_argument('-b', '--base-namespace', dest='base_namespace', type=str, required=True)

    TYPES = PARSER.add_mutually_exclusive_group(required=True)
    TYPES.add_argument('-t', '--types-namespace', dest='types_namespace', type=str)
    TYPES.add_argument(
        '-n', '--no-types-namespace', dest='types_namespace', action='store_const', const=None)

    RPC = PARSER.add_mutually_exclusive_group(required=True)
    RPC.add_argument('-r', '--rpc-namespace', dest='rpc_namespace', type=str)
    RPC.add_argument(
        '-e', '--no-rpc-namespace', dest='rpc_namespace', action='store_const', const=None)

    PARSER.add_argument('-d', '--metadata-schema', dest='metadata_schema', type=str, default=None)

    PARSER.add_argument('-k', '--key-schema', dest='key_schema', type=str, default=None)

    PARSER.add_argument(
        '-ksns',
        '--key-subject-name-strategy',
        dest='key_subject_name_strategy',
        type=str,
        default='TopicRecordNameStrategy'
    )

    PARSER.add_argument(
        '-p', '--schema-mapping-path', dest='schema_mapping_path', type=str, default=None)

    PARSER.add_argument(
        '-ie', '--input-schema-file-extension', dest='input_schema_file_extension', type=str,
        default='exavsc')

    PARSER.add_argument(
        '-oe', '--output-schema-file-extension', dest='output_schema_file_extension', type=str,
        default='avsc')

    PARSER.add_argument('-v', '--verbose', dest='verbose', action='store_true')
    PARSER.set_defaults(verbose=False)

    PARSER.add_argument('-s', '--schema-registry', dest='schema_registry', type=str, default='')

    INDENT = PARSER.add_mutually_exclusive_group()
    INDENT.add_argument('-j', '--json_indent', dest='json_indent', type=int, default=4)
    INDENT.add_argument(
        '-c', '--json_compact', dest='json_indent', action='store_const', const=None)

    AVAILABLE_MODULES = ' '.join(AvroPreprocessor.available_preprocessing_modules.keys())
    PARSER.add_argument('-m', '--modules', dest='modules', nargs='*', default=None,
                        help='Available modules: {}'.format(AVAILABLE_MODULES))

    ARGS = PARSER.parse_args()

    SCHEMA_MAPPING_PATH = Path(ARGS.schema_mapping_path).absolute() if ARGS.schema_mapping_path \
        else Path('./schema-mapping.json')

    AVRO_PREPROCESSOR: AvroPreprocessor = AvroPreprocessor(
        AvroPaths(
            input_path=ARGS.input_path,
            output_path=ARGS.output_path,
            base_namespace=ARGS.base_namespace,
            types_namespace=ARGS.types_namespace,
            rpc_namespace=ARGS.rpc_namespace,
            metadata_schema=ARGS.metadata_schema,
            key_schema=ARGS.key_schema,
            key_subject_name_strategy=ARGS.key_subject_name_strategy,
            input_schema_file_extension=ARGS.input_schema_file_extension,
            output_schema_file_extension=ARGS.output_schema_file_extension,
            schema_mapping_path=SCHEMA_MAPPING_PATH,
            avro_tools_path=ARGS.avro_tools
        ),
        verbose=ARGS.verbose,
        json_indent=ARGS.json_indent,
        schema_registry_url=ARGS.schema_registry
    )

    AVRO_PREPROCESSOR.process(ARGS.modules)
