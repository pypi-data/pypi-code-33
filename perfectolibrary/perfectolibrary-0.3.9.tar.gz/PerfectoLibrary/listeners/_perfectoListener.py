import os
import robot
import inspect
import pdb
import sys
import PerfectoLibrary
from perfecto import *
import traceback
# from SeleniumLibrary import SeleniumLibrary
# from Selenium2Library import Selenium2Library
# from AppiumLibrary import AppiumLibrary
# from Selenium2LibraryExtension import Selenium2LibraryExtension
from robot.libraries.BuiltIn import BuiltIn


class _PerfectoListener(object):
    ROBOT_LISTENER_API_VERSION = 2
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    driver = ''
    projectname = 'Robotframework Test Project'
    projectversion = '1.0'
    jobname = 'Robotframework Test Job'
    jobnumber = 1

    def __init__(self):
        # pdb.Pdb(stdout=sys.__stdout__).set_trace()
        self.ROBOT_LIBRARY_LISTENER = self
        self.bi = BuiltIn()
        self.reporting_client = None
        self.active = False
        self.stop_reporting = False
        self.tags = ''
        self.longname = 'Robotframework Script'
        self.id = 's1-t1'
        self.running = False
        self.suitesetup = False
        self.setupclient = None

    def init_listener(self, projectname=None, projectversion=None, jobname=None, jobnumber=None):
        """
        This key word helps to initialize the listener with proper project info
        :param projectname: current project name
        :param projectversion: current project version
        :param jobname: the CI job name
        :param jobnumber: the CI job number
        :return:
        """
        if projectname != None:
            self.projectname = projectname
        if projectversion != None:
            self.projectversion = projectversion
        if jobname != None:
            self.jobname = jobname
        if jobnumber != None:
            self.jobnumber = long(float(jobnumber))

    def _start_suite(self, name, attrs):
        #         pdb.Pdb(stdout=sys.__stdout__).set_trace()

        if not self.active:
            self._get_execontext()

    def _start_test(self, name, attrs):
        # pdb.Pdb(stdout=sys.__stdout__).set_trace()
        self.id = attrs['id']
        self.longname = self.bi.get_variable_value('${TEST NAME}')
        self.tags = attrs['tags']
        #         if not self.active:
        self._get_execontext()
        if self.active and self.reporting_client != None and self.running == False:
            self._suitesetup_result()
            self.reporting_client.test_start(self.longname, TestContext([], self.tags))
            self.running = True

    def _suitesetup_result(self):
        if self.suitesetup:
            if self.bi.get_variable_value('${TEST STATUS}') == 'FAIL':
                self.setupclient.test_stop(
                    TestResultFactory.create_failure(self.bi.get_variable_value('${TEST MESSAGE}')))
            else:
                self.setupclient.test_stop(TestResultFactory.create_success())
            self.suitesetup = False

    def _start_keyword(self, name, attrs):
        try:
            if not self.active:
                self._get_execontext()

            if self.active and self.reporting_client != None and self.stop_reporting != True \
                    and self.running == False and "tear" not in attrs['type'].lower():
                if self.bi.get_variable_value('${TEST NAME}') != None:
                    self._suitesetup_result()
                    self.reporting_client.test_start(self.bi.get_variable_value('${TEST NAME}'),
                                                     TestContext([], self.tags))

                else:
                    self.reporting_client.test_start('Suite Setup', TestContext([], self.tags))
                    self.setupclient = self.reporting_client
                    self.suitesetup = True
                self.running = True

            # pass
            if self.active and self.reporting_client != None and self.stop_reporting != True \
                    and "tear" in attrs['type'].lower():
                if self.bi.get_variable_value('${TEST STATUS}') == 'FAIL':
                    self.reporting_client.test_stop(
                        TestResultFactory.create_failure(self.bi.get_variable_value('${TEST MESSAGE}')))
                else:
                    self.reporting_client.test_stop(TestResultFactory.create_success())
                self.stop_reporting = True
                self.running = False

            if self.active and self.reporting_client != None and self.stop_reporting != True \
                    and "comment" not in attrs['kwname'].lower() \
                    and "excel" not in attrs['kwname'].lower() \
                    and "csv" not in attrs['kwname'].lower() \
                    and "sheet" not in attrs['kwname'].lower() \
                    and "cell" not in attrs['kwname'].lower() \
                    and "column" not in attrs['kwname'].lower() \
                    and ("keyword" in attrs['type'].lower() \
                         or "setup" in attrs['type'].lower()) \
                    and "builtin" not in attrs['libname'].lower() \
                    and "collections" not in attrs['libname'].lower() \
                    and "dialogs" not in attrs['libname'].lower() \
                    and "easter" not in attrs['libname'].lower() \
                    and "operatingsystem" not in attrs['libname'].lower() \
                    and "process" not in attrs['libname'].lower() \
                    and "screenshot" not in attrs['libname'].lower() \
                    and "string" not in attrs['libname'].lower() \
                    and "telnet" not in attrs['libname'].lower() \
                    and "xml" not in attrs['libname'].lower() \
                    and "excellibrary" not in attrs['libname'].lower() \
                    and "selenium" not in attrs['libname'].lower() \
                    and "database" not in attrs['libname'].lower() \
                    and "appium" not in attrs['libname'].lower():
                self.reporting_client.step_start(attrs['kwname'] + ' ' + ' '.join(attrs['args']))

        except Exception as e:
            self.bi.log_to_console(traceback.format_exc())
            pass

    #     def _end_keyword(self, name, attrs):
    #         if "setup" in attrs['type'].lower() \
    #             and ("selenium" in attrs['libname'].lower() \
    #             or "appium"  in attrs['libname'].lower()):
    #                 self._get_execontext()

    def _get_execontext(self):
        # self.bi.log_to_console("_get_execontext")
        try:
            aplib = self.bi.get_library_instance('AppiumLibrary')
            self.driver = aplib._current_application()
            # self.bi.log_to_console(aplib)
            self.active = True
        except:
            try:
                aplib = self.bi.get_library_instance('SeleniumLibrary')
                self.driver = aplib.driver
                # self.bi.log_to_console(aplib)
                self.active = True
            except:
                try:
                    aplib = self.bi.get_library_instance('Selenium2Library')
                    self.driver = self.driver = aplib._current_browser()
                    self.active = True
                except:
                    try:
                        aplib = self.bi.get_library_instance('Selenium2LibraryExtension')
                        self.driver = self.driver = aplib._current_browser()
                        self.active = True
                    except:
                        self.active = False

        if self.active:
            self.execontext = PerfectoExecutionContext(self.driver, self.tags, Job(self.jobname, self.jobnumber),
                                                       Project(self.projectname, self.projectversion))
            self.reporting_client = PerfectoReportiumClient(self.execontext)

    def _end_test(self, name, attrs):
        if self.stop_reporting != True:
            try:
                if attrs['status'] == "PASS":
                    self.reporting_client.test_stop(TestResultFactory.create_success())
                else:
                    self.reporting_client.test_stop(TestResultFactory.create_failure(attrs['message']))
            except Exception as e:
                # trace = traceback.format_exc()
                # self.bi.log_to_console(trace)
                pass
        self.stop_reporting = False
        self.reporting_client = None
        self.active = False
        self.running = False