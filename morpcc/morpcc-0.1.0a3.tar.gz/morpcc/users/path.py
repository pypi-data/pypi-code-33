from .model import UserModelUI, UserCollectionUI
from ..app import App
from morpfw.authn.pas.user.path import get_user, get_user_collection


@App.path(model=UserCollectionUI, path='/manage-users')
def get_user_collection_ui(request):
    newreq = request.get_authn_request()
    col = get_user_collection(newreq)
    return UserCollectionUI(newreq, col)


@App.path(model=UserModelUI, path='/manage-users/{username}',
          variables=lambda obj: {'username': obj.model.data['username']})
def get_user_model_ui(request, username):
    newreq = request.get_authn_request()
    user = get_user(newreq, username)
    col = get_user_collection(newreq)
    return UserModelUI(newreq, user, UserCollectionUI(newreq, col))
