import os
import pandas as pd
from abc import ABCMeta, abstractmethod
import json
from io import StringIO
from azure.storage.blob import BlockBlobService


class StorageContext(object, metaclass=ABCMeta):
    """
    .. py:class:: StorageContext
    Abstract class for holding storage context.
    """
    @abstractmethod
    def reader(self, file_name, *args, **kwargs):
        pass

    @abstractmethod
    def writer(self, data, file_name, *args, **kwargs):
        pass

    @classmethod
    def construct_from_json(cls, json_str):
        attribute_dict = json.loads(json_str)
        return cls(**attribute_dict)

    @abstractmethod
    def to_json(self):
        pass


class LocalStorageContext(StorageContext):
    """
    .. py:class:: LocalStorageContext
    Class for local storage context.

    :param base_dir:
        The local directory path.
    :type base_dir:str
    """
    def __init__(self, base_dir=os.getcwd()):
        self._base_dir = os.path.abspath(base_dir)

    @property
    def base_dir(self):
        return self._base_dir

    def reader(self, file_name):
        """
        .. py:method:: reader
        Read files from the local directory. Only csv files are supported for
        now.

        :param file_name:
            Name of the file to read.
        :type file_name: str

        :return: data read from the local file
        :rtype: pandas.DataFrame
        """
        file_path = os.path.join(self._base_dir, file_name)
        data = pd.read_csv(file_path)
        return data

    def writer(self, data, file_name):
        """
        .. py:method:: writer
        Write data to local file.

        :param data:
            Data to write to the file.
        :type data: pandas.DataFrame

        :param file_name:
            Name of the file to write.
        :type file_name: str
        """
        file_path = os.path.join(self._base_dir, file_name)
        data.to_csv(file_path, index=False)

    def to_json(self):
        """
        .. py:method:: to_json
        Convert the LocalStorageContext object to json string.

        :return:
            json string representation of the LocalStorageContext
            object
        :rtype: str
        """
        attributes_dict = {'base_dir': self.base_dir}
        return json.dumps(attributes_dict)


class AzureBlobStorageContext(StorageContext):
    """
    .. py:class:: AzureBlobStorageContext
    Class for Azure Blob storage context.

    :param blob_account_name:
        The name of the blob storage account.
    :type blob_account_name: str

    :param blob_container_name:
        The name of the blob container.
    :type blob_container_name: str

    :param blob_key:
        The connection string of the blob storage account.
    :type blob_key: str
    """
    def __init__(self, blob_account_name=None, blob_container_name=None,
                 blob_key=None):
        self._blob_account_name = blob_account_name
        self._blob_container_name = blob_container_name
        self._blob_key = blob_key
        self._blob_service = None

    @property
    def blob_account_name(self):
        return self._blob_account_name

    @property
    def blob_container_name(self):
        return self._blob_container_name

    @property
    def blob_key(self):
        return self._blob_key

    def create_blob_service(self):
        """
        .. py:method:: create_blob_service
        Create a BlockBlobService object for the blob storage account. The
        BlockBlobService has methods to access Azure Blob Storage.

        azure.storage.blob.blockblobservice: http://azure-storage.readthedocs.io/ref/azure.storage.blob.blockblobservice.html

        """
        if self._blob_service is None:
            self._blob_service = BlockBlobService(
                account_name=self._blob_account_name, account_key=self._blob_key)

    def reader(self, file_name):
        """
        .. py:method:: reader
        Read files from Azure Blob Storage. Only csv files are supported for
        now.

        :param file_name:
            Name of the blob to read.
        :type file_name: str

        :return: data read from blob storage
        :rtype: pandas.DataFrame
        """
        self.create_blob_service()
        data_string = self._blob_service.get_blob_to_text(
            self._blob_container_name, blob_name=file_name)
        data_string = data_string.content
        data = pd.read_csv(StringIO(data_string))
        return data

    def writer(self, data, file_name):
        """
        .. py:method:: writer
        Write data into Azure Blob Storage blobs.

        :param data:
            Data to write to blob.
        :type data: pandas.DataFrame

        :param file_name:
            Name of the blob to write.
        :type file_name: str
        """

        self.create_blob_service()
        output_df = data.to_csv(index=False).encode('utf-8')
        self._blob_service.create_blob_from_text(
            container_name=self._blob_container_name, blob_name=file_name,
            text=output_df)

    def to_json(self):
        """
        .. py:method:: to_json
        Convert the AzureBlobStorageContext object to json string.

        :return:
            json string representation of the AzureBlobStorageContext
            object
        :rtype: str
        """
        attributes_dict = {'blob_account_name': self._blob_account_name,
                           'blob_container_name': self._blob_container_name,
                           'blob_key': self._blob_key}
        return json.dumps(attributes_dict)







