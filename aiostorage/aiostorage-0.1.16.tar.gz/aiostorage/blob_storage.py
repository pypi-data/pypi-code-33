"""
This module contains the `BlobStorage` class.
"""
import logging

from .exceptions import (BlobStorageMissingCredentialsError,
                         BlobStorageUnrecognizedProviderError, )
from .providers import PROVIDERS
from .providers.backblaze import Backblaze
from .providers.exceptions import (ProviderAuthorizationError,
                                   ProviderFileUploadError)

LOGGER = logging.getLogger(__name__)


class BlobStorage:
    """
    Asynchronous object storage interface for common operations, e.g.
    uploading a file to a bucket.

    Providers currently supported:

    Backblaze.
    """
    PROVIDER_ADAPTER = {
        'backblaze': {
            'adapter': Backblaze,
            'required': ('account_id', 'app_key'),
        }
    }

    def __init__(self, provider, **kwargs):
        r"""
        Set the object storage provider.

        :param str provider: Name of the object storage provider. Must be one
               of `'backblaze'`.
        :param \**kwargs: Credentials for the object storage provider, see
               below.

        : Keyword arguments:
            * *account_id* (``str``) --
              Account id (Backblaze).
            * *app_key* (``str``) --
              Application key (Backblaze).
        """
        LOGGER.debug('Creating instance of `BlobStorage` class')
        if provider not in PROVIDERS:
            raise BlobStorageUnrecognizedProviderError
        if not all(r in kwargs
                   for r in self.PROVIDER_ADAPTER[provider]['required']):
            raise BlobStorageMissingCredentialsError
        self.provider = self.PROVIDER_ADAPTER[provider]['adapter'](**kwargs)

    async def upload_file(self, bucket_id, file_to_upload):
        """
        **async** Upload a single file to the object storage provider.

        :param str bucket_id: Object storage provider bucket to upload files
               to.
        :param dict file_to_upload: Local file to upload,
               `{'path': str, 'content_type': str}`.
        :raise ProviderAuthorizationError: If authorization to the object
               storage provider is unsuccessful.
        :raise ProviderFileUploadError: If uploading of the file to the object
               storage provider bucket is unsuccessful.
        :return: Response from object storage provider.
        :rtype: ``dict``
        """
        upload_file_meta = (file_to_upload['path'],
                            type(self.provider).__name__, bucket_id)
        LOGGER.info('Uploading file "%s" to %s bucket %s' % upload_file_meta)
        LOGGER.debug('Authenticating')
        auth_response = await self.provider.authorize()
        if not auth_response:
            raise ProviderAuthorizationError
        LOGGER.debug('Authentication successful')
        LOGGER.debug('Uploading')
        upload_file_response = await self.provider.upload_file(
            bucket_id, file_to_upload['path'], file_to_upload['content_type'])
        if not upload_file_response:
            raise ProviderFileUploadError
        LOGGER.info('Successfully uploaded file "%s" to %s bucket %s'
                    % upload_file_meta)
        LOGGER.debug(upload_file_response)
        return upload_file_response
