#!/usr/bin/env python3
"""
Test class for the Avro classes generator.
"""

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2019, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"

import unittest
from pathlib import Path

from avro_preprocessor.avro_paths import AvroPaths

from pyavro_gen.generator import AvroGenerator
from pyavro_gen.pyavrogen_test import do_test_generated_classes

ROOT_DIR = Path(__file__).absolute().parent.parent


class AvroPreprocessorTest(unittest.TestCase):
    """
    Test class for the Avro schema extension.
    """

    @staticmethod
    def test_fixtures() -> None:
        """
        Standard test.
        """
        generator = AvroGenerator(
            AvroPaths(
                input_path=str(ROOT_DIR.joinpath('fixtures/')),
                output_path=str(ROOT_DIR.joinpath('avroclasses/')),
                input_schema_file_extension='avsc',
                base_namespace='com.jaumo.schema',
                rpc_namespace='com.jaumo.schema.rpc',
                types_namespace='com.jaumo.schema.type',
            )
        )

        generator.process()
        do_test_generated_classes(
            module=str(ROOT_DIR.joinpath('avroclasses/')),
            domain_namespace='com.jaumo.schema.domain',
            number_of_cycles=100
        )

    # @unittest.skip("fixture not available")
    @staticmethod
    def test_large_set() -> None:
        """
        Test on a large set of schemas.
        """

        generator = AvroGenerator(
            AvroPaths(
                input_path=str(ROOT_DIR.joinpath('../event_schema/build/schema/')),
                output_path=str(ROOT_DIR.joinpath('avroclasses/')),
                input_schema_file_extension='avsc',
                base_namespace='com.jaumo.message_schema',
                rpc_namespace='com.jaumo.message_schema.rpc',
                types_namespace='com.jaumo.message_schema.type',
            )
        )

        generator.process()
        do_test_generated_classes(str(ROOT_DIR.joinpath('avroclasses/')),
                                  'com.jaumo.message_schema.domain')
