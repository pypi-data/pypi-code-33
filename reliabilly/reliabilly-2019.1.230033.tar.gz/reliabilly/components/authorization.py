import json

from reliabilly.components.services.okta import check_session
from reliabilly.settings import Settings, Constants
from reliabilly.components.tools.secret_manager import SecretManager


def get_permitted_no_authentication(request):
    try:
        if request.method == Constants.OPTIONS_REQUEST:
            return True
        route_path_split = list(filter(None, request.path.split(Constants.FORWARD_SLASH)))
        return f'{route_path_split[-1]}{Constants.FORWARD_SLASH}' in \
               [Constants.PING_ROUTE, Constants.VERSION_ROUTE, Constants.HEALTH_ROUTE, Constants.CALENDAR_ROUTE]
    except Exception:  # pylint: disable=broad-except
        return False


def get_acceptable_token_list(version=Settings.VERSION, secret_manager=SecretManager()):
    token_list = [version]
    if Settings.ENV and Settings.ENV != Constants.LOCAL:
        tokens = secret_manager.get_secret(Constants.DEV_TOKEN)
        if tokens:
            token_list.extend(json.loads(tokens))
    return token_list


class Authorization:
    """ DependencyProvider giving services authorization """

    @staticmethod
    def get_auth_token(request):
        if not request or not request.headers:
            return None
        auth_token = request.headers.get(Constants.AUTHORIZATION_HEADER, None)
        return auth_token

    @staticmethod
    def get_auth_token_log(request):
        auth_token = Authorization.get_auth_token(request)
        if auth_token:
            if len(auth_token) > 3:
                return auth_token[-3:]
        return Constants.NONE

    @staticmethod
    def is_permitted(request, token_list_func=get_acceptable_token_list, check_session_fn=check_session):
        if get_permitted_no_authentication(request):
            return True
        auth_token = Authorization.get_auth_token(request)
        if not auth_token:
            return False
        if Constants.BEARER_PREFIX in auth_token:
            return check_session_fn(auth_token)
        return auth_token in token_list_func()

    @staticmethod
    def get_unauthorized_response():
        return Constants.UNAUTHORIZED_CODE, Constants.EMPTY, Constants.UNAUTHORIZED_REQUEST_MESSAGE
