from .app import App
from .root import Root
from morpfw.crud import permission as crudpermission
from . import permission


@App.permission_rule(model=Root, permission=permission.ViewHome)
def root_view_permission(identity, model, permission):
    return True


@App.permission_rule(model=Root, permission=permission.EditOwnProfile)
def edit_own_profile(identity, model, permission):
    return True
