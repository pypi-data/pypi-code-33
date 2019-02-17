import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pelops.myconfigtools import read_config, validate_config
from hippodamia_agent.monitoringagent import MonitoringAgent


class TestValidateConfig(unittest.TestCase):
    def test_validate_config(self):
        filename = "config.yaml"
        if not os.getcwd().endswith("tests_unit"):
            filename = "tests_unit/"+filename
        config = read_config(filename)
        k, s = MonitoringAgent.get_schema()
        schema = {k: s}
        validation_result = validate_config(config, schema)

        self.assertIsNone(validation_result)


if __name__ == '__main__':
    unittest.main()
