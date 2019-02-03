"""Aeon Cloud Client"""
from aeoncloud.cloud.cloud_adapter import ICloudAdapter
from aeoncloud.cloud.async_http_cloud_adapter import AsyncCloudAdapter
from aeoncloud.cloud.http_cloud_adapter import HttpCloudAdapter
from aeoncloud.sessions.http_session_factory_adapter import HttpSessionFactoryAdapter
from aeoncloud.sessions.session_factory_adapter import ISessionFactoryAdapter


def get_session_factory() -> ISessionFactoryAdapter:
    """Gets a factory for creating Aeon Cloud Sessions

        Returns:
            ISessionFactoryAdapter
        """
    return HttpSessionFactoryAdapter()


def get_cloud_adapter(aeon_cloud_url, credentials, callback_url='', asyncronous=False) \
    -> ICloudAdapter:
    """Gets an Aeon Cloud adapter for managing runners.

    Args:
        aeon_cloud_url: URL of the Aeon cloud
        credentials: Cloud credentials
        callback_url: Callback URL for commands (defaults to '')
        asyncrounous: Should an async client be provided (default is False)

    Returns:
        ICloudAdapter concrete Cloud adapter
    """
    if asyncronous:
        return AsyncCloudAdapter(aeon_cloud_url, credentials, callback_url)
    return HttpCloudAdapter(aeon_cloud_url, credentials, callback_url)
