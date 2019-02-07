import uuid
from django.core.cache import cache
from django.shortcuts import redirect
from django.urls import reverse
try:
    from singular_api.client import Client
    from singular_api.exceptions import SessionMismatchException
    from singular_api.settings import SINGULAR_URL
except ModuleNotFoundError:
    from .client import Client
    from .exceptions import SessionMismatchException
    from .settings import SINGULAR_URL


def build_full_url(request, url, hostname, connection_protocol='https', ):
    return '{}://{}{}'.format(connection_protocol, hostname, url)


def init_singular(request, client_id, hostname, register_user_endpoint,
                  connection_protocol='https', timeout=60,
                  singular_url=SINGULAR_URL):
    """
    init_singular endpoint is called from singular center when user wants to use this connector,
    works only with django
    :param request:
    :return django redirect obj:
    """

    callback_uri = request.GET.get('callback')
    state = uuid.uuid4()
    cache.set(state, callback_uri, timeout)
    redirect_uri = build_full_url(request,
                                  reverse(register_user_endpoint),
                                  hostname,
                                  connection_protocol)

    scopes = ['all']  # TODO replace with proper scopes
    client = Client(singular_url=singular_url)
    url = client.get_authorization_url(client_id,
                                       redirect_uri,
                                       state,
                                       scopes)

    return redirect(url)


def register_user_singular(request, client_id, client_secret, hostname,
                           register_user_endpoint,
                           connection_protocol='https',
                           connect_timeout=60,
                           read_timeout=60):
    """
    register_user_singular endpoint is called from singular after redirect in
    init_singular.
    :param request:
    :return token, refresh_token:

    """
    code = request.GET.get('code')
    state = request.GET.get('state')

    original_callback = cache.get(state)
    if original_callback is None:
        raise SessionMismatchException

    redirect_uri = build_full_url(request,
                                  reverse(register_user_endpoint),
                                  hostname,
                                  connection_protocol,)

    client = Client(connect_timeout=connect_timeout, read_timeout=read_timeout)
    token, refresh_token = client.register_user(client_id,
                                                client_secret,
                                                code,
                                                redirect_uri)
    return token, refresh_token
