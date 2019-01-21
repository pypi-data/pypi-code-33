import json
import logging
import os

from python_agent import __file__ as root_directory_module
from python_agent.common.autoupgrade.autoupgrade_manager import AutoUpgrade
from python_agent.common.config_data import ConfigData
from python_agent.common.constants import BUILD_SESSION_ID_FILE, TOKEN_FILE, CONFIG_ENV_VARIABLE
from python_agent.common.environment_variables_resolver import EnvironmentVariablesResolver
from python_agent.common.http.backend_proxy import BackendProxy
from python_agent.common.log.sealights_logging import SealightsHTTPHandler
from python_agent.common.token.token_data import TokenData
from python_agent.common.token.token_parser import TokenParser
from python_agent.test_listener.integrations.multiprocessing_patcher import patch_multiprocessing

log = logging.getLogger(__name__)

# A list off properties, which should be converted to integer
INT_PROPERTIES = ['commitHistoryLength']


class ConfigurationManager(object):

    def __init__(self):
        self.config_data = ConfigData()
        self.env_resolver = EnvironmentVariablesResolver(INT_PROPERTIES, self.config_data)

    def init_configuration(self, is_config_cmd, token, buildsessionid, tokenfile=TOKEN_FILE, buildsessionidfile=BUILD_SESSION_ID_FILE, proxy=None, scm_args=None):
        config_data = self.try_load_configuration(scm_args, token, buildsessionid, tokenfile, buildsessionidfile, proxy, is_config_cmd)
        self.init_features()
        return config_data

    def try_load_configuration_from_config_environment_variable(self):
        config_data = os.environ.get(CONFIG_ENV_VARIABLE)
        if config_data:
            config_data = json.loads(config_data)
            self.config_data.__dict__.update(config_data)

    def _try_load_configuration_from_environment_variables(self):
        self.config_data.__dict__.update(self.env_resolver.resolve())
        return self.config_data

    def _try_load_configuration_from_server(self):
        backend_proxy = BackendProxy(self.config_data)
        result = backend_proxy.get_remote_configuration()
        self.config_data.__dict__.update(result)
        return self.config_data

    def init_features(self):
        self.init_logging()
        patch_multiprocessing()
        # self.init_coloring()
        self._upgrade_agent()

    def try_load_configuration(self, scm_args, token, buildsessionid, tokenfile, buildsessionidfile, proxy, is_config_cmd):
        self.config_data.proxy = proxy
        self.config_data.apply_scm_args(scm_args)
        self._try_load_configuration_from_environment_variables()

        is_resolved_token = self.resolve_token_data(token, tokenfile, self.config_data.tokenFile)
        if not is_resolved_token:
            return None

        if not is_config_cmd:
            is_resolved_build_session_id = self.resolve_build_session_id(buildsessionid, buildsessionidfile, self.config_data.buildSessionIdFile)
            if not is_resolved_build_session_id:
                return None

        self._try_load_configuration_from_server()

        return self.config_data

    def update_build_session_data(self, build_session_id):
        backend_proxy = BackendProxy(self.config_data)
        build_session_data = backend_proxy.get_build_session(build_session_id)
        self.config_data.__dict__.update(build_session_data.__dict__)
        if not build_session_data.additionalParams:
            return
        for config, value in list(build_session_data.additionalParams.items()):
            setattr(self.config_data, config, value)

    def update_token_data(self, token, token_data):
        self.config_data.token = token
        self.config_data.customerId = token_data.customerId
        self.config_data.server = token_data.server

    def resolve_token_data(self, token, tokenfile, env_tokenfile):
        token = token or self.read_from_file(tokenfile) or self.read_from_file(env_tokenfile)
        if not token:
            log.error("--token, --tokenfile options or sl.token or sl.tokenFile environment variables must be provided")
            return False
        token_data, token = TokenParser.parse_and_validate(token)
        self.update_token_data(token, token_data)
        return True

    def _upgrade_agent(self):
        auto_upgrade = AutoUpgrade(self.config_data)
        auto_upgrade.upgrade()

    def resolve_build_session_id(self, buildsessionid, buildsessionidfile, env_buildsessionidfile):
        build_session_id = buildsessionid or self.read_from_file(buildsessionidfile) or self.read_from_file(env_buildsessionidfile)
        if not build_session_id:
            log.error("--buildsessionid, --buildsessionidfile options or "
                      "sl.buildSessionId, sl.buildSessionIdFile environment variables must be provided")
            return False
        self.config_data.buildSessionId = build_session_id
        self.update_build_session_data(build_session_id)
        return True

    def read_from_file(self, file_path):
        if file_path and os.path.isfile(file_path):
            with open(os.path.abspath(file_path), 'r') as f:
                value = f.read()
                return value.rstrip()
        return None

    def init_logging(self):
        if self.config_data.isSendLogs:
            sl_handler = SealightsHTTPHandler(self.config_data, capacity=50)
            sl_formatter = logging.Formatter('%(asctime)s %(levelname)s [%(process)d|%(thread)d] %(name)s: %(message)s')
            sl_handler.setFormatter(sl_formatter)
            agent_logger = logging.getLogger("python_agent")
            agent_logger.addHandler(sl_handler)

    def init_coloring(self):
        self.init_coloring_incoming()
        self.init_coloring_outgoing()

    def init_coloring_outgoing(self):
        pass
        # from python_agent.test_listener.coloring import __all__
        # for coloring_framework_name in __all__:
        #     __import__(
        #         "%s.%s.%s.%s" % ("python_agent", "test_listener", "coloring", coloring_framework_name),
        #         fromlist=[coloring_framework_name]
        #     )
        #     log.debug("Imported Coloring Framework: %s" % coloring_framework_name)
        # log.info("Imported Coloring Frameworks: %s" % __all__)

    def init_coloring_incoming(self):
        from python_agent.test_listener.web_frameworks import __all__
        for web_framework_name in __all__:
            web_framework = __import__(
                "%s.%s.%s.%s" % ("python_agent", "test_listener", "web_frameworks", web_framework_name),
                fromlist=[web_framework_name]
            )
            bootstrap_method = getattr(web_framework, "bootstrap", None)
            if bootstrap_method:
                bootstrap_method()
                log.debug("Bootstrapped Framework: %s" % web_framework_name)
        log.info("Bootstrapped Frameworks: %s" % __all__)


