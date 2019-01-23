from collections import OrderedDict

from longitude.models.sql import SQLCRUDModel
from longitude import config


class BaseUserModel(SQLCRUDModel):
    table_name = 'longitude_auth_user'

    select_columns = tuple(
        x
        for x
        in [
            'id',
            'name',
            'username',
            'email',
            ('_role_id', 'r.id'),
            ('_role_name', 'r.name'),
            ('_role_is_admin', 'r.is_admin')
        ]
        if (
            config.LONGITUDE_PERMISSION_PLUGIN_ENABLED or
            not x.startswith('r.')
        )
    )

    filters = (
        'username',
        'password',
        'email',
        'active'
    )

    joins = OrderedDict()
    if config.LONGITUDE_PERMISSION_PLUGIN_ENABLED:
        joins['r'] = '''
            LEFT JOIN longitude_permission_role r
                ON r.id=_t.role_id
        '''


class UserTokenModel(SQLCRUDModel):
    table_name = 'longitude_auth_user_refresh_token'

    filters = (
        'auth_user_id',
    )

    async def upsert(self, values, **filters):
        return await super().upsert(values, auth_user_id=values['auth_user_id'], **filters)

# The base user model may be overwritten if LONGITUDE_AUTH_PLUGIN_USER_MODEL
# option is set.
if config.LONGITUDE_AUTH_PLUGIN_USER_MODEL and \
    config.LONGITUDE_AUTH_PLUGIN_USER_MODEL != 'longitude.auth.models.UserModel':

    from importlib import import_module

    _cls, _module = (
        ''.join(reversed(x))
        for x
        in ''.join(reversed(config.LONGITUDE_AUTH_PLUGIN_USER_MODEL)).split('.', 1)
    )

    UserModel = getattr(import_module(_module), _cls)

else:
    class UserModel(BaseUserModel):
        pass
