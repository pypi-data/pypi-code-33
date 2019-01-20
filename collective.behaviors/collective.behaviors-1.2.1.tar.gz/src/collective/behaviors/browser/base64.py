
from plone.formwidget.namedfile.converter import b64decode_file
from Products.Five import BrowserView
from plone.namedfile.file import NamedImage


class Base64Image(BrowserView):

    def get(self, picture):
        if not picture:
            return None
        filename, data = b64decode_file(picture)
        data = NamedImage(data=data, filename=filename)
        return data
