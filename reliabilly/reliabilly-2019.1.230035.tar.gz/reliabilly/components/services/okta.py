from reliabilly.components.logger import Logger
from reliabilly.settings import Settings, Constants
from reliabilly.components.web.http_requestor import HttpRequestor


def check_session(session_token, http_client=HttpRequestor(), logger=Logger()):
    try:
        response = http_client.get(Settings.SESSION_URL.format(session_token=session_token)).json()
        return response.get(Constants.STATUS, Constants.EMPTY) == Constants.OKTA_ACTIVE_STATUS
    except Exception as ex:  # pylint: disable=broad-except
        logger.error(f'Error checking session. ex: {ex}')
        return False
