"""Blocking Http Client"""
import json

import requests

from aeoncloud.exceptions.aeon_session_error import AeonSessionError
from aeoncloud.exceptions.not_found_error import NotFoundError

DEFAULT_BASE_URL = 'http://localhost:8080/api/v1/'
HEADERS = {'content-type': 'application/json'}


def create_session(body, base_url=None) -> str:
    """Creates a new Aeon session with the provided settings as the body

    Args:
        body: Dictionary of settings
        base_url: Base host url (defaults to None)

    Returns:
        String session id

    Raises:
        AeonSessionError: occurs for any error in sending the command.
    """

    if base_url is None:
        base_url = DEFAULT_BASE_URL
    url = f'{base_url}sessions'
    session_body = json.dumps(body)

    response = requests.post(url, session_body, headers=HEADERS)
    if response.status_code != 201:
        raise AeonSessionError(f'Error creating session, status code {response.status_code}')
    return json.loads(response.content)['sessionId']


def execute_command(session_id, body, base_url=None) -> dict:
    """Executes an Aeon command with the given arguments.

    Args:
        session_id: String session ID
        body: Dictionary containing the command and arguments
        base_url: base url host (defaults to None)

    Returns:
        Response JSON

    Raises:
        AeonSessionError: occurs for any error in sending the command.
        NotFoundError: occurs if the session is not found
    """

    if base_url is None:
        base_url = DEFAULT_BASE_URL
    url = f'{base_url}sessions/{session_id}/commands'
    command_body = json.dumps(body)

    response = requests.post(url, command_body, headers=HEADERS)

    if response.status_code == 404:
        raise NotFoundError(url)
    if response.status_code != 200:
        raise AeonSessionError(f'Error executing command, status code {response.status_code}')

    return json.loads(response.content)


def execute_async_command(session_id, body, base_url=None) -> dict:
    """Executes an Aeon command with the given arguments and in async mode.

    Args:
        session_id: String session ID
        body: Dictionary containing the command and arguments
        base_url: base url host (defaults to None)

    Returns:
        Response JSON

    Raises:
        AeonSessionError: occurs for any error in sending the command.
        NotFoundError: occurs if the session is not found
    """

    if base_url is None:
        base_url = DEFAULT_BASE_URL
    url = f'{base_url}sessions/{session_id}/async_commands'
    command_body = json.dumps(body)

    response = requests.post(url, command_body, headers=HEADERS)

    if response.status_code == 404:
        raise NotFoundError(url)
    if response.status_code != 200:
        raise AeonSessionError(f'Error executing command, status code {response.status_code}')

    return json.loads(response.content)


def quit_session(session_id, base_url=None) -> None:
    """Closes the session

    Args:
        session_id: string session ID
        base_url: base url host (defaults to None)

    Returns:
        None

    Raises:
        AeonSessionError: occurs for any error in sending the command.
        NotFoundError: occurs if the session is not found
    """

    if base_url is None:
        base_url = DEFAULT_BASE_URL
    url = f'{base_url}sessions/{session_id}'

    response = requests.delete(url)

    if response.status_code == 404:
        raise NotFoundError(url)
    if response.status_code != 200:
        raise AeonSessionError(f'Error quiting session, status code {response.status_code}')
