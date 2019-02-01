# imports
import argparse
import sys
import os
from ._grrargparse_helpers import j
from ._module import APIModule
from .grr_logging import Logger,log, set_debugging

# end imports

# Global instance of grrargparse
cmdline = None


# Command Line class - main entry point to application.
class grrargparse(object):

    DEFAULT_BASE_DIR = j(os.getcwd())
    DEFAULT_OUT_DB = "out.db"
    NO_ARGS = "####NOARGS####"

    def __init__(self, args=None):

        self.registered_modules = []
        self._auto_modules = []
        self._run_all_modules = False

        if args is None:
            self.args = {}
            self.args
        else:

            # these are the global args
            try:
                assert isinstance(args,dict)
            except AssertionError:
                log("Supplied args to CommandLine that is not a dict: " + type(args),Logger.FATAL)
            self.args = args

        self.parser = argparse.ArgumentParser()

        # add global args
        self.parser.add_argument('-X',"--debug",action="store_true", dest="debug", help="Enable Debugging", required=False)
        self.subp = self.parser.add_subparsers(help="Available Commands", dest="cmd")

    def add_global_argument(self, *args, **kwargs):

        #add global tag on args to make sure it isn't overwritten by module arg
        kwargs['dest'] = kwargs['dest']+"_global"
        self.parser.add_argument(*args, **kwargs)

    def _parse(self):

        a = vars(self.parser.parse_args())
        for l in list(a.keys()):

            val = a.get(l)

            if val is not None:
                self.args[l] = val

    def get_var(self,name):
        return self.args[name]


    def register_module(self, module):

        m = module(self.subp, self.args)

        # pre-process command line arguments
        m.preprocess()

        # update list of arguments
        self.args.update(m.get_args())

        # add module to list
        self.registered_modules.append(m)

    def run(self):
        self._parse()

        # enable debugging if specified
        if self.args['debug']:
            set_debugging(True)

        self._handle_no_args()

        for module in self.registered_modules:
            assert isinstance(module,APIModule)

            # run 1 module specified by cmd or All modules or any auto module
            if self._run_all_modules or module in self._auto_modules or ("cmd" in self.args and self.args["cmd"] == module.name):
                module.update_args(self.args)
                module.proc()


    def _handle_no_args(self):
        if not self._run_all_modules:
            if len(self._auto_modules) == 0 and "cmd" not in self.args:
                log("No auto/default modules specified and no module specified",Logger.DEBUG)
                self.parser.print_help()
                sys.exit()

    def add_auto_module(self, module):
        self._auto_modules.append(module)

    def run_all_modules(self):
        self._run_all_modules = True


def get_instance():
    global cmdline
    if cmdline is None:
        cmdline = grrargparse()
    return cmdline






