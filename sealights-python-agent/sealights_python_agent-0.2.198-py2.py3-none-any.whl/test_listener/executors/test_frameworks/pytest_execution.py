import inspect
import logging
import imp
import os
import sys

from python_agent.test_listener.executors.test_frameworks.agent_execution import AgentExecution

log = logging.getLogger(__name__)


class PytestAgentExecution(AgentExecution):

    def __init__(self, config_data, labid, test_stage, cov_report, args):
        super(PytestAgentExecution, self).__init__(config_data, labid, test_stage=test_stage, cov_report=cov_report)
        self.args = args

    def execute(self):
        try:
            args = list(self.args)
            from pytest import main as pytest_main
            from python_agent.test_listener.integrations import pytest_helper

            # we're appending the current working directory for customers running pytest using: "python -m pytest"
            # https://github.com/pytest-dev/pytest/blob/beacecf29ba0b99511a4e5ae9b96ff2b0c42c775/doc/en/usage.rst
            sys.path.append(os.getcwd())

            # we add the pytest_helper plugin here so it will be discovered after xdist, as this is a must
            # according to https://docs.pytest.org/en/latest/writing_plugins.html#plugin-discovery-order-at-tool-startup
            # plugins using -p are loaded after plugins that are registered using setuptools (xdist)
            self.set_original_argv(args)
            args.extend(["-p", inspect.getmodule(pytest_helper).__name__])
            pytest_main(args=args)
        except ImportError as e:
            log.exception("Failed Importing pytest. Error: %s" % str(e))

    def set_original_argv(self, args):
        try:
            import pytest
            pytest_path = imp.find_module(pytest.__name__)[1]
            sys.argv = [pytest_path] + args
        except ImportError as e:
            log.exception("Failed Importing pytest. Error: %s" % str(e))
