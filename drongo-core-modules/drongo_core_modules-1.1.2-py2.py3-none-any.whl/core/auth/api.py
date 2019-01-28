from drongo.status_codes import HttpStatusCodes
from drongo.utils import dict2
from drongo_utils.endpoint import APIEndpoint
from drongo_utils.helpers import URLHelper


class UserMe(APIEndpoint):
    __url__ = '/users/me'
    __http_methods__ = ['GET']

    def init(self):
        self.token = self.ctx.auth.get('token')
        self.auth = self.ctx.modules.auth
        self.user_token_svc = self.auth.services.UserForTokenService(
            token=self.token
        )

    def validate(self):
        if self.token is None:
            self.valid = False
            self.error(message='No auth token specified.')
            return

        self.user = self.user_token_svc.call()
        if self.user is None:
            self.valid = False
            self.errors.setdefault('_', []).append(
                'Invalid or unauthorized token.'
            )

    def call(self):
        return {
            'username': self.user.username,
            'is_authenticated': True,
            'is_superuser': self.user.superuser
        }


class UserCreate(APIEndpoint):
    __url__ = '/users'
    __http_methods__ = ['POST']

    def init(self):
        self.query = self.ctx.request.json
        self.auth = self.ctx.modules.auth
        self.create_user_svc = self.auth.services.UserCreateService(
            username=self.query.get('username'),
            password=self.query.get('password'),
            active=self.auth.config.active_on_register
        )

    def validate(self):
        UsernameValidator = self.ctx.modules.auth.config.username_validator
        PasswordValidator = self.ctx.modules.auth.config.password_validator
        self.valid = (
            self.valid and
            UsernameValidator(self, self.query.get('username')).validate()
        )

        self.valid = (
            self.valid and
            PasswordValidator(self, self.query.get('password')).validate()
        )

        if self.create_user_svc.check_exists():
            self.error(
                group='username',
                message='Username already exists.'
            )
            self.valid = False

    def call(self):
        self.create_user_svc.call()
        return 'OK'


class UserChangePassword(APIEndpoint):
    __url__ = '/users/operations/change-password'
    __http_methods__ = ['POST']

    def init(self):
        self.query = dict2.from_dict(self.ctx.request.json)
        self.auth = self.ctx.modules.auth

        if not self.query.username:
            self.query.username = self.ctx.auth.user.username

        self.login_svc = self.auth.services.UserLoginService(
            username=self.query.username,
            password=self.query.password
        )

        self.change_pwd_svc = self.auth.services.UserChangePasswordService(
            username=self.query.username,
            password=self.query.new_password
        )

    def validate(self):
        UsernameValidator = self.ctx.modules.auth.config.username_validator
        PasswordValidator = self.ctx.modules.auth.config.password_validator

        self.valid = (
            self.valid and
            UsernameValidator(self, self.query.get('username')).validate()
        )

        self.valid = (
            self.valid and
            PasswordValidator(self, self.query.get('new_password')).validate()
        )

        # Let superuser change password without old password
        if 'user' in self.ctx.auth and self.ctx.auth.user.superuser:
            return

        if 'password' not in self.query or not self.query.password:
            self.error(
                group='password',
                message='Current password is required.'
            )
            return

        if not self.login_svc.check_credentials():
            self.error(
                group='_',
                message='Invalid username or password.'
            )

    def call(self):
        self.change_pwd_svc.call()
        return 'OK'


class UserLogin(APIEndpoint):
    __url__ = '/users/operations/login'
    __http_methods__ = ['POST']

    def init(self):
        self.query = dict2.from_dict(self.ctx.request.json)
        self.auth = self.ctx.modules.auth

        self.login_svc = self.auth.services.UserLoginService(
            username=self.query.username,
            password=self.query.password
        )

    def validate(self):
        UsernameValidator = self.ctx.modules.auth.config.username_validator
        PasswordValidator = self.ctx.modules.auth.config.password_validator
        self.valid = (
            self.valid and
            UsernameValidator(self, self.query.get('username')).validate()
        )

        self.valid = (
            self.valid and
            PasswordValidator(self, self.query.get('password')).validate()
        )

        if not self.valid:
            return

        if not self.login_svc.check_credentials():
            self.valid = False
            self.error(message='Invalid username or password.')
            self.auth.services.UserLogoutService().call(self.ctx)

    def call(self):
        token = self.login_svc.create_token()

        self.status(HttpStatusCodes.HTTP_202)
        return {
            'token': token
        }


class UserLogout(APIEndpoint):
    __url__ = '/users/operations/logout'
    __http_methods__ = ['GET']

    def init(self):
        self.auth = self.ctx.modules.auth
        self.token = self.ctx.auth.get('token')

    def call(self):
        self.auth.services.UserLogoutService().expire_token(self.token)
        self.status(HttpStatusCodes.HTTP_202)
        return 'Bye!'


class UserTokenRefresh(APIEndpoint):
    __url__ = '/users/operations/refresh-token'
    __http_methods__ = ['GET']

    def init(self):
        self.auth = self.ctx.modules.auth
        self.token = self.ctx.auth.get('token')

    def call(self):
        token = self.auth.services.UserTokenRefresh(self.token).call()
        return {'token': token}


class UserList(APIEndpoint):
    __url__ = '/users'
    __http_methods__ = 'GET'

    def init(self):
        self.auth = self.ctx.modules.auth
        self.user = self.ctx.auth.user

    def validate(self):
        if self.user and self.user.superuser:
            return True

        self.error(
            group='_',
            message='Access denied.'
        )

    def _transform(self, obj):
        return {
            'username': obj.username,
            'active': obj.active,
            'superuser': obj.superuser
        }

    def call(self):
        return list(map(
            self._transform,
            self.auth.services.UserListService().call(self.ctx)
        ))


class GroupList(APIEndpoint):
    __url__ = '/groups'
    __http_methods__ = 'GET'

    def init(self):
        self.auth = self.ctx.modules.auth
        self.user = self.ctx.auth.user

    def validate(self):
        if self.user and self.user.superuser:
            return True

        self.error(
            group='_',
            message='Access denied.'
        )

    def _transform(self, obj):
        return {
            'name': obj.name,
            'users': obj.users
        }

    def call(self):
        return list(map(
            self._transform,
            self.auth.services.GroupListService().call()
        ))


class GroupCreate(APIEndpoint):
    __url__ = '/groups'
    __http_methods__ = 'POST'

    def init(self):
        self.auth = self.ctx.modules.auth
        self.user = self.ctx.auth.user
        self.obj = self.ctx.request.json

    def validate(self):
        if self.user and self.user.superuser:
            return True

        self.error(
            group='_',
            message='Access denied.'
        )

    def call(self):
        self.auth.services.GroupCreateService(name=self.obj['name']).call()
        return 'OK'


class GroupDelete(APIEndpoint):
    __url__ = '/groups/{group}'
    __http_methods__ = 'DELETE'

    def init(self):
        self.auth = self.ctx.modules.auth
        self.user = self.ctx.auth.user

    def validate(self):
        if self.user and self.user.superuser:
            return True

        self.error(
            group='_',
            message='Access denied.'
        )

    def call(self):
        self.auth.services.GroupDeleteService(name=self.group).call()
        return 'OK'


class GroupUserAdd(APIEndpoint):
    __url__ = '/groups/{group}/users'
    __http_methods__ = 'POST'

    def init(self):
        self.auth = self.ctx.modules.auth
        self.user = self.ctx.auth.user

    def validate(self):
        if self.user and self.user.superuser:
            return True

        self.error(
            group='_',
            message='Access denied.'
        )

    def call(self):
        self.auth.services.GroupUserAddService(
            name=self.group,
            username=self.ctx.request.json['username']
        ).call()
        return 'OK'


class GroupUserDelete(APIEndpoint):
    __url__ = '/groups/{group}/users/{username}'
    __http_methods__ = 'DELETE'

    def init(self):
        self.auth = self.ctx.modules.auth
        self.user = self.ctx.auth.user

    def validate(self):
        if self.user and self.user.superuser:
            return True

        self.error(
            group='_',
            message='Access denied.'
        )

    def call(self):
        self.auth.services.GroupUserDeleteService(
            name=self.group,
            username=self.username
        ).call()


class GroupUserList(APIEndpoint):
    __url__ = '/groups/{group}/users'

    def init(self):
        self.auth = self.ctx.modules.auth
        self.user = self.ctx.auth.user

    def validate(self):
        if self.user and self.user.superuser:
            return True

        self.error(
            group='_',
            message='Access denied.'
        )

    def call(self):
        return self.auth.services.GroupUserListService(name=self.group).call()


class GroupForUserList(APIEndpoint):
    __url__ = '/users/{username}/groups'

    def init(self):
        self.auth = self.ctx.modules.auth
        self.user = self.ctx.auth.user

    def validate(self):
        if self.user and self.user.superuser:
            return True

        self.error(
            group='_',
            message='Access denied.'
        )

    def call(self):
        return self.auth.services.GroupsForUserListService(
            username=self.username).call()


class ObjectOwnerSet(APIEndpoint):
    __url__ = '/objects/{_type}/{_id}/operations/set-owner'
    __http_methods__ = 'POST'

    def init(self):
        self.auth = self.ctx.modules.auth
        self.user = self.ctx.auth.user
        self.obj = self.ctx.request.json

    def validate(self):
        if self.user and self.user.superuser:
            return True

        self.error(
            group='_',
            message='Access denied.'
        )

    def call(self):
        self.auth.services.ObjectOwnerSetService(
            object_type=self._type,
            object_id=self._id,
            username=self.obj.get('username')
        ).call()
        return 'OK'


class ObjectOwnerGet(APIEndpoint):
    __url__ = '/objects/{_type}/{_id}/owner'
    __http_methods__ = 'GET'

    def init(self):
        self.auth = self.ctx.modules.auth
        self.user = self.ctx.auth.user

    def validate(self):
        if self.user and self.user.superuser:
            return True

        self.error(
            group='_',
            message='Access denied.'
        )

    def call(self):
        return self.auth.services.ObjectOwnerGetService(
            object_type=self._type,
            object_id=self._id
        ).call()


class PermissionSet(APIEndpoint):
    __url__ = '/permissions/{_id}'
    __http_methods__ = 'POST'

    def init(self):
        self.auth = self.ctx.modules.auth
        self.user = self.ctx.auth.user
        self.obj = self.ctx.request.json

    def validate(self):
        if self.user and self.user.superuser:
            return True

        self.error(
            group='_',
            message='Access denied.'
        )

    def call(self):
        self.auth.services.PermissionSetService(
            permission_id=self._id,
            client=self.obj.get('client')
        ).call()
        return 'OK'


class PermissionUnset(APIEndpoint):
    __url__ = '/permissions/{_id}/unset'
    __http_methods__ = 'POST'

    def init(self):
        self.auth = self.ctx.modules.auth
        self.user = self.ctx.auth.user
        self.obj = self.ctx.request.json

    def validate(self):
        if self.user and self.user.superuser:
            return True

        self.error(
            group='_',
            message='Access denied.'
        )

    def call(self):
        self.auth.services.PermissionUnsetService(
            permission_id=self._id,
            client=self.obj.get('client')
        ).call()
        return 'OK'


class ObjectPermissionSet(APIEndpoint):
    __url__ = '/permissions/{_id}/objects/{object_type}/{object_id}'
    __http_methods__ = 'POST'

    def init(self):
        self.auth = self.ctx.modules.auth
        self.user = self.ctx.auth.user
        self.obj = self.ctx.request.json

    def validate(self):
        if self.user and self.user.superuser:
            return True

        self.error(
            group='_',
            message='Access denied.'
        )

    def call(self):
        self.auth.services.ObjectPermissionSetService(
            object_type=self.object_type,
            object_id=self.object_id,
            permission_id=self._id,
            client=self.obj.get('client')
        ).call()
        return 'OK'


class ObjectPermissionUnset(APIEndpoint):
    __url__ = '/permissions/{_id}/objects/{object_type}/{object_id}/unset'
    __http_methods__ = 'POST'

    def init(self):
        self.auth = self.ctx.modules.auth
        self.user = self.ctx.auth.user
        self.obj = self.ctx.request.json

    def validate(self):
        if self.user and self.user.superuser:
            return True

        self.error(
            group='_',
            message='Access denied.'
        )

    def call(self):
        self.auth.services.ObjectPermissionUnsetService(
            object_type=self.object_type,
            object_id=self.object_id,
            permission_id=self._id,
            client=self.obj.get('client')
        ).call()
        return 'OK'


class PermissionCheck(APIEndpoint):
    __url__ = '/permissions/{_id}/check'
    __http_methods__ = 'POST'

    def init(self):
        self.auth = self.ctx.modules.auth
        self.user = self.ctx.auth.user
        self.obj = self.ctx.request.json

    def validate(self):
        if self.user and self.user.superuser:
            return True

        self.error(
            group='_',
            message='Access denied.'
        )

    def call(self):
        return self.auth.services.PermissionCheckService(
            permission_id=self._id,
            username=self.obj.get('username')
        ).call()


class ObjectPermissionCheck(APIEndpoint):
    __url__ = '/permissions/{_id}/objects/{object_type}/{object_id}/check'
    __http_methods__ = 'POST'

    def init(self):
        self.auth = self.ctx.modules.auth
        self.user = self.ctx.auth.user
        self.obj = self.ctx.request.json

    def validate(self):
        if self.user and self.user.superuser:
            return True

        self.error(
            group='_',
            message='Access denied.'
        )

    def call(self):
        return self.auth.services.ObjectPermissionCheckService(
            object_type=self.object_type,
            object_id=self.object_id,
            permission_id=self._id,
            username=self.obj.get('username')
        ).call()


class PermissionList(APIEndpoint):
    __url__ = '/permissions/for/{client}'
    __http_methods__ = 'GET'

    def init(self):
        self.auth = self.ctx.modules.auth
        self.user = self.ctx.auth.user

    def validate(self):
        if self.user and self.user.superuser:
            return True

        self.error(
            group='_',
            message='Access denied.'
        )

    def call(self):
        return self.auth.services.PermissionListForClientService(
            client=self.client
        ).call()


AVAILABLE_API = [
    UserMe,
    UserCreate,
    UserLogin,
    UserLogout,
    UserTokenRefresh,
    UserChangePassword,
    UserList,

    GroupCreate,
    GroupDelete,
    GroupList,

    GroupUserAdd,
    GroupUserDelete,
    GroupUserList,
    GroupForUserList,

    ObjectOwnerSet,
    ObjectOwnerGet,

    PermissionSet,
    PermissionUnset,
    ObjectPermissionSet,
    ObjectPermissionUnset,
    PermissionCheck,
    ObjectPermissionCheck,

    PermissionList
]


class AuthAPI(object):
    def __init__(self, app, module, base_url):
        self.app = app
        self.module = module
        self.base_url = base_url

        self.init_endpoints()

    def init_endpoints(self):
        for endpoint in AVAILABLE_API:
            URLHelper.endpoint(
                app=self.app,
                klass=endpoint,
                base_url=self.base_url
            )
