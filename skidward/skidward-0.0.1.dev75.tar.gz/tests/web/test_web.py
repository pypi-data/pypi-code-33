from pathlib import Path

from dotenv import load_dotenv
import pytest

from skidward.web import app


@pytest.fixture
def init_env_vars():
    path_to_project_root = Path(__file__).parent.parent.parent
    path_to_module_env_file = (path_to_project_root / "skidward" / ".env").resolve()

    load_dotenv(dotenv_path=path_to_module_env_file, verbose=True)


def test_it_creates_app(init_env_vars):
    assert app
