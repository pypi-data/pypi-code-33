# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Safe resource limits class for early termination.

Implementation of resource limits with fallback for systems
which do not support the python resource module.
"""

import sys
import time
import warnings
from io import StringIO
from logging import getLogger
from sys import platform

if platform == "linux" or platform == "linux2":
    simple_platform = "linux"
elif platform == "darwin":
    simple_platform = "osx"
elif platform == "win32":
    simple_platform = "win"
else:
    simple_platform = "unknown"

TIME_CONSTRAINT = 'wall_time_in_s'
MEM_CONSTRAINT = 'mem_in_mb'

default_resource_limits = {
    # note that this is approximate
    MEM_CONSTRAINT: None,
    'cpu_time_in_s': None,
    # use 1 min for cluster runs.
    TIME_CONSTRAINT: 60 * 10,
    'num_processes': None,
    'grace_period_in_s': None,
    'logger': None
}


# use this for module functions
class safe_enforce_limits(object):
    """Method to allow for early termination of an execution."""

    try:
        import resource
        # see https://github.com/sfalkner/pynisher
        from automl.client.core.common import limit_function_call_spawn \
            as pynisher_spawn
        from automl.client.core.common import limit_function_call \
            as pynisher_sub
        ok = True
    except ImportError as e:
        # this is the error we're expecting
        assert str(e) == "No module named 'resource'"
        ok = False

    def get_param_str(self, kwargs):
        """
        Combine the key-value in kwargs as a string.

        :param kwargs:
        :return: str.
        """
        s = ""
        for k, v in kwargs.items():
            s += k + "=" + str(v) + ", "
        return s

    def __init__(self, *args, run_as_spawn=True, **kwargs):
        """
        Init the class.

        :param args:
        :param kwargs:
        """
        self.log = getLogger(__name__)
        self.log.info("limits set to %s" % self.get_param_str(kwargs))

        if kwargs.get('logger', None) is not None:
            self.log.warning("logger specified for pynisher.")
        else:
            kwargs['logger'] = self.log
        if not self.ok:
            # TODO Add the windows resource limit in core sdk
            # change the code to use the libray's resource enforcement.
            if simple_platform != "win":
                self.log.warning("Unable to enforce resource limits.")
                warnings.warn("Unable to enforce resource limits.")
        self.obj = None
        if self.ok:
            if run_as_spawn:
                pynisher_module = self.pynisher_spawn
            else:
                pynisher_module = self.pynisher_sub
            self.obj = pynisher_module.enforce_limits(*args, **kwargs)

        self.exit_status = None
        self.wall_clock_time = None
        self.result = None

    def __call__(self, func):
        """
        Adding a call function to the class.

        :param func:
        :return:
        """
        if self.ok:
            def func2(*args, **kwargs):

                # capture and log stdout, stderr
                # out, err = sys.stdout, sys.stderr
                # out_str, err_str = StringIO(), StringIO()
                # sys.stdout, sys.stderr = out_str, err_str

                f_obj = self.obj.__call__(func)
                r = f_obj(*args, **kwargs)
                self.exit_status = f_obj.exit_status
                self.wall_clock_time = f_obj.wall_clock_time
                self.result = f_obj.result

                # out_str, err_str = out_str.getvalue(), err_str.getvalue()
                # if err_str != "": self.log.error(err_str)
                # if out_str != "": self.log.info(out_str)
                # sys.stdout, sys.stderr = out, err
                return r
            return func2
        return func
