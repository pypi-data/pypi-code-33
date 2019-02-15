import pytest
from pathlib import Path
from fastgenomics.process import FGProcess
from fastgenomics.testing import cleanoutput

HERE = Path(__file__).parent
DATA = HERE / "data"
APPS = HERE / "apps"


@pytest.fixture
def app_dir():
    return APPS / "working"


@pytest.fixture
def app_dir_validation_error():
    return APPS / "validation_error"


@pytest.fixture
def app_dir_missing_files():
    return APPS / "missing_files"


@pytest.fixture
def app_dir_non_existing():
    path = APPS / "non_existing"
    assert not path.exists()
    return path


@pytest.fixture
def app_dir_runtime_error():
    return APPS / "runtime_error"


@pytest.fixture
def data_root():
    return DATA / "working_1"


@pytest.fixture
def data_root_2():
    return DATA / "working_2"


@pytest.fixture
def data_root_none():
    return DATA / "non_existing"


@pytest.fixture
def data_root_missing_files():
    return DATA / "missing_files"


@pytest.fixture
def fgprocess(app_dir, data_root):
    fg = FGProcess(app_dir, data_root)
    cleanoutput(fg)
    return fg


@pytest.fixture
def summary(fgprocess):
    fgprocess.summary.template = fgprocess.app.app_dir / "summary.md.j2"
    return fgprocess.summary


@pytest.mark.anndata
@pytest.fixture
def adata(fgprocess):
    import fastgenomics.external.anndata as fgad

    return fgad.read_data(
        fgprocess, expr="some_input", gene_meta="genes", cell_meta="cells"
    )
