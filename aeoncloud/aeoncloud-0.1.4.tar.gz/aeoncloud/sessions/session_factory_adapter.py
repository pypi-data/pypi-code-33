"""Session Factor Adapter Interface"""
from aeoncloud.sessions.session_adapter import ISessionAdapter


class ISessionFactoryAdapter:
    """Creates or gets session based on settings.
    """

    def get_session(self, request_body=None) -> ISessionAdapter:
        """Gets or creates a blocking session adapter.

        Gets or creates a session adapter if no session is provided as
        'aeon.platform.session_id' in settings.

        Args:
            request_body: Aeon properties for the session configuration,
                only used if 'aeon.platform.session_id' is not set.

        Returns:
            ISessionAdapter

        Raises:
            AeonSessionError: occurs for any error in creating the session.
        """
        pass

    async def get_async_session(self, request_body=None) -> ISessionAdapter:
        """Gets or creates an async session adapter.

        Gets or creates a session adapter if no session is provided as
        'aeon.platform.session_id' in settings.

        Args:
            request_body: Aeon properties for the session configuration,
                only used if 'aeon.platform.session_id' is not set.

        Returns:
            ISessionAdapter

        Raises:
            AeonSessionError: occurs for any error in creating the session.
        """
        pass
