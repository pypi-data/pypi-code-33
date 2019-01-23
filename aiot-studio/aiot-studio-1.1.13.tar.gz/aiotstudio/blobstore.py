from __future__ import absolute_import

from aiotstudio._core.client import get_default_client
from aiotstudio._core import services


_client = get_default_client()


def save(bucket_name, object_name, content):
    # type: (str, str, bytes) -> None
    """Store an object from the blob store

    Objects are identified by a (bucket name, object name) pair. Content can be anything (machine learning model, image,
    text content...) but must be of type ``bytes``.


    Args:
        bucket_name (str): Name of the bucket to store the object into
        object_name (str): Object name that will serve as identifier
        content (bytes): Arbitrary data in bytes

    Example:
        >>> from aiotstudio.blobstore import save
        >>> save("my_bucket", "my_object", b"AIoT Studio")
    """
    return services.blob_store_save(_client, bucket_name, object_name, content)


def fetch(bucket_name, object_name):
    # type: (str, str) -> bytes
    """Fetch and returns an object from the blob store

    Args:
        bucket_name (str): Name of the bucket where the blob is stored
        object_name (str): Object name inside the bucket

    Returns:
        bytes: Content of the blob as bytes

    Example:
        >>> from aiotstudio.blobstore import fetch
        >>> fetch("my_bucket", "my_object")
        b'AIoT Studio'
    """
    return services.blob_store_fetch(_client, bucket_name, object_name)


def delete(bucket_name, object_name):
    # type: (str, str) -> None
    """Delete an object from the blob store

    Args:
        bucket_name (str): Name of the bucket where the blob is stored
        object_name (str): Object name inside the bucket
    """
    return services.blob_store_delete_object(_client, bucket_name, object_name)


def list(bucket_name):
    # type (str) -> List[str]
    """Returns the list of objects inside a specific bucket

    Args:
        bucket_name (str): Name of the bucket to be listed

    Returns:
        List[str]: object names (up to 1000)

    Note:
        A maximum of 1000 object name are returned. Ordering is not guaranteed.
    """
    return services.blob_store_list_objects(_client, bucket_name)


def list_buckets():
    # type: () -> List[str]
    """Returns the list of buckets in the blob store (can be empty).

    Returns:
        List[str]: bucket names

    """
    return services.blob_store_bucket_names(_client)


def delete_bucket(bucket_name):
    # type: (str) -> None
    """Delete a bucket from the blob store and all objects inside it.

    Args:
        bucket_name (str): Name of the bucket to delete
    """
    return services.blob_store_delete_bucket(_client, bucket_name)
