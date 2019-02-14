import unittest

from cloudshell.devices.runners.interfaces.state_runner_interface import StateOperationsInterface


class TestCliCliHandlerInterface(unittest.TestCase):
    def setUp(self):
        class TestedClass(StateOperationsInterface):
            pass
        self.tested_class = TestedClass

    def test_abstract_methods(self):
        """Check that instance can't be instantiated without implementation of all abstract methods"""
        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass with "
                                                "abstract methods health_check, shutdown"):
            self.tested_class()

    def test_abstract_methods_do_nothing(self):
        class TestedClass(StateOperationsInterface):
            def shutdown(self):
                return super(TestedClass, self).shutdown()

            def health_check(self):
                return super(TestedClass, self).health_check()

        tested_class = TestedClass()

        self.assertIsNone(tested_class.health_check())
        self.assertIsNone(tested_class.shutdown())
