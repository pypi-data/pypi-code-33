"""Session Adapter Interface"""

class ISessionAdapter:
    """Session service class

    Supports executing commands and quiting a session.
    """

    def execute_command(self, command, arguments) -> None:
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
        pass

    def execute_async_command(self, command, arguments):
        """Executes an Aeon command with the given arguments in async mode.

        Args:
            command: String name of the Aeon command to be executed.
            arguments: List of arguments associated with the command.

        Returns:
            None

        Raises:
            AeonSessionError: occurs for any error in sending the command.
            NotFoundError: occurs if the session is not found
        """
        pass

    def quit_session(self) -> None:
        """Closes an active session

        Returns:
            None

        Raises:
            AeonSessionError: occurs for any error in sending the delete request
                or errors returned from the request.
            NotFoundError: occurs if the session is not found
        """
        pass
