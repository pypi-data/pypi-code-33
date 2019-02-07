"""
This module handles every message of error to be output on screen.
"""

import http
import json
import xml
import xmlrpc

from opensubtitles_downloader.logger import logger
from opensubtitles_downloader.opensubtitles_client import OpenSubtitleError


def handle(err, file_path: str = '') -> None:
    """ Error handler for every error type. """

    err_type = type(err)

    if file_path:
        logger.error(file_path)

    # xmlrpc.client error
    if err_type is xmlrpc.client.Fault:
        logger.error("A fault occurred")
        logger.error("Fault code: {}".format(err.faultCode))
        logger.error("Fault string: {}".format(err.faultString))

    # xmlrpc.client error
    elif err_type is xmlrpc.client.ProtocolError:
        logger.error("A protocol error occurred")
        logger.error("URL: {}".format(err.url))
        logger.error("HTTP/HTTPS headers: {}".format(err.headers))
        logger.error("Error code: {}".format(err.errcode))
        logger.error("Error message: {}".format(err.errmsg))

    elif err_type is http.client.ResponseNotReady:
        logger.error('http client error: ResponseNotReady')

    elif err_type is OSError:
        logger.error(err)

    elif err_type is OverflowError:
        logger.error('An overflow error occurred while downloading subtitle')
        logger.error(err)

    elif err_type is IOError:
        logger.error(err)

    elif err_type is ValueError:
        logger.error(err)

    elif err_type is OpenSubtitleError:
        logger.error(err)

    elif err_type is xml.parsers.expat.ExpatError:
        logger.error(err)

    elif err_type is json.decoder.JSONDecodeError:
        logger.error(err)

