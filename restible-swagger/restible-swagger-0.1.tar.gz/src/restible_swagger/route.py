# -*- coding: utf-8 -*-
# Copyright 2019 Mateusz Klos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
""" Helper for defining API route mappings through config. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
from typing import Any, Dict, List, Type

# 3rd party imports
import attr
from restible import RestResource

# local imports
from .endpoint import EndpointBuilder


@attr.s
class Route(object):
    """ Represents a single API route.

    A route is just a mapping of URL to resource that handles it. Each route
    will generate multiple URLs handled as each resource can handle generic and
    detail REST operation as well as all actions defined on the resource.
    """
    url = attr.ib(type=str)
    resource = attr.ib(type=str)
    id_param = attr.ib(type=str)
    actions = attr.ib(type=List[int])
    _res_cls = attr.ib(type=type, default=None)

    @classmethod
    def load(cls, url, route_info):
        """ Load route instance from configuration item. """
        return Route(
            url=url,
            resource=route_info['resource'],
            id_param=route_info['id_param'],
            actions=route_info.get('actions', []),
        )

    @property
    def res_cls(self):
        # type: () -> Type[RestResource]
        """ Return the resource class instance associated with this route. """
        if self._res_cls is None:
            mod_name, cls_name = self.resource.rsplit('.', 1)
            mod = __import__(mod_name, fromlist=[str(cls_name)])
            self._res_cls = getattr(mod, cls_name)

        return self._res_cls

    def build_spec(self):
        # type: () -> Dict[str, Any]
        """ Extract all OpenAPI specs for paths defined by the resource.

        Returns:
            Dict[str, Any]:
        """
        from restible import api_action

        builder = EndpointBuilder(self)

        list_path = self.res_cls.name
        detail_path = self.res_cls.name + '-detail'
        paths = {
            list_path: builder.generic_endpoint(),
            detail_path: builder.detail_endpoint(),
        }

        generic = []
        detail = []
        for action in self.res_cls().rest_actions():
            meta = api_action.get_meta(action)
            (generic if meta.generic else detail).append(action)

        actions_by_name = {}
        for action in detail:
            meta = api_action.get_meta(action)
            actions = actions_by_name.setdefault(meta.name, [])
            actions.append(action)

        for name, actions in actions_by_name.items():
            endp_name = '{res}-{action}'.format(res=self.res_cls.name, action=name)
            paths[endp_name] = builder.actions_endpoint(actions)

        return paths


# Used only in type hint comments
del Any, Dict, Type, RestResource
