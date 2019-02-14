from morpcc.crud.model import ModelUI, CollectionUI


class {{cookiecutter.type_name}}ModelUI(ModelUI):
    pass


class {{cookiecutter.type_name}}CollectionUI(CollectionUI):
    modelui_class = {{cookiecutter.type_name}}ModelUI
