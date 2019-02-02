import os
import sys
import yaml
import json
import shutil
import importlib
from pprint import pprint
from PIL import Image
from eorg import tokens
from eorg.tokens import Token
from elcato import settings
from elcato.settings import TEMPLATE, BLOG, AUTHOR
from elcato.data import PathData, PathMapping
from elcato.data import BlogData, AuthorData, fill


from css_html_js_minify import (
    process_single_html_file,
    process_single_js_file,
    process_single_css_file,
)


class nostdout:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def serialize(doc):
    return AttributeDict({
        "doc": "",
        "title": doc.title,
        "description": getattr(doc, "description", ""),
        "date": getattr(doc, "date", ""),
        "index": doc.index,
        "path": doc.path,
        "relative": doc.relative,
        "absolute": doc.absolute,
        "taglist": doc.taglist,
        "thumbnail": getattr(doc, "thumbnail", ""),
        "filetags": doc.filetags,
        "slug": doc.slug,
        "pos": doc.pos,
    })


def handle_config(config_path):
    if not os.path.exists(config_path):
        print("Missing elcato.yaml at {destination_path} bailing")
        sys.exit(1)
    with open(config_path, "r") as fp:
        config = yaml.load(fp)
    siteConfig = config.get("Config", {})
    settings.BLOG = fill(BlogData, config["Blog"])
    settings.AUTHOR = fill(AuthorData, config["Author"])
    settings.TEMPLATE = load_template(siteConfig)
    return config


def load_template(config):
    return importlib.import_module(
        f"elcato.templates.{config.get('theme', 'enaml')}.template"
    )


def loadconfig(path, key=None, name="elcato.yaml"):
    config = {}
    config_path = f"{path}/{name}"
    if os.path.exists(config_path):
        with open(config_path, "r") as fp:
            config = yaml.load(fp)
    if key is None:
        return config

    return config.get(key, {})


def minify(path):
    with nostdout():
        if path.endswith(".htm"):
            process_single_html_file(path, overwrite=False)
        if path.endswith(".js"):
            process_single_js_file(path, overwrite=False)
        if path.endswith(".css"):
            process_single_css_file(path, overwrite=False)


def webfinger(root, author):
    folder = f"{root}/.well-known/"
    makefolder(folder, "")

    packet = {"subject": author.name, "links": [l[-1] for l in author.links]}
    with open(f"{folder}webfinger", "w") as fp:
        fp.write(json.dumps(packet))
    return


def makefolder(path, folder):
    if not os.path.exists(f"{path}/{folder}"):
        os.makedirs(f"{path}/{folder}")


def files(path):
    for root, dirs, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(".org"):
                yield root + os.sep + filename


def path_relative_to_document(root, document_location, relative_path):
    return PathMapping(
        root=root,
        relative=os.path.relpath(document_location, root),
        absolute=document_location,
        file_absolute=os.path.abspath(document_location + relative_path),
    )


def update_relative_to_document(paths, relative_path):
    paths.file_absolute = (
        os.path.abspath(paths.rootdocument_location + relative_path),
    )
    return paths


def calculate_paths(
    source_root,
    destination_root,
    source_file,
    source_image,
    destination_folder="",
):
    relative = os.path.relpath(source_file, source_root)
    relative = "" if relative == "." else relative
    depth = len([part for part in os.path.split(relative) if part])
    filename = os.path.basename(source_image)
    destination_relative = os.sep.join(
        [destination_folder.strip("/"), relative.strip("/")]
    )
    p = PathData(
        filename=filename,
        depth=depth,
        source_root=source_root,
        destination_root=destination_root,
        source_absolute=source_image,
        source_relative=relative,
        destination_relative=destination_relative,  # ("../" * depth)
        destination_absolute=destination_root + os.sep + destination_relative,
    )
    return p


# never let go


def images(source, path, destination, doc):
    image_list = [i for i in doc.images()]
    if hasattr(doc, "thumbnail"):
        print(f"########## Thumbnail {doc.thumbnail}")
        thumb_paths = calculate_paths(
            source_root=source,
            source_file=path,
            source_image=os.path.abspath(path + "/" + doc.thumbnail.strip()),
            destination_root=destination,
            destination_folder="/images/thumbnails/",
        )
        thumb = Token(tokens.IMAGE, [doc.thumbnail, doc.title])
        makefolder(destination, f"{thumb_paths.destination_relative}")
        filename = image_size_thumbnail(thumb_paths) or ""
        doc.thumbnail = thumb_paths.destination_relative + os.sep + filename
        image_list.append(thumb)

    if len(image_list) is 0:
        return

    print("## Images")
    for item in image_list:
        image = item.value[0]
        if image.startswith("http://") or image.startswith("https://"):
            continue

        paths = calculate_paths(
            source_root=source,
            source_file=path,
            source_image=os.path.abspath(path + "/" + image.strip()),
            destination_root=destination,
            destination_folder="/images/originals/",
        )

        if not os.path.exists(paths.source_absolute):
            print(f"Missing image {paths.source_absolute}")
            continue

        print(f"Copying {paths.source_absolute}")
        relative = "../" * (paths.depth + 1)
        item.value[
            0
        ] = f"{relative}{paths.destination_relative}/{paths.filename}"
        makefolder(paths.destination_root, f"{paths.destination_relative}")
        shutil.copy(
            paths.source_absolute,
            paths.destination_absolute + os.sep + paths.filename,
        )


def image_size_thumbnail(path):
    if not os.path.exists(path.source_absolute):
        print(f"missing {path.source_absolute}")
        return None

    filename, extension = os.path.splitext(path.filename)
    if extension == ".svg":
        return None

    min_size = 512
    im = Image.open(path.source_absolute)
    x, y = im.size
    size = max(min_size, x, y)
    print(f"## Resizing {size}")
    thumbnail = Image.new("RGBA", (size, size), (0, 0, 0, 1))
    box = (int((size - x) / 2), int((size - y) / 2))
    thumbnail.paste(im, box)
    thumbnail.save(f"{path.destination_absolute}{os.sep}{filename}.png")
    return filename + ".png"


def output_folders(path, folder):
    makefolder(path, "")
    makefolder(path, f"{folder}/tags/")
    makefolder(path, f"{folder}/posts/")
    makefolder(path, f"{folder}/images/")
    makefolder(path, f"{folder}/css/")
    makefolder(path, f"{folder}/javascript/")
