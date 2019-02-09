import morpfw
from .schema import PageSchema


class PageModel(morpfw.Model):
    schema = PageSchema


class PageCollection(morpfw.Collection):
    schema = PageSchema
