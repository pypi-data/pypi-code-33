from unittest import TestCase

from cloudshell.tg.breaking_point.rest_api.rest_requests import RestRequests


class TestRestRequests(TestCase):
    def setUp(self):
        class TestedClass(RestRequests):
            pass

        self._tested_class = TestedClass

    def test_init_abstract(self):
        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass"):
            self._tested_class()
