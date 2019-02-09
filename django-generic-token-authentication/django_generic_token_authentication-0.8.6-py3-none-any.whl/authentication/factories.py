from django.core import signing

from generic.helpers import get_uuid1

from authentication.models import AuthToken
from authentication.helper import get_rand_str


def token_factory(model_class=AuthToken, user=None):
    """
    Creates and returns a new access and refresh token pair
    """
    id = get_uuid1()
    key = signing.dumps({'token_id': str(id),
                         'rand': get_rand_str(8)}, salt='access_token', compress=True)

    salt = user.password + user.username
    refresh_key = signing.dumps({'rand': get_rand_str(64)}, salt=salt, compress=True)

    return model_class(id=id, refresh_key=refresh_key, user=user), key
