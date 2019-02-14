# -*- coding: utf-8 -*-
"""
Author: Amir Mofakhar <amir@mofakhar.info>
Date created: 2019-02-14
"""
from time import time
from unittest import TestCase

from memory_profiler import memory_usage

class ExecutionTest:

    ExecutionTestException = TestCase.failureException

    def assertMaximumExecutionTime(self, max_execution_time_seconds, func, *args, **kwargs):
        start_time = time()
        func(*args, **kwargs)
        e_time = time() - start_time
        if e_time > max_execution_time_seconds:
            msg = 'Execution time {} seconds is greater than {} seconds!'.format(e_time,
                                                                                         max_execution_time_seconds)
            raise self.ExecutionTestException(msg)

    def assertMaximumMemoryUsage(self, max_memory_usage, func, *args, **kwargs):
        mem_usage = memory_usage((func, args, kwargs))
        max_used_memory = max(mem_usage)

        if max_used_memory > max_memory_usage:
            msg = 'Memory usage {} is greater than {}!'.format(max_used_memory, max_memory_usage)
            raise self.ExecutionTestException(msg)
