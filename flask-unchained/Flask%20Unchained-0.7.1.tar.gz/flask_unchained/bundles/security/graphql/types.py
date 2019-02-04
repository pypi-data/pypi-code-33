import graphene

from flask_unchained.bundles.graphene import SQLAlchemyObjectType

from .. import models


class Role(SQLAlchemyObjectType):
    class Meta:
        model = models.Role
        only_fields = ('id', 'name')

    users = graphene.List(lambda: User)
    role_users = graphene.List(lambda: UserRole)


class User(SQLAlchemyObjectType):
    class Meta:
        model = models.User
        only_fields = ('id', 'email', 'active')

    roles = graphene.List(Role)
    user_roles = graphene.List(lambda: UserRole)


class UserRole(SQLAlchemyObjectType):
    class Meta:
        model = models.UserRole
        only_fields = ('id',)

    user = graphene.Field(User)
    role = graphene.Field(Role)
