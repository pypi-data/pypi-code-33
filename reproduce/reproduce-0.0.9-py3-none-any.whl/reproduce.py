"""Framework for reproducible computational science."""
import hashlib
import os
import errno
import logging
import sqlite3
import re

ALL_DIR_LIST = [
    ('DATA_DIR', 'data'),
    ('CACHE_DIR', 'cache'),
    ]

LOGGER = logging.getLogger('reproduce.Reproduce')


def hash_file(file_path, hash_algorithm, buf_size=2**20):
    """Return a hex digest of `file_path`.

    Parameters:
        file_path (string): path to file to hash.
        hash_algorithm (string): a hash function id that exists in
            hashlib.algorithms_available.
        buf_size (int): number of bytes to read from `file_path` at a time
            for digesting.

    Returns:
        hex digest with hash algorithm `hash_algorithm` of the binary
        contents of `file_path`.

    """
    hash_func = hashlib.new(hash_algorithm)
    with open(file_path, 'rb') as f:
        data = f.read(buf_size)
        while data:
            hash_func.update(data)
            data = f.read(buf_size)
    # We return the md5 hash in hexadecimal format
    return hash_func.hexdigest()


def valid_hash(file_path, expected_hash, buf_size=2**20):
    """Validate that the file at `file_path` matches `expected_hash`.

    Parameters:
        file_path (str): path to file location on disk.
        expected_hash (str or tuple): if a tuple, a "hash algorithm",
            "expected_hash" pair that will be used to hash `expected_path`
            and confirm that the hash of that file is equivalent to the
            expected hash value. If the `expected_path` does not
            match the hash, this function will raise an AssertionError.

            Otherwise must be the value "embedded" which attempts to parse
            `file_path` for the pattern
            filename_{hash_algorthm}_{hash_value}.ext.
        buf_size (int): (optional) number of bytes to read from `file_path`
            at a time for digesting.

    Returns:
        True if `file_path` hashes to `expected_hash`.

    Raises:
        ValueError if `expected_hash == 'embedded'` and `file_path` does not
        match the appropriate file pattern.

        IOError if `file_path` not found.

    """
    if not os.path.exists(file_path):
        raise IOError(f'{file_path} not found.')
    if isinstance(expected_hash, tuple):
        hash_algorithm = expected_hash[0]
        expected_hash_value = expected_hash[1]
    elif expected_hash == 'embedded':
        hash_re_pattern = r'.*_([^_]+)_([0-9a-f]+)(\.[^\.]*)?$'
        hash_match = re.match(hash_re_pattern, file_path)
        if not hash_match:
            raise ValueError(
                f"file_path: {file_path} did not end "
                "in an [hash_alg]_[hexhash][.ext] format")
        hash_algorithm = hash_match.group(1)
        expected_hash_value = hash_match.group(2)
    else:
        raise ValueError(
            "Invalid value for `expected_hash`, expecting either a tuple "
            "or 'embedded': {expected_hash}")

    actual_hash = hash_file(file_path, hash_algorithm)
    return expected_hash_value == actual_hash


class Reproduce(object):
    """Object to initialize and store state of reproduction library."""

    def __init__(self, root_path):
        """Initialize directory structure."""
        self._id_data_map = {}
        for dir_id, dir_root_name in ALL_DIR_LIST:
            try:
                self._id_data_map[dir_id] = os.path.join(
                    root_path, dir_root_name)
                os.makedirs(self._id_data_map[dir_id])
                LOGGER.debug(f'{self._id_data_map[dir_id]} created')
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
                else:
                    LOGGER.debug(
                        f'{self._id_data_map[dir_id]} already exists')

        reproduce_db_path = os.path.join(
            self._id_data_map['CACHE_DIR'], 'reproduce.db')
        LOGGER.debug(reproduce_db_path)
        self._reproduce_db = _ReproduceDatabase(reproduce_db_path)
        LOGGER.debug(self._reproduce_db)

    def __getitem__(self, data_id):
        """Given a `data_id` from `register_data` returns data value."""
        return self._id_data_map[data_id]

    def predict_path(self, path):
        """Return the predicted path if the data object was registered."""
        return os.path.join(self._id_data_map['DATA_DIR'], path)

    def register_data(
            self, data_id, expected_path, expected_hash=None,
            constructor_func=None, constructor_args=None,
            constructor_kwargs=None):
        """Register a data file and create it if it doesn't exist.

        Parameters:
            data_id (str): a unique  identifier for this data that can
                be used later to index back into the Reproduce object.
            expected_path (str): path to the expected file within the
                DATA_DIR directory.
            constructor_func (func): a function with a path argument to
                invoke if the file does not already exist. This function
                will be called with the effective path passed to it as well
                as effective constructor_args and kwargs equivalent to:
                    constructor_func(
                        path, *constructor_args, **constructor_kwargs)
            constructor_args (list): additional positional arguments to
                `constructor_func` if not None.
            constructor_kwargs (dict); additional keyword arguments to
                `constructor_func` if not None.
            expected_hash (str or tuple): if a tuple, a 'hashname',
                'expected_hash' pair that will be used to hash `expected_path`
                and confirm that the hash of that file is equivalent to the
                expected hash value. If the `expected_path` exists, but does
                not match the hash, this function will attempt to create the
                file by invoking `constructor_func`. If the final file does
                not match the hash, a RuntimeError is raised.

                If the value is 'embedded' the hash/value pair is parsed from
                the suffix of the non-extension part of the path. A ValueError
                is raised if an algorithm/hash value cannot be parsed from the
                file name, or the hash doesn't match.

        Returns:
            None.

        """
        if data_id in self._id_data_map:
            raise ValueError(f"{data_id} already registered.")
        expected_path_full = os.path.join(
            self._id_data_map['DATA_DIR'], expected_path)
        try:
            dir_path = os.path.dirname(expected_path_full)
            os.makedirs(dir_path)
            LOGGER.info(f'{dir_path} created')
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        if isinstance(expected_hash, tuple):
            hash_algorithm = expected_hash[0]
            expected_hash_value = expected_hash[1]
        elif expected_hash == 'embedded':
            hash_re_pattern = r'.*_([^_]+)_([0-9a-f]+)(\.[^\.]*)?$'
            hash_match = re.match(hash_re_pattern, expected_path_full)
            if not hash_match:
                raise ValueError(
                    f"expected_path_full: {expected_path_full} did not end "
                    "in an [hash_alg]_[hexhash] [.ext] format")
            hash_algorithm = hash_match.group(1)
            expected_hash_value = hash_match.group(2)
        elif expected_hash is not None:
            raise ValueError(
                "Invalid value for `expected_hash`, expecting either a tuple "
                "or 'embedded': {expected_hash}")

        need_to_create_file = True
        # first attempt to skip creation of file if hash exists
        if os.path.exists(expected_path_full):
            if expected_hash:
                actual_hash = hash_file(expected_path_full, hash_algorithm)
                if expected_hash_value != actual_hash:
                    LOGGER.warn(
                        f'{expected_path_full} exists, but does not match '
                        f'the hash (expected: {expected_hash_value}'
                        f' actual: {actual_hash}')
                else:
                    need_to_create_file = False
                    LOGGER.info(
                        f'{expected_path_full} exists and matches expected '
                        'hash')
            else:
                LOGGER.info(
                    f'{expected_path_full} exists and no hash provided')
                need_to_create_file = False

        if need_to_create_file:
            if constructor_func is None:
                raise ValueError(
                    '{expected_path_full} does not exist and data '
                    'constructor not provided')
            LOGGER.info(
                f'{expected_path_full} does not exist, invoking data '
                'constructor')
            if not constructor_args:
                constructor_args = []
            if not constructor_kwargs:
                constructor_kwargs = {}
            constructor_func(
                expected_path_full, *constructor_args, **constructor_kwargs)
            if expected_hash:
                actual_hash = hash_file(expected_path_full, hash_algorithm)
                if expected_hash_value != actual_hash:
                    raise RuntimeError(
                        f'{expected_path_full} created, but does not match '
                        f'the expected hash (expected: {expected_hash_value}'
                        f' actual: {actual_hash}')

        self._id_data_map[data_id] = expected_path_full


class _ReproduceDatabase(object):

    def __init__(self, database_path):
        """Create a new instance of ReproduceDatabse.

        Parameters:
            database_path (string): path to a database file. If one does
                not exist, it will be created by this call, otherwise
                the database will be opened and verified to be a valid
                file.

        Returns:
            None.

        """
        self.database_path = database_path
        LOGGER.debug(f'creating database at {self.database_path}')
        db_connection = sqlite3.connect(database_path)
        db_connection.execute(
            """CREATE TABLE IF NOT EXISTS reproduce_table """
            """(hash_val TEXT primary key, location_uri TEXT, """
            """generator_hash TEXT)""")

    def foo(self):
        LOGGER.debug(self.database_path)
