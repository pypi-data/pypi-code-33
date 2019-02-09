from ..app import App
from .model import AppRoot
from morpcc import permission
from webob import static
import os


@App.html(model=AppRoot, template='approot/index.pt', permission=permission.ViewHome)
def index(context, request):
    return {}
