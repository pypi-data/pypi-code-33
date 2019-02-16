from unittest import mock
import os
from hashlib import md5
from unittest import mock

from aletheia.exceptions import NotJsonObjectError, UnparseableFileError
from aletheia.file_types import JsonFile
from cryptography.exceptions import InvalidSignature

from ...base import TestCase


class JsonTestCase(TestCase):

    def test_get_raw_data(self):
        unsigned = os.path.join(self.DATA, "original", "test.json")
        self.assertEqual(
            md5(JsonFile(unsigned, "").get_raw_data()).hexdigest(),
            "f9cfeb28eeb0f628b1f347a80e1823b4"
        )

        signed = os.path.join(self.DATA, "signed", "test.json")
        self.assertEqual(
            md5(JsonFile(signed, "").get_raw_data()).hexdigest(),
            "f9cfeb28eeb0f628b1f347a80e1823b4",
            "Modifying the metadata should have no effect on the raw data"
        )

    def test_sign(self):

        path = self.copy_for_work("original", "json")

        f = JsonFile(path, "")
        f.generate_signature = mock.Mock(return_value="signature")
        f.generate_payload = mock.Mock(return_value="payload")
        f.sign(None, "example.com")

        with open(path) as f:
            self.assertIn("__aletheia__", f.read())

    def test_verify_no_signature(self):

        path = self.copy_for_work("original", "json")

        f = JsonFile(path, "")
        self.assertRaises(UnparseableFileError, f.verify)

    def test_verify_bad_signature(self):

        cache = self.cache_public_key()
        path = self.copy_for_work("bad", "json")

        f = JsonFile(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify_broken_signature(self):

        cache = self.cache_public_key()
        path = self.copy_for_work("broken", "json")

        f = JsonFile(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify(self):

        path = self.copy_for_work("signed", "json")

        f = JsonFile(path, "")
        f.verify_signature = mock.Mock(return_value=True)
        self.assertTrue(f.verify())

    def test_verify_future_version(self):
        path = self.copy_for_work("future", "json")
        self.assertRaises(UnparseableFileError, JsonFile(path, "").verify)

    @mock.patch("aletheia.file_types.documents.json.JsonFile._get_json")
    def test_get_raw_data_only_run_once(self, m):
        m.return_value = {"x": "y"}
        f = JsonFile("/dev/null", "")
        f.get_raw_data()
        self.assertEqual(m.call_count, 1)
        f.get_raw_data()
        self.assertEqual(m.call_count, 1)

    @mock.patch("aletheia.file_types.documents.json.JsonFile._get_json")
    def test_get_raw_data_not_dict(self, m):
        m.return_value = [1, 2, 3]
        f = JsonFile("/dev/null", "")
        self.assertRaises(NotJsonObjectError, f.get_raw_data)

    def test__get_json_not_json(self):
        path = self.copy_for_work("original", "html")
        f = JsonFile(path, "")
        self.assertRaises(UnparseableFileError, f._get_json)
