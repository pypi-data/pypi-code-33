"""
This module implements OpenSubtitles interface.
"""

import binascii
import gzip
import http.client
import os
import struct
import xmlrpc.client

from opensubtitles_downloader import error_handler
from opensubtitles_downloader.constants import OPENSUBTITLES_URL, VERBOSE_OPTION
from opensubtitles_downloader.logger import logger


def hash_file(name: str) -> str:
    """
    Copied from
    https://trac.opensubtitles.org/projects%3Cscript%20type=/opensubtitles/wiki/HashSourceCodes
    """
    with open(name, "rb") as f:
        longlongformat = '<q'  # little-endian long long
        bytesize = struct.calcsize(longlongformat)

        filesize = os.path.getsize(name)
        filehash = filesize

        if filesize < 65536 * 2:
            return "SizeError"

        for _ in range(65536 // bytesize):
            buffer = f.read(bytesize)
            (l_value, ) = struct.unpack(longlongformat, buffer)
            filehash += l_value
            filehash = filehash & 0xFFFFFFFFFFFFFFFF  # to remain as 64bit number

        f.seek(max(0, filesize-65536), 0)
        for _ in range(65536 // bytesize):
            buffer = f.read(bytesize)
            (l_value, ) = struct.unpack(longlongformat, buffer)
            filehash += l_value
            filehash = filehash & 0xFFFFFFFFFFFFFFFF

        return "%016x" % filehash

    return None


def query_struct(filename: str, sublanguageid: str) -> list:
    """ Return a OpenSubtitles API compatible object for search queries. """
    info = {
        'sublanguageid': sublanguageid,
        'moviehash': hash_file(filename),
        'moviebytesize': os.path.getsize(filename),
        'imdbid': '',
        'query': '',
        'season': '',
        'episode': '',
        'tag': ''
    }
    return [info]  # for OpenSubtitle API support


def decode(content: str) -> str:
    """ Try to decode 'content' with various codec. """
    try:
        data = content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            data = content.decode('latin-1')
        except UnicodeDecodeError:
            data = content.decode('ascii')
    return data


class Singleton(object):
    __instance = None

    def __new__(cls):
        if Singleton.__instance is None:
            Singleton.__instance = object.__new__(cls)
        return Singleton.__instance


class OpenSubtitle(Singleton):

    def __init__(self):
        """
        Inizialize a client for xml-rpc connection with OpenSubtitle.org
        """
        self.__token = None
        self.__language = None
        try:
            self.__proxy = xmlrpc.client.ServerProxy(OPENSUBTITLES_URL)
        except (xmlrpc.client.Fault, xmlrpc.client.ProtocolError) as err:
            error_handler.handle(err)

    def login(self,
              username: str = "",
              password: str = "",
              language: str = "all",
              useragent: str = "OSTestUserAgentTemp") -> None:
        """ Token is a unique identifier given by OpenSubtitle. """
        if self.__token:  # login already done
            return True

        try:
            login = self.__proxy.LogIn(username, password, language, useragent)
            if not login:
                raise OpenSubtitleError("login problem...")
        except (xmlrpc.client.Fault,
                xmlrpc.client.ProtocolError,
                OpenSubtitleError) as err:
            self.__token = None
            error_handler.handle(err)
        else:
            self.__token = login['token']
        self.__language = language

    def logout(self, token: str = "") -> None:
        """ Opensubtitle logout """
        token = token if token else self.__token
        try:
            self.__proxy.LogOut(token)
        except (xmlrpc.client.Fault, xmlrpc.client.ProtocolError,
                TypeError) as err:
            error_handler.handle(err)

    def keep_alive(self, token: str = "") -> None:
        """ Should be called every 15 minutes to keep session alive. """
        token = token if token else self.__token
        try:
            self.__proxy.NoOperation(token, 'allow_none')
        except (xmlrpc.client.Fault, xmlrpc.client.ProtocolError) as err:
            error_handler.handle(err)

    def get_token(self) -> str:
        return self.__token

    def _search_subtitle(self, sublanguage: str = 'all', filenames: list = None) -> list:
        try:
            results = [self.__proxy.SearchSubtitles(self.__token, query_struct(f, sublanguage)) for f in filenames]
        except (xmlrpc.client.Fault, xmlrpc.client.ProtocolError,
                http.client.ResponseNotReady, OverflowError, TypeError) as err:
            if VERBOSE_OPTION:
                error_handler.handle(err)
            return None
        else:
            result = results[0] if any(results) else None

            if not result:
                return None

            elif (result['status'] == '503 Service Unavailable'
                  or result['status'] == '414 Unknown User Agent'
                  or result['status'] == '415 Disabled user agent'):
                logger.info(result['status'])
                return None

            return result['data']

    def _download_subtitles(self, filenames: list = None) -> list:
        """
        More compatible with OpenSubtitles API.
        Return a list of dictionary:
        each 'data' in dictionary has to decode from base64 and gunzip to be
        readable.
        """
        result = self._search_subtitle(self.__language, filenames)

        # If no subtitle was found, try with english one
        result = self._search_subtitle('eng', filenames) if not any([result]) else result
        if not any([result]):
            return None  # neither english subtitle was found

        subtitle_id = result[0]['IDSubtitleFile']
        token = self.__token

        try:
            subtitle = self.__proxy.DownloadSubtitles(token, [subtitle_id])
        except (xmlrpc.client.Fault, xmlrpc.client.ProtocolError) as err:
            if VERBOSE_OPTION:
                error_handler.handle(err)
        else:
            if subtitle['status'] == '407 Download limit reached' and VERBOSE_OPTION:
                logger.warning(subtitle['status'], ': retry later.')

            return subtitle['data']

        return None

    def download_subtitle(self, filename: str = "") -> str:
        """ Not compatible with OpenSubtitles API. """
        result = self._download_subtitles([filename])
        if not result:
            return None

        subtitle = result[0]['data']
        content = gzip.decompress(binascii.a2b_base64(subtitle))
        return decode(content)


class OpenSubtitleError(Exception):
    def __init__(self, message):
        self.message = "[*] Opensubtitle " + message
