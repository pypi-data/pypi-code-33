import os
from ex4ml.datasets.helpers import BASE_PATH, fetch_data, txt_file_to_do, targets_folder_to_do
from ex4ml.objects.dataobject import DataObject


BBC_ARTICLES_URL = "http://mlg.ucd.ie/files/datasets/bbc-fulltext.zip"
BBC_SPORTS_URL = "http://mlg.ucd.ie/files/datasets/bbcsport-fulltext.zip"


def load_bbc(n_samples=None, indices=None, force_download=False):
    """Load the BBC articles data into a DataObject

        n_samples (int, optional): Defaults to None. The number of samples to load
        indices (index, optional): Defaults to None. The index to load
        force_download (bool, optional): Defaults to False. Whether to download the data even if it already exists

    Returns:
        DataObject: The DataObject containing the BBC articles data
    """
    # Download files
    bbc_path = os.path.join(BASE_PATH, "datasets/nlp/bbc/")
    bbc_full_path = os.path.join(bbc_path, "bbc")

    fetch_data(BBC_ARTICLES_URL, bbc_path, force_download)

    # Loop through directories to create DataObject
    return targets_folder_to_do(bbc_full_path, "topic", ".txt", txt_file_to_do)


def load_bbc_sport(n_samples=None, indices=None, force_download=False):

    # Download files
    bbc_sport_path = os.path.join(BASE_PATH, "datasets/nlp/bbcsport/")

    fetch_data(BBC_SPORTS_URL, bbc_sport_path, force_download)
    bbc_sport_full_path = os.path.join(bbc_sport_path, "bbcsport")

    # Loop through directories to create DataObject
    return targets_folder_to_do(bbc_sport_full_path, "topic", ".txt", txt_file_to_do)
