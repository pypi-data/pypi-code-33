"""Helpers for loading nlp datasets
"""
import os
from os.path import join
from zipfile import ZipFile
import urllib
from ex4ml.objects.dataobject import DataObject

BASE_PATH = join(os.path.expanduser('~'), ".ex4ml/")


def fetch_data(url, save_path, force_download=False):
    """Fetch data from a url and save it

    Args:
        url (str): The url string to fetch data from
        save_path (str): The path to save the data to folllowing the base path
        force_download (bool): Defaults to False. Whether to download the data if it already exists
    """
    full_save_path = join(BASE_PATH, save_path)
    if not os.path.exists(os.path.dirname(full_save_path)) or force_download:
        if url.endswith(".zip"):
            # Download the zip file
            file_name = os.path.basename(url)
            file_path = join(BASE_PATH, "downloads/", file_name)
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            urllib.request.urlretrieve(url, file_path)
            # Extract the zip file
            if not os.path.exists(os.path.dirname(full_save_path)):
                os.makedirs(os.path.dirname(full_save_path))
            zip_ref = ZipFile(file_path, 'r')
            zip_ref.extractall(full_save_path)
            zip_ref.close()
            # Delete the zip file
            os.remove(file_path)
        else:
            file_name = os.path.basename(url)
            file_path = join(BASE_PATH, save_path, file_name)
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            urllib.request.urlretrieve(url, file_path)
    else:
        print("Data already exists. Will not re-download. If you would like to download it anyway, please set force_download to True.")


def txt_file_to_do(path, targets):
    """Read a file's contents to a DataObject

    Args:
        path (str): Path to the file to read
        targets (iterable): Targets to pass through to the DataObject

    Returns:
        DataObject: The DataObject created from the file
    """
    with open(path, "rb") as file:
        return DataObject(file.read().decode(errors="ignore"), singular=True, targets=targets)


def targets_folder_to_do(path, target_name, file_type, func):
    """Convert a folder of files organized by target into a DataObject by applying a function

    Args:
        path (str): Path to folder
        target_name (str): The key specified for the targets dictionary
        func (function): The function to apply to each file

    Returns:
        DataObject: The resulting DataObject from traversing the folder
    """
    return DataObject([
        func(os.path.join(path, target, f), {target_name: target})  # Create a DataObject from the file
        for target in os.listdir(path) if os.path.isdir(os.path.join(path, target))  # For every target folder (if it's a directory)
        for f in os.listdir(os.path.join(path, target)) if f.endswith(file_type)  # For every txt file in the target folder
    ])
