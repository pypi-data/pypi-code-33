"""Limit function calls to specified resource constraints.

Adapted from:
 https://github.com/sfalkner/pynisher
"""
import logging
import multiprocessing
import os
import sys
import time

from automl.client.core.common import killable_subprocess
from automl.client.core.common import limit_function_call_base as lfcb
from automl.client.core.common import limit_function_call_exceptions as lfce
from automl.client.core.common import limit_function_call_limits as lfcl


class enforce_limits(lfcb.enforce_limits_base):
    """Class to enforce resource limits using multiprocessing.Process."""

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

                # create a pipe to retrieve the return value
                parent_conn, child_conn = multiprocessing.Pipe()

                # create and start the process
                subproc = multiprocessing.Process(
                    target=enforce_limits.subprocess_func,
                    name="pynisher function call",
                    args=(
                        self2.func,
                        child_conn,
                        self.logger,
                        self.mem_in_mb,
                        self.cpu_time_in_s,
                        self.wall_time_in_s,
                        self.num_processes,
                        self.grace_period_in_s) + args,
                    kwargs=kwargs)

                if self.log_function_parameters:
                    self.logger.debug(
                        "Function called with argument: {}, {}".format(
                            args, kwargs))

                # start the process

                start = time.time()
                subproc.start()
                child_conn.close()

                try:
                    # read the return value
                    if (self.wall_time_in_s is not None):
                        if parent_conn.poll(
                                self.wall_time_in_s +
                                self.grace_period_in_s):
                            (self2.result,
                                self2.exit_status) = parent_conn.recv()
                        else:
                            subproc.terminate()
                            self2.exit_status = lfce.TimeoutException()

                    else:
                        self2.result, self2.exit_status = \
                            parent_conn.recv()

                except EOFError as e:
                    # Don't see that in the unit tests :(
                    self.logger.error(
                        "Your function call closed the pipe prematurely ->"
                        " Subprocess probably got an uncatchable signal.",
                        exc_info=True)

                    import resource

                    self2.resources_function = resource.getrusage(
                        resource.RUSAGE_CHILDREN)
                    self2.resources_pynisher = resource.getrusage(
                        resource.RUSAGE_SELF)
                    self2.exit_status = lfce.AnythingException()

                except Exception as e:
                    self.logger.error(
                        "Something else went wrong, sorry.", exc_info=True)
                finally:
                    self2.wall_clock_time = time.time() - start
                    self2.exit_status = (
                        5 if self2.exit_status is None
                        else self2.exit_status)
                    # don't leave zombies behind

                    # subproc.join hangs in mac, due to empty queue
                    # deadlock join with timeout doesn't work either,
                    # so forcing terminate. finally is called only after
                    # the timeout period
                    if subproc.is_alive() and sys.platform == 'darwin':
                        subproc.terminate()
                    else:
                        subproc.join()

                return (self2.result)

        return (function_wrapper(func))

    def subprocess_func(func, pipe, logger, mem_in_mb, cpu_time_limit_in_s,
                        wall_time_limit_in_s, num_procs,
                        grace_period_in_s, *args, **kwargs):
        """
        Create the function the subprocess can execute.

        :param func: the functiom to enforce limit on
        :param pipe: the pipe to communicate the result
        :param logger:
        :param mem_in_mb:
        :param cpu_time_limit_in_s:
        :param wall_time_limit_in_s:
        :param num_procs:
        :param grace_period_in_s:
        :param args: the args fot the functiom
        :param kwargs: the kwargs for function
        :return:
        """
        lfcl.set_limits(logger, mem_in_mb, num_procs, wall_time_limit_in_s,
                        cpu_time_limit_in_s, grace_period_in_s)

        try:
            res = lfcb.enforce_limits_base.call(func, logger, *args, **kwargs)
            return res
        finally:
            try:
                logger.debug("return value: {}".format(res))

                pipe.send(res)
                pipe.close()

            except Exception:
                # this part should only fail if the parent process is already
                # dead, so there is not much to do anymore :)
                pass
            finally:
                # recursively kill all children
                pid = os.getpid()
                killable_subprocess.kill_process_tree_in_linux(pid)
