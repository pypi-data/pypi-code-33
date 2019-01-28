""" Save and retrieve configuration settings """
import os
import json

__DEFAULT_UPDATE_INTERVAL__ = 15 * 60
__DEFAULT_CONFIG_FILE_NAME__ = 'config.json'
__DEFAULT_RESOUCES_DIR__ = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
__DEFAULT_CONFIG_PATH__ = os.path.join(__DEFAULT_RESOUCES_DIR__, __DEFAULT_CONFIG_FILE_NAME__)
__DAEMON_PID_LOCK_PATH__ = os.path.join(__DEFAULT_RESOUCES_DIR__, "daemon.lock")
__LOG_FILENAME__ = 'quack_dns.log'
__LOG_PATH__ = os.path.join(__DEFAULT_RESOUCES_DIR__, __LOG_FILENAME__)

def create_resources_folder():
    if not os.path.exists(__DEFAULT_RESOUCES_DIR__):
        os.makedirs(__DEFAULT_RESOUCES_DIR__)


class Settings:
    def __init__(self, domain="", token=""):
        if domain != "":
            self.__domain__ = domain
        if token != "":
            self.__token__ = token

    # Save and load methods
    def save(self, settings_file_path: str):
        create_resources_folder()
        with open(settings_file_path, "w") as settings_file:
            settings_dict = {'domain': self.get_domain(),
                             'token': self.get_token()}
            json.dump(settings_dict, settings_file)

    def load(self, settings_file_path: str):
        try:
            with open(settings_file_path) as settings_file:
                settings_dict = json.load(settings_file)
                self.set_domain(settings_dict['domain'])
                self.set_token(settings_dict['token'])
        except json.JSONDecodeError as error:
            raise InvalidSettingsError(path=settings_file_path,
                                       reason=str(error))

    # Set methods
    def set_domain(self, domain):
        self.__domain__ = domain

    def set_token(self, token):
        self.__token__ = token

    # Get methods
    def get_domain(self):
        return self.__domain__

    def get_token(self):
        return self.__token__


class InvalidSettingsError(Exception):
    def __init__(self, path: str, reason: str = None):
        self.msg = "Settings file could not be read at {}.".format(path)
        if reason:
            self.msg += " Reason: {}.".format(reason)

    def __str__(self):
        return repr(self.msg)