import html
from .app import App


class Root(object):

    def __init__(self, request):
        self.request = request


@App.path(model=Root, path='/')
def get_root(request):
    return Root(request)
