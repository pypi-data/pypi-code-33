from fastgenomics.process import FGProcess
import pytest


def test_io_throws_on_non_existing_files(app_dir, data_root_none):
    with pytest.raises(FileNotFoundError):
        FGProcess(app_dir, data_root_none)
