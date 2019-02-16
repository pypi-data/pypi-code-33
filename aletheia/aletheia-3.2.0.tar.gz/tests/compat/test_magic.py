from unittest import TestCase, mock

from aletheia.compat.magic import get_mimetype


class MagicTestCase(TestCase):
    """
    These are tough to test without explicitly installing the different
    modules, so these mocks are the best I could do.
    """

    python_magic = mock.Mock(spec=object)
    python_magic.from_file = mock.Mock(return_value="test")

    file_magic = mock.Mock(spec=object)
    file_magic.detect_from_filename = mock.Mock()
    file_magic.detect_from_filename.return_value.mime_type = "test2"

    @mock.patch("aletheia.compat.magic.magic", new=python_magic)
    def test_get_mimetype_python_magic(self):
        self.assertEqual(get_mimetype(""), "test")

    @mock.patch("aletheia.compat.magic.magic", new=file_magic)
    def test_get_mimetype_file_magic(self):
        self.assertEqual(get_mimetype(""), "test2")
