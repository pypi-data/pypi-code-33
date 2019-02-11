# -*- coding: utf-8 -*-

import pysimplehttpdownloader.http_downloader
from pysimplehttpdownloader.metadata import Metadata
import os
import argparse


def empty_url(url):
    if url == "":
        raise argparse.ArgumentTypeError("Empty URL")
    return url


def exists_path(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError("%s is not valid path" % path)
    return path


def main():
    meta = Metadata()

    # Parse arguments provided
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=meta.get_version())
    parser.add_argument('-u', '--url', dest='url', help='URL', type=empty_url, default="")
    parser.add_argument('-p', '--path', dest='path', help='Output path', type=exists_path, default=".")
    parser.add_argument('-n', '--name', dest='name', help='Output filename', default=None)
    args = parser.parse_args()

    pysimplehttpdownloader.http_downloader.HTTPDownloader(args.url, args.path, args.name).run()


if __name__ == "__main__":
    main()
