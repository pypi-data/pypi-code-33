from .model import APIKeyModelUI, APIKeyCollectionUI
from ..app import App
from morpfw.authn.pas.apikey.path import get_apikey, get_apikey_collection


@App.path(model=APIKeyCollectionUI, path='/manage-apikeys')
def get_apikey_collection_ui(request):
    newreq = request.get_authn_request()
    col = get_apikey_collection(newreq)
    return APIKeyCollectionUI(newreq, col)


@App.path(model=APIKeyModelUI, path='/manage-apikeys/{identifier}',
          variables=lambda obj: {'identifier': obj.model.data['uuid']})
def get_apikey_model_ui(request, identifier):
    newreq = request.get_authn_request()
    apikey = get_apikey(newreq, identifier)
    col = get_apikey_collection(newreq)
    return APIKeyModelUI(newreq, apikey, APIKeyCollectionUI(newreq, col))
