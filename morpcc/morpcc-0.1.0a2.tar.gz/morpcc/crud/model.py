import html


class ModelUI(object):

    view_include_fields: list = []
    view_exclude_fields: list = []
    edit_include_fields: list = []
    edit_exclude_fields: list = [
        'id', 'uuid', 'creator', 'created', 'modified', 'state', 'deleted',
        'xattrs', 'blobs'
    ]

    default_view = 'view'

    @property
    def identifier(self):
        return self.model.identifier

    def __init__(self, request, model, collection_ui):
        self.request = request
        self.model = model
        self.collection_ui = collection_ui


class CollectionUI(object):

    modelui_class = ModelUI

    create_include_fields: list = []
    create_exclude_fields: list = [
        'id', 'uuid', 'creator', 'created', 'modified', 'state', 'deleted',
        'xattrs', 'blobs'
    ]

    default_view = 'listing'

    @property
    def page_title(self):
        return str(self.collection.__class__.__name__)

    @property
    def listing_title(self):
        return 'Contents'

    columns = [
        {'title': 'Type', 'name': 'structure:type'},
        {'title': 'Object', 'name': 'structure:object_string'},
        {'title': 'UUID', 'name': 'uuid'},
        {'title': 'Created', 'name': 'created'},
        {'title': 'Actions', 'name': 'structure:buttons'},
    ]

    def get_buttons(self, obj, request):
        uiobj = self.modelui_class(request, obj, self)
        buttons = [{
            'icon': 'eye',
            'url': request.link(uiobj, '+%s' % uiobj.default_view),
            'title': 'View'
        }, {
            'icon': 'edit',
            'url': request.link(uiobj, '+edit'),
            'title': 'Edit'
        }, {
            'icon': 'trash',
            'url': request.link(uiobj, '+delete'),
            'title': 'Delete'
        }]
        return buttons

    def __init__(self, request, collection):
        self.request = request
        self.collection = collection

    def get_structure_column(self, obj, request, column_type):
        column_type = column_type.replace('structure:', '')
        if column_type == 'type':
            return str(obj.__class__.__name__)
        elif column_type == 'object_string':
            return html.escape(str(obj))
        elif column_type == 'buttons':
            results = ''
            for button in self.get_buttons(obj, request):
                results += ('<a title="%(title)s" href="%(url)s">'
                            '<i class="fa fa-%(icon)s">'
                            '</i></a> ') % button
            return results
        return ''
