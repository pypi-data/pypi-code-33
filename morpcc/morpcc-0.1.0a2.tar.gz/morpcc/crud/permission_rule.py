from morpfw.crud import permission as crudpermission
from ..app import App
from .model import ModelUI, CollectionUI


@App.permission_rule(model=ModelUI, permission=crudpermission.All)
def allow_modelui_crud_permissions(identity, model, permission):
    # allow all logged in users
    return True


@App.permission_rule(model=CollectionUI, permission=crudpermission.All)
def allow_collectionui_crud_permissions(identity, model, permission):
    # allow all logged in users
    return True
