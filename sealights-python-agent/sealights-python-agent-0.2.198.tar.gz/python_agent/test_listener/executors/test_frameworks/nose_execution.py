import os
import sys
import logging
from python_agent.test_listener.executors.test_frameworks.agent_execution import AgentExecution

log = logging.getLogger(__name__)


class NoseAgentExecution(AgentExecution):
    def __init__(self, config_data, labid, test_stage, cov_report, args):
        super(NoseAgentExecution, self).__init__(config_data, labid, test_stage, cov_report=cov_report)
        self.args = args

    def execute(self):
        sys.path.insert(0, os.getcwd())
        try:
            import nose
            from python_agent.test_listener.integrations.nose_helper import SealightsNosePlugin
            nose.main(addplugins=[SealightsNosePlugin()], argv=self.args, exit=False)
        except ImportError as e:
            log.exception("Failed importing nose. Error: %s" % str(e))