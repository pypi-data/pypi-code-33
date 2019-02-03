"""Asyncrounous (non-blocking) Http Client"""
import json

import aiohttp

from aeoncloud.exceptions.aeon_session_error import AeonSessionError
from aeoncloud.exceptions.not_found_error import NotFoundError

DEFAULT_BASE_URL = 'http://localhost:8080/api/v1/'


async def create_session(body, base_url=None) -> str:
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

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=body) as response:
            if response.status != 201:
                raise AeonSessionError(f'Error creating session, status {response.status}.')
            content = await response.text()
            return json.loads(content)['sessionId']

    raise AeonSessionError('Error occured in attemping to create session.')


async def execute_command(session_id, body, base_url=None) -> dict:
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

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=body) as response:
            if response.status == 404:
                raise NotFoundError(url)
            if response.status != 200:
                raise AeonSessionError(f'Error executing command, status {response.status}.')
            content = await response.text()
            return json.loads(content)

    raise AeonSessionError('Error occured in attemping to execute command.')


async def execute_async_command(session_id, body, base_url=None) -> dict:
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

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=body) as response:
            if response.status == 404:
                raise NotFoundError(url)
            if response.status != 200:
                raise AeonSessionError(f'Error executing command, status {response.status}.')
            content = await response.text()
            return json.loads(content)

    raise AeonSessionError('Error occured in attemping to execute command.')


async def quit_session(session_id, base_url=None) -> None:
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

    async with aiohttp.ClientSession() as session:
        async with session.delete(url) as response:
            if response.status == 404:
                raise NotFoundError(url)
            if response.status != 200:
                raise AeonSessionError(f'Error quitting session, status {response.status}.')
            await response.text()
