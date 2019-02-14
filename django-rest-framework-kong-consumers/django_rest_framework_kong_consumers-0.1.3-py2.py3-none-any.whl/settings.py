import os
from django.conf import settings


def env_to_bool(name, default=False):
    var = os.environ.get(name, '')
    res = default
    if default == True:
        if var in ['false', 'False', 0]:
            res = False
    else:
        if var in ['true', 'True', 1]:
            res = True
    return res


KONG_CONSUMER_ID_HEADER = getattr(settings, 'KONG_CONSUMER_ID_HEADER', os.environ.get('KONG_CONSUMER_ID_HEADER', 'HTTP_X_CONSUMER_USERNAME'))
KONG_ANONYMOUS_CONSUMER_ID = getattr(settings, 'KONG_ANONYMOUS_CONSUMER_ID', os.environ.get('KONG_ANONYMOUS_CONSUMER_ID', 'anonymous'))
KONG_ANONYMOUS_CONSUMER_HEADER = getattr(settings, 'KONG_ANONYMOUS_CONSUMER_HEADER', os.environ.get('KONG_ANONYMOUS_CONSUMER_HEADER', 'HTTP_X_ANONYMOUS_COMSUMER'))
KONG_CREATE_CONSUMER_GROUPS = getattr(settings, 'KONG_CREATE_CONSUMER_GROUPS', env_to_bool('KONG_CREATE_CONSUMER_GROUPS', True))
