import aether
import time
from aether.Sky import Sky
from aether.session.GlobalConfig import GlobalConfig
from aether.session import Exceptions
from aether.proto.api_pb2 import ErrorMessage
import traceback

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkySession(object):

    def __init__(self, app=None):
        self._app = app
        self._sky = None

    def GlobalConfig(self):
        return GlobalConfig._getInstance()

    def aether_client(self):
        return GlobalConfig._getInstance()._aether_client()

    @staticmethod
    def _package_diagnostic(p):
        return "SDK INFO: {} version {}; Location: {}; Egg Name: {}\n".format(p.project_name, p.version, p.location, p.egg_name)

    def __enter__(self):
        self._sky = Sky(self.aether_client(), app=self._app)
        return self._sky

    def __exit__(self, type, value, trace_b):

        # Error catching on the Sky
        if isinstance(value, Exceptions.SkyError):
            msg = "\n----------------------------------------------------------------------------------\n"
            msg += "Aether SDK Diagnostic Stack BELOW. Please provide when reporting errors or issues.\n"
            msg += "Timestamp: {}\n".format(time.ctime())

            actual_runtime_path = "/".join(aether.__path__[0].split("/")[:-1])
            msg += "SDK INFO: Runtime package path: {}\n".format(actual_runtime_path)
            msg += "SDK INFO: Aether SDK version: {}\n".format(aether.__version__)
            msg += "SDK INFO: {}".format(self.GlobalConfig()._diagnostic_debug_report())
            msg += "\n\n"

            last_n = 3
            msg += "Last N={} Requests Made This Sky Session:\n".format(last_n)
            for call_made in self._sky._aether_client.get_call_stack()[-last_n:]:
                msg += "Hostport: {}\n".format(call_made[0])
                msg += "Request: {}\n".format(str(call_made[1])[:10000])
                msg += "\n"

            for arg_i, arg in enumerate(value.args):
                if isinstance(arg, ErrorMessage):
                    msg += "Traceback Error Received From Server. Error Number {}:\n".format(arg_i)
                    msg += "Name: {}\n".format(arg.name)
                    msg += "Code: {}\n".format(arg.code)
                    msg += "Headline: {}\n".format(arg.message)
                    msg += "Traceback:\n"
                    msg += "".join(arg.trace)
                else:
                    msg += "Server Returned A Non-ErrorMessage Message. Error Number {}:\n".format(arg_i)
                    msg += str(arg)
                    msg += "\n"

            # Add Stack Trace
            msg += "\n"
            msg += "Aether SDK Client-Side Trace:\n"
            msg += traceback.format_exc()

            msg += "\nAether SDK Diagnostic Stack ABOVE. Please provide when reporting errors or issues.\n"
            msg += "---------------------------------------------------------------------------------\n"
            logger.info(msg)

        # Throw the error still.
        return False
