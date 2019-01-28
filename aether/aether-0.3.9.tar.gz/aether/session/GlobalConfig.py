########################################################################################
#
# A Singleton class for managing global values across modules, to be inherited.
#
########################################################################################

from aether.aether_client import aether_client
import aether.aetheruserconfig as cfg

class GlobalConfig():

    protocol = cfg._default_protocol
    hostport = cfg._default_hostport
    uuid = None

    def set_user(self, uuid):
        self.uuid = uuid

    def unset_user(self):
        self.uuid = None

    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def _getInstance():
        """ Static access method. """
        if GlobalConfig.__instance == None:
            GlobalConfig()
        return GlobalConfig.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if GlobalConfig.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            GlobalConfig.__instance = self

    def _switch_service_locality(self, to_local=False):
        if to_local:
            self.hostport = cfg._local_hostport
        else:
            self.hostport = cfg._default_hostport

    def _aether_client(self):
        return aether_client(self.uuid, hostport=self.hostport, protocol=self.protocol)

    def _diagnostic_debug_report(self):
        return "Hostport: {}; Protocol: {}".format(self.hostport, self.protocol)