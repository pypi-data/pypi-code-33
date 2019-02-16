from aletheia.exceptions import (
    AletheiaException,
    DependencyMissingError,
    NotJsonObjectError,
    PrivateKeyNotDefinedError,
    PublicKeyNotExistsError,
    UnacceptableLocationError,
    UnknownFileTypeError,
    UnparseableFileError,
    UnrecognisedKeyError
)

from .base import TestCase


class AletheiaExceptionTestCase(TestCase):

    def test_base(self):
        self._test_exception(AletheiaException, "unknown error")

    def test_unknown_filetype_error(self):
        self._test_exception(UnknownFileTypeError, "doesn't recognise")

    def test_private_key_not_exists_error(self):
        self._test_exception(PrivateKeyNotDefinedError, "without a private key")

    def test_public_key_not_exists_error(self):
        self._test_exception(PublicKeyNotExistsError, "does not contain")

    def test_unparseable_file_error(self):
        self._test_exception(UnparseableFileError, "can't find a signature")

    def test_dependency_missing_error(self):
        self._test_exception(DependencyMissingError, "dependency appears to be missing")

    def test_unacceptable_location_error(self):
        self._test_exception(UnacceptableLocationError, "does not appear to be valid")

    def test_unrecognised_key_error(self):
        self._test_exception(UnrecognisedKeyError, "could not be recognised")

    def test_not_json_object_error(self):
        self._test_exception(NotJsonObjectError, "kind of JSON file")

    def _test_exception(self, klass, message):

        try:
            raise klass()
        except klass as e:
            self.assertIn(message, str(e))

        try:
            raise klass("[[ test ]]")
        except klass as e:
            self.assertEqual("[[ test ]]", str(e))
