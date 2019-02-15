# -*- coding: utf-8 -*-

import centreonapi.webservice.configuration.common as common
from centreonapi.webservice.configuration.poller import Poller
from centreonapi.webservice import Webservice


class ResourceCFG(common.CentreonObject):

    def __init__(self, properties):
        self.webservice = Webservice.getInstance()
        self.__clapi_action = 'RESOURCECFG'
        self.id = properties.get('id')
        self.instance = properties.get('instance')
        self.name = properties.get('name')
        self.activate = properties.get('activate')
        self.value = properties.get('value')

    def setparam(self, name, value):
        values = [
            self.id,
            name,
            value
        ]
        return self.webservice.call_clapi('setparam',
                                          self.__clapi_action,
                                          values)


class ResourceCFGs(common.CentreonDecorator, common.CentreonClass):
    """
    Centreon Web Resource object
    """
    def __init__(self):
        super(ResourceCFGs, self).__init__()
        self.resources = dict()
        self.__clapi_action = "RESOURCECFG"

    @staticmethod
    def _build_resource_line(line):
        if line:
            rsc = line
            if rsc[0] != '$':
                rsc = '$' + rsc
            if rsc[len(rsc) - 1] != '$':
                rsc = rsc + '$'
            return str(rsc)
        else:
            return ""

    def __contains__(self, name):
        rsc = self._build_resource_line(name)
        return rsc in self.resources.keys()

    def __getitem__(self, name):
        if not self.resources:
            self.list()
        rsc = self._build_resource_line(name)
        if rsc in self.resources.keys():
            return True, self.resources[rsc]
        else:
            return False, None


    def _refresh_list(self):
        self.resources.clear()
        state, resource = self.webservice.call_clapi(
                            'show',
                            self.__clapi_action)
        if state and len(resource['result']) > 0:
            for r in resource['result']:
                resource_obj = ResourceCFG(r)
                self.resources[resource_obj.name] = resource_obj

    @common.CentreonDecorator.pre_refresh
    def list(self):
        return self.resources

    @common.CentreonDecorator.post_refresh
    def add(self, rscname, rscvalue, rscinstance,
            rsccomment, post_refresh=True):
        values = [
            rscname,
            rscvalue,
            str(common.build_param(rscinstance, Poller)[0]),
            rsccomment
        ]
        return self.webservice.call_clapi('add', self.__clapi_action, values)

    @common.CentreonDecorator.post_refresh
    def delete(self, resource, post_refresh=True):
        value = str(common.build_param(resource, ResourceCFG, attr='id')[0])
        return self.webservice.call_clapi('del', self.__clapi_action, value)
