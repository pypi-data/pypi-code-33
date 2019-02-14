import unittest

import mock

from cloudshell.devices.standards.traffic.virtual.blade.configuration_attributes_structure import \
    TrafficGeneratorVBladeResource


class TestTrafficGeneratorVBladeResource(unittest.TestCase):
    def test_create_resource_from_context(self):
        shell_name = 'test shell name'
        context = mock.MagicMock()

        result = TrafficGeneratorVBladeResource.from_context(context, shell_name=shell_name)

        self.assertIsInstance(result, TrafficGeneratorVBladeResource)

    def test_no_shell_name(self):
        shell_name = ''

        resource = TrafficGeneratorVBladeResource(shell_name=shell_name)

        self.assertEqual('', resource.namespace_prefix)
        self.assertEqual('', resource.shell_type)
