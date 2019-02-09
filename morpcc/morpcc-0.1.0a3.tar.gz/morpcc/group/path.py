from .model import GroupModelUI, GroupCollectionUI
from ..app import App
from morpfw.authn.pas.group.path import get_group, get_group_collection


@App.path(model=GroupCollectionUI, path='/manage-groups')
def get_group_collection_ui(request):
    newreq = request.get_authn_request()
    col = get_group_collection(newreq)
    return GroupCollectionUI(newreq, col)


@App.path(model=GroupModelUI, path='/manage-groups/{groupname}',
          variables=lambda obj: {'groupname': obj.model.data['groupname']})
def get_group_model_ui(request, groupname):
    newreq = request.get_authn_request()
    col = get_group_collection(newreq)
    group = get_group(newreq, groupname)
    return GroupModelUI(newreq, group, GroupCollectionUI(newreq, col))
