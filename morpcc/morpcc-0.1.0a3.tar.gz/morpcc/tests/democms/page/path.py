from ..app import App
from .model import PageModel, PageCollection
from .modelui import PageModelUI, PageCollectionUI
from .storage import PageStorage


def get_collection(request):
    storage = PageStorage(request)
    return PageCollection(request, storage)


def get_model(request, identifier):
    col = get_collection(request)
    return col.get(identifier)


@App.path(model=PageCollection, path='/api/v1/page')
def _get_collection(request):
    return get_collection(request)


@App.path(model=PageModel, path='/api/v1/page/{identifier}')
def _get_model(request, identifier):
    return get_model(request, identifier)


@App.path(model=PageCollectionUI, path='/page')
def get_collection_ui(request):
    col = get_collection(request)
    return PageCollectionUI(request, col)


@App.path(model=PageModelUI, path='/page/{identifier}')
def get_model_ui(request, identifier):
    col = get_collection(request)
    model = get_model(request, identifier)
    return PageModelUI(request, model, PageCollectionUI(request, col))
