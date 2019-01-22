from morpcc.crud.model import ModelUI, CollectionUI


class PageModelUI(ModelUI):
    pass


class PageCollectionUI(CollectionUI):
    modelui_class = PageModelUI
