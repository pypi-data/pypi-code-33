from crosscompute.scripts.serve import import_upload_from
from crosscompute_table import TableType
from os.path import exists

from .fallbacks import load_geotable, save_geotable
from .routines import DisplayTable


class GeoTableType(TableType):
    suffixes = 'geotable',
    style = 'crosscompute_geotable:assets/part.min.css'
    script = 'crosscompute_geotable:assets/part.min.js'
    template = 'crosscompute_geotable:type.jinja2'
    views = [
        'import_geotable',
    ]
    requires_value_for_path = False

    @classmethod
    def load_for_view(Class, path, default_value=None):
        t = Class.load(path, default_value, partly=True)
        t = DisplayTable(t, is_abbreviated=t.is_abbreviated)
        return t

    @classmethod
    def load(Class, path, default_value=None, partly=False):
        if not exists(path):
            raise IOError('file not found (%s)' % path)
        return load_geotable(path, partly)

    @classmethod
    def save(Class, path, table):
        return save_geotable(path, table)


def import_geotable(request):
    return import_upload_from(request, GeoTableType, {})
