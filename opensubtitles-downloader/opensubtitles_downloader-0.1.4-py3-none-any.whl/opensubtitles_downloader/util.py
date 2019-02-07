"""
This module implements functions usefull for scannning a directory and divide
tv-shows files by type.
"""

import datetime
import json
import os
import re
import xml
from typing import Callable, Tuple

from opensubtitles_downloader import error_handler
from opensubtitles_downloader.constants import SUBTITLE_EXTENSIONS, VIDEO_EXTENSIONS, ARCHIVE_EXTENSIONS, \
    USER_CONFIG_FILE
from opensubtitles_downloader.logger import logger
from opensubtitles_downloader.opensubtitles_client import OpenSubtitle, OpenSubtitleError


def are_same_type(extensions: list) -> Callable:
    """
    Return a function that find if 'filename' has an extension that is in
    'extensions'.
    """
    def is_in(filename: str) -> bool:
        """ Return boolean value. """
        return any(filter(filename.endswith, extensions))
    return is_in


# Next functions are an attempt to emprically detect the type of file by its
# extension.
is_subtitle = are_same_type(SUBTITLE_EXTENSIONS)
is_video = are_same_type(VIDEO_EXTENSIONS)
is_archive = are_same_type(ARCHIVE_EXTENSIONS)


def get_subdirs(path: str = '.') -> list:
    return filter(os.path.isdir, os.listdir(path))


def get_videos(path: str = '.') -> list:
    return filter(lambda v: is_video(v) and not os.path.isdir(v), os.listdir(path))


def get_subtitles(path: str = '.') -> list:
    return filter(is_subtitle, os.listdir(path))


def get_archives(path: str = '.') -> list:
    return filter(is_archive, os.listdir(path))


def get_season_episode(filename: str) -> Tuple[str, str]:
    """ Return a couple '(season, episode)' or 'None'. """

    # find season-episode values
    regex = r"season{0,1}|episode{0,1}|[sne. ]{0,1}\d+"
    str_pattern = re.compile(regex, re.IGNORECASE)
    results = str_pattern.findall(filename)  # strings list matching str_pattern

    # if no season-episode found or if too many numbers for season-episode
    if not results or (results and len(results[0]) > 3):
        return None

    # get rid of chars
    num_pattern = re.compile(r"\d{1,2}")
    result = num_pattern.findall(''.join(results))

    zfill = lambda string: string.zfill(2)  # '1' -> '01'
    return (zfill(result[0]), zfill(result[1])) if len(result) >= 2 else None


def get_title(filename: str) -> str:
    """ Return a lowercase string of the tv-serie title separated by dot. """

    if not get_season_episode(filename):
        return filename

    # normalize string
    filename_normalized = re.sub(r"[\W_]+", '.', filename.lower())

    # get actual title of the show
    pattern = re.compile(r"(?=(season|s).{0,1}\d{1,2})")
    match = re.search(pattern, filename_normalized)
    title = filename_normalized[:match.start()] if match else None

    # get rid of last '.'
    return title[:-1] if title and title[-1] == '.' else title


def get_filename_no_ext(filename: str) -> str:
    """ Return filename without file extension. """
    return filename[:filename.rfind('.')]


def is_tvshow(filename: str) -> str:
    """ Return True if 'filename' is a tv-shows, False otherwise """
    return get_season_episode(filename) and get_title(filename)


def same_show_and_episode(filename1: str, filename2: str) -> bool:
    """
    Compare title and season-episode, return True if they are equal, False
    otherwise.
    """
    return (get_title(filename1) == get_title(filename2) and
            get_season_episode(filename1) == get_season_episode(filename2))


def correlation_founded(filename: str, files: list) -> bool:
    """
    Every member of 'files' is compared against 'filename'.
    Return True if at least one file has same name as 'filename',
           False otherwise.
    """
    equal = lambda f: get_filename_no_ext(filename) == get_filename_no_ext(f)
    return any(filter(equal, files))


def get_related(list1: list, list2: list) -> list:
    """ Return a list of matched FileObject couples. """
    return [(el1, el2) for el1 in list1 for el2 in list2
            if same_show_and_episode(el1, el2)]


def get_unrelated(list1: list, list2: list) -> list:
    """
    Return a list of FileObjects from 'list1': none of them match with an
    element in 'list2'.
    """
    return [elem for elem in list1 if not any(get_related([elem], list2))]


def web_service_login() -> 'OpenSubtitle':
    """
    Login to OpenSubtitles using credentials in default configuration file
    location:
        {SubtitleDownloader_script}/opensubtitles_config.json
    """
    config_file = USER_CONFIG_FILE

    # Get OpenSubtitle user account info from config.json file.
    if not os.path.exists(config_file) or not os.path.isfile(config_file):
        logger.error("file '{}' couldn't be found.".format(config_file))
        return None

    with open(config_file, 'r') as config:
        try:
            decoder = json.JSONDecoder()

            userconfig = decoder.decode(config.read())

            username = userconfig['username']
            password = userconfig['password']
            language = userconfig['language']
            useragent = userconfig['useragent']

            # OpenSubtitle login
            opensubtitle = OpenSubtitle()
            opensubtitle.login(username, password, language, useragent)

        except (json.decoder.JSONDecodeError,
                OpenSubtitleError,
                xml.parsers.expat.ExpatError) as err:
            error_handler.handle(err)
        else:
            return opensubtitle

    return None


def keep_alive_signal(opensubtitle: 'OpenSubtitle', start: datetime) -> None:
    """ Send keep-alive signal every 15 minutes (14 to be sure)  """
    delta = datetime.timedelta(minutes=14)
    if datetime.datetime.now() >= start + delta:
        opensubtitle.keep_alive()


def write_subtitle(subtitle_path: str, subtitle: str) -> None:
    """
    Write 'subtitle' content into 'subtitle_path' file. Overwrite if it already
    exists.
    """
    def normalize(string: str) -> str:
        return re.sub(r"(\n)|(\r\n)|(\n\r)", os.linesep, string)

    norm_subtitle = normalize(subtitle)

    def write(encoding):
        with open(subtitle_path, 'r+', encoding=encoding) as subf:
            content = subf.read()
            norm_content = normalize(content)
            if norm_content != (norm_subtitle + os.linesep):
                subf.write(norm_subtitle)

    if os.path.exists(subtitle_path):
        try:
            write('utf-8')
        except (UnicodeDecodeError, UnicodeDecodeError):
            try:
                write('latin-1')
            except (UnicodeDecodeError, UnicodeEncodeError):
                try:
                    write('ascii')
                except (UnicodeDecodeError, UnicodeDecodeError) as err:
                    error_handler.handle(err)
    else:
        with open(subtitle_path, 'w') as subf:
            subf.write(norm_subtitle)

    logger.info('Subtitle file downloaded: {}'.format(subtitle_path))
