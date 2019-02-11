from __future__ import absolute_import, division, print_function

import os

import autest.api
import autest.core.streamwriter as streamwriter
import autest.testers as testers
from autest.common.constructor import call_base, smart_init
from autest.core.testenity import TestEnity
from autest.core.testerset import TesterSet

from .file import File
from .process import Process


@smart_init
class Streams(TestEnity):
    @call_base(TestEnity=("runable", ))
    def __init__(self, runable):

        self.__all = File(
            self._Runable,
            os.path.join(self._Runable.StreamOutputDirectory, streamwriter.full_stream_file),
            runtime=False
        )

        self.__stdout = File(
            self._Runable,
            os.path.join(self._Runable.StreamOutputDirectory, streamwriter.out_stream_file),
            runtime=False
        )

        self.__stderr = File(
            self._Runable,
            os.path.join(self._Runable.StreamOutputDirectory, streamwriter.err_stream_file),
            runtime=False
        )

        self.__error = File(
            self._Runable,
            os.path.join(self._Runable.StreamOutputDirectory, streamwriter.error_stream_file),
            runtime=False
        )

        self.__warning = File(
            self._Runable,
            os.path.join(self._Runable.StreamOutputDirectory, streamwriter.warning_stream_file),
            runtime=False
        )

        self.__verbose = File(
            self._Runable,
            os.path.join(self._Runable.StreamOutputDirectory, streamwriter.verbose_stream_file),
            runtime=False
        )

        self.__debug = File(
            self._Runable,
            os.path.join(self._Runable.StreamOutputDirectory, streamwriter.debug_stream_file),
            runtime=False
        )

    @property
    def stdout(self):
        return self.__stdout

    @stdout.setter
    def stdout(self, tester):
        self.__stdout.Content = tester

    @property
    def stderr(self):
        return self.__stdout

    @stderr.setter
    def stderr(self, tester):
        self.__stderr.Content = tester

    @property
    def All(self):
        return self.__all

    @All.setter
    def All(self, tester):
        self.__all.Content = tester

    @property
    def Warning(self):
        return self.__warning

    @Warning.setter
    def Warning(self, tester):
        self.__warning.Content = tester

    @property
    def Error(self):
        return self.__error

    @Error.setter
    def Error(self, tester):
        self.__error.Content = tester

    @property
    def Debug(self):
        return self.__debug

    @Debug.setter
    def Debug(self, tester):
        self.__debug.Content = tester

    @property
    def Verbose(self):
        return self.__verbose

    @Verbose.setter
    def Verbose(self, tester):
        self.__verbose.Content = tester


autest.api.AddTestEnityMember(Streams, classes=[Process])
