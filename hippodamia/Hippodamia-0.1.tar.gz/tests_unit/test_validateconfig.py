import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pelops.myconfigtools import read_config, validate_config
from hippodamia.monitoringservice import Monitoringservice


class TestValidateConfig(unittest.TestCase):
    def test_validate_config(self):
        config = read_config(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))+"/tests_unit/config.yaml")
        validation_result = validate_config(config, Monitoringservice.get_schema())
        self.assertIsNone(validation_result)


if __name__ == '__main__':
    unittest.main()
