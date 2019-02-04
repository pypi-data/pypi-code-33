from datetime import datetime
from abc import abstractmethod, ABC
import time, os, re, json, threading

from colorama import Fore, Back, Style

from zoot.testing.common import Suite, Test, TestListener

class Reporter(TestListener):

    def __init__(self):
        TestListener.__init__(self)

    @abstractmethod
    def report(self, message:str):
        pass

class Reporting(ABC):

    @abstractmethod
    def json(self, *suites:Suite)->str:
        pass

    @abstractmethod
    def xml(self, *suites:Suite)->str:
        pass

    
class ConsoleReporter(Reporter):

    def __init__(self):
        Reporter.__init__(self)
        self.__lock = threading.Lock()

    def report(self, message:str):
        self.__lock.acquire()
        print(message)
        self.__lock.release()   

    def on_test_started(self, test:Test):
        self.report("\n\t{}{}, STARTED:{} '{}'".format(str(datetime.now()), Fore.WHITE, Style.RESET_ALL, str(test)))

    def on_test_skipped(self, test:Test):
        self.report("\n\t{}{}, SKIPPED:{} '{}'".format(str(datetime.now()), Fore.CYAN, Style.RESET_ALL, str(test)))

    def on_test_success(self, test:Test):
        self.report("\n\t{}{}, SUCCESS:{} '{}'".format(str(datetime.now()), Fore.GREEN, Style.RESET_ALL, str(test)))

    def on_test_failed(self, test:Test):
        self.report("\n\t{}{}, FAILED:{} '{}'".format(str(datetime.now()), Fore.RED, Style.RESET_ALL, str(test)))
        


    