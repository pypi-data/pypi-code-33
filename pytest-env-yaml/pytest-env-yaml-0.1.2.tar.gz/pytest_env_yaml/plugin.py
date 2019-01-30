import pytest
import yaml


def pytest_addoption(parser):
    parser.addoption('--env-yaml', action='store', default=None, required=True)


@pytest.fixture(scope='session')
def env_yaml(request):
    filename = request.config.getoption('--env-yaml')
    with open(filename) as stream:
        return yaml.load(stream)
