from plone import api
from zope.component import ComponentLookupError
from plone.formwidget.namedfile.converter import b64decode_file
from plone.namedfile.file import NamedImage


def convert_datagrid_iamge(picture):
    filename, data = b64decode_file(picture)
    data = NamedImage(data=data, filename=filename)
    return data


def subfield_values(field, subfield_name):
    if not field:
        return []
    return [
        item[subfield_name] for item in field if item[subfield_name]
    ]


def get_registry_entry(entry):
    _entry = None
    try:
        _entry = api.portal.get_registry_record(entry)
    except ComponentLookupError:
        pass
    return _entry
