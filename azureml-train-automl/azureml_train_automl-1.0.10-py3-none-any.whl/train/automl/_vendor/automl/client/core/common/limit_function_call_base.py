"""Limit function calls to specified resource constraints.

Limit function calls to specified resource constraints, but guarantees
the use of "spawn" instead of "fork" in order to be compatible with
libraries that aren't fork-safe (e.g. LightGBM).

Adapted from https://github.com/sfalkner/pynisher
"""
import logging
import multiprocessing
from abc import abstractmethod
from automl.client.core.common import limit_function_call_exceptions as lfce


class enforce_limits_base(object):
    """Base class to enforce resource limits on Linux."""

    def __init__(self, mem_in_mb=None, cpu_time_in_s=None,
                 wall_time_in_s=None, num_processes=None,
                 grace_period_in_s=None, logger=None,
                 log_function_parameters=False):
        """
        Resource limit to be enforced.

        :param mem_in_mb:
        :param cpu_time_in_s:
        :param wall_time_in_s:
        :param num_processes:
        :param grace_period_in_s:
        :param logger:
        :param log_function_parameters:
        """
        self.mem_in_mb = mem_in_mb
        self.cpu_time_in_s = cpu_time_in_s
        self.num_processes = num_processes
        self.wall_time_in_s = wall_time_in_s
        self.grace_period_in_s = (
            0 if grace_period_in_s is None else grace_period_in_s)
        self.logger = (
            logger if logger is not None else multiprocessing.get_logger())
        self.log_function_parameters = log_function_parameters

        if self.mem_in_mb is not None:
            self.logger.debug(
                "Restricting your function to {} mb memory."
                .format(self.mem_in_mb))
        if self.cpu_time_in_s is not None:
            self.logger.debug(
                "Restricting your function to {} seconds cpu time."
                .format(self.cpu_time_in_s))
        if self.wall_time_in_s is not None:
            self.logger.debug(
                "Restricting your function to {} seconds wall time."
                .format(self.wall_time_in_s))
        if self.num_processes is not None:
            self.logger.debug(
                "Restricting your function to {} threads/processes."
                .format(self.num_processes))
        if self.grace_period_in_s is not None:
            self.logger.debug(
                "Allowing a grace period of {} seconds."
                .format(self.grace_period_in_s))

    @abstractmethod
    def __call__(self, func):
        """
        Execute the function with the resource constraints applied.

        :param func: The function to be restricted.
        :return:
        """
        ...

    def call(func, logger, *args, **kwargs):
        """
        Execute the function with the supplied arguments.

        :param func:
        :param logger:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            logger.debug("call function")
            res = (func(*args, **kwargs), 0)
            logger.debug("function returned properly: {}".format(res))
        except MemoryError as e:
            res = (None, lfce.MemorylimitException())
        except OSError as e:
            if (e.errno == 11):
                res = (None, lfce.SubprocessException())
            else:
                res = (None, lfce.AnythingException())
        except lfce.CpuTimeoutException as e:
            res = (None, lfce.CpuTimeoutException())
        except lfce.TimeoutException as e:
            res = (None, lfce.TimeoutException())
        except lfce.AnythingException as e:
            res = (None, lfce.AnythingException())
        except Exception as e:
            res = (None, e)
            logger.error("Unexpected Error", exc_info=True)

        return res
