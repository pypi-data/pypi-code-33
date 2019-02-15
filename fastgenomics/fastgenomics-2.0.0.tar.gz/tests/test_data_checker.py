from fastgenomics.data import FGData
import pytest


def test_data_1(data_root):
    FGData(data_root)


def test_data_2(data_root_2):
    FGData(data_root_2)


def test_data_file_not_found(data_root_missing_files):
    with pytest.raises(FileNotFoundError) as e:
        FGData(data_root_missing_files)

    files = ["data", "config", "output", "summary", "config/input_file_mapping.json"]
    for file in files:
        assert file in str(e.value)
