"""
Limit function calls using spawn.

Limit function calls to specified resource constraints, but guarantees
the use of "spawn" instead of "fork" in order to be compatible with
libraries that aren't fork-safe (e.g. LightGBM).

Adapted from https://github.com/sfalkner/pynisher
"""
import logging
import multiprocessing
import os
import subprocess
import time

from automl.client.core.common import killable_subprocess
from automl.client.core.common import limit_function_call_base as lfcb
from automl.client.core.common import limit_function_call_exceptions as lfce
from automl.client.core.common import limit_function_call_limits as lfcl
from automl.client.core.common import spawn_client


class enforce_limits(lfcb.enforce_limits_base):
    """Class to enforce resource limits using subprocess.Popen."""

    def __call__(self, func):
        """
        Execute the function with the resource constraints applied.

        :param func: The function to be restricted.
        :return:
        """
        class function_wrapper(object):
            def __init__(self2, func):
                self2.func = func
                self2.result = None
                self2.exit_status = None

            def __call__(self2, *args, **kwargs):

                if self.log_function_parameters:
                    self.logger.debug(
                        "Function called with argument: {}, {}".format(
                            args, kwargs))

                # determine timeout
                timeout = None
                if self.wall_time_in_s:
                    timeout = self.wall_time_in_s + self.grace_period_in_s

                # create and start the process
                start = time.time()
                try:
                    res = spawn_client.run_in_proc(
                        timeout,
                        enforce_limits.subprocess_func,
                        args=(
                            self2.func,
                            self.mem_in_mb,
                            self.cpu_time_in_s,
                            self.wall_time_in_s,
                            self.num_processes,
                            self.grace_period_in_s) + args,
                        **kwargs)

                    # read the return value
                    (self2.result, self2.exit_status) = res
                except subprocess.TimeoutExpired:
                    self2.exit_status = lfce.TimeoutException()
                except Exception as e:
                    self.logger.error(
                        "Something else went wrong, sorry.", exc_info=True)
                finally:
                    self2.wall_clock_time = time.time() - start
                    self2.exit_status = (
                        5 if self2.exit_status is None
                        else self2.exit_status)

                return self2.result

        return function_wrapper(func)

    def subprocess_func(func, mem_in_mb, cpu_time_limit_in_s,
                        wall_time_limit_in_s, num_procs,
                        grace_period_in_s, *args, **kwargs):
        """
        Create the function the subprocess can execute.

        :param func: the function to enforce limit on
        :param mem_in_mb:
        :param cpu_time_limit_in_s:
        :param wall_time_limit_in_s:
        :param num_procs:
        :param grace_period_in_s:
        :param args: the args for the function
        :param kwargs: the kwargs for function
        :return:
        """
        logger = logging.Logger("spawn")

        lfcl.set_limits(logger, mem_in_mb, num_procs, wall_time_limit_in_s,
                        cpu_time_limit_in_s, grace_period_in_s)

        return lfcb.enforce_limits_base.call(func, logger, *args, **kwargs)
