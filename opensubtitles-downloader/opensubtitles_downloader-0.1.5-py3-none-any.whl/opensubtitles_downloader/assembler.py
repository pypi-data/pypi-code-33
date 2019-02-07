"""
This module is the core of the program, its 'run' method is the actual
implementation of the whole program.
"""

import datetime
import os
import time
import zipfile

from opensubtitles_downloader.constants import VERBOSE_OPTION
from opensubtitles_downloader import util, error_handler
from opensubtitles_downloader.logger import logger
from opensubtitles_downloader.opensubtitles_client import OpenSubtitleError


def extract(archive: str) -> None:
    """
    Extract subtitle from archive named with a tv show name and episode.
    """
    with zipfile.ZipFile(archive, 'r') as arc:
        for subtitle in filter(util.is_subtitle, arc.namelist()):
            try:
                if os.fork() == 0:
                    arc.extract(subtitle)
                    os._exit(0)
                else:
                    res = os.wait()
                    if res[1] == -1:
                        logger.warning("Error in child process ", res[0])
            except OSError as err:
                error_handler.handle(err)


def move(msg: str, src: str, dst: str) -> None:
    """ Move file from 'src' to 'dst' only if it doesn't already exists. """
    if src != dst:
        try:
            os.rename(src, dst)
        except OSError as err:
            error_handler.handle(err, src)
        else:
            logger.info('{}: {} -> {}'.format(msg, src, dst))


def run(path: str) -> None:
    """
    This is just a wrapper for the work that the program do in every folder.

    At first it looks for related archive and video files, than extracts
    subtitles from archives.
    After that, it looks for related archive and subdirectories and move
    archives to subdirectories.
    When archives are completly handle, it looks for related videos and
    subtitles and rename subtitles with related video.
    If some tvshows are not related with any subtitle file, it tries to
    download them from 'OpenSubtitles.org'.
    """

    # Extract archives that match with video files.
    for archive, _ in util.get_related(util.get_archives(), util.get_videos()):
        extract(archive)

    # Move archives to directories if they match.
    for subdir, archive in util.get_related(util.get_subdirs(), util.get_archives()):
        arc = archive.get_filename()
        src = os.path.join(path, arc)
        dst = os.path.join(path, subdir.get_filename(), arc)
        move('moving', src, dst)

    # Rename subtitles with video filename.
    for video, subtitle in util.get_related(util.get_videos(), util.get_subtitles()):
        src = os.path.join(path, subtitle)
        dst = os.path.join(path, util.get_filename_no_ext(video) + '.srt')
        move('renaming', src, dst)


    ################# OpenSubtitle search section ########################

    opensubtitle = util.web_service_login()

    if not opensubtitle:
        logger.warning('OpenSubtitles object initialization failed.')
        return None

    # this variable is used to send a token to keep alive OpenSubtitles
    # session.
    start = datetime.datetime.now()

    for video in util.get_videos():
        subtitle_filename = util.get_filename_no_ext(video) + '.srt'
        subtitle_path = os.path.join(path, subtitle_filename)

        try:
            subtitle = opensubtitle.download_subtitle(video)
        except OpenSubtitleError as err:
            error_handler.handle(err)
        else:
            if subtitle:
                util.write_subtitle(subtitle_path, subtitle)
            elif VERBOSE_OPTION:
                logger.info('No subtitle founded for {}'.format(video))
        time.sleep(0.5)

    # check if it's time to send a signal to OpenSubtitles.org
    util.keep_alive_signal(opensubtitle, start)
