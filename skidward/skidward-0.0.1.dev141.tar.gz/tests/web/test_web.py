import pytest
from dotenv import load_dotenv

from skidward.web import app


@pytest.fixture
def init_env_vars():
    load_dotenv(verbose=True)


def test_it_creates_app(init_env_vars):
    assert app
