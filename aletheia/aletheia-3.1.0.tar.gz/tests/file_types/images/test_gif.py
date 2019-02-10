import os
import subprocess
from hashlib import md5
from unittest import mock

from aletheia.exceptions import DependencyMissingError, UnparseableFileError
from aletheia.file_types import GifFile
from cryptography.exceptions import InvalidSignature

from ...base import EnvironmentVarGuard, TestCase


class GifTestCase(TestCase):

    def test_get_raw_data_unsigned(self):
        unsigned = os.path.join(self.DATA, "original", "test.gif")
        self.assertEqual(
            md5(GifFile(unsigned, "").get_raw_data()).hexdigest(),
            "aa41bc501a8c9f8532914524c0b046b6"
        )

    def test_get_raw_data_signed(self):
        signed = os.path.join(self.DATA, "signed", "test.gif")
        self.assertEqual(
            md5(GifFile(signed, "").get_raw_data()).hexdigest(),
            "aa41bc501a8c9f8532914524c0b046b6",
            "Modifying the metadata should have no effect on the raw data"
        )

    def test_get_raw_data_not_exists(self):
        """
        We're testing for the case where attempting to call exiftool results
        in a FileNotFoundError, which means that we have to make sure that it
        doesn't show up in the PATH even if it's installed.
        """
        env = EnvironmentVarGuard()
        env["PATH"] = "/tmp"
        with env:
            self.assertRaises(
                DependencyMissingError,
                GifFile("/dev/null", "").get_raw_data
            )

    @mock.patch(
        "aletheia.file_types.images.base.subprocess.Popen",
        side_effect=RuntimeError
    )
    def test_get_raw_data_runtime_error(self, *args):
        self.assertRaises(
            UnparseableFileError,
            GifFile("/dev/null", "").get_raw_data
        )

    def test_sign(self):

        path = self.copy_for_work("original", "gif")

        f = GifFile(path, "")
        f.generate_signature = mock.Mock(return_value="signature")
        f.generate_payload = mock.Mock(return_value="payload")
        f.sign(None, "example.com")

        self.assertIn(
            "payload",
            subprocess.Popen(
                ("exiftool", path),
                stdout=subprocess.PIPE
            ).stdout.read().decode()
        )

    @mock.patch(
        "aletheia.file_types.images.base.subprocess.call",
        side_effect=RuntimeError
    )
    def test_sign_runtime_error(self, *args):

        f = GifFile(self.copy_for_work("original", "png"), "")
        f.generate_signature = mock.Mock(return_value="signature")
        f.generate_payload = mock.Mock(return_value="payload")

        self.assertRaises(UnparseableFileError, f.sign, None, "example.com")

    def test_verify_no_signature(self):

        path = self.copy_for_work("original", "gif")

        f = GifFile(path, "")
        self.assertRaises(UnparseableFileError, f.verify)

    def test_verify_bad_signature(self):

        cache = self.cache_public_key()
        path = self.copy_for_work("bad", "gif")

        f = GifFile(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify_broken_signature(self):

        cache = self.cache_public_key()
        path = self.copy_for_work("broken", "gif")

        f = GifFile(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify_future_version(self):
        path = self.copy_for_work("future", "gif")
        self.assertRaises(UnparseableFileError, GifFile(path, "").verify)

    def test_verify_file_not_found(self):
        env = EnvironmentVarGuard()
        env["PATH"] = "/tmp"
        with env:
            path = self.copy_for_work("signed", "png")
            self.assertRaises(
                DependencyMissingError,
                GifFile(path, "").verify
            )

    @mock.patch(
        "aletheia.file_types.images.base.subprocess.Popen",
        side_effect=RuntimeError
    )
    def test_verify_runtime_error(self, *args):
        path = self.copy_for_work("signed", "png")
        self.assertRaises(
            UnparseableFileError,
            GifFile(path, "").verify
        )

    def test_verify(self):

        path = self.copy_for_work("signed", "gif")

        f = GifFile(path, "")
        f.verify_signature = mock.Mock(return_value=True)
        self.assertTrue(f.verify())
