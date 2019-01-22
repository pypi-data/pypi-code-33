'''
    Utility functions To use:
        from imagekitio.utils import (PY3, to_bytes, to_bytearray, to_string, string_types, unquote,
                                      urlencode, Error)
        Or
        from imagekitio import utils
'''


from __future__ import absolute_import

from os import path
from hashlib import sha1
import hmac
import sys
from .contants import constants as ct

PY3 = (sys.version_info[0] == 3)

if PY3:
    import http.client as httplib
    NotConnected = httplib.NotConnected
    import urllib.request as urllib2
    import urllib.error
    HTTPError = urllib.error.HTTPError
    from io import StringIO, BytesIO
    from urllib.parse import urlencode, unquote, urlparse, parse_qs, quote_plus
    to_bytes = lambda s: s.encode('utf8')
    to_bytearray = lambda s: bytearray(s, 'utf8')
    to_string = lambda b: b.decode('utf8')
    string_types = str

else:
    import httplib
    from httplib import NotConnected
    from io import BytesIO
    import StringIO
    import urllib2
    HTTPError = urllib2.HTTPError
    from urllib import urlencode, unquote, quote_plus
    from urlparse import urlparse, parse_qs
    to_bytes = str
    to_bytearray = str
    to_string = str
    string_types = (str, unicode)


__all__ = ['get_host', 'get_protocol', 'get_image_upload_api', 'get_image_upload_url_api',
           'calculate_purge_signature', 'calculate_delete_signature', 'calculate_signature',
           'get_infinite_expiry']


class Error(Exception): pass
class NotFound(Error): pass
class NotAllowed(Error): pass
class AlreadyExists(Error): pass
class RateLimited(Error): pass
class BadRequest(Error): pass
class GeneralError(Error): pass
class AuthorizationRequired(Error): pass

EXCEPTION_CODES = {
    400: BadRequest,
    401: AuthorizationRequired,
    403: NotAllowed,
    404: NotFound,
    409: AlreadyExists,
    420: RateLimited
}


def get_host(imagekit_id, use_subdomain=None):
    ''' Get imagekit host for api request '''
    if not use_subdomain:
        return ct["COMMON_GET_SUBDOMAIN"] + ct["BASE_GET"]
    else:
        return imagekit_id + ct["BASE_GET"]


def get_protocol(use_secure):
    ''' Get protocol for api request '''
    if use_secure:
        return ct["HTTPS_PROTOCOL"]
    else:
        return ct["HTTPS_PROTOCOL"]


def get_image_upload_api(imagekit_id):
    ''' Get image upload api url '''
    #return path.join(ct["BASE_UPLOAD"], ct["UPLOAD_API"], imagekit_id)
    return ct["BASE_UPLOAD"] + '/' + ct["UPLOAD_API"] + '/' + imagekit_id

def get_image_upload_url_api(imagekit_id):
    ''' Get image upload via url api url '''
    return ct["BASE_UPLOAD"] + '/' + ct["UPLOAD_URL_API"] + '/' + imagekit_id

def get_image_delete_api():
    ''' Get image delete api url '''
    return ct["BASE_DASHBOARD"] + '/' + ct["DELETE_API"]

def get_image_purge_api():
    ''' Get image purge api url '''
    return ct["BASE_DASHBOARD"] + '/' + ct["PURGE_API"]

def get_list_media_api():
    ''' Get list media api url '''
    return ct["BASE_DASHBOARD"] + '/' + ct["LIST_MEDIA_API"]

def _sort_key_func(item):
    # sort function
    pairs = []
    for k, v in item:
        pairs.append((k, v))
    return sorted(pairs)


class Custom(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return '{}'.format(self.value)


def calculate_list_media_signature(options):
    ''' Calculate signature for list media request '''
    _message = ['skip=' + options["skip"], 'limit=' + options["limit"], 'imagekitId=' + str(options["imagekit_id"])]
    _message = sorted(_message)
    _str = "&".join(str(v) for v in _message)
    hashed = hmac.new(to_bytes(options["api_secret"]), to_bytes(_str), sha1)
    hex_dig = hashed.hexdigest()
    return hex_dig


def calculate_purge_signature(options):
    ''' Calculate signature for purge request '''
    _message = ['url=' + options["path"], 'imagekitId=' + str(options["imagekit_id"])]
    _message = sorted(_message)
    _str = "&".join(str(v) for v in _message)
    hashed = hmac.new(to_bytes(options["api_secret"]), to_bytes(_str), sha1)
    hex_dig = hashed.hexdigest()
    return hex_dig


def calculate_delete_signature(options):
    ''' Calculate signature for delete request '''
    _message = ['path=' + options["path"], 'imagekitId=' + str(options["imagekit_id"])]
    _message = sorted(_message)
    _str = "&".join(str(v) for v in _message)
    hashed = hmac.new(to_bytes(options["api_secret"]), to_bytes(_str), sha1)
    hex_dig = hashed.hexdigest()
    return hex_dig


def calculate_signature(options):
    ''' Calculate signature for upload request '''
    _message = ['filename=' + options["filename"], 'timestamp=' + str(options["timestamp"]),
                'apiKey=' + options["api_key"]]

    # Sample sorted value
    _message = sorted(_message)

    _str = "&".join(str(v) for v in _message)
    hashed = hmac.new(to_bytes(options["api_secret"]), to_bytes(_str), sha1)
    hex_dig = hashed.hexdigest()
    return hex_dig


def get_infinite_expiry():
    ''' return infinite expiry time '''
    return ct["INFINITE_EXPIRY_TIME"]
