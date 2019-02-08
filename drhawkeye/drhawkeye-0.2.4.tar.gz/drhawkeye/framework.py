from inicheck.config import MasterConfig, UserConfig
from inicheck.tools import get_user_config, check_config
from inicheck.output import print_config_report, generate_config
from inicheck.tools import cast_all_variables
import os


class HealthCheck():
    """
    Args:
        configFile (str):  path to configuration file.

    Returns:
        drhawkeye

    Attributes:
    """

    def __init__(self, config):

        if isinstance(config, str):
            if not os.path.isfile(config):
                raise Exception('Configuration file does not exist --> {}'
                                .format(config))

            configFile = config

            try:
                mcfg = MasterConfig(modules = 'drhawkeye')

                # Read in the original users config
                self.ucfg = get_user_config(configFile, mcfg=mcfg)
                self.configFile = configFile

            except UnicodeDecodeError as e:
                print(e)
                raise Exception(('The configuration file is not encoded in '
                                 'UTF-8, please change and retry'))

        elif isinstance(config, UserConfig):
            self.ucfg = config
            configFile = ''

        else:
            raise Exception('Config passed to drhawkeye is neither file name nor UserConfig instance')

        # Check the user config file for errors and report issues if any
        print("Checking config file for issues...")
        warnings, errors = check_config(self.ucfg)
        print_config_report(warnings, errors)

        self.config = self.ucfg.cfg

        # Exit AWSM if config file has errors
        if len(errors) > 0:
            print("Errors in the config file. "
                  "See configuration status report above.")
            sys.exit()
