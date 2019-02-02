import enaml
from web.core.app import WebApplication


EXT = "htm"

app = WebApplication()

with enaml.imports():
    from elcato.templates.enaml.index import Index
    from elcato.templates.enaml.page import Page
    from elcato.templates.enaml.tags import Tags

pageIndex = Index()
pageTags = Tags()
pagePage = Page()


def viewIndex(**data):
    return pageIndex.render(**data)


def viewTags(**data):
    return pageTags.render(**data)


def viewPage(**data):
    return pagePage.render(**data)
