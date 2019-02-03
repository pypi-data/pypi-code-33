"""Asyncronous (non-blocking) Http Session Adapter"""
from aeoncloud.exceptions.aeon_session_error import AeonSessionError
from aeoncloud.sessions.async_http_client import execute_command, execute_async_command, quit_session
from aeoncloud.sessions.session_adapter import ISessionAdapter


class AsyncHttpSessionAdapter(ISessionAdapter):
    """Session service class

    Supports executing commands and quiting a session.
    """

    def __init__(self, session_id, base_url=None):
        self.base_url = base_url
        self.session_id = session_id

    async def execute_command(self, command, arguments) -> None:
        """Executes an Aeon command with the given arguments.

        Args:
            command: String name of the Aeon command to be executed.
            arguments: List of arguments associated with the command.

        Returns:
            None

        Raises:
            AeonSessionError: occurs for any error in sending the command.
            NotFoundError: occurs if the session is not found
        """

        if not self.session_id:
            raise AeonSessionError('Session not initialized')

        await execute_command(self.session_id, {
            'command': command,
            'args': arguments
        }, self.base_url)

    async def execute_async_command(self, command, arguments) -> None:
        """Executes an Aeon command with the given arguments in async mode
            which allows for a callback endpoint to be provided for the 
            command results to be sent.

        Args:
            command: String name of the Aeon command to be executed.
            arguments: List of arguments associated with the command.

        Returns:
            None

        Raises:
            AeonSessionError: occurs for any error in sending the command.
        """

        if not self.session_id:
            raise AeonSessionError('Session not initialized')

        await execute_async_command(self.session_id, {
            'command': command,
            'args': arguments
        }, self.base_url)

    async def quit_session(self) -> None:
        """Closes an active session

        Returns:
            None

        Raises:
            AeonSessionError: occurs for any error in sending the delete request
                or errors returned from the request.
            NotFoundError: occurs if the session is not found
        """

        if not self.session_id:
            raise AeonSessionError('Session not initialized')
        await quit_session(self.session_id, self.base_url)
