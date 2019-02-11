import json
import unittest


class ApiTestBase(unittest.TestCase):
    def _assert_success(self, response, content):
        self.assertEqual(response.status_code, 200, response.data.decode('utf-8'))
        self.assertEqual(
            json.loads(response.data.decode('utf-8')),
            {
                "error_code": None,
                "error_message": "",
                "status": True,
                "data": content
            }
        )

    def _assert_error(self, response, code, message, content):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.data.decode('utf-8')),
            {
                "error_code": code,
                "error_message": message,
                "status": False,
                "data": content
            }
        )
