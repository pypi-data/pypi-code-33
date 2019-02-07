"""
This module is for when clean option is activated.
"""
import os

# if module send2trash isn't installed, print a suggestion for user
from opensubtitles_downloader import util
from opensubtitles_downloader.logger import logger

try:
    from send2trash import send2trash
except ImportError:
    def send2trash(path):
        logger.warning('You should remove file: ', path)


def send_to_trash(path: str) -> None:
    """
    File 'path' is moved into trash. If trash is unreachable or doesn't exist,
    file is removed from the system.
    """
    try:
        send2trash(path)
    except OSError as err:
        logger.error(str(err))

        # if error was related to trash problem, remove file from the system
        if os.path.exists(path):
            if os.path.isdir(path) and not os.listdir(path):  # empty dir
                os.rmdir(path)
            elif os.path.isfile(path):  # regular file
                os.remove(path)
    finally:
        logger.info("deleted: {}\n".format(path))


def run(path: str) -> None:
    """
    Clean folder 'path'.
    Remove:
        - every subtitle file that has no matching tv-show file
        - remove every subdirectory that is empty
    """
    # Remove empty directories.
    for subdir in util.get_subdirs(path):
        subdir_path = os.path.join(path, subdir)
        if not os.listdir(subdir_path):
            send_to_trash(subdir_path)

    videos = util.get_videos(path)
    archives = util.get_archives(path)
    subtitles = util.get_subtitles(path)

    for subtitle in subtitles:
        # Looking for subtitles which are not more usefull because
        # there is no video file related to them
        if not util.correlation_founded(subtitle, videos):
            subtitle_path = os.path.join(path, subtitle)
            send_to_trash(subtitle_path)

            # Looking for archive related to unusefull subtitle
            for archive in archives:
                if util.same_show_and_episode(subtitle, archive):
                    archive_path = os.path.join(path, archive)
                    send_to_trash(archive_path)
