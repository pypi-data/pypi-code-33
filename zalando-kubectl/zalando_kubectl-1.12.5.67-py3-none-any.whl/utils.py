import jwt
import zign.api


def auth_token():
    return zign.api.get_token('kubectl', ['uid'])


def _token_username():
    decoded_token = jwt.decode(auth_token(), verify=False)
    if decoded_token.get("https://identity.zalando.com/realm") == "users":
        return decoded_token.get("https://identity.zalando.com/managed-id")


def current_user():
    return zign.api.get_config().get('user') or _token_username()


def auth_headers():
    return {'Authorization': 'Bearer {}'.format(auth_token())}


def get_api_server_url(config):
    try:
        return config['api_server']
    except Exception:
        raise Exception("Unable to determine API server URL, please run zkubectl login")
