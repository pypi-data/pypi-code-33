''' This module if for generting signed or unsigned urls '''

from __future__ import absolute_import

import time
import hmac
from hashlib import sha1
from imagekitio import utils
from imagekitio.transform import Transform


class Image(object):
    ''' Image class initialization '''
    def __init__(self, key=None, options=None, globl=None):
        self.key = key
        self.raw = options
        _tmp = {}
        for i in options:
            if utils.PY3:
                _tmp = dict(_tmp, **i)
            else:
                _tmp = dict(_tmp.items() + i.items())
        self.option = _tmp

        if utils.PY3:
            self.options = dict(get_defaults(), **globl)
            self.options = dict(self.options, **self.option)
        else:
            self.options = dict(get_defaults().items() + globl.items() + self.option.items())


    def url(self):
        ''' Get a URL for the image with different transformations and patterns '''
        transformation_string = self._get_transform_string()

        if self.options.pop('use_subdomain', None):
            if self.options["pattern"]:
                _pathname = "/".join([self.options["pattern"], 'tr:' + transformation_string, self.key])
            else:
                _pathname = "/".join(['tr:' + transformation_string, self.key])
        else:
            if self.options["pattern"]:
                _pathname = "/".join([self.options["imagekit_id"], self.options["pattern"], 'tr:' + transformation_string, self.key])
            else:
                _pathname = "/".join([self.options["imagekit_id"], 'tr:' + transformation_string, self.key])

        msg = {'host': utils.get_host(self.options["imagekit_id"], self.options.pop('use_subdomain', None)),
                    'protocol': utils.get_protocol(self.options["use_secure"]),
                    'pathname': _pathname,
                    'url': utils.get_protocol(self.options["use_secure"]) + '//' + utils.get_host(self.options["imagekit_id"], self.options.pop('use_subdomain', None)) + '/' + _pathname
                    }
        return msg


    def signed_url(self, expiry_seconds=None):
        ''' Get signed URL for the image with different transformations and patterns '''
        transformation_string = self._get_transform_string()

        expiry_timestamp = int(time.time()) + expiry_seconds if expiry_seconds else utils.get_infinite_expiry()

        query = {
            "ik-s": get_digest(transformation_string, expiry_timestamp, self.key, **self.options)
        }
        query_str = "ik-s=" + get_digest(transformation_string, expiry_timestamp, self.key, **self.options)

        if expiry_seconds:
            query["ik-t"] = expiry_timestamp
            query_str += '&' + "ik-t=" + expiry_timestamp

        if self.options.pop('use_subdomain', None):
            if self.options["pattern"]:
                _pathname = "/".join([self.options["pattern"], 'tr:' + transformation_string, self.key])
            else:
                _pathname = "/".join(['tr:' + transformation_string, self.key])
        else:
            if self.options["pattern"]:
                _pathname = "/".join([self.options["imagekit_id"], self.options["pattern"], 'tr:' + transformation_string, self.key])
            else:
                _pathname = "/".join([self.options["imagekit_id"], 'tr:' + transformation_string, self.key])
        msg = {'host': utils.get_host(self.options["imagekit_id"], self.options.pop('use_subdomain', None)),
               'protocol': utils.get_protocol(self.options["use_secure"]),
               'pathname': _pathname,
               'query': query,
               'url': utils.get_protocol(self.options["use_secure"]) + '//' + utils.get_host(self.options["imagekit_id"], self.options.pop('use_subdomain', None)) + '/' + _pathname + '?' + query_str
               }
        return msg


    def _get_transform_string(self):
        ''' Get the transformation string validated and rearranged '''
        transform_string = Transform(self.raw)
        _parsed_transforms = transform_string.valid_transforms()

        return _parsed_transforms


def get_defaults():
    ''' return defaults '''
    return {"pattern": ""}


def get_digest(transformation_string, expiry_timestamp, key, **options):
    ''' return hash signature '''
    _str = options["imagekit_id"] + transformation_string + str(expiry_timestamp) + key
    hashed = hmac.new(utils.to_bytes(options["api_secret"]), utils.to_bytes(_str), sha1)
    hex_dig = hashed.hexdigest()
    return hex_dig
