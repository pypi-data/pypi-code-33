import os
import sys
import shutil
import datetime

from slugify import slugify
from elcato.helpers import loadconfig, makefolder, files, minify, handle_config
from elcato import settings
from elcato.elcato import build, build_file
from elcato.data import template
from eorg.parser import parse


def output_folders(path, folder):
    makefolder(path, "")
    makefolder(path, f"{folder}/tags/")
    makefolder(path, f"{folder}/posts/")
    makefolder(path, f"{folder}/images/")
    makefolder(path, f"{folder}/css/")
    makefolder(path, f"{folder}/javascript/")


def default_assets(path, folder):
    shutil.copy(
        f"{settings.ELCATO_ROOT}/templates/media/javascript/elcato.js",
        f"{path}{folder}/javascript/elcato.js",
    )
    if not os.path.exists(f"{path}{folder}/css/default.css"):
        shutil.copy(
            f"{settings.ELCATO_ROOT}/templates/static/default.css",
            f"{path}{folder}/css/default.css",
        )
    minify(f"{path}{folder}/css/default.css")
    minify(f"{path}{folder}/javascript/elcato.js")


def default_images(path, folder):
    if not os.path.exists(path + folder + "images/me.png"):
        shutil.copy(
            f"{settings.ELCATO_ROOT}/templates/media/me.png",
            f"{path}{folder}/images/me.png",
        )

    if not os.path.exists(path + folder + "images/placeholder.jpg"):
        shutil.copy(
            f"{settings.ELCATO_ROOT}/templates/media/placeholder.jpg",
            f"{path}{folder}/images/placeholder.jpg",
        )


def init(args):
    path = args.path
    output_folders(path, "site")
    default_images(path, "site")
    default_assets(path, "site")
    makefolder(path, f"posts/")
    shutil.copy(
        f"{settings.ELCATO_ROOT}/posts/org-markup.org",
        f"{path}/posts/org-markup.org",
    )
    shutil.copy(
        f"{settings.ELCATO_ROOT}/posts/hosting.org",
        f"{path}/posts/hosting.org",
    )
    shutil.copy(
        f"{settings.ELCATO_ROOT}/templates/example.yaml", f"{path}/elcato.yaml"
    )

    shutil.copy(f"{settings.ELCATO_ROOT}/../readme.org", f"{path}/readme.org")
    config = loadconfig(path)
    build(path, path + "/site/", config=config)


def info(args):
    root = os.path.abspath(args.path)
    if not os.path.exists(root):
        return

    for filename in files(root):
        with open(filename, "r") as fp:
            doc = parse(fp)
            taglist = getattr(doc, "filetags", "").strip().split(":")
            if args.tag is None or args.tag in taglist:
                print(filename + " " + getattr(doc, "title", ""))


def create(args, config=None):
    root = os.path.abspath(args.path)
    if not os.path.exists(root):
        return

    config = loadconfig(root, "Config")
    slug = slugify(args.title)
    path = (
        os.path.abspath(config.get("org_file_path", ""))
        + os.sep
        + slug
        + ".org"
    )

    if os.path.exists(path):
        print(f"Exited {path} already exists !")
        return

    # filename = os.path.basename(path)
    # folder = os.path.dirname(path)
    # makefolder(args.path, folder)
    with open(path, "w") as fp:
        fp.write(
            template.format(
                **{
                    "now": datetime.datetime.now().isoformat(),
                    "title": args.title,
                    "slug": slug,
                }
            )
        )


def build_cmd(args):
    config = None
    source_path = settings.ROOT
    destination_path = settings.PATH
    config_path = os.path.abspath("./") + os.sep + "elcato.yaml"

    config = handle_config(config_path)
    siteConfig = config.get("Config", {})
    source_path = siteConfig.get("org_file_path", source_path)
    destination_path = os.path.abspath("./") + siteConfig.get(
        "output_path", ""
    )

    if args.path:
        # Allow user to override and build in another folder
        destination_path = os.path.abspath(args.path)
    if args.filepath:
        build_file(
            args.filepath,
            source=source_path,
            destination=destination_path,
            config=config,
        )

    print(destination_path)
    output_folders(destination_path, "")
    default_images(destination_path, "")
    default_assets(destination_path, "")

    print(f"Reading org files from {source_path}")
    print(f"Generting files to {destination_path}")
    build(source=source_path, destination=destination_path, config=config)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Process some .org files")
    subparsers = parser.add_subparsers(dest="cmd")
    #    parser.add_argument('init', help='Show meta data')
    init_parser = subparsers.add_parser("init", help="Initialize a new blog")
    init_parser.add_argument(
        "-p",
        "--path",
        nargs="?",
        dest="path",
        default="./",
        help="Create blog in this location.",
    )
    init_parser.add_argument(
        "-w",
        "--webroot",
        nargs="?",
        dest="output",
        default="./site",
        help="Output the site into this location.",
    )
    init_parser.set_defaults(func=init)

    build_parser = subparsers.add_parser("build", help="secondary options")
    build_parser.add_argument(
        "-p",
        "--path",
        dest="path",
        default=None,
        action="store",
        help="Generate html in this location",
    )
    build_parser.add_argument(
        "-f",
        "--file",
        dest="filepath",
        default=None,
        action="store",
        help="Build a single file relative to root, "
        "will not be added to the index",
    )
    build_parser.set_defaults(func=build_cmd)

    create_parser = subparsers.add_parser("create", help="secondary options")
    create_parser.add_argument(
        "-p",
        "--path",
        dest="path",
        default="./",
        action="store",
        help="Show meta data",
    )
    create_parser.add_argument(
        "-n",
        "--name",
        dest="title",
        action="store",
        help="Name of new blog entry",
    )
    create_parser.set_defaults(name="create", func=create)

    info_parser = subparsers.add_parser("info", help="Info")
    info_parser.add_argument(
        "-t", "--tag", nargs="?", default=None, help="Show meta data"
    )
    info_parser.add_argument(
        "-p",
        "--path",
        dest="path",
        default="./",
        action="store",
        help="Show meta data",
    )
    info_parser.set_defaults(name="info", func=info)

    args = parser.parse_args()
    if args.cmd is None:
        parser.print_usage()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
