"""
This package provides the API for public consumption.

Example usage

.. highlight:: python
.. code-block:: python

    import asyncio

    from aiostorage import BlobStorage

    file1 = {'content': 'application/pdf', 'path': '/path/to/pdf'}
    file2 = {'content': 'video/mp4', 'path': '/path/to/video'}
    storage = BlobStorage('backblaze', app_key='key8923', account_id='234234')
    coros = [storage.upload_file('bucket-1234', file1),
             storage.upload_file('bucket-1234', file2)]
    parent_future = asyncio.gather(*coros)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(parent_future)
    loop.close()
"""
from .blob_storage import BlobStorage
from .exceptions import (BlobStorageMissingCredentialsError,
                         BlobStorageUnrecognizedProviderError,)

__version__ = '0.1.16'

__all__ = ['BlobStorage', 'BlobStorageUnrecognizedProviderError',
           'BlobStorageMissingCredentialsError']
