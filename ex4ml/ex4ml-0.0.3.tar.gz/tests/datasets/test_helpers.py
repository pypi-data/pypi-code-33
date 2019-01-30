"""Testing the helper functions for datasets
"""

import pytest
import os
import shutil
import ex4ml.datasets.helpers as h


def test_fetch_data_file():
    """Test fetching a data file
    """
    minds_img_url = "http://minds.mines.edu/img/MInDS%20Logo.png"
    data_file_path = "tests/"
    data_file_full_path = os.path.join(h.BASE_PATH, data_file_path)
    if os.path.exists(data_file_full_path):
        shutil.rmtree(data_file_full_path)
    h.fetch_data(minds_img_url, data_file_path)
    assert os.path.exists(data_file_full_path)


def test_fetch_data_zip():
    """Test fetching a zip file and extracting it
    """
    bbc_sports_url = "http://mlg.ucd.ie/files/datasets/bbcsport-fulltext.zip"
    data_zip_path = "tests/zip/"
    data_zip_full_path = os.path.join(h.BASE_PATH, data_zip_path)
    if os.path.exists(data_zip_full_path):
        shutil.rmtree(data_zip_full_path)
    h.fetch_data(bbc_sports_url, data_zip_path)
    assert os.path.exists(os.path.join(h.BASE_PATH, data_zip_path))
    assert os.path.isdir(os.path.join(h.BASE_PATH, data_zip_path))
