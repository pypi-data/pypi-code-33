import unittest

import mock

from cloudshell.devices.standards.traffic.virtual.chassis.configuration_attributes_structure import \
    TrafficGeneratorVChassisResource


class TestTrafficGeneratorVBladeResource(unittest.TestCase):
    def setUp(self):
        self.shell_name = 'test shell name'
        self.resource = TrafficGeneratorVChassisResource(shell_name=self.shell_name)

    def test_create_resource_from_context(self):
        shell_name = 'test shell name'
        context = mock.MagicMock()

        result = TrafficGeneratorVChassisResource.from_context(context, shell_name=shell_name)

        self.assertIsInstance(result, TrafficGeneratorVChassisResource)

    def test_no_shell_name(self):
        shell_name = ''

        resource = TrafficGeneratorVChassisResource(shell_name=shell_name)

        self.assertEqual('', resource.namespace_prefix)
        self.assertEqual('', resource.shell_type)

    def test_user(self):
        expected_val = 'test value'
        self.resource.attributes = {
            '{}{}'.format(self.resource.namespace_prefix, 'User'): expected_val
        }

        self.assertEqual(expected_val, self.resource.user)

    def test_password(self):
        expected_val = 'test value'
        self.resource.attributes = {
            '{}{}'.format(self.resource.namespace_prefix, 'Password'): expected_val
        }

        self.assertEqual(expected_val, self.resource.password)

    def test_license_server(self):
        expected_val = 'test value'
        self.resource.attributes = {
            '{}{}'.format(self.resource.shell_type, 'License Server'): expected_val
        }

        self.assertEqual(expected_val, self.resource.license_server)

    def test_cli_connection_type(self):
        expected_val = 'test value'
        self.resource.attributes = {
            '{}{}'.format(self.resource.namespace_prefix, 'CLI Connection Type'): expected_val
        }

        self.assertEqual(expected_val, self.resource.cli_connection_type)

    def test_cli_tcp_port(self):
        expected_val = 'test value'
        self.resource.attributes = {
            '{}{}'.format(self.resource.namespace_prefix, 'CLI TCP Port'): expected_val
        }

        self.assertEqual(expected_val, self.resource.cli_tcp_port)

    def test_sessions_concurrency_limit(self):
        expected_val = 'test value'
        self.resource.attributes = {
            '{}{}'.format(self.resource.namespace_prefix, 'Sessions Concurrency Limit'):
                expected_val
        }

        self.assertEqual(expected_val, self.resource.sessions_concurrency_limit)
