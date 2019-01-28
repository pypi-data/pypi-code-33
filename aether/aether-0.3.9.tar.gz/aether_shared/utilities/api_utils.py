from PIL import Image
import numpy as np
import urllib2
import json
from google.protobuf import json_format
from aether.proto.api_pb2 import ErrorMessage
import sys
import traceback

class api_utils(object):

    @staticmethod
    def hash_config(request_config):
        return frozenset(request_config.to_dict().items())

    @staticmethod
    def rest_api_call(url, uri_dict):
        url += "&".join(["{}={}".format(k,v) for k,v in uri_dict.iteritems()]).replace(" ", "")
        print("Making REST API call to: {}".format(url))
        response = urllib2.urlopen(url).read()
        return json.loads(response)

    @staticmethod
    def url_exists(url):
        try:
            urllib2.urlopen(url)
            return True
        except urllib2.HTTPError, e:
            # print("{}: {}".format(e.code, url))
            return False
        except urllib2.URLError, e:
            # print("{}: {}".format(e.args, url))
            return False

    @staticmethod
    def resource_location_endpoint(resource_name, blob_form, request_config):
        resource_filename = resource_name + "/" + blob_form.format(**request_config)
        return resource_filename

    @staticmethod
    def display_numpy(data, filename=None, show_image=False, data_is_normalized_to_one=True):
        if data_is_normalized_to_one:
            data = data * 255.

        image = Image.fromarray(np.array(data, dtype=np.uint8))
        if filename is not None:
            image.save(filename)
        if show_image:
            image.show()

    @staticmethod
    def _rectangular_polygon(c, r):
        p = []
        p.append([c[0] - r, c[1] - r])
        p.append([c[0] + r, c[1] - r])
        p.append([c[0] + r, c[1] + r])
        p.append([c[0] - r, c[1] + r])
        p.append([c[0] - r, c[1] - r])
        return p

    @staticmethod
    def _chicago_test_aoi():
        center = [41.2, -87.5]
        radius = 1.5
        aoi = api_utils._rectangular_polygon(center, radius)
        return aoi

    @staticmethod
    def _imperial_test_aoi():
        center = [32.843454, -115.6003187]
        radius = 0.1
        aoi = api_utils._rectangular_polygon(center, radius)
        return aoi

    @staticmethod
    def log_and_return_status(msg, code, request, logger, exc_info=False):
        error_type, message, trace = sys.exc_info()
        logger.info("{}: {:.10000} \n Request: {:.10000}".format(code, str(msg), str(request)), exc_info=exc_info)

        if error_type is not None:
            e = api_utils.create_error_message(error_type, message, trace, code, pb=None)
            return json_format.MessageToJson(e), code

        return msg, code

    @staticmethod
    def simple_cache_get(app, name, default):
        c = app.cache.get(name)
        if c is None:
            return default
        else:
            return c

    @staticmethod
    def simple_cache_set(app, name, value):
        app.cache.set(name, value)

    @staticmethod
    def create_error_message(error_type, message, trace, code, pb=None):
        # Compile Error Information
        e = ErrorMessage()
        if error_type is not None:
            e.name = type(message).__name__
            e.code = code
            e.message = message.message
            e.trace.extend(traceback.format_tb(trace))
            if pb is not None:
                e.accompanying_pb = pb.SerializeToString()
                e.accompanying_pb_name = type(pb).__name__
        return e