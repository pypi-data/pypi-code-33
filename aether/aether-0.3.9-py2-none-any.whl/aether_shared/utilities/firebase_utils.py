import google.cloud
import json
from google.protobuf import json_format
from google.protobuf.message import DecodeError
from aether.sky_utils import sky_utils

class firebase_utils(object):

    @staticmethod
    def document_exists(doc_ref, return_dict_if_exists=False):
        try:
            doc = doc_ref.get()
            if return_dict_if_exists:
                return doc.to_dict()
            else:
                return True
        except google.cloud.exceptions.NotFound:
            if return_dict_if_exists:
                return None
            else:
                return False

    @staticmethod
    def verify_json(j, return_dict_if_valid=False):
        try:
            d = json.loads(j)
            if return_dict_if_valid:
                return d
            else:
                return True
        except ValueError:
            if return_dict_if_valid:
                return None
            else:
                return False

    @staticmethod
    def verify_pb(json_string, pb, return_pb_if_valid=False):
        try:
            pb = sky_utils.deserialize_pb(json_string, pb)
            if return_pb_if_valid:
                return pb
            else:
                return True
        except DecodeError:
            if return_pb_if_valid:
                return None
            else:
                return False

