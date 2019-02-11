# -*- coding: utf-8 -*-

import centreonapi.webservice.configuration.common as common


class HostGroup(common.CentreonObject):

    def __init__(self, properties):
        self.id = properties.get('id')
        self.alias = properties.get('alias')
        self.name = properties.get('name')


class HostGroups(common.CentreonDecorator, common.CentreonClass):

    def __init__(self):
        super(HostGroups, self).__init__()
        self.hostgroups = dict()
        self.__clapi_action = 'HG'

    def __contains__(self, name):
        return name in self.hostgroups.keys() or None

    def __getitem__(self, name):
        if not self.hostgroups:
            self.list()
        if name in self.hostgroups.keys():
            return True, self.hostgroups[name]
        else:
            return False, None

    def _refresh_list(self):
        self.hostgroups.clear()
        state, hostgroup = self.webservice.call_clapi(
                            'show',
                            self.__clapi_action)
        if state and len(hostgroup['result']) > 0:
            for hg in hostgroup['result']:
                hg_obj = HostGroup(hg)
                self.hostgroups[hg_obj.name] = hg_obj

    @common.CentreonDecorator.pre_refresh
    def list(self):
        return self.hostgroups

    @common.CentreonDecorator.post_refresh
    def add(self, name, alias):
        values = [name, alias]
        return self.webservice.call_clapi('add', self.__clapi_action, values)

    @common.CentreonDecorator.post_refresh
    def delete(self, hg):
        value = str(common.build_param(hg, HostGroup)[0])
        return self.webservice.call_clapi('del', self.__clapi_action, value)
