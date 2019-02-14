import unittest

import mock

from cloudshell.devices.flows.snmp_action_flows import BaseSnmpFlow, AutoloadFlow


class TestBaseSnmpFlow(unittest.TestCase):
    def test_init(self):
        """Check that __init__ method will set up object with correct params"""
        snmp_handler = mock.MagicMock()
        logger = mock.MagicMock()
        # act
        snmp_flow = BaseSnmpFlow(snmp_handler=snmp_handler, logger=logger)
        # verify
        self.assertEqual(snmp_flow._snmp_handler, snmp_handler)
        self.assertEqual(snmp_flow._logger, logger)


class TestAutoloadFlow(unittest.TestCase):
    def test_execute_flow_does_nothing(self):
        class TestedClass(AutoloadFlow):
            def execute_flow(self, supported_os, shell_name, shell_type, resource_name):
                return super(TestedClass, self).execute_flow(
                    supported_os, shell_name, shell_type, resource_name)

        snmp_handler = mock.MagicMock()
        logger = mock.MagicMock()
        tested_class = TestedClass(snmp_handler, logger)

        supported_os = mock.MagicMock()
        shell_name = mock.MagicMock()
        shell_type = mock.MagicMock()
        resource_name = mock.MagicMock()

        self.assertIsNone(tested_class.execute_flow(
            supported_os, shell_name, shell_type, resource_name))
