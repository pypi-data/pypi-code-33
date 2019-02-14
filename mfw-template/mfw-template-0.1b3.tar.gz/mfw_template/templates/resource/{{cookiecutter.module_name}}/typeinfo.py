from ..app import App
from .model import {{cookiecutter.type_name}}Collection
from .model import {{cookiecutter.type_name}}Model
from .schema import {{cookiecutter.type_name}}Schema
from .path import get_collection, get_model
# {% if cookiecutter.project_type == "morpcc" %}
from .modelui import {{cookiecutter.type_name}}CollectionUI
from .modelui import {{cookiecutter.type_name}}ModelUI
from .path import get_collection_ui, get_model_ui
# {% endif %}


@App.typeinfo(name='{{ cookiecutter.project_name }}.{{ cookiecutter.module_name }}')
def get_typeinfo(request):
    return {
        'title': '{{ cookiecutter.type_name }}',
        'description': '{{ cookiecutter.type_description }}',
        'schema': {{cookiecutter.type_name}}Schema,
        'collection': {{cookiecutter.type_name}}Collection,
        'collection_factory': get_collection,
        'model': {{cookiecutter.type_name}}Model,
        'model_factory': get_model,
        # {% if cookiecutter.project_type == "morpcc" %}
        'collection_ui': {{cookiecutter.type_name}}CollectionUI,
        'collection_ui_factory': get_collection_ui,
        'model_ui': {{cookiecutter.type_name}}ModelUI,
        'model_ui_factory': {{cookiecutter.type_name}}ModelUI,
        # {% endif %}
    }
