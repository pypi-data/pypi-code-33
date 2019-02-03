"""Session Factor Adapter"""
from aeoncloud.sessions.async_http_client import create_session as create_async_session
from aeoncloud.sessions.async_http_session_adapter import AsyncHttpSessionAdapter
from aeoncloud.sessions.http_client import create_session
from aeoncloud.sessions.http_session_adapter import HttpSessionAdapter
from aeoncloud.sessions.session_adapter import ISessionAdapter
from aeoncloud.sessions.session_factory_adapter import ISessionFactoryAdapter


class HttpSessionFactoryAdapter(ISessionFactoryAdapter):
    """Creates or gets session based on settings.
    """

    def get_session(self, request_body=None) -> ISessionAdapter:
        """Gets or creates a blocking session adapter.

        Gets or creates a session adapter if no session is provided as
        'aeon.platform.http.session.id' in settings.

        Args:
            request_body: Aeon properties for the session configuration,
                only used if 'aeon.platform.http.session.id' is not set.

        Returns:
            ISessionAdapter

        Raises:
            AeonSessionError: occurs for any error in creating the session.
            NotFoundError: occurs if the session is not found
        """

        base_url, session_id = self.__get_base_url_and_session_id(request_body)

        if not session_id:
            session_id = create_session(request_body, base_url)

        return HttpSessionAdapter(session_id=session_id, base_url=base_url)

    async def get_async_session(self, request_body=None) -> ISessionAdapter:
        """Gets or creates an async session adapter.

        Gets or creates a session adapter if no session is provided as
        'aeon.platform.http.session.id' in settings.

        Args:
            request_body: Aeon properties for the session configuration,
                only used if 'aeon.platform.http.session.id)' is not set.

        Returns:
            ISessionAdapter

        Raises:
            AeonSessionError: occurs for any error in creating the session.
            NotFoundError: occurs if the session is not found
        """

        base_url, session_id = self.__get_base_url_and_session_id(request_body)

        if not session_id:
            session_id = await create_async_session(request_body, base_url)

        return AsyncHttpSessionAdapter(session_id=session_id, base_url=base_url)

    @staticmethod
    def __get_base_url_and_session_id(request_body):
        """Returns a tuple based on the settings configuration

        Args:
            request_body: Aeon properties for the session configuration

        Returns:
            base_url, session_id
        """
        base_url = None
        session_id = None

        if request_body and 'settings' in request_body:
            if request_body and 'aeon.platform.http.url' in request_body['settings']:
                base_url = request_body['settings']['aeon.platform.http.url']

            if request_body and 'aeon.platform.http.session.id' in request_body['settings']:
                session_id = request_body['settings']['aeon.platform.http.session.id']

        return base_url, session_id
