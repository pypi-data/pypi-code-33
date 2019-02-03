import sys
import pytest
import conficus

if sys.version.startswith('3'):
    from pathlib import Path
else:
    from pathlib2 import Path

CWD = Path().resolve()
DOCS = Path(CWD, 'test', 'samples')
PATHS = {
    'config': Path(DOCS, 'config.txt'),
    'coerce': Path(DOCS, 'config_coerce.txt'),
    'multiline': Path(DOCS, 'config_multiline.txt'),
    'wilderness': Path(DOCS, 'the_wild.txt'),
    'sample': Path(DOCS, 'docs-sample.ini'),
    'format': Path(DOCS, 'config_format.txt')
}


@pytest.fixture
def cfg_pth():
    return PATHS


@pytest.fixture
def raw_cfg():
    lines = conficus.read_config(str(PATHS['config']))
    return conficus._parse(lines)


@pytest.fixture
def coerce_cfg():
    lines = conficus.read_config(str(PATHS['coerce']))
    return conficus._parse(lines)


@pytest.fixture
def multiline_cfg():
    lines = conficus.read_config(str(PATHS['multiline']))
    return conficus._parse(lines)


@pytest.fixture
def format_cfg():
    lines = conficus.read_config(str(PATHS['format']))
    return conficus._parse(lines)
