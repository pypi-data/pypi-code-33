import logging
import pytest

from migration_runner import Helpers, DatabaseTools, Controller


@pytest.fixture
def logger():
    return logging.getLogger(__name__)


@pytest.fixture
def helpers():
    return Helpers()


@pytest.fixture
def database_tools():
    return DatabaseTools()


@pytest.fixture
def controller():
    return Controller()


@pytest.fixture
def sql_filename_expected():
    return "045.createtable.sql"


@pytest.fixture
def sql_filename_hyphen():
    return "045-createtable.sql"


@pytest.fixture
def sql_filename_not_zero_padded():
    return "45.createtable.sql"


@pytest.fixture
def sql_filename_spaced():
    return "45 .createtable.sql"


@pytest.fixture
def sql_filename_no_sql_suffix():
    return "45.createtable.jpg"


@pytest.fixture
def sql_filename_no_separator():
    return "45createtable.sql"


@pytest.fixture
def sql_filename_bigint():
    return "23514352834592347502351435283459234750.createtable.sql"


@pytest.fixture
def sql_filename_no_version():
    return "createtable.sql"


@pytest.fixture
def unsorted_migrations_tuple_list():
    return [
        (45, '/tmp/045.createtable.sql'),
        (2, '/tmp/2-createtable.sql'),
        (1, '/tmp/001.createtable.sql'),
        (60, '/tmp/60.createtable.sql'),
    ]


@pytest.fixture
def sorted_migrations_tuple_list():
    return [
        (1, '/tmp/001.createtable.sql'),
        (2, '/tmp/2-createtable.sql'),
        (45, '/tmp/045.createtable.sql'),
        (60, '/tmp/60.createtable.sql'),
    ]


@pytest.fixture
def unsorted_migrations_string_list():
    return [
        '/tmp/045.createtable.sql',
        '/tmp/2-createtable.sql',
        '/tmp/001.createtable.sql',
        '/tmp/60.createtable.sql'
    ]


@pytest.fixture
def unsorted_migrations_non_versioned_list():
    return [
        ('/tmp/045.createtable.sql', 'test'),
        ('/tmp/2-createtable.sql', 'test'),
        ('/tmp/001.createtable.sql', 'test'),
        ('/tmp/60.createtable.sql', 'test')
    ]


@pytest.fixture
def db_params_dict():
    return {
        "host": "db_host",
        "user": "db_user",
        "password": "db_password",
        "database": "db_name"
    }


@pytest.fixture
def db_params_tup():
    return (
        "db_host",
        "db_user",
        "db_password",
        "db_name"
    )
