import graphene

from flask_unchained.bundles.graphene import MutationsObjectType, QueriesObjectType

from . import types
from . import mutations


class SecurityBundleQueries(QueriesObjectType):
    role = graphene.Field(types.Role, id=graphene.ID(required=True))
    roles = graphene.List(types.Role)

    user = graphene.Field(types.User, id=graphene.ID(required=True))
    users = graphene.List(types.User)

    user_role = graphene.Field(types.UserRole, id=graphene.ID(required=True))
    user_roles = graphene.List(types.UserRole)


class SecurityBundleMutations(MutationsObjectType):
    login = mutations.LoginUser.Field()
    logout = mutations.LogoutUser.Field()

    create_user = mutations.RegisterUser.Field()
    edit_user = mutations.EditUser.Field()
    delete_user = mutations.DeleteUser.Field()
