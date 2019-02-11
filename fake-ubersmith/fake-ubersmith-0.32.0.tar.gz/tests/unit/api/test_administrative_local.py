import json
import unittest
from unittest.mock import patch, Mock

from flask import Flask

from fake_ubersmith.api.administrative_local import AdministrativeLocal


class TestAdministrativeLocal(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)

        self.admin = AdministrativeLocal()
        self.admin.hook_to(self.app)

    def test_status_works(self):
        with self.app.test_client() as c:
            resp = c.get('/status')

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')).get('data'),
            "Service is running"
        )

    def test_shutdown_works(self):
        patch_path = 'fake_ubersmith.api.administrative_local.request'
        environ_path = 'werkzeug.server.shutdown'

        with patch(patch_path, Mock(environ={environ_path: Mock()})) as m:
            with self.app.test_client() as c:
                resp = c.get('/__shutdown')

            self.assertTrue(m.environ.get('werkzeug.server.shutdown').called)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(
                json.loads(resp.data.decode('utf-8')).get('data'),
                "Shutting down server..."
            )

    def test_shutdown_raises(self):
        patch_path = 'fake_ubersmith.api.administrative_local.request'

        with patch(patch_path, Mock(environ={})):
            with self.assertRaises(RuntimeError):
                self.admin.shutdown()
