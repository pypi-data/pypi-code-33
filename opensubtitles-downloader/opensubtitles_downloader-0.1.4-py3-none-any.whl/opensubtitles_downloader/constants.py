"""
List of all constants needed in tv_series_renamer.py
"""
import json
import os

from opensubtitles_downloader.logger import logger

OPENSUBTITLES_URL = "https://api.opensubtitles.org/xml-rpc"

# Boolean for user arguments
CLEAN_OPTION = False
VERBOSE_OPTION = False

HOME = os.path.expanduser("~")  # compatible with Linux, Windows and MacOS

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

USER_CONFIG_DIR = os.path.join(HOME, '.opensubtitles_downloader')
if not os.path.exists(USER_CONFIG_DIR):
    os.makedirs(USER_CONFIG_DIR)

USER_CONFIG_FILE = os.path.join(USER_CONFIG_DIR, "opensubtitles.json")
if not os.path.exists(USER_CONFIG_FILE):
    with open(USER_CONFIG_FILE, 'w') as fd:
        fd.write(json.dumps({
            "username": "username",
            "password": "password",
            "language": "eng",
            "useragent": "mistalbo"
        }))
    logger.warning(
        'Modify file "{}" with your OpenSubtitles credentials and language of choice.'.format(USER_CONFIG_FILE))

VIDEO_EXTENSIONS = {".3g2", ".3gp", ".3gp2", ".3gpp", ".60d", ".ajp", ".asf",
                    ".asx", ".avchd", ".avi", ".bik", ".bix", ".box", ".cam",
                    ".dat", ".divx", ".dmf", ".drc", ".dv", ".dvr-ms", ".evo",
                    ".f4a ", ".f4b", ".f4p", ".f4v", ".flc", ".fli", ".flic",
                    ".flv", ".flx", ".gvi", ".gvp", ".h264", ".m1v", ".m2p",
                    ".m2ts", ".m2v", ".m4e", ".m4v", ".mjp", ".mjpeg", ".mjpg",
                    ".m4p", ".m4v", ".mp4", ".mkv", ".moov", ".mov", ".movhd",
                    ".movie", ".movx", ".mpe", ".mpeg", ".mp2", ".mpe", ".mpg",
                    ".mpv", ".mpv2", ".mxf", ".nsv", ".nut", ".ogg", ".ogm",
                    ".ogv", ".omf", ".ps", ".qt", ".ram", ".rm", ".rmvb",
                    ".swf", ".ts", ".vfw", ".vid", ".video", ".viv", ".vivo",
                    ".vob", ".vro", ".webm", ".wm", ".wmv", ".wmx", ".wrap",
                    ".wvx", ".wx", ".x264", ".xvid", ".yuv"}

SUBTITLE_EXTENSIONS = {".srt", ".sub", ".smi", ".ssa", ".ass", ".mpl"}

ARCHIVE_EXTENSIONS = {".zip", ".zipx", ".7z", ".s7z", ".rar", ".xar", ".gz",
                      ".bz2", ".lz", ".xz", ".lz", ".s7z", ".arc", ".tar.gz",
                      ".tgz", ".tar.Z", ".tar.bz2", ".tbz2", ".tar.lzma",
                      ".tlz"}
