"""
This module contains exceptions for object storage provider API errors.
"""


class ProviderError(Exception):
    """
    Base exception class.
    """


class ProviderGetUploadUrlError(ProviderError):
    """
    Unable to get file upload URL.
    """


class ProviderAuthorizationError(ProviderError):
    """
    Unable to authorize.
    """


class ProviderFileUploadError(ProviderError):
    """
    Unable to upload file.
    """
