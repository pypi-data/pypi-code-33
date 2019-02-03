"""Blocking Http Client for Aeon Cloud"""
import json

import requests

from aeoncloud.exceptions.not_found_error import NotFoundError
from aeoncloud.exceptions.aeon_cloud_error import AeonCloudError

HEADERS = {'content-type': 'application/json'}


def post(url, body) -> dict:
    """Posts a json body to the url

    Args:
        url: url to post
        body: dict json body

    Returns:
        Json response as dict

    Raises:
        AeonCloudError: occurs for any error in POSTing.
    """

    response = requests.post(url, body, headers=HEADERS)

    if response.status_code != 200:
        raise AeonCloudError(f'Error POSTing, status code {response.status_code}\
            with message {response.content}')

    return json.loads(response.content)


def delete(url, body) -> dict:
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

    response = requests.delete(url, body, headers=HEADERS)

    if response.status_code == 404:
        raise NotFoundError(f'Error, could not find {url}')
    if response.status_code != 200:
        raise AeonCloudError(f'Error DELETEing, status code {response.status_code}\
            with message {response.content}')

    return json.loads(response.content)


def get(url) -> dict:
    """Gets the JSON content from the given url

    Args:
        url: url to to request from

    Returns:
        Json response as dict

    Raises:
        AeonCloudError: occurs for any error in GETing.
        NotFoundError: occurs if the url is not found.
    """

    response = requests.get(url, headers=HEADERS)

    if response.status_code == 404:
        raise NotFoundError(f'Error, could not find {url}')
    if response.status_code != 200:
        raise AeonCloudError(f'Error GETing, status code {response.status_code}\
            with message {response.content}')

    return json.loads(response.content)
