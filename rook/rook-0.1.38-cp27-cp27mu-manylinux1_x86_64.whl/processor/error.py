import sys
import traceback

from rook.protobuf import rook_pb2
from rook.exceptions import ToolException
from .namespace_serializer import NamespaceSerializer
from .namespaces.python_object_namespace import PythonObjectNamespace


class Error(object):

    def __init__(self, exc=None, type=None, message=None, parameters=None, traceback=None):
        self.exc = exc

        if isinstance(exc, ToolException):
            self.type = exc.get_type()
            self.message = exc.get_message()
            self.parameters = exc.get_parameters()
        else:
            self.type = type or "Unknown"
            self.message = message
            self.parameters = parameters

        # Extract traceback if was not supplied
        self.traceback = traceback
        if self.traceback is None and sys.exc_info()[2]:
            self.traceback = sys.exc_info()[2]

    def dump(self, error):
        try:
            if self.message:
                error.message = NamespaceSerializer.normalize_string(self.message)
            else:
                error.message = ''
        except Exception:
            pass

        try:
            error.type = NamespaceSerializer.normalize_string(self.type)
        except Exception:
            pass

        try:
            serializer = NamespaceSerializer()
            serializer.dump(PythonObjectNamespace(self.parameters), error.parameters, False)
        except Exception:
            pass

        try:
            serializer = NamespaceSerializer()
            serializer.dump(PythonObjectNamespace(self.exc), error.exc, False)
        except Exception:
            pass

        try:
            if self.traceback:
                serializer = NamespaceSerializer()
                serializer.dump(PythonObjectNamespace('\n'.join(traceback.format_tb(self.traceback))), error.traceback, False)
        except Exception:
            pass

    def dumps(self):
        error = rook_pb2.Error()
        self.dump(error)
        return error
