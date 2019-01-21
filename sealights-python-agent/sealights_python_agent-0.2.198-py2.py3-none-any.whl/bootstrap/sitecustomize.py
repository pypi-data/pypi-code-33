import imp
import os
import sys
import traceback

from python_agent.common.configuration_manager import ConfigurationManager
from python_agent.test_listener.executors.test_frameworks.agent_execution import AgentExecution

boot_directory = os.path.dirname(__file__)
root_directory = os.path.dirname(os.path.dirname(boot_directory))

path = list(sys.path)

if boot_directory in path:
    del path[path.index(boot_directory)]

try:
    (file, pathname, description) = imp.find_module('sitecustomize', path)
except ImportError:
    pass
else:
    imp.load_module('sitecustomize', file, pathname, description)


if root_directory not in sys.path:
    sys.path.insert(0, root_directory)

try:
    cm = ConfigurationManager()
    cm.try_load_configuration_from_config_environment_variable()
    cm.init_features()
    AgentExecution(cm.config_data, cm.config_data.labId, cov_report=cm.config_data.covReport)
except SystemExit as e:
    if getattr(e, "code", 1) != 0:
        sys.exit(4)
except BaseException as e:
    result = {
        "PYTHONPATH": os.environ.get("PYTHONPATH"),
        "error": str(e),
        "traceback": traceback.format_exc()
    }
    sys.exit(result)

