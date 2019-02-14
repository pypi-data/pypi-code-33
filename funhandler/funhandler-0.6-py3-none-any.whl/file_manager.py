import sys
import time
import pandas as pd
from distributed.worker import thread_state
# this is a pointer to the module object instance itself.
this = sys.modules['funhandler']

AVAILABLE_STORAGE_TYPES = {'local': 'local', 'cloud': 's3'}


def set_storage_model(model_type, **model_info):
    if not isinstance(model_type, str):
        return False
    
    if model_type not in AVAILABLE_STORAGE_TYPES:
        return False
    this.current_storage_type = model_type

def set_local_storage_info(**kwargs):
    """ 
        Set configs for local file storage
            Should set a storage_folder inside of the system
            Should set a base_path

        storage_folder: str
            Name of the folder where all the files will be stored
        base_path: str
            Absolute path to the folder
    """
    storage_folder = kwargs.get('storage_folder', None)
    base_path = kwargs.get('base_path', None)
    if not storage_folder or not base_path:
        raise AttributeError(
            "storage_folder or base_path cannot be None"
           f"Data provided: {kwargs}")

    this.storage_information = {
        'storage_folder': storage_folder,
        'base_path': base_path,
    }

def set_cloud_storage_info(**kwargs):
    """ Set configs for cloud file storage
        Should set a bucket_name
        Should set a base_path

    bucket_name: str
        Name of the bucket in the cloud (S3/GCS)
    base_path: str
        Absolute path to the folder
    ami_key: str
        key to access cloud storage
    ami_secret: str
        secret key to access cloud storage
    """
    bucket_name = kwargs.get('bucket_name', None)
    base_path = kwargs.get('base_path', None)
    # Should ensure to set the AMI key
    # Should ensure to set the AMI secret
    # Should set the bucket
    if (not storage_folder
        or not base_path
        or not ami_key
        or not ami_secret):
        raise AttributeError(
            "bucket_name or base_path or ami_key or ami_secret"
           f"cannot be None; Data provided: {kwargs}")

    this.storage_information = {
        'ami_key': ami_key,
        'ami_secret': ami_secret,
        'bucket_name': storage_folder,
        'base_path': base_path
    }
    # Should check to see if we have access to write to the bucket
    raise NotImplementedError()

def store_local_storage(file):
    """ Stores the file locally with the desired storage information """
    pass

def store_cloud_storage(file):
    """ Stores the file inside of an s3 bucket """
    raise NotImplementedError()
