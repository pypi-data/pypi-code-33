import logging

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel('INFO')

import signal, os, sys
import importlib


class Configurator:
    def __init__(self):
        self._subscribers = {}

    def register_subscriber(self, name, subscriber):
        self._subscribers[name] = subscriber

    def include(self, module_name):
        module = importlib.import_module(module_name)
        setup = getattr(module, 'subsetup_')
        if setup:
            setup(self)

    @property
    def subscribers(self):
        return [s for s in self._subscribers.values()]


class AppConfig:
    def __init__(self, cmd_obj, app_path):
        mod_path, app_name = app_path.split(':')
        mod = importlib.import_module(mod_path)
        self.app = getattr(mod, app_name)
        cmd_obj.app_config = self


class Command:
    USAGE = """
Usage: gces_subsfm [option] [option argument]

options:
   -A <application path>: example "-A mypackage.mymodule:app"
    """
    OPTION = 'OPTION'
    ARGS = 'ARGS'

    def __init__(self):
        self.cmds_map = {
            '-A': (1, AppConfig),
        }
        self.app_config = None

    def _usage(self):
        print(self.USAGE)
        sys.exit(1)

    def execute(self):
        cmds = sys.argv[1:]
        if not cmds:
            self._usage()

        cmd_stack = []
        cmd_stack_place = self.OPTION
        cmd_options_count = 0
        for i in cmds:
            if cmd_stack_place == self.OPTION:
                cmd_info = self.cmds_map.get(i)
                if not cmd_info:
                    self._usage()
                cmd_options_count, _func = cmd_info
                cmd_stack.append([_func, []])
                cmd_stack_place = self.ARGS
            elif cmd_stack_place == self.ARGS:
                cmd_stack[-1][-1].append(i)
                cmd_options_count -= 1
                if cmd_options_count == 0:
                    cmd_stack_place = self.OPTION

        for cmd in cmd_stack:
            _f, _a = cmd
            try:
                _f(self, *_a)
            except Exception as exc:
                # Create more meaninful errors
                print('Error: {}'.format(exc))
                self._usage()

def main():
    cmd = Command()
    cmd.execute()
    configurator = cmd.app_config.app

    def exit_gracefully(self,signum):
        for s in configurator.subscribers:
            s.subscriber.future.cancel()

    def start_all():
        for s in configurator.subscribers:
            s.start()
        # Is it ok to use the last subscribe to block it here?
        s.subscriber.future.result()

    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    start_all()
