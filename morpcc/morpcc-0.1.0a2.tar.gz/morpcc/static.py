from .app import App
from webob import static
from pkg_resources import resource_filename
import os


class StaticRoot(object):

    def __init__(self, path):
        self.path = path


@App.path(model=StaticRoot, path='/static', absorb=True)
def get_staticroot(absorb):
    return StaticRoot(absorb)


@App.view(model=StaticRoot)
def serve_static(context, request):
    path = os.path.join(os.path.dirname(__file__), 'static_files')
    return request.get_response(static.FileApp(os.path.join(path, context.path)))


class DeformStaticRoot(object):

    def __init__(self, path):
        self.path = path


@App.path(model=DeformStaticRoot, path='/deform_static', absorb=True)
def get_deformstaticroot(absorb):
    return DeformStaticRoot(absorb)


@App.view(model=DeformStaticRoot)
def serve_deformstatic(context, request):
    path = resource_filename('deform', 'static')
    return request.get_response(static.FileApp(os.path.join(path, context.path)))
