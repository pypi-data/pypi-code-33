"""Async (Non-Blocking) Http Client for Aeon Cloud"""

import aiohttp

from aeoncloud.exceptions.aeon_cloud_error import AeonCloudError
from aeoncloud.exceptions.not_found_error import NotFoundError

HEADERS = {'content-type': 'application/json'}


async def post(url, body) -> dict:
    """Posts a json body to the url

    Args:
        url: url to post
        body: dict json body

    Returns:
        Json response as dict

    Raises:
        AeonCloudError: occurs for any error in POSTing.
    """
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.post(url, data=body) as response:
            if response.status != 200:
                raise AeonCloudError('Error POSTing, status {}. Body {}.'.format(response.status,
                                                                                 await response.text()))
            return await response.json()


async def delete(url, body) -> dict:
    """Deletes a json body given a url

    Args:
        url: url to request a delete from
        body: dict json body

    Returns:
        Json response as dict

    Raises:
        AeonCloudError: occurs for any error in DELETEing.
        NotFoundError: occurs if the url is not found.
    """

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.delete(url, data=body) as response:
            if response.status == 404:
                raise NotFoundError('Error, could not find {}'.format(url))
            if response.status != 200:
                raise AeonCloudError('Error DELETEing, status {}.  Body {}.'.format(response.status,
                                                                                    await response.text()))
            return await response.json()


async def get(url) -> dict:
    """Gets the JSON content from the given url

    Args:
        url: url to to request from

    Returns:
        Json response as dict

    Raises:
        AeonCloudError: occurs for any error in GETing.
        NotFoundError: occurs if the url is not found.
    """

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 404:
                raise NotFoundError('Error, could not find {}'.format(url))
            if response.status != 200:
                raise AeonCloudError('Error POSTing, status {}.  Body {}.'.format(response.status,
                                                                                  await response.text()))
            return await response.json()
