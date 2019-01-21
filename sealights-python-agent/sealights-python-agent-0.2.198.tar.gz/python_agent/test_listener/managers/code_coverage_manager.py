import logging
import threading

import os

import python_agent
from python_agent.common import constants
from python_agent.test_listener.line_footprints_collector import LineFootprintsCollector
from python_agent.test_listener.method_footprints_collector import MethodFootprintsCollector

try:
    from coverage import Coverage, CoverageData
except ImportError:
    from coverage import coverage as Coverage

log = logging.getLogger(__name__)


class CodeCoverageManager(object):
    def __init__(self, config_data):
        self.config_data = config_data
        self.should_reset_coverage = not bool(self.config_data.covReport)
        self.coverage = self.init_coverage()
        self.coverage_lock = threading.Lock()
        self.coverage_collectors = {}
        self.coverage_collectors["methods"] = MethodFootprintsCollector(config_data.workspacepath)
        # self.coverage_collectors["lines"] = LineFootprintsCollector(config_data.workspacepath)
        log.info("Started Code Coverage Manager")

    def get_footprints_and_clear(self):
        footprints = {}
        with self.coverage_lock:
            if constants.IN_TEST:
                # save coverage data that can be later be converted to footprints before reset
                self.coverage.save()
            # get_data creates or updates coverage.data with the CoverageData object and
            # clears counters on the collector but not on the coverage.data object
            # we make sure to clear coverage.data as well by creating a new one
            log.debug("before clearing coverage: %s" % self.coverage.collector.data)
            coverage_object = self.coverage.get_data()
            if self.should_reset_coverage:
                self.reset_coverage()
            if not coverage_object:
                log.info("No Coverage Found")
                return footprints

            for coverage_type, coverage_collector in list(self.coverage_collectors.items()):
                footprints[coverage_type] = coverage_collector.get_footprints_and_clear(coverage_object)
        return footprints

    def shutdown(self):
        self.coverage.stop()
        if constants.IN_TEST:
            # save coverage data that can be later be converted to footprints
            self.coverage.save()
        if self.config_data.covReport:
            self.coverage.xml_report(ignore_errors=True, outfile=self.config_data.covReport)
            log.info("Coverage report created in %s" % self.config_data.covReport)
        log.info("Finished Shutting Down Code Coverage Manager")

    def register_collector(self, coverage_type, collector):
        self.coverage_collectors[coverage_type] = collector

    def get_trace_function(self):
        return self.coverage.collector._installation_trace

    def reset_coverage(self):
        self.coverage.data = CoverageData(debug=self.coverage.debug)

    def init_coverage(self):
        self.config_data.include = self.config_data.include or []
        self.config_data.include.append("*%s*" % os.path.abspath(self.config_data.workspacepath))
        if constants.IN_TEST:
            # coverage.py ignores "include" if source is given so, in order to include python agent coverage
            # we move workspacepath to include, include python_agent, remove exclude and add "data_suffix=True" so
            # coverage files will be saved each time with a unique suffix so we won't loose coverage after each reset
            self.config_data.include.append("*%s*" % python_agent.__name__)
            coverage = Coverage(source=None, include=self.config_data.include, omit=None, data_suffix=True, branch=False)
        else:
            coverage = Coverage(source=None, include=self.config_data.include, omit=self.config_data.exclude, branch=False)
        if getattr(coverage, "_warn_no_data", False):
            coverage._warn_no_data = False
        if self.config_data.isOfflineMode:
            # no actual tracing is done here
            # we're loading the raw coverage data from the .coverage file
            # so coverage.get_data() will return it and we'll convert it to footprints
            coverage.load()
        else:
            coverage.start()

        return coverage

