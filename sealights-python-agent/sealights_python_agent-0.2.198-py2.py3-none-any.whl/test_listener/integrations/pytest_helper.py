"""
PYTEST_DONT_REWRITE
Do not delete!!!
This string was added so pytest won't try to apply its rewrite plugin
on the agent and warn the user that the agent was already imported
https://docs.pytest.org/en/latest/assert.html#advanced-assertion-introspection
"""
import functools
import json
import logging
import os
from collections import defaultdict

import operator
from python_agent.common.config_data import ConfigData

try:
    from _pytest.junitxml import mangle_test_address
except ImportError:
    from _pytest.junitxml import mangle_testnames as mangle_test_address

from python_agent.test_listener.managers.agent_manager import AgentManager
from python_agent.test_listener.sealights_api import SeaLightsAPI

log = logging.getLogger(__name__)


class SealightsPlugin(object):
    def __init__(self, is_dist=False):
        self.test_status = defaultdict(lambda: defaultdict(lambda: defaultdict(bool)))
        self.execution_id = None
        self.is_dist = is_dist

    def pytest_sessionstart(self, session):
        try:
            self.try_initialize_agent_on_xdist_node(session)
            if self.is_dist and not self.is_slave(session):
                return
            self.execution_id = SeaLightsAPI.create_execution_id()
            SeaLightsAPI.notify_execution_start(self.execution_id)
        except Exception as e:
            log.exception("Failed Notifying Execution Start. Execution Id: %s. Error: %s" % (self.execution_id, str(e)))

    def pytest_sessionfinish(self, session, exitstatus):
        try:
            if self.is_dist and not self.is_slave(session):
                return
            SeaLightsAPI.notify_execution_end(self.execution_id)
        except Exception as e:
            log.exception("Failed Notifying Execution End. Execution Id: %s. Error: %s" % (self.execution_id, str(e)))
        if os.environ.get("SL_TEST"):
            AgentManager().shutdown()

    def pytest_runtest_logstart(self, nodeid, location):
        try:
            if self.is_dist and not self.is_slave(None):
                return
            SeaLightsAPI.notify_test_start(self.execution_id, get_test_name(nodeid))
        except Exception as e:
            log.exception("Failed Notifying Test Start. Full Test Name: %s. Error: %s" % (nodeid, str(e)))

    def pytest_runtest_logreport(self, report):
        try:
            if self.is_dist and not self.is_slave(None):
                return
            self.test_status[report.nodeid]["passed"][report.when] = report.passed
            self.test_status[report.nodeid]["skipped"][report.when] = report.skipped
            self.test_status[report.nodeid]["failed"][report.when] = report.failed
            if report.when == "teardown":
                test = self.test_status[report.nodeid]
                passed = functools.reduce(operator.and_, list(test["passed"].values()))
                skipped = functools.reduce(operator.or_, list(test["skipped"].values()))
                failed = functools.reduce(operator.or_, list(test["failed"].values()))
                if passed:
                    SeaLightsAPI.notify_test_end(self.execution_id, get_test_name(report.nodeid), report.duration, "passed")
                elif skipped:
                    SeaLightsAPI.notify_test_end(self.execution_id, get_test_name(report.nodeid), report.duration, "skipped")
                elif failed:
                    SeaLightsAPI.notify_test_end(self.execution_id, get_test_name(report.nodeid), report.duration, "failed")
        except Exception as e:
            log.exception("Failed Notifying Test End, Skip or Failed. Full Test Name: %s. Error: %s"
                          % (report.nodeid, str(e)))

    def pytest_configure_node(self, node):
        """
        Mark this hook as optional in case xdist is not installed.
        """
        node.slaveinput["sl_config_data"] = json.dumps(AgentManager().config_data.__dict__)

    def is_slave(self, session):
        if session:
            if not hasattr(session, "config"):
                return False
            # slaveinput/workerinput is a variable created in session config by the xdist plugin
            # https://github.com/pytest-dev/pytest-xdist/blob/fd2e8a67111542e03a1469dee6cfa6bff155b099/xdist/remote.py#L202
            return hasattr(session.config, 'slaveinput') or hasattr(session.config, 'workerinput')
        else:
            if self.execution_id:
                return True
            return False

    def pytest_internalerror(excrepr, excinfo):
        log.exception("Test Internal Error. Exception: %s. Excinfo: %s" % (excrepr, excinfo))

    def pytest_exception_interact(node, call, report):
        log.exception("Test Exception. Node: %s. Call: %s. Report: %s" % (node, call, report))

    def try_initialize_agent_on_xdist_node(self, session):
        if self.is_slave(session):
            config_data = ConfigData()
            config_data.__dict__.update(self.get_config_data(session))
            AgentManager(config_data=config_data)

    def get_config_data(self, session):
        worker_input = getattr(session.config, "slaveinput", getattr(session.config, "workerinput", {}))
        return json.loads(worker_input.get("sl_config_data", "{}"))

    pytest_configure_node.optionalhook = True


def get_test_name(nodeid):
    # Parametrized tests can be very long.
    # We account it as a single test
    # node_id = [nodeid] if not isinstance(nodeid, list) else nodeid
    node_id = ".".join(mangle_test_address(nodeid))
    node_id = node_id.replace("::", ".")
    return node_id


def pytest_configure(config):
    is_dist = (config.getoption("numprocesses", default=False) or
               config.getoption("distload", False) or
               config.getoption("dist", "no") != "no")
    plugin = SealightsPlugin(is_dist=is_dist)
    config.pluginmanager.register(plugin, '_sealights')
