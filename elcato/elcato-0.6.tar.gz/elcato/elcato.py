import os
import json
import yaml
import importlib
from slugify import slugify
from feedgen.feed import FeedGenerator

from eorg.parser import parse
from eorg.generate import html

from elcato.helpers import images, files, webfinger, minify, makefolder, load_template, serialize, AttributeDict, output_folders

from elcato.data import BlogData, AuthorData, fill
from elcato import settings
from elcato.settings import TEMPLATE
from datetime import datetime

def build_feed(destination, items):
    fg = FeedGenerator()
    fg.id(settings.BLOG.domain)
    fg.title(settings.BLOG.title)
    fg.author({"name": settings.AUTHOR.name, "email": settings.AUTHOR.email})
    fg.logo(settings.BLOG.domain + settings.BLOG.image)
    fg.subtitle(settings.BLOG.description)
    fg.link(href=settings.BLOG.domain + "/rss.xml", rel="self")
    fg.language("en")

    for item in items:
        fe = fg.add_entry()
        fe.id(settings.BLOG.domain + "/posts/" + item.slug.strip())
        fe.title(item.title)
        fe.category(
            [{"term": i, "scheme": i, "label": i} for i in item.filetags]
        )
        fe.pubDate(item.date)
        fe.link(
            href=settings.BLOG.domain + "/posts/" + item.slug.strip()
        )

    fg.rss_file(f"{destination}/rss.xml")


def build_tag_indexes(template, destination, tag, pages, ext='htm'):
    with open(f"{destination}/tags/{tag}.{ext}", "wb") as f:
        f.write(
            template.viewIndex(
                title=f"{tag}",
                search=tag,
                path="../",
                relative="../",
                cards=pages,
                author=settings.AUTHOR._asdict(),
                blog=settings.BLOG._asdict(),
            )
        )

    search = {}
    for page in pages:
        search[page.title.strip()] = page.slug.strip()

    with open(f"{destination}/tags/{tag}.js", "w") as f:
        f.write("var searchData = ")
        json.dump(search, f)
        minify(f"{destination}/tags/{tag}.js")


def build_tag_page(template, destination, tags, Author, ext='htm'):
    with open(f"{destination}/tags/all.ext", "wb") as f:
        f.write(
            template.viewTags(
                title=f"Tags", path="../", tags=tags, author=settings.AUTHOR
            )
        )


def build_activitypub(destination, author):
    webfinger(destination, author)


def skip_rules(doc):
    if "draft" in doc.filetags:
        print(f"## Skipped file in draft mode.")
        return True

    if getattr(doc, "filetags") is None:
        print(
            f"## Skipped without file tags add #+FILETAGS: to the document head."
        )
        return True

    if getattr(doc, "date", None) is None:
        print(f"## Skipped no date add #+DATE: to the document head.")
        return True

    return False


def filter_post(filename, match=None):
    if match is None:
        return False

    if match in filename:
        return False

    return True


def build_file(filename, source, destination, destination_folder="", ext="htm"):
    print(f"#### Processing {filename}")
    output_folders(destination, "")
    filepath = os.path.abspath(os.path.dirname(filename))
    with open(filename, "r") as fp:
        folders = os.path.dirname(filename[len(source):])
        # image_folder = f"/images{folders}"
        post_folder = f"/posts{folders}"
        doc = parse(fp)
        doc.path = destination_folder + post_folder
        doc.relative = "../" * (len(os.path.split(folders)))
        doc.absolute = f"posts{folders}"

        filetags = getattr(doc, "filetags", "")
        doc.taglist = [tag.strip() for tag in filetags.split(":")]
        doc.filetags = doc.taglist
        doc.slug = getattr(doc, "slug", slugify(doc.title)).strip() + f".{ext}"
        print(doc.filetags)
        if skip_rules(doc) is True:
            return None

        images(source, filepath, destination, doc)
        makefolder(destination, post_folder)
        with open(f"{destination}{post_folder}/{doc.slug}", "wb") as f:
            f.write(
                settings.TEMPLATE.viewPage(
                    title=doc.title,
                    path=f"../{post_folder}",
                    relative=doc.relative,
                    absolute=doc.absolute,
                    doc=serialize(doc),
                    body=html(doc).read(),
                    blog=settings.BLOG,
                )
            )
        return doc


def build(source, destination, config):
    SiteConfig = config.get("Config")
    template = load_template(SiteConfig)
    ext = template.EXT
    pages = []
    tags = {}
    search = {"all": {}}
    source = os.path.abspath(source)
    destination = os.path.abspath(destination)
    if config:
        Blog = fill(BlogData, config["Blog"])
        Author = fill(AuthorData, config["Author"])
    pos = 0
    for filename in files(source):
        if filter_post(filename) is True:
            continue

        print(f"#### Processing {filename}")
        doc = build_file(filename, source, destination, ext=ext)
        if doc:
            search["all"][doc.title.strip()] = doc.path + "/" + doc.slug
            pages.append(serialize(doc))
            for tag in doc.filetags:
                tags.setdefault(tag, []).append(pos)
            pos += 1

    pages.sort(key=lambda x:  datetime.strptime(x.date.strip(), '%Y-%m-%d %H:%M:%S %Z'))
    with open(f"{destination}/index.{ext}", "wb") as f:
        f.write(
            template.viewIndex(
                title="Index",
                ext=ext,
                #search="search",
                path="./",
                relative="./",
                cards=pages,
                author=AttributeDict(settings.AUTHOR._asdict()),
                blog=AttributeDict(settings.BLOG._asdict()),
            )
        )

    with open(f"{destination}/tags/search.js", "w") as f:
        f.write("var searchData = ")
        json.dump(search["all"], f)

    build_tag_page(template, destination, tags, Author)
    build_feed(destination, pages)

    for (tag, tag_pages) in tags.items():
        build_tag_indexes(
            template, destination, tag, [pages[p] for p in tag_pages]
        )
    build_activitypub(destination, settings.AUTHOR)


if __name__ == "__main__":
    source_path = settings.ROOT
    destination_path = settings.PATH

    config_path = os.path.abspath("./") + os.sep + "elcato.yaml"
    if os.path.exists(config_path):
        with open(config_path, "r") as fp:
            config = yaml.load(fp)
        source_path = config.org_file_path
    print(f"Reading org files from {source_path}")
    print(f"Generting files to {destination_path}")

    # init(settings.PATH)
    build(source=source_path, destination=destination_path, config=None)
# build(settings.ROOT, settings.PATH)
