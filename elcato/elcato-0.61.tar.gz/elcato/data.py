from collections import namedtuple


def fill(nt, values):
    return nt(
        *[
            values.get(field.lower(), field + " - not set")
            for field in nt._fields
        ]
    )


TagData = namedtuple("Tag", ["name", "count"])
BlogData = namedtuple("Blog", ["root", "title", "domain", "image", "description"])
AuthorData = namedtuple("Author", ["name", "email", "photo", "blurb", "links"])
PathMapping = namedtuple(
    "PathMapping",
    [
        "root",
        "absolute",
        "relative",
        "file_absolute",
    ],
)

PathData = namedtuple(
    "Paths",
    [
        "filename",
        "source_root",
        "destination_root",
        "source_relative",
        "source_absolute",
        "destination_absolute",
        "destination_relative",
        "depth",
    ],
)

template = """
#+TITLE: {title}
#+DATE: {now}
#+DESCRIPTION:
#+FILETAGS: colon:seperated:tags
#+LATEX_CLASS: article
#+CATEGORY: cato
#+SLUG: {slug}"""
