# {% if cookiecutter.project_type == "morpfw" %}
import morpfw
from morpfw.authz.pas import DefaultAuthzPolicy
from morpfw.crud import permission as crudperm
# {% elif cookiecutter.project_type == "morpcc" %}
import morpcc
import morpcc.permission as ccperm
import morpfw
from morpfw.authz.pas import DefaultAuthzPolicy
from morpfw.crud import permission as crudperm
# {% endif %}

# {% if cookiecutter.project_type == "morpfw" %}


class AppRoot(object):

    def __init__(self, request):
        self.request = request


class App(DefaultAuthzPolicy, morpfw.SQLApp):
    pass


@App.path(model=AppRoot, path='/')
def get_approot(request):
    return AppRoot(request)


@App.json(model=AppRoot, permission=crudperm.View)
def index(context, request):
    return {
        'message': 'Hello World'
    }


@App.permission_rule(model=AppRoot, permission=crudperm.View)
def allow_view(identity, context, permission):
    return True

# {% elif cookiecutter.project_type == "morpcc" %}


class AppRoot(morpcc.Root):
    pass


class App(morpcc.App):
    pass


@App.path(model=AppRoot, path='/')
def get_approot(request):
    return AppRoot(request)


@App.html(model=AppRoot, template='{{cookiecutter.project_name}}/index.pt',
          permission=ccperm.ViewHome)
def index(context, request):
    return {
        "message": "Hello world"
    }


@App.template_directory()
def get_template_directory():
    return 'templates'

# {% endif %}
