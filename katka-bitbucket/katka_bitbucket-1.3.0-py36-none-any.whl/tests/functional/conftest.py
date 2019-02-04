import json
from pathlib import Path
from typing import Callable

from django.core.management import call_command

import pytest


@pytest.fixture
def load_db_fixture(request: 'pytest.fixtures.SubRequest', django_db_blocker) -> None:
    """
    Run Django's `loaddata` command to populate the DB from JSON/YAML fixtures

    Args:
        request(pytest.fixtures.SubRequest): the fixture request
        django_db_blocker(pytest_django.plugin._DatabaseBlocker): the database blocker (can't use type annotations
        sue to bug on pyflakes https://github.com/PyCQA/pyflakes/issues/356 which throws a `F821` violation)

    Usage:

        @pytest.mark.usefixtures('load_db_fixture')
        @pytest.mark.parametrize(
            'load_db_fixture', [{'fixture_filename': 'my_fixture.json'}], indirect=True)
        def test_something():
            ...

    This assumes that fixture files are located under a `fixtures`
    subdirectory, at the same level as the test module.
    """
    fixture_filename = request.param['fixture_filename']
    fixture_path_abs = Path(request.fspath.dirname) / 'fixtures' / fixture_filename
    with django_db_blocker.unblock():
        call_command('loaddata', str(fixture_path_abs))


@pytest.fixture
def load_json_fixture(request: 'pytest.fixtures.SubRequest') -> Callable[[str], dict]:
    """
    Load a JSON fixture and return its primitive Python representation

    Usage:

        def test_something(load_json_fixture):
            fixture_data = load_json_fixture('my_fixture.json')
            ...

    This assumes that fixture files are located under a `fixtures`
    subdirectory, at the same level as the test module.
    """

    def load_fixture(json_filename: str) -> dict:
        fixture_path_abs = Path(request.fspath.dirname) / 'fixtures' / json_filename
        with fixture_path_abs.open(encoding='utf-8') as f:
            return json.load(f)

    return load_fixture
