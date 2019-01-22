from ..app import App
from .model import UserCollectionUI
from ..permission import ViewHome


@App.permission_rule(model=UserCollectionUI, permission=ViewHome)
def allow_view_user_collection(identity, model, permission):
    return True
