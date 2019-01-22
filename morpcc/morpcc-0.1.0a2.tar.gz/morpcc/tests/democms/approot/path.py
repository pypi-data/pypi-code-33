from ..app import App
from .model import AppRoot


@App.path(model=AppRoot, path='/')
def get_approot(request):
    return AppRoot(request)
