#!/usr/bin/env python

"""
Command line entrypoint for pyavro-gen
"""

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2019, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"

import argparse

from avro_preprocessor.avro_paths import AvroPaths
from pyavro_gen.generator import AvroGenerator

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        description='A typed class generator for Avro Schemata.')

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

    PARSER.add_argument(
        '-ie', '--input-schema-file-extension', dest='input_schema_file_extension', type=str,
        default='avsc')

    PARSER.add_argument('-v', '--verbose', dest='verbose', action='store_true')
    PARSER.set_defaults(verbose=False)

    # INDENT = PARSER.add_mutually_exclusive_group()
    # INDENT.add_argument('-ci', '--classes_indent', dest='classes_indent', type=int, default=4)

    AVAILABLE_MODULES = ' '.join(AvroGenerator.available_preprocessing_modules.keys())
    PARSER.add_argument('-m', '--modules', dest='modules', nargs='*', default=None,
                        help='Available modules: {}'.format(AVAILABLE_MODULES))

    ARGS = PARSER.parse_args()

    AVRO_GENERATOR: AvroGenerator = AvroGenerator(
        AvroPaths(
            input_path=ARGS.input_path,
            output_path=ARGS.output_path,
            base_namespace=ARGS.base_namespace,
            types_namespace=ARGS.types_namespace,
            rpc_namespace=ARGS.rpc_namespace,
            input_schema_file_extension=ARGS.input_schema_file_extension,
        ),
        verbose=ARGS.verbose,
        # classes_indent=ARGS.classes_indent,
    )

    AVRO_GENERATOR.process(ARGS.modules)
