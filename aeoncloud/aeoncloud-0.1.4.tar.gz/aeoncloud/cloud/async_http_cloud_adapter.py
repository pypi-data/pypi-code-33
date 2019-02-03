"""Async (Non-Blocking) Http Cloud Adapter"""
import json

from aeoncloud.cloud.cloud_adapter import ICloudAdapter
from aeoncloud.cloud.async_http_client import post, delete, get
from aeoncloud.exceptions.aeon_cloud_error import AeonCloudError


class AsyncCloudAdapter(ICloudAdapter):
    """Async (Non-Blocking) Http Cloud Adapter"""

    def __init__(self, aeon_cloud_url, credentials, callback_url=''):
        if not aeon_cloud_url:
            raise AeonCloudError("No cloud URL provided")

        if not credentials:
            raise AeonCloudError("No cloud credentials provided")

        if not isinstance(credentials, dict):
            raise AeonCloudError("Cloud credentials must be provided as a dictionary")

        self.aeon_cloud_url = aeon_cloud_url
        self.callback_url = callback_url
        self.credentials = credentials

    async def create_runners(self, count):
        """Creates count number of runners

        Args:
            count: Number of runners to create

        Returns:
            Json response as dict

        Raises:
            AeonCloudError: occurs for any error encountered.
        """

        url = f'{self.aeon_cloud_url}/runners'
        body = json.dumps({
            "count": count,
            "type": "aeon-runner",
            "credentials": self.credentials,
            "callbackUrl": self.callback_url
        })

        return await post(url, body)

    async def delete_runner(self, runner_id, force=False):
        """Deletes runner by id

        Args:
            runner_id: The id of the runner to delete
            force: force to delete (defaults to False)

        Returns:
            Json response as dict

        Raises:
            AeonCloudError: occurs for any error in DELETEing.
            NotFoundError: occurs if the url is not found.
        """

        url = f'{self.aeon_cloud_url}/runners/{runner_id}?force={force}'
        body = json.dumps({
            "credentials": self.credentials,
            "callbackUrl": self.callback_url
        })

        return await delete(url, body)

    async def delete_runners(self, force=False):
        """Deletes all runners

        Args:
            force: force to delete (defaults to False)

        Returns:
            Json response as dict

        Raises:
            AeonCloudError: occurs for any error in DELETEing.
            NotFoundError: occurs if the url is not found.
        """

        url = f'{self.aeon_cloud_url}/runners/delete-all?force={force}'
        body = json.dumps({
            "credentials": self.credentials,
            "callbackUrl": self.callback_url
        })

        return await delete(url, body)

    async def get_runner(self, runner_id):
        """Gets a runner by ID

        Args:
            url: runner id to get

        Returns:
            Json response as dict

        Raises:
            AeonCloudError: occurs for any error in GETing.
            NotFoundError: occurs if the url is not found.
        """

        url = f'{self.aeon_cloud_url}/runners/{runner_id}'

        return await get(url)

    async def get_runners(self):
        """Gets all runners.

        Returns:
            Json response as dict

        Raises:
            AeonCloudError: occurs for any error in GETing.
            NotFoundError: occurs if the url is not found.
        """

        url = f'{self.aeon_cloud_url}/runners'

        return await get(url)
