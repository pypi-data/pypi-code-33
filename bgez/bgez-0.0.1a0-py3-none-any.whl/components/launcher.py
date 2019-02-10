import asyncio
import atexit
import sys

from collections import OrderedDict
from importlib import import_module

from bgez.asyn import task

from . import PythonComponent

__all__ = [
    'Launcher'
]

MODULE = 'Main Python Module'

class Launcher(PythonComponent):
    # pylint: disable=E0401

    args = OrderedDict([
        (MODULE, ''),
    ])

    def start(self, args):
        from bge.logic import endGame
        self.error = None

        module_id = args.get(MODULE)
        try: self.module = import_module(module_id)
        except Exception as e:
            self.error = e
            endGame()
            raise e

        from bgez.game import logic
        self.logic = logic

        original_excepthook = sys.excepthook
        def excepthook(type, value, traceback):
            original_excepthook(type, value, traceback)
            endGame()
        sys.excepthook = excepthook

        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        atexit.register(self.exit)

    def update(self):
        if self.error is not None: return
        from bge.logic import getLogicTicRate
        self.logic._update()
        frametime = 1 / getLogicTicRate()
        self.loop.run_until_complete(asyncio.sleep(frametime / 3))

    def exit(self):
        self.loop.run_until_complete(self.logic._exit())
