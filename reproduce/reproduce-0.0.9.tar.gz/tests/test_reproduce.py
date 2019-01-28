"""Tests for taskgraph."""
import os
import shutil
import tempfile
import unittest
import logging
import hashlib


logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def _make_file(target_path, data):
    """Make a file containing `data`."""
    with open(target_path, 'w') as target_file:
        target_file.write(data)

def _touch_file(path):
    """Create an empty file at `path`."""
    f = open(path, 'w')
    f.close()

class ReproduceTests(unittest.TestCase):
    """Tests for the Reproduce library."""

    def setUp(self):
        """Overriding setUp function to create temp workspace directory."""
        # this lets us delete the workspace after its done no matter the
        # the rest result
        self.workspace_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Overriding tearDown function to remove temporary directory."""
        shutil.rmtree(self.workspace_dir)

    def test_reproduce(self):
        """Reproduce: base test."""
        import reproduce
        reproduce_env = reproduce.Reproduce(self.workspace_dir)

        data = 'this is a string to test with'

        hash_func = hashlib.new('md5')
        hash_func.update(data.encode('utf-8'))
        digest = hash_func.hexdigest()

        local_path = 'test_files/test.txt'
        predicted_path = reproduce_env.predict_path(local_path)
        self.assertFalse(
            os.path.exists(predicted_path),
            'test.txt not supposed to exist yet')

        reproduce_env.register_data(
            'test_file', local_path, expected_hash=('md5', digest),
            constructor_func=_make_file,
            constructor_args=(data,))

        self.assertTrue(
            os.path.exists(predicted_path), 'test.txt is supposed to exist')

        actual_data = open(reproduce_env['test_file'], 'r').read()
        self.assertEqual(data, actual_data, "data do not match")


    def test_reproduce_duplicate(self):
        """Reproduce: test error handling for dual registration."""
        import reproduce

        reproduce_env = reproduce.Reproduce(self.workspace_dir)
        data = 'this is a string to test with'
        reproduce_env.register_data(
            'test_file', 'test.txt',
            constructor_func=_make_file,
            constructor_args=(data,))

        # try to register a different file
        with self.assertRaises(ValueError):
            reproduce_env.register_data(
                'test_file', 'test.txt',
                constructor_func=_make_file,
                constructor_args=("new data",))


    def test_embedded_hashes(self):
        """Reproduce: test embedded filename hashes."""
        import reproduce

        reproduce_env = reproduce.Reproduce(self.workspace_dir)
        data = 'this is a string to test with'

        hash_func = hashlib.new('md5')
        hash_func.update(bytes(data, 'utf-8'))
        digest = hash_func.hexdigest()

        reproduce_env.register_data(
            'test_file', f'test_md5_{digest}.txt',
            expected_hash='embedded',
            constructor_func=_make_file,
            constructor_args=(data,))


        reproduce_env = reproduce.Reproduce(self.workspace_dir)
        data_2 = 'this is a different string to test with'

        hash_func = hashlib.new('md5')
        hash_func.update(bytes(data, 'utf-8'))
        digest = hash_func.hexdigest()

        with self.assertRaises(RuntimeError):
            reproduce_env.register_data(
                'test_file2', f'test2_md5_{digest}.txt',
                expected_hash='embedded',
                constructor_func=_make_file,
                constructor_args=(data_2,))

    def test_a_file_to_overwrite(self):
        """Reproduce: test a file exists and needs to be updated."""
        import reproduce
        reproduce_env = reproduce.Reproduce(self.workspace_dir)
        predicted_path = reproduce_env.predict_path('test.txt')

        # first make a file that won't match
        with open(predicted_path, 'w') as test_file:
            test_file.write("this won't match the file hash")

        data = 'this is a string to test with'
        hash_func = hashlib.new('md5')
        hash_func.update(bytes(data, 'utf-8'))
        digest = hash_func.hexdigest()

        reproduce_env.register_data(
            'test_file', 'test.txt', expected_hash=('md5', digest),
            constructor_func=_make_file,
            constructor_args=(data,))

        actual_data = open(reproduce_env['test_file'], 'r').read()
        self.assertEqual(data, actual_data, "data do not match")

    def test_a_file_exists_no_update(self):
        """Reproduce: test a file exists and no need to update."""
        import reproduce
        reproduce_env = reproduce.Reproduce(self.workspace_dir)
        predicted_path = reproduce_env.predict_path('test.txt')

        # make a file that will match the hash
        data = 'this is a string to test with'
        with open(predicted_path, 'w') as test_file:
            test_file.write(data)

        hash_func = hashlib.new('md5')
        hash_func.update(bytes(data, 'utf-8'))
        digest = hash_func.hexdigest()

        reproduce_env.register_data(
            'test_file', 'test.txt', expected_hash=('md5', digest),
            constructor_func=_make_file,
            constructor_args=(data,))

        actual_data = open(reproduce_env['test_file'], 'r').read()
        self.assertEqual(data, actual_data, "data do not match")

    def test_a_file_exist_but_no_hash(self):
        """Reproduce: test a file exists but no way to hash."""
        import reproduce
        reproduce_env = reproduce.Reproduce(self.workspace_dir)
        predicted_path = reproduce_env.predict_path('test.txt')

        # first make a file that won't match
        original_data = "this won't match the file hash"
        with open(predicted_path, 'w') as test_file:
            test_file.write(original_data)

        new_data = 'this is a string to test with'

        reproduce_env.register_data(
            'test_file', 'test.txt', expected_hash=None,
            constructor_func=_make_file,
            constructor_args=(new_data,))

        actual_data = open(reproduce_env['test_file'], 'r').read()
        self.assertNotEqual(
            new_data, actual_data, "data are not supposed to match")
        self.assertEqual(
            original_data, actual_data, "data are supposed to match")

    def test_error_handling(self):
        """Reproduce: test that common errors raise exceptions."""
        import reproduce
        reproduce_env = reproduce.Reproduce(self.workspace_dir)

        # file won't exist and no constructor provided
        with self.assertRaises(ValueError):
            reproduce_env.register_data(
                'test_file', 'test.txt', expected_hash=None,
                constructor_func=None,
                constructor_args=None)

        # no arguments passed to constructor and it needs some
        with self.assertRaises(TypeError):
            reproduce_env.register_data(
                'test_file', 'test.txt', expected_hash=None,
                constructor_func=_make_file,
                constructor_args=None)

        data = 'test data for the file'
        # hash won't match the embedded hash
        with self.assertRaises(RuntimeError):
            reproduce_env.register_data(
                'test_file', 'test_md5_0123456789abcdef.txt',
                expected_hash='embedded',
                constructor_func=_make_file,
                constructor_args=(data,))

        # filename does not conform to a name_[fun]_[hash] extension
        with self.assertRaises(ValueError):
            reproduce_env.register_data(
                'test_file', 'test.txt',
                expected_hash='embedded',
                constructor_func=_make_file,
                constructor_args=(data,))

        # invalid value for expected hash (should be (alg, digst) tuple)
        hash_func = hashlib.new('md5')
        hash_func.update(bytes(data, 'utf-8'))
        digest = hash_func.hexdigest()

        with self.assertRaises(ValueError):
            reproduce_env.register_data(
                'test_file', 'test.txt',
                expected_hash=digest,
                constructor_func=_make_file,
                constructor_args=(data,))
