"""
This module handles every message of error to be output on screen.
"""

import http
import json
import logging
import xml
import xmlrpc

from opensubtitles_downloader.opensubtitles_client import OpenSubtitleError


def handle(err, file_path: str = '') -> None:
    """ Error handler for every error type. """

    err_type = type(err)

    if file_path:
        logging.error(file_path)

    # xmlrpc.client error
    if err_type is xmlrpc.client.Fault:
        logging.error("A fault occurred")
        logging.error("Fault code: {}".format(err.faultCode))
        logging.error("Fault string: {}".format(err.faultString))

    # xmlrpc.client error
    elif err_type is xmlrpc.client.ProtocolError:
        logging.error("A protocol error occurred")
        logging.error("URL: {}".format(err.url))
        logging.error("HTTP/HTTPS headers: {}".format(err.headers))
        logging.error("Error code: {}".format(err.errcode))
        logging.error("Error message: {}".format(err.errmsg))

    elif err_type is http.client.ResponseNotReady:
        logging.error('http client error: ResponseNotReady')

    elif err_type is OSError:
        logging.error(err)

    elif err_type is OverflowError:
        logging.error('An overflow error occurred while downloading subtitle')
        logging.error(err)

    elif err_type is IOError:
        logging.error(err)

    elif err_type is ValueError:
        logging.error(err)

    elif err_type is OpenSubtitleError:
        logging.error(err)

    elif err_type is xml.parsers.expat.ExpatError:
        logging.error(err)

    elif err_type is json.decoder.JSONDecodeError:
        logging.error(err)

