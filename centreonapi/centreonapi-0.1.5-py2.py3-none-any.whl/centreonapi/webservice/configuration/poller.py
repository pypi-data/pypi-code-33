# -*- coding: utf-8 -*-

import centreonapi.webservice.configuration.common as common
from centreonapi.webservice import Webservice


class Poller(common.CentreonObject):

    def __init__(self, properties):
        self.webservice = Webservice.getInstance()
        self.__clapi_action = 'INSTANCE'
        self.id = properties.get('id')
        self.bin = properties.get('bin')
        self.activate = properties.get('activate')
        self.init_script = properties.get('init script')
        self.ipaddress = properties.get('ip address')
        self.localhost = properties.get('localhost')
        self.name = properties.get('name')
        self.ssh_port = properties.get('ssh port')
        self.stats_bin = properties.get('stats bin')
        self.status = properties.get('status')
        self.pollerHost = dict()

    def add(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass

    def setparam(self, *args, **kwargs):
        pass

    def gethosts(self):
        state, poller  = self.webservice.call_clapi(
                            'gethosts',
                            self.__clapi_action,
                            self.name)
        if state and len(poller['result']) > 0:
            for p in poller['result']:
                p['poller'] = self.name
                pollerhost_obj = PollerHost(p)
                self.pollerHost[pollerhost_obj.name] = pollerhost_obj
            return state, self.pollerHost
        else:
            return state, poller

    def applycfg(self):
        return self.webservice.call_clapi(
            'applycfg',
            None,
            self.id)

    def restart(self):
        return self.webservice.call_clapi(
            'pollerrestart',
            None,
            self.id)

    def relaod(self):
        return self.webservice.call_clapi(
            'pollerreload',
            None,
            self.id)

    def generatecfg(self):
        return self.webservice.call_clapi(
            'pollergenerate',
            None,
            self.id)

    def testcfg(self):
        return self.webservice.call_clapi(
            'pollertest',
            None,
            self.id)

    def movecfg(self):
        return self.webservice.call_clapi(
            'cfgmove',
            None,
            self.id)


class PollerHost(common.CentreonObject):

    def __init__(self, properties):
        self.id = properties.get('id')
        self.address = properties.get('address')
        self.name = properties.get('name')
        self.poller = properties.get('poller')


class Pollers(common.CentreonDecorator, common.CentreonClass):

    def __init__(self):
        super(Pollers, self).__init__()
        self.pollers = dict()
        self.__clapi_action = 'INSTANCE'

    def __contains__(self, name):
        return name in self.pollers.keys() or None

    def __getitem__(self, name):
        if not self.pollers:
            self.list()
        if name in self.pollers.keys():
            return True, self.pollers[name]
        else:
            return False, None

    def _refresh_list(self):
        self.pollers.clear()
        state, poller = self.webservice.call_clapi(
                            'show',
                            self.__clapi_action)
        if state and len(poller['result']) > 0:
            for p in poller['result']:
                poller_obj = Poller(p)
                self.pollers[poller_obj.name] = poller_obj

    def applycfg(self, pollername):
        """
        Apply the configuration to a poller name
        """
        return self.webservice.call_clapi('applycfg', None, pollername)

    @common.CentreonDecorator.pre_refresh
    def list(self):
        return self.pollers
