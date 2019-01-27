from app import current_app as app
from tests.unittests.utils.base_test_case import BaseTestCase
from app.api.helpers.utilities import dasherize


class TestUtilitiesHelperValidation(BaseTestCase):

    def test_dasherize(self):
        """Check UtilitiesHelper: dasherize"""
        with app.test_request_context():
            field = "starts_at"
            dasherized_field = "starts-at"
            result = dasherize(field)
            self.assertEqual(result, dasherized_field)
