from aether.app_io_utilities import app_io_utilities
import aether.aetheruserconfig as cfg
from aether_shared.utilities.user_api_utils import user_api_utils
from aether.proto.api_pb2 import ErrorMessage
import json
import copy
import requests
from session.Exceptions import SkyRuntimeError
import StringIO
from aether.sky_utils import sky_utils

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class aether_client(object):

    def __init__(self, uuid, hostport, protocol):
        self._uuid = uuid
        self._hostport = hostport
        self._protocol = protocol
        self._request_call_stack = []

    def get_call_stack(self):
        return self._request_call_stack

    def clear_call_stack(self):
        self._request_call_stack = []

    def _make_call(self, request, hostport):
        logger.info("Making REST call to: {} with {}".format(hostport, str(request)[:10000]))
        self._request_call_stack.append((hostport, request))
        try:
            url = "{protocol}{hostport}{entry}".format(protocol=self._protocol, hostport=hostport, entry=request["entry"])
            headers = {'Content-Transfer-Encoding': 'base64'}
            response = requests.request(request["method"], url, json=request["data"], headers=headers, stream=True)

            content = StringIO.StringIO()
            text_status = user_api_utils.rc_updating_format_text("Downloaded {mb:.{digits}f} MB...")
            bytes_transferred = 0
            for chunk in response.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    content.write(chunk)
                    bytes_transferred += len(chunk)
                    text_status.to_print(args=dict(mb=bytes_transferred / 1024. / 1024, digits=6))
            text_status.to_print(args=dict(mb=bytes_transferred / 1024. / 1024, digits=6), finished=True)

        except Exception, err:
            raise SkyRuntimeError(err)

        return response, content.getvalue()

    def _make_request(self, entry_name, entry_parameters, uri_parameters):
        if entry_name not in cfg._rest_entrypoints:
            raise SkyRuntimeError("Requested entrypoint unrecognized: {}".format(entry_name))

        request = copy.deepcopy(cfg._rest_entrypoints[entry_name])
        try:
            request["entry"] = request["entry"].format(**entry_parameters)
        except Exception:
            raise SkyRuntimeError("Requested entrypoint required parameters missing: {}".format(entry_name))

        request["data"] = uri_parameters
        return request

    def post_to(self, entry_name, entry_parameters, uri_parameters, output_structure=None, app=None):
        uri_parameters = copy.deepcopy(uri_parameters)
        uri_parameters.update(dict(uuid=self._uuid))

        # if input_structure is not None:
        #     uri_parameters = self.serialize_to_input(uri_parameters, input_structure)
        #     if uri_parameters is None:
        #         logger.error("uri_parameters incorrectly formed by input_structure.")
        #         return None

        request = self._make_request(entry_name, entry_parameters, uri_parameters)

        if app is not None:
            return app.add(request, None, output_structure, "MICROSERVICE")
        return self.post_request(request, output_structure)

    def post_request(self, request, output_structure):
        response, r_content = self._make_call(request, self._hostport)

        try:
            content = json.loads(r_content)
        except Exception:
            raise SkyRuntimeError("Request returned ill formed JSON: {}".format(r_content))

        if not response.ok:
            # Try to identify whether the client call returned an ErrorMessage protocall buffer.
            is_error_pb, error_pb = aether_client._try_parsing_error_message(content)
            if is_error_pb:
                raise SkyRuntimeError(error_pb)
            else:
              raise SkyRuntimeError("Request failed {}: {}".format(response.reason, r_content))

        if output_structure is not None:
            return app_io_utilities.marshal_output(content, output_structure)
        return content

    @staticmethod
    def _try_parsing_error_message(content):
        try:
            e = sky_utils.deserialize_pb(content, ErrorMessage())
            return True, e
        except:
            return False, None
