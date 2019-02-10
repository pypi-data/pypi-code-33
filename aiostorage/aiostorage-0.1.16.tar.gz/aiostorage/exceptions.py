"""
This module contains exceptions for the `BlobStorage` class.
"""
from .providers import PROVIDERS


class BlobStorageError(Exception):
    """
    Base exception class.
    """


class BlobStorageUnrecognizedProviderError(BlobStorageError):
    """
    Unrecognized object storage provider.
    """
    def __str__(self):
        return ('Unrecognized object storage provider. Please select one of'
                f' {", ".join(PROVIDERS)}')


class BlobStorageMissingCredentialsError(BlobStorageError):
    """
    Missing credentials for object storage provider authorization.
    """
    def __str__(self):
        return 'Missing credentials for object storage provider authorization'
