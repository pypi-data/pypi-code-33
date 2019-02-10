import os
import subprocess
from hashlib import md5
from unittest import mock

from aletheia.exceptions import DependencyMissingError, UnparseableFileError
from aletheia.file_types import PngFile
from cryptography.exceptions import InvalidSignature

from ...base import EnvironmentVarGuard, TestCase


class PngTestCase(TestCase):

    def test_get_raw_data_unsigned(self):

        unsigned = os.path.join(self.DATA, "original", "test.png")
        self.assertEqual(
            md5(PngFile(unsigned, "").get_raw_data()).hexdigest(),
            "65027be33b8b7b26a95695b5dc582c32"
        )

    def test_get_raw_data_signed(self):

        signed = os.path.join(self.DATA, "signed", "test.png")
        self.assertEqual(
            md5(PngFile(signed, "").get_raw_data()).hexdigest(),
            "65027be33b8b7b26a95695b5dc582c32",
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
                PngFile("/dev/null", "").get_raw_data
            )

    @mock.patch(
        "aletheia.file_types.images.base.subprocess.Popen",
        side_effect=RuntimeError
    )
    def test_get_raw_data_runtime_error(self, *args):
        self.assertRaises(
            UnparseableFileError,
            PngFile("/dev/null", "").get_raw_data
        )

    def test_sign(self):

        path = self.copy_for_work("original", "png")

        f = PngFile(path, "")
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

        f = PngFile(self.copy_for_work("original", "png"), "")
        f.generate_signature = mock.Mock(return_value="signature")
        f.generate_payload = mock.Mock(return_value="payload")

        self.assertRaises(UnparseableFileError, f.sign, None, "example.com")

    def test_verify_no_signature(self):

        path = self.copy_for_work("original", "png")

        f = PngFile(path, "")
        self.assertRaises(UnparseableFileError, f.verify)

    def test_verify_bad_signature(self):

        cache = self.cache_public_key()
        path = self.copy_for_work("bad", "png")

        f = PngFile(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify_broken_signature(self):

        cache = self.cache_public_key()
        path = self.copy_for_work("broken", "png")

        f = PngFile(path, cache)
        self.assertRaises(InvalidSignature, f.verify)

    def test_verify_future_version(self):
        path = self.copy_for_work("future", "png")
        self.assertRaises(UnparseableFileError, PngFile(path, "").verify)

    def test_verify_file_not_found(self):
        env = EnvironmentVarGuard()
        env["PATH"] = "/tmp"
        with env:
            path = self.copy_for_work("signed", "png")
            self.assertRaises(
                DependencyMissingError,
                PngFile(path, "").verify
            )

    @mock.patch(
        "aletheia.file_types.images.base.subprocess.Popen",
        side_effect=RuntimeError
    )
    def test_verify_runtime_error(self, *args):
        path = self.copy_for_work("signed", "png")
        self.assertRaises(
            UnparseableFileError,
            PngFile(path, "").verify
        )

    def test_verify(self):

        path = self.copy_for_work("signed", "png")

        f = PngFile(path, "")
        f.verify_signature = mock.Mock(return_value=True)
        self.assertTrue(f.verify())
