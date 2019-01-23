import copy
import json
import uuid
from copy import copy
from longitude import config
from sanic.log import logger
import aiohttp

from sanic_oauth.providers import OAuth2Client
from sanic_session import InMemorySessionInterface

from longitude.auth.models import UserModel
from longitude.response import json as json_response

session_interface = InMemorySessionInterface()


class MicrosoftClient(OAuth2Client):
    access_token_url = 'https://login.microsoftonline.com/{}oauth2/v2.0/token'.format(
        config.LONGITUDE_AUTH_MICROSOFT_CLIENT_TENANT + '/'
            if config.LONGITUDE_AUTH_MICROSOFT_CLIENT_TENANT
            else ''
    )
    authorize_url = 'https://login.microsoftonline.com/{}oauth2/v2.0/authorize'.format(
        config.LONGITUDE_AUTH_MICROSOFT_CLIENT_TENANT + '/'
            if config.LONGITUDE_AUTH_MICROSOFT_CLIENT_TENANT
            else ''
    )

    name = 'microsoft'

    def user_parse(cls, data):
        pass


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

        client_id = config.LONGITUDE_AUTH_MICROSOFT_CLIENT_ID
        client_secret = bytes.fromhex(config.LONGITUDE_AUTH_MICROSOFT_CLIENT_SECRET).decode()
        secret_key = str(uuid.uuid4())

    @app.get(cfg.oauth_redirect_path)
    @app.post(cfg.oauth_redirect_path)
    async def oauth(request):
        client = MicrosoftClient(
            request.app.async_session,
            client_id=cfg.client_id,
            client_secret=cfg.client_secret
        )

        do_generate_url = not all(
            param in request.args or (
                isinstance(request.json, dict) and
                param in request.json
            )
            for param
            in ('code', 'redirect_uri')
        )

        if do_generate_url:
            return json_response({
                'redirect_uri': client.get_authorize_url(
                    state=cfg.secret_key,
                ) + '&redirect_uri={}&scope=user.read openid email'
            })

        code = request.args.get('code', (request.json or {}).get('code', None))
        redirect_uri = request.args.get('redirect_uri', (request.json or {}).get('redirect_uri', None))

        access_token, data = await client.get_access_token(
            code,
            redirect_uri=redirect_uri
        )

        client.access_token = None

        res = await client.request('get', 'https://graph.microsoft.com/v1.0/me/', headers={
            'Authorization': f'Bearer {access_token}'
        })

        res.raise_for_status()

        user = await res.json()

        logger.info('Microsoft login success: {}'.format(json.dumps(user, indent=2)))

        user_model = UserModel(request.app.sql_model, request.args['sql_conn'])

        user = await user_model.get(
            columns=('id', 'username', 'password'),
            email=user['userPrincipalName']
        )

        user['password'] = user['password'].decode()

        login_request = copy(request)
        login_request.method = 'POST'
        login_request.parsed_json = user

        login_function = next(x for x in request.app.blueprints['auth_bp'].routes if x[1] == '/')[0]

        return await login_function(login_request)

