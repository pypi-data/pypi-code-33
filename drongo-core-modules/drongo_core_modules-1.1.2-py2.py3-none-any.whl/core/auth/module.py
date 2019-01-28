import logging

from drongo_modules.core.database import Database
from drongo_modules.core.module import Module

from .middleware import AuthMiddleware
from .validators import PasswordValidator, UsernameValidator


class Auth(Module):
    """Drongo module for authentication and authorization"""

    __default_config__ = {
        'api_base_url': '/api/auth',

        'create_admin_user': True,
        'admin_user': 'admin',
        'admin_password': 'admin',

        'active_on_register': False,

        'token_secret': 'drongo.auth.secret',
        'token_age': 7 * 24 * 60 * 60,  # A week (in seconds)

        # Validators
        'username_validator': UsernameValidator,
        'password_validator': PasswordValidator
    }

    logger = logging.getLogger('drongo_modules.core.auth')

    def init(self, config):
        self.logger.info('Initializing [auth] module.')

        self.app.context.modules.auth = self

        self.database = self.app.context.modules.database[config.database]

        if self.database.type == Database.MONGO:
            from .backends._mongo import services
            self.services = services

        elif self.database.type == Database.POSTGRES:
            from .backends._postgres import services
            self.services = services

        else:
            raise NotImplementedError

        services.AuthServiceBase.init(module=self)

        if config.create_admin_user:
            try:
                services.UserCreateService(
                    username=config.admin_user,
                    password=config.admin_password,
                    active=True,
                    superuser=True
                ).call()
            except Exception as e:
                self.logger.info(str(e))

        self.app.add_middleware(AuthMiddleware())
        self.init_api()

    def init_api(self):
        from .api import AuthAPI
        self.api = AuthAPI(
            app=self.app,
            module=self,
            base_url=self.config.api_base_url
        )

    def object_owner_set(self, object_type, object_id, username):
        return self.services.ObjectOwnerSetService(
            object_type, object_id, username
        ).call()

    def permission_check(self, permission_id, username):
        return self.services.PermissionCheckService(
            permission_id, username).call()

    def object_permission_check(self, object_type, object_id, permission_id,
                                username):
        return self.services.ObjectPermissionCheckService(
            object_type, object_id, permission_id, username).call()
