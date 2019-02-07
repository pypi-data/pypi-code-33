#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported OS: Linux

Supported video files: look at 'VIDEO_EXTENSIONS' variable
Supported subtitle files: look at 'SUBTITLES_EXTENSION' variable
Supported archive files: look at 'ARCHIVE_EXTENSIONS' variable
"""

import argparse
import logging
import os
import pathlib
import sys

from opensubtitles_downloader import error_handler, util, assembler, cleaner
from opensubtitles_downloader.constants import VERBOSE_OPTION, USER_CONFIG_FILE, CLEAN_OPTION, HOME
from opensubtitles_downloader.opensubtitles_client import OpenSubtitleError, OpenSubtitle


def launch(root: str) -> None:
    """
    Launch program and initialize opensubitle client.
    Eventually start directory cleaning.
    """

    def walk(fun, root_dir, way=True):
        """
        Walk through path starting from 'rootdir'. Function applies 'stretegy'
        in order to decide if walk is top-down or bottom-up.
        """
        for _root, _, _ in os.walk(root_dir, topdown=way, onerror=error_handler.handle):
            os.chdir(_root)
            fun(_root)

    # try to open subtitle client
    opensubtitle = util.web_service_login()
    if not opensubtitle:
        logging.warning('OpenSubtitles object initialization failed.')
        return None

    # file case
    if not os.path.isdir(root):
        file_path = root
        dir_path, filename = os.path.split(file_path)

        subtitle_filename = util.get_filename_no_ext(filename) + '.srt'
        subtitle_path = os.path.join(dir_path, subtitle_filename)
        try:
            subtitle = opensubtitle.download_subtitle(file_path)
        except OpenSubtitleError as err:
            error_handler.handle(err)
        else:
            if subtitle:
                # write subtitle only if file doesn't already exists or
                # has a different content.
                util.write_subtitle(subtitle_path, subtitle)
            else:
                if VERBOSE_OPTION:
                    logging.info('No subtitle founded for {}\n'.format(filename))

    # directory case
    else:
        walk(assembler.run, root)

    # OpenSubtitle logout, no more downloads
    if os.path.isfile(USER_CONFIG_FILE):
        OpenSubtitle().logout()

    # Handle clean option
    if CLEAN_OPTION:
        walk(cleaner.run, root, False)


def get_parser() -> 'ArgumentParser':
    """ Argument parser """
    parser = argparse.ArgumentParser(
        description='launch, a simple subtitles downloader and organizer.')

    parser.add_argument('-c', '--clean', help='activate clean option', action='store_true')
    parser.add_argument('-d', '--directory', help='directory to scan', type=str)
    parser.add_argument('-f', '--file', help='file to scan', type=str)
    parser.add_argument('-v', '--verbose', help='print video files for which no subtitle was found',
                        action='store_true')
    parser.add_argument('-s', '--settings', help='JSON with opensubtitle user login')

    return parser


def main():
    """ Parse arguments and launch program """
    # Setting default directory: ~/Downloads
    # (e.g. C:\Users|<user>\Downloads , /home/<user>/Downloads)
    root = os.path.join(HOME, 'Downloads')

    # parse arguments
    parser = get_parser()
    args = parser.parse_args()

    def extend_path(s):
        return str(pathlib.Path(s).resolve())

    if args.file:
        dir_path = os.getcwd()
        filename = extend_path(args.file)
        file_path = os.path.join(dir_path, filename)

        if not os.path.exists(file_path):
            logging.error("Input file doesn't exists: {}".format(file_path))
            sys.exit(3)

        root = os.path.abspath(file_path)

    if args.directory:
        directory = extend_path(args.directory)

        if not os.path.exists(directory):
            logging.error("Input directory doesn't exists: {}".format(directory))
            sys.exit(3)

        root = os.path.abspath(directory)

    if args.settings:
        settings = extend_path(args.settings)

        USER_CONFIG_FILE = settings

    VERBOSE_OPTION = args.verbose
    CLEAN_OPTION = args.clean

    # launch program
    launch(root)
