import unittest

import mock

from cloudshell.devices.runners.interfaces.configuration_runner_interface import ConfigurationOperationsInterface


class TestCliCliHandlerInterface(unittest.TestCase):
    def setUp(self):
        class TestedClass(ConfigurationOperationsInterface):
            pass

        self.tested_class = TestedClass

    def test_abstract_methods(self):
        """Check that instance can't be instantiated without implementation of all abstract methods"""
        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass with "
                                                "abstract methods orchestration_restore, orchestration_save, "
                                                "restore, save"):
            self.tested_class()

    def test_abstract_methods_do_nothing(self):
        class TestedClass(ConfigurationOperationsInterface):
            def orchestration_save(self, *args, **kwargs):
                return super(TestedClass, self).orchestration_save(*args, **kwargs)

            def orchestration_restore(self, *args, **kwargs):
                return super(TestedClass, self).orchestration_restore(*args, **kwargs)

            def restore(self, *args, **kwargs):
                return super(TestedClass, self).restore(*args, **kwargs)

            def save(self, *args, **kwargs):
                return super(TestedClass, self).save(*args, **kwargs)

        tested_class = TestedClass()
        path = mock.MagicMock()
        configuration_type = mock.MagicMock()
        restore_method = mock.MagicMock()
        saved_artificat_info = mock.MagicMock()

        self.assertIsNone(tested_class.save(path, configuration_type))
        self.assertIsNone(tested_class.restore(path, configuration_type, restore_method))
        self.assertIsNone(tested_class.orchestration_save())
        self.assertIsNone(tested_class.orchestration_restore(saved_artificat_info))
