import uuid

from longitude import config
import aiohttp
from sanic.response import redirect, text

from sanic_oauth.providers import UserInfo, OAuth2Client
from sanic_session import InMemorySessionInterface

session_interface = InMemorySessionInterface()


class MicrosoftClient(OAuth2Client):
    access_token_url = 'https://login.microsoftonline.com/{}/oauth2/token'.format(
        config.LONGITUDE_AUTH_MICROSOFT_CLIENT_STATE
    )
    authorize_url = 'https://login.microsoftonline.com/{}/oauth2/authorize'.format(
        config.LONGITUDE_AUTH_MICROSOFT_CLIENT_STATE
    )
    # base_url = 'https://www.googleapis.com/plus/v1/'
    name = 'microsoft'
    # user_info_url = 'https://www.googleapis.com/userinfo/v2/me'

    @classmethod
    def user_parse(cls, data) -> UserInfo:
        return {}


def init_microsoft(app):

    @app.middleware('request')
    async def add_session_to_request(request):
        # before each request initialize a session
        # using the client's request
        await session_interface.open(request)

    @app.middleware('response')
    async def save_session(request, response):
        # after each request save the session,
        # pass the response to set client cookies
        await session_interface.save(request, response)

    @app.listener('before_server_start')
    async def init_aiohttp_session(sanic_app, _loop) -> None:
        sanic_app.async_session = aiohttp.ClientSession()

    @app.listener('after_server_stop')
    async def close_aiohttp_session(sanic_app, _loop) -> None:
        await sanic_app.async_session.close()

    class cfg:
        oauth_redirect_path = '/auth/microsoft'
        redirect_uri = f'{config.APP_URL}'

        client_id = config.LONGITUDE_AUTH_MICROSOFT_CLIENT_ID
        client_secret = config.LONGITUDE_AUTH_MICROSOFT_CLIENT_SECRET

        # secret_key for session encryption
        # key must be 32 url-safe base64-encoded bytes
        # secret_key = uuid.uuid4() + uuid.uuid4()

    @app.get(cfg.oauth_redirect_path)
    async def oauth(request):
        client = MicrosoftClient(
            request.app.async_session,
            client_id=cfg.client_id,
            client_secret=cfg.client_secret
        )
        if 'code' not in request.args:
            return redirect(client.get_authorize_url(
                scope='email profile'
            ) + f'&redirect_uri={cfg.redirect_uri}')

        token, data = await client.get_access_token(
            request.args.get('code'),
            redirect_uri=cfg.redirect_uri
        )
        request['session']['token'] = token
        return redirect('/')

