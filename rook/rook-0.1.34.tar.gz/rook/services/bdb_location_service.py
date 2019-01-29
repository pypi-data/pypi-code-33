import sys
import platform
import inspect
import importlib
import six

from rook.logger import logger
from rook.processor.namespaces.frame_namespace import FrameNamespace
from ..exceptions import RookBdbFailedException


class BdbLocationService(object):
    NAME = "Bdb"

    def __init__(self):
        self._bdb = self._get_bdb().Bdb()
        self._bdb.user_line = self.user_line

        self._breakpoints = dict()
        self._positions = dict()

        self._bdb.set_trace()

    def ignore_current_thread(self):
        self._bdb.ignore_current_thread()

    def add_breakpoint_aug(self, module, lineno, aug):
        filepath = inspect.getsourcefile(module)
        logger.info("Setting breakpoint at %s:%s", filepath, lineno)

        canonic = self._bdb.canonic(filepath)
        pos = (canonic, lineno)

        if pos in self._breakpoints:
            self._breakpoints[pos].append(aug)
        else:
            result = self._bdb.set_break(module, canonic, lineno)
            if result:
                raise RookBdbFailedException(result)
            else:
                self._breakpoints[pos] = [aug]

        self._positions[aug.aug_id] = pos
        aug.set_active()

    def remove_aug(self, aug_id):
        # Get current augs in position
        try:
            pos = self._positions[aug_id]
        except KeyError:
            return

        current_augs = self._breakpoints[pos]

        # Divide augs into delete and keep
        augs_to_delete = [aug for aug in current_augs if aug.aug_id == aug_id]
        augs_to_keep = [aug for aug in current_augs if aug.aug_id != aug_id]

        # Update list
        if augs_to_keep:
            self._breakpoints[pos] = augs_to_keep
        else:
            del self._breakpoints[pos]
            self._bdb.clear_break(pos[0], pos[1])

        # Update status
        for aug in augs_to_delete:
            aug.set_removed()

        # Remove from pos list
        del self._positions[aug_id]

    def clear_augs(self):
        # Attempt to clean nicely
        for aug_id in list(self._positions.keys()):
            self.remove_aug(aug_id)

        # Clean hard any left overs
        self._breakpoints = dict()
        self._positions = dict()
        self._bdb.clear_all_breaks()

    def close(self):
        self.clear_augs()
        self._bdb.close()

    def user_line(self, frame, lineno=None):
        try:
            filename = self._bdb.canonic(frame.f_code.co_filename)

            # Some Bdb implementations report line numbers before the break
            frame_namespace = FrameNamespace(frame)
            if lineno:
                frame_namespace._lineno = lineno

            augs = self._breakpoints.get((filename, frame_namespace._lineno))

            if augs:
                for aug in augs:
                    aug.execute(frame_namespace, dict())
            else:
                logger.error("Aug not found! %s@%d", str(filename), frame_namespace._lineno)
        except:
            logger.exception("Error while processing breakpoint")

    def get_canonical_path(self, module):
        return self._bdb.canonic(inspect.getsourcefile(module))

    @staticmethod
    def _get_bdb():
        from rook.config import InstrumentationConfig
        if InstrumentationConfig.ENGINE == "auto":
            if 'CPython' == platform.python_implementation() and sys.platform in ('darwin', 'linux2', 'linux'):
                if (six.PY2 and sys.version_info > (2, 7, 0)) or (six.PY3 and sys.version_info >= (3, 5, 0)):
                    from . import google_bdb as bdb
                else:
                    from . import py_bdb as bdb
            else:
                from . import py_bdb as bdb
        else:
            bdb = importlib.import_module(".." + InstrumentationConfig.ENGINE, __name__)

        return bdb
