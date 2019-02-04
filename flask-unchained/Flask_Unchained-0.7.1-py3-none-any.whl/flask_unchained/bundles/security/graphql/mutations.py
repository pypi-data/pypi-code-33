import graphene

from flask_unchained import unchained, current_app as app, lazy_gettext as _
from flask_unchained.bundles.security import (
    AuthenticationError, SecurityService, SecurityUtilsService, UserManager)
from flask_unchained.bundles.sqlalchemy import SessionManager, db
from graphql import GraphQLError

from . import types


security_service: SecurityService = unchained.get_local_proxy('security_service')
security_utils_service: SecurityUtilsService = \
    unchained.get_local_proxy('security_utils_service')

session_manager: SessionManager = unchained.get_local_proxy('session_manager')
user_manager: UserManager = unchained.get_local_proxy('user_manager')


class LoginUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(types.User)
    success = graphene.Boolean()

    def mutate(self, info, email, password, **kwargs):
        user = security_utils_service.user_loader(email)
        if not user or not security_utils_service.verify_password(user, password):
            # FIXME-identity
            identity_attrs = app.config.SECURITY_USER_IDENTITY_ATTRIBUTES
            error = f"Invalid {', '.join(identity_attrs)} and/or password."
            raise GraphQLError(error)

        try:
            security_service.login_user(user)
        except AuthenticationError as e:
            raise GraphQLError(str(e))

        return LoginUser(user=user, success=True)


class LogoutUser(graphene.Mutation):
    """Authentication mutation, deletes the session."""

    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        security_service.logout_user()
        return LogoutUser(success=True)


class RegisterUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        _login = graphene.Boolean()

    user = graphene.Field(types.User)
    logged_in = graphene.Boolean()
    success = graphene.Boolean()

    def mutate(self, email, password, _login=True, **kwargs):
        try:
            user = user_manager.create(email=email, password=password, commit=True)
        except db.ValidationErrors as e:
            raise GraphQLError(str(e))

        logged_in = security_service.register_user(user, allow_login=_login)
        return RegisterUser(user=user, logged_in=logged_in, success=True)


# FIXME make change password a separate mutation
class EditUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        email = graphene.String()
        password = graphene.String()
        new_password = graphene.String()

    user = graphene.Field(types.User)
    success = graphene.Boolean()

    def mutate(self, id, password=None, new_password=None, **kwargs):
        user = user_manager.get(id)
        if not user:
            raise GraphQLError(
                _('flask_unchained.bundles.security:error.user_does_not_exist'))

        if password or new_password and not all([password, new_password]):
            # FIXME-i18n
            raise GraphQLError('Both current password and new password are required.')

        if password:
            if not security_utils_service.verify_password(user, password):
                # FIXME-i18n
                raise GraphQLError('Incorrect password.')

            user.password = new_password
            user_manager.save(user, commit=True)

        fields = {k: v for k, v in kwargs.items() if hasattr(user, k)}
        try:
            user_manager.update(user, **fields, commit=True)
        except db.ValidationErrors as e:
            raise GraphQLError(str(e))

        return EditUser(user=user, success=True)


class DeleteUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    id = graphene.Int()
    success = graphene.Boolean()

    def mutate(self, id, **kwargs):
        user = user_manager.get(id)
        user_manager.delete(user, commit=True)
        return DeleteUser(id=id, success=True)
