from __future__ import absolute_import


class AiotStudioError(Exception):
    """Base AIoT Studio error."""


class UnauthorizedError(AiotStudioError):
    """Action was not authorized (did you provide correct credentials?)."""


class ConfigurationError(AiotStudioError):
    """Configuration is invalid or not found."""


class FeatureUnavailableError(AiotStudioError):
    """Feature or service is not available in the current context."""


class RestitutionError(AiotStudioError):
    """Base restitution error."""


class RestitutionTimeoutError(RestitutionError):
    """Call to restitution (e.g. from a nested search) timed out."""


class RestitutionResultError(RestitutionError):
    """Call to restitution was successful but result indicated an error."""


class BlobStoreError(AiotStudioError):
    """Base blob storage error."""


class BlobStoreTimeoutError(BlobStoreError):
    """Call to blob storage timed out."""


class BlobStoreBucketNotFound(BlobStoreError):
    """Blob store bucket was not found."""


class BlobStoreObjectNotFound(BlobStoreError):
    """Blob store object was not found."""
