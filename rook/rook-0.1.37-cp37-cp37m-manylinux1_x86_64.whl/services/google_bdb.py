# -*- coding: utf-8 -*-
import os
import sys
import six
from functools import partial

from .exts.cloud_debug_python.module_explorer import GetCodeObjectAtLine, _GetModuleCodeObjects, _GetLineNumbers

from rook.logger import logger

from ..exceptions import RookBdbCodeNotFound, RookBdbSetBreakpointFailed, RookInvalidPositionException

try:
    from . import cdbg_native
    cdbg_native.InitializeModule(None)
except ImportError:
    # Special handling for Google AppEngine (Python 2.7)
    from google.devtools.cdbg.debuglets.python import cdbg_native


class Bdb(object):
    def __init__(self):
        self.fncache = {}
        self._cookies = {}
        self.user_line = None

    def set_trace(self):
        # Not needed
        pass

    def canonic(self, filename):
        if filename[0] == "<" and filename[-1] == ">":
            return filename
        canonic = self.fncache.get(filename)
        if not canonic:
            canonic = os.path.abspath(filename)
            canonic = os.path.normpath(canonic)
            self.fncache[filename] = canonic
        return canonic

    def ignore_current_thread(self):
        # Not needed
        pass

    def set_break(self, module, filename, lineno):
        status, code_object = GetCodeObjectAtLine(module, lineno)
        if not status:
            if hasattr(module, '__file__'):
                logger.debug("CodeNotFound module filename %s", module.__file__)

            for cobj in _GetModuleCodeObjects(module):
                logger.debug("Name: %s", cobj.co_name)
                for cline in _GetLineNumbers(cobj):
                    logger.debug("Name: %s, Line %d", cobj.co_name, cline)

            if code_object == (None, None):
                raise RookBdbCodeNotFound(filename=filename)
            else:
                raise RookInvalidPositionException(filename=filename, line=lineno, alternatives=code_object)

        # Install the breakpoint
        cookie = cdbg_native.SetConditionalBreakpoint(code_object, lineno, None, partial(self._callback, lineno=lineno))
        if not cookie:
            raise RookBdbSetBreakpointFailed()

        self._cookies[filename, lineno] = cookie

    def clear_break(self, filename, lineno):
        pos = filename, lineno
        try:
            cookie = self._cookies[pos]
        except KeyError:
            return

        cdbg_native.ClearConditionalBreakpoint(cookie)
        del self._cookies[pos]

    def clear_all_breaks(self):
        for cookie in six.itervalues(self._cookies):
            cdbg_native.ClearConditionalBreakpoint(cookie)

        self._cookies = {}

    def close(self):
        pass

    def _callback(self, event, frame, lineno):
        if event != cdbg_native.BREAKPOINT_EVENT_HIT:
            logger.error("Unexpected event- %d", event)
            return

        if frame and self.user_line:
            self.user_line(frame, lineno=lineno)
