import unittest
from cloudshell.devices.standards.traffic.chassis.autoload_structure import TrafficGeneratorChassis, \
    AVAILABLE_SHELL_TYPES, GenericTrafficGeneratorModule, GenericTrafficGeneratorPort, GenericPowerPort


class TestTrafficGeneratorChassis(unittest.TestCase):
    def setUp(self):
        self.shell_name = "test shell name"
        self.name = "test name"
        self.unique_id = "test unique id"
        self.shell_type = AVAILABLE_SHELL_TYPES[-1]
        self.resource = TrafficGeneratorChassis(shell_name=self.shell_name,
                                                name=self.name,
                                                unique_id=self.unique_id,
                                                shell_type=self.shell_type)

    def test_generic_resource_no_shell_name(self):
        name = "test name"
        unique_id = "test unique id"
        shell_type = ""
        resource = TrafficGeneratorChassis(shell_name="",
                                           name=name,
                                           unique_id=unique_id,
                                           shell_type=shell_type)
        self.assertEqual(resource.shell_name, "")
        self.assertEqual(resource.shell_type, "")

    def test_model_name_getter(self):
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.shell_type, "Model Name"): expected_val
        }
        # act
        result = self.resource.model_name
        # verify
        self.assertEqual(result, expected_val)

    def test_model_name_setter(self):
        attr_value = "test value"
        # act
        self.resource.model_name = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.shell_type, "Model Name")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_serial_number_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.shell_type, "Serial Number"): expected_val
        }
        # act
        result = self.resource.serial_number
        # verify
        self.assertEqual(result, expected_val)

    def test_serial_number_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.serial_number = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.shell_type, "Serial Number")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_server_description_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.shell_type, "Server Description"): expected_val
        }
        # act
        result = self.resource.server_description
        # verify
        self.assertEqual(result, expected_val)

    def test_server_description_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.server_description = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.shell_type, "Server Description")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_vendor_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.shell_type, "Vendor"): expected_val
        }
        # act
        result = self.resource.vendor
        # verify
        self.assertEqual(result, expected_val)

    def test_vendor_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.vendor = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.shell_type, "Vendor")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_version_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.shell_type, "Version"): expected_val
        }
        # act
        result = self.resource.version
        # verify
        self.assertEqual(result, expected_val)

    def test_version_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.version = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.shell_type, "Version")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_raise_exception_if_unavailable_shell_type(self):
        shell_type = 'unavailable_shell_type'

        self.assertRaisesRegexp(
            Exception,
            'Unavailable shell type',
            TrafficGeneratorChassis,
            self.shell_name,
            self.name,
            self.unique_id,
            shell_type,
        )


class TestGenericTrafficGeneratorModule(unittest.TestCase):
    def setUp(self):
        self.shell_name = "test shell name"
        self.name = "test name"
        self.unique_id = "test unique id"
        self.resource = GenericTrafficGeneratorModule(shell_name=self.shell_name,
                                                      name=self.name,
                                                      unique_id=self.unique_id)

    def test_model_name_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Model Name"): expected_val
        }
        # act
        result = self.resource.model_name
        # verify
        self.assertEqual(result, expected_val)

    def test_model_name_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.model_name = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Model Name")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_version_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Version"): expected_val
        }
        # act
        result = self.resource.version
        # verify
        self.assertEqual(result, expected_val)

    def test_version_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.version = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Version")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_serial_number_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Serial Number"): expected_val
        }
        # act
        result = self.resource.serial_number
        # verify
        self.assertEqual(result, expected_val)

    def test_serial_number_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.serial_number = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Serial Number")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])


class TestGenericTrafficGeneratorPort(unittest.TestCase):
    def setUp(self):
        self.shell_name = "test shell name"
        self.name = "test name"
        self.unique_id = "test unique id"
        self.resource = GenericTrafficGeneratorPort(shell_name=self.shell_name,
                                                    name=self.name,
                                                    unique_id=self.unique_id)

    def test_media_type_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Media Type"): expected_val
        }
        # act
        result = self.resource.media_type
        # verify
        self.assertEqual(result, expected_val)

    def test_media_type_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.media_type = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Media Type")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_configured_controllers_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Configured Controllers"): expected_val
        }
        # act
        result = self.resource.configured_controllers
        # verify
        self.assertEqual(result, expected_val)

    def test_configured_controllers_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.configured_controllers = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Configured Controllers")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])


class TestGenericPowerPort(unittest.TestCase):
    def setUp(self):
        self.shell_name = "test shell name"
        self.name = "test name"
        self.unique_id = "test unique id"
        self.resource = GenericPowerPort(shell_name=self.shell_name,
                                         name=self.name,
                                         unique_id=self.unique_id)

    def test_model_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Model"): expected_val
        }
        # act
        result = self.resource.model
        # verify
        self.assertEqual(result, expected_val)

    def test_model_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.model = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Model")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_model_name_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Model Name"): expected_val
        }
        # act
        result = self.resource.model_name
        # verify
        self.assertEqual(result, expected_val)

    def test_model_name_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.model_name = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Model Name")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_serial_number_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Serial Number"): expected_val
        }
        # act
        result = self.resource.serial_number
        # verify
        self.assertEqual(result, expected_val)

    def test_serial_number_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.serial_number = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Serial Number")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_version_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Version"): expected_val
        }
        # act
        result = self.resource.version
        # verify
        self.assertEqual(result, expected_val)

    def test_version_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.version = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Version")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_port_description_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        attr_value = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Port Description"): attr_value
        }
        # act
        result = self.resource.port_description
        # verify
        self.assertEqual(result, attr_value)

    def test_port_description_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.port_description = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Port Description")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])
