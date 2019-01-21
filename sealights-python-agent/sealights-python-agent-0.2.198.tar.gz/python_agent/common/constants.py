import os
import sys

PREFIXES = ["sl.", "sl_", "SL.", "SL_"]
TOKEN_FILE = "sltoken.txt"
BUILD_SESSION_ID_FILE = "buildSessionId.txt"
CONFIG_ENV_VARIABLE = "sl_configuration"

TECHNOLOGY = "python"
DEFAULT_ENV = "Unit Tests"
DEFAULT_LAB_ID = "DefaultLabId"
TEST_IDENTIFIER = "x-sl-testid"
PYTHON_FILES_REG = r"^[^.#~!$@%^&*()+=,]+\.pyw?$"  # regex taken from coverage.py for finding python files
INIT_TEST_NAME = "__init"
INITIAL_COLOR = "00000000-0000-0000-0000-000000000000/__init"
MAX_ITEMS_IN_QUEUE = 5000
INTERVAL_IN_MILLISECONDS = 10000
ACTIVE_EXECUTION_INTERVAL_IN_MILLISECONDS = 30000
WINDOWS = sys.platform.startswith('win')
LINUX = sys.platform.startswith("linux")
IN_TEST = os.environ.get("SL_TEST")
DEFAULT_WORKSPACEPATH = os.path.relpath(os.getcwd())
DEFAULT_COMMIT_LOG_SIZE = 100
NONE_SCM = 'none'
GIT_SCM = 'git'
GITHUB = 'Github'
WAIT_TIMEOUT = 120.0
XDIST_EXIT_TIMEOUT_IN_SECONDS = 60


FUTURE_STATEMENTS = {
    "nested_scopes": 0x0010,
    "generators": 0,
    "division": 0x2000,
    "absolute_import": 0x4000,
    "with_statement": 0x8000,
    "print_function": 0x10000,
    "unicode_literals": 0x20000,
}

MESSAGES_CANNOT_BE_NONE = " cannot be 'None'."


class MetadataKeys(object):
    APP_NAME = "appName"
    BUILD = "build"
    BRANCH = "branch"
    CUSTOMER_ID = "customerId"
    GENERATED = "generated"
    TECHNOLOGY = "technology"
    SCM_PROVIDER = "scmProvider"
    SCM_VERSION = "scmVersion"
    SCM_BASE_URL = "scmBaseUrl"
    SCM = "scm"
    COMMIT = "commit"
    HISTORY = "history"
    COMMIT_LOG = "commitLog"
    CONTRIBUTORS = "contributors"
    REPOSITORY_URL = "repositoryUrl"


# https://greentreesnakes.readthedocs.io/en/latest/nodes.html#arguments
AST_ARGUMENTS_EMPTY_VALUES = {
    "args": [],
    "vararg": None,
    "kwarg": None,
    "defaults": [],
    "kw_defaults": [],
    "kwonlyargs": [],
    "varargannotation": None,
    "kwargannotation": None
}