from python_agent.common import constants
from python_agent.common.constants import DEFAULT_WORKSPACEPATH
from python_agent.utils import to_str_obj

class ScmConfigArgs(object):
    def __init__(self, scm_provider, scm_version, scm_base_url, scm_type):
        self.scmProvider = scm_provider
        self.scmVersion = scm_version
        self.scmBaseUrl = scm_base_url
        self.scmType = scm_type


class ConfigData(object):
    def __init__(self, token=None, customer_id=None, server=None, proxy=None, build_session_id=None, is_compress=True):
        self.token = token
        self.server = server
        self.proxy = proxy
        self.isCompress = is_compress
        self.buildSessionId = build_session_id
        self.customerId = customer_id
        self.appName = None
        self.buildName = None
        self.branchName = None
        self.labId = None
        self.testStage = constants.DEFAULT_ENV
        self.additionalParams = {}
        self.workspacepath = DEFAULT_WORKSPACEPATH
        self.include = None
        self.exclude = None
        self.isInitialColor = True
        self.initialColor = constants.INITIAL_COLOR
        self.args = None
        self.program = None
        self.isSendLogs = False
        self.isOfflineMode = False
        self.scmType = constants.GIT_SCM
        self.scmProvider = None
        self.scmVersion = None
        self.scmBaseUrl = None
        self.commitHistoryLength = constants.DEFAULT_COMMIT_LOG_SIZE
        self.tokenFile = None
        self.buildSessionIdFile = None
        self.covReport = None

    def apply_scm_args(self, scm_args):
        """
        Overrides scm properties by not None values of scm_args
        None scm_args are ignored
        :param scm_args:
        :return:
        """
        if scm_args:
            if scm_args.scmProvider:
                self.scmProvider = scm_args.scmProvider
            if scm_args.scmBaseUrl:
                self.scmBaseUrl = scm_args.scmBaseUrl
            if scm_args.scmVersion:
                self.scmVersion = scm_args.scmVersion
            if scm_args.scmType:
                self.scmType = scm_args.scmType

    def __str__(self):
        return 'ConfigData:\n' + to_str_obj(self)
