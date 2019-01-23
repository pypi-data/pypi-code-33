from copy import copy

import pgpy

from datetime import datetime

from sanic_jwt import Initialize, utils, Authentication as OriginalAuthentication

from longitude.exceptions import InvalidUsage, AuthenticationFailed, InvalidAuthorizationHeader
from longitude import config
from longitude.auth.models import UserModel, UserTokenModel


SCOPE_ADMIN = 'admin'
SCOPE_USER = 'user'


class Authentication(OriginalAuthentication):

    async def _get_payload(self, user):
        user = copy(user)
        payload = await super()._get_payload(user)
        user.pop(self.config.user_id, None)
        payload.update(user)

        return payload


async def authenticate(request):

    if request.json is None:
        raise InvalidUsage("JSON payload required.")

    payload_invalid = not isinstance(request.json, dict) or \
                      len({'username', 'password'} & set(request.json.keys()))!=2

    if payload_invalid:
        raise InvalidUsage("JSON payload must include username and password.")

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    model = UserModel(request.app.sql_model, request.args['sql_conn'])

    user_columns = ['id', 'password']

    user_columns += list(request.app.auth.config.kwargs.get('extra_user_columns', []))

    if config.LONGITUDE_PERMISSION_PLUGIN_ENABLED:
        user_columns.append(('role_name', 'r.name'))
        user_columns.append(('is_admin', 'r.is_admin'))

    user = await model.get(username=username, columns=user_columns, active=True)

    if config.PGP_PRIVATE_KEY:
        db_crypted_password = pgpy.PGPMessage.from_blob(user['password'])
        db_password = config.PGP_PRIVATE_KEY[0].decrypt(db_crypted_password).message
    else:
        db_password = user['password'].decode('utf-8')

    if password != db_password:
        raise AuthenticationFailed("User not found or password incorrect.")

    user.pop('password')

    payload = {'user_id': user['id']}

    if request.app.auth.config.kwargs.get('_extend_payload', None):
        payload = await utils.call(
            request.app.auth.config.kwargs['_extend_payload'],
            payload,
            user=user,
            request=request
        )

    if config.LONGITUDE_PERMISSION_PLUGIN_ENABLED:
        payload['role'] = user['role_name']
        payload['is_admin'] = user['is_admin']

    return payload


async def retrieve_user(request, payload):
    model = UserModel(request.app.sql_model, request.args['sql_conn'])

    if not payload:
        raise InvalidAuthorizationHeader('Token expired')

    user = await model.get(payload['user_id'])

    user['exp_date'] = str(datetime.fromtimestamp(payload['exp']))
    user['user_id'] = user['id']

    if config.LONGITUDE_PERMISSION_PLUGIN_ENABLED:
        role_id = user.pop('_role_id')
        role_name = user.pop('_role_name')
        role_is_admin = user.pop('_role_is_admin')

        if role_id:
             role_fk_desc = {
                'id': role_id,
                'label': role_name
            }
        else:
            role_fk_desc = {
                'id': None,
                'label': 'user'
            }

        user['role'] = role_fk_desc
        user['is_admin'] = bool(role_is_admin)

    user['scopes'] = await get_user_scopes(user)

    return user


async def store_refresh_token(request, user_id, refresh_token):
    model = UserTokenModel(request.app.sql_model, request.args['sql_conn'])
    await model.upsert({
        'auth_user_id': user_id,
        'token': refresh_token
    })


async def retrieve_refresh_token(request, user_id, *args, **kwargs):
    model = UserTokenModel(request.app.sql_model, request.args['sql_conn'])
    ret = await model.get(auth_user_id=user_id, columns=('token',))
    return ret['token']


async def get_user_scopes(user, *args, **kwargs):
    scopes = set()

    if user.get('is_admin', False):
        scopes.add(SCOPE_ADMIN)

    if user.get('user_id', None) is not None:
        scopes.add(SCOPE_USER)

    if config.LONGITUDE_PERMISSION_PLUGIN_ENABLED and user.get('role', None):
        role = user['role'] if isinstance(user['role'], str) \
            else user['role']['label']

        if role != SCOPE_USER:
            scopes.add('role__' + role)

    return list(scopes)


def init_jwt(app, *args, **kwargs):

    # Rename Sanic JWT's extend_payload argument to call
    # call it from the authenticate method instead.
    # This way, we can inject, apart from the payload, the
    # user model and the request in the extend_payload method
    if 'extend_payload' in kwargs:
        kwargs['_extend_payload'] = kwargs.pop('extend_payload')

    Initialize(
        app,
        authenticate=kwargs.get('authenticate', authenticate),
        authentication_class=Authentication,
        retrieve_user=retrieve_user,
        secret=config.SECRET_KEY,
        refresh_token_enabled=True,
        store_refresh_token=store_refresh_token,
        retrieve_refresh_token=retrieve_refresh_token,
        expiration_delta=config.API_TOKEN_EXPIRATION,
        add_scopes_to_payload=get_user_scopes,
        *args,
        **kwargs
    )
