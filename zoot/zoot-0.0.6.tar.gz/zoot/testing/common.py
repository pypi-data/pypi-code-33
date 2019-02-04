from abc import ABC, abstractmethod

import unittest, re

from typing import List, Callable
from colorama import Fore, Back, Style

from zoot.utils.collections import TupleMap

class Before(ABC):

    def __init__(self, name:str="Before"):
        self.__name = name

    def get_name(self) -> str:
        return self.__name

    @abstractmethod
    def get_error(self) -> Exception:
        pass

    @abstractmethod
    def has_error(self) -> bool:
        pass

    def to_xml(self, classname:str="zoot.common.testing.Before") -> (str):

        if self.has_error():
            return '\t<testcase classname="{}" name="{}">\n\t\t<failure type="BeforeException" message="{}"></failure>\n\t</testcase>\n'.format(classname, self.get_name(), self.get_error())

        return '\t<testcase classname="{} name="{}"/>\n'.format(classname, self.get_name())

    @abstractmethod
    def run(self) -> Exception:
        pass

class Test(ABC, unittest.TestCase):

    def __init__(self, name:str):
        unittest.TestCase.__init__(self, "execute")
        self.__name = name
        self.__skip = False

    def get_name(self) -> str:
        return self.__name

    def skip(self, skip:bool):
        self.__skip = skip

    def is_skipped(self) -> bool:
        self.__skip

    @abstractmethod
    def has_error(self) -> bool:
        pass

    @abstractmethod
    def get_error(self) -> Exception:
        pass

    def set_before(self, before:Before):
        self.__before = before

    def get_before(self)->Before:
        return self.__before

    def execute(self):
        self.run_test()

    @abstractmethod
    def run_test(self):
        pass

    def to_xml(self, classname:str="zoot.common.testing.Test") -> (str):

        if self.has_error():
            return '\t<testcase classname="{}" name="{}">\n\t\t<failure type="TestException" message="{}"></failure>\n\t</testcase>\n'.format(classname, self.get_name(), self.get_error())

        return '\t<testcase classname="{} name="{}"/>\n'.format(classname, self.get_name())

class TestListener(ABC):


    @abstractmethod
    def on_test_started(self, test:Test):
        pass

    @abstractmethod
    def on_test_skipped(self, test:Test):
        pass

    @abstractmethod
    def on_test_success(self, test:Test):
        pass

    @abstractmethod
    def on_test_failed(self, test:Test):
        pass

class TestListenerHandler():

    def __init__(self, listener:TestListener=None):
        self.__listener = listener

    def has_listener(self)->bool:
        return True if self.__listener else False

    def set_listener(self, listener:TestListener):
        self.__listener = listener

    def get_listener(self)->TestListener:
        return self.__listener

class Suite(unittest.TestSuite, TestListenerHandler):

    def __init__(self, name:str, *tests:Test):
        unittest.TestSuite.__init__(self, ())
        TestListenerHandler.__init__(self, None)

        self.__name = name
        self.__before = None
        self.__tests = []

        self.add_tests(*tests)

    def to_xml(self)->str:

        successes = 0
        skipped = 0
        failures = 0

        xml = ""

        for test in self.__tests:
            
            if test.is_skipped(): skipped = skipped + 1
            elif test.has_error(): failures = failures + 1
            else: successes = successes + 1

            xml += test.to_xml()

        total = successes + failures + skipped

        return '\t<testsuite name="{}" tests="{}" skipped="{}" failures="{}">\n\t\t{}\n\t</testsuite>\n'.format(self.__name, total, skipped, failures, xml)

    def get_name(self) -> str:
        return self.__name
    
    def get_tests(self) -> List[Test]:
        return self.__tests

    def add_tests(self, *tests:Test):

        for test in tests:
            if isinstance(test, TestListenerHandler):
                if not test.has_listener():
                    test.set_listener(self.get_listener())

            self.addTest(test)

    def has_before(self)->bool:
        return True if self.__before else False

    def set_before(self, before:Before):
        self.__before = before

    def get_before(self)->Before:
        return self.__before
    
    def __str__(self):
        return "Suite: {}, Count: {}".format(self.__name, len(self.get_tests()))

