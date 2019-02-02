import os
from jinja2 import Template
from jinja2 import Environment, BaseLoader
from jinja2 import Environment, FileSystemLoader


EXT = "htm"

path = os.path.dirname(os.path.realpath(__file__))
env = Environment(loader=FileSystemLoader(path))

with open(f"{path}/index.html", "r") as fp:
    #    pageIndex = Template(fp.read(), env)
    pageIndex = env.get_template("index.html")
with open(f"{path}/tags.html", "r") as fp:
    # pageTags = Template(fp.read())
    pageTags = env.get_template("tags.html")

with open(f"{path}/page.html", "r") as fp:
    #    pagePage = Template(fp.read())
    pagePage = env.get_template("page.html")


def viewIndex(**data):
    return pageIndex.render(**data).encode()


def viewTags(**data):
    return pageTags.render(**data).encode()


def viewPage(**data):
    o = pagePage.render(
        title=data.get("title"),
        path="../",
        doc=data.get("doc"),
        body=data.get("body"),
    )
    return o.encode()
