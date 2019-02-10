#!/usr/bin/env python
##########################################################################

import copy
import os
import uuid
import pprint

from . import codec
from munge import util

##########################################################################


class State(object):

    """
    Instance state info

    definition overlay in key 'definition'
    """

    def __init__(self, fax):
        self._fax = fax
        self.state_dir = fax.state_dir
        self.defined = fax.defined

        self.instances_file = os.path.join(self.state_dir, "instances.json")
        self.state_file = os.path.join(self.state_dir, 'state.' + self._fax.write_codec.extension)
        self._load()

    def _load(self):
        self._fax.debug_msg('looking for state dir %s' % self.state_dir)
        if not os.path.exists(self.state_dir):
            os.mkdir(self.state_dir)

        self.__state = self._fax.load_datafile("state", self.state_dir, default={})
        self.__state.setdefault('passwd', {})

        instances = self.__state.get('instances', {})
        instances.setdefault("inmap", dict())
        instances.setdefault("uiidmap", dict())

        envconf = self.defined.get("config", {})
        envsvc = self.defined.get("service", {})
        envmods = self.defined.get("modules", {})

        # mangle modules as needed
        modmap = {}

        # print 'START OF DEFINED'
        # pprint.pprint(self.defined.modules())
        # print 'END OF DEFINED'

        defined_modules = self.defined.modules()
        fresh_modules = []

        for each in defined_modules:
            if "daemon" in each:
                k = each["daemon"]
                each["username"] = each["daemon"]
            else:
                k = each["name"]
                each["username"] = each["name"]

            # need to append d to name if not set
            if "service" in each:
                if "name" not in each["service"]:
                    each["service"]["name"] = k + "d"

            # password gen step
            each["password"] = self.get_passwd(each["username"])

            # environment service overlay, needs to happen before we clone the
            # services & gen uiid and n_instances (below)
            if k in envsvc:
                if "service" in each:
                    svc = each["service"]
                    for section, child in envsvc[k].items():
                        if section in svc:
                            util.recursive_update(svc[section], child)
                        else:
                            svc[section] = child
                else:
                    each["service"] = envsvc[k]

            # environment config overlay
            if k in envconf:
                if "freeform" in each:
                    eachff = each["freeform"]
                    for section, child in envconf[k].items():
                        if section in eachff:
                            util.recursive_update(eachff[section], child)
                        else:
                            eachff[section] = child
                else:
                    each["freeform"] = envconf[k]

            modmap[k] = copy.deepcopy(each)

            # want to make more than one instance of a module, which will come
            # with instance_name and uiid uniqueness
            if "service" in each and "logical_name" in each:
                logical_name = each["logical_name"]

                n_instances = 1
                try:
                    n_instances = envmods[each["name"]][
                        "service"]["n_instances"]
                    print 'got %d for %s instance count' % (n_instances, each["name"])
                except KeyError:
                    try:
                        print 'envmods only had %s for %s...' % (envmods[each["name"]], each['name'])
                    except KeyError:
                        print 'no envmods for %s' % each['name']

                for instance_number in range(n_instances):
                    # here is where we want to set up the multiple instances
                    # out of extra.
                    instance_name = each["name"] + ('d.%d' % instance_number)

                    if instance_number != 0:
                        # ok, here we are adding another effective module to the modules defined; this will create more configs in the end.
                        # copy the each dictionary, and insert it by the instance_name into the
                        # defined_modules. we leave the first one the same as it would have been for simplicity of leaving non-sharded/HA systems alone.
                        # this may end up being overly complex in the end; need
                        # to revisit later.

                        print 'CLONING instance!'

                        each = copy.deepcopy(each)
                        fresh_modules.append(each)

                    if n_instances > 1:
                        each["config_name"] = instance_name

                    if instance_name not in instances["inmap"]:
                        uiid = max(
                            [int(ui) for ui in instances["uiidmap"].keys()] + [0]) + 1
                        assert uiid < 256

                        each["service"]["uiid"] = str(uiid)
                        each["service"]["logical_name"] = logical_name
                        each["service"]["instance_name"] = instance_name

                        entry = {
                            "uiid": uiid,
                            "logical_name": logical_name,
                            "instance_name": instance_name
                        }

                        if instance_name not in instances["inmap"]:
                            instances["inmap"][instance_name] = entry
                        if str(uiid) not in instances["uiidmap"]:
                            instances["uiidmap"][str(uiid)] = entry
                    else:
                        each["service"]["uiid"] = str(instances["inmap"][instance_name]['uiid'])
                        each["service"]["logical_name"] = logical_name
                        each["service"]["instance_name"] = instance_name

        self.__state['instances'] = instances

        for mod in fresh_modules:
            defined_modules.append(mod)

        # merge modules overlay from instance
        if "modules" in self.defined:
            modmap = util.merge(modmap, self.defined["modules"])

        self.__tree = {
            "facs": self._fax,
            # instance deprecated
            "instance": self.defined.data,
            # definition deprecated
            "definition": self.defined.data,
            "env": self.defined.data,
            "module": modmap
        }

        # auto save for now
        self.write()

    def passwd(self):
        return self.__state.get('passwd')

    def get_passwd(self, name):
        return self.__state['passwd'].setdefault(name, str(uuid.uuid4()))

    def instances(self):
        return self.__state.get('instances')

    def tree(self):
        return self.__tree

    @property
    def state(self):
        return self.__state

    def write(self):
        """ write all needed state info to filesystem """
        dumped = self._fax.codec.dump(self.__state, open(self.state_file, 'w'))

