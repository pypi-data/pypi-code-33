from ..crud.model import ModelUI, CollectionUI


class APIKeyModelUI(ModelUI):

    edit_include_fields = ['label']


class APIKeyCollectionUI(CollectionUI):

    modelui_class = APIKeyModelUI

    create_include_fields = ['label']

    columns = [
        {'title': 'Label', 'name': 'label'},
        {'title': 'Identity', 'name': 'api_identity'},
        {'title': 'Actions', 'name': 'structure:buttons'}
    ]
