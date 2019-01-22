# Copyright (C) 2018  Sean Z <sean.z.ealous@gmail.com>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=W0614
import sys
import time
import random
import netaddr
from common import *
from docker import *
from ovs import *

class DockerNetworking(object):
    def __init__(self):
        self.docker = DockerCmd()
        self.vswitch = VSCtl()
    
    def create_bridge(self, br_name, interface=None, br_ip=None):
        self.vswitch.add_br(br_name)
        if interface:
            self.vswitch.add_port(br_name, interface)
        
        run_cmd('ifconfig {} up'.format(br_name))

        if netaddr.valid_ipv4(br_ip) or netaddr.valid_ipv6(br_ip):
            run_cmd('ifconfig {} {}'.format(br_name, br_ip))
    
    def del_bridge(self, br_name):
        self.vswitch.del_br(br_name)
    
    def attach_container(self, container_name, br_name, veth_name, ip, tag=0, gw=False, txoff=False):
        logger.debug("Configure for container: {}".format(container_name))
        nspid = self.docker.nspid(container_name)

        self._create_veth(container_name, br_name, veth_name, tag)

        logger.debug("Container {}: add ip address {} for {}.\n".format(container_name, ip, veth_name))
        self._config_ip(nspid, veth_name, ip, txoff)

        if gw and netaddr.valid_ipv4(gw) or netaddr.valid_ipv6(gw):
            self._config_add_route(container_name, gw)
    
    def dettach_container(self, container_name, br_name, veth_name):
        veth_name_host = self._veth_name_host(container_name, veth_name)
        self.vswitch.del_port(br_name, veth_name_host)
        run_cmd("ip link del {}".format(veth_name_host))
        
    def _create_veth(self, container_name, br_name, container_veth, tag_id=0):
        nspid = self.docker.nspid(container_name)
        # Generate vethnet pair
        veth_name_host = self._veth_name_host(container_name, container_veth)
        logger.debug("veth_name_host: {}".format(veth_name_host))

        run_cmd("ip link del {}".format(veth_name_host))

        veth_name_peer = "if.{:.6f}".format(time.time())[-8:].replace('.', '')
        logger.debug("veth_name_peer: {}".format(veth_name_peer))

        res = run_cmd("ip link add {} type veth peer name {}".format(veth_name_peer, veth_name_host)).replace('\n', '')
        if 'long' in res:
            logger.error(res)
            sys.exit(1)
        logger.debug("Create veth pair (host:{}, container_out:{}) for container {}.".format(veth_name_host, veth_name_peer, container_name))

        self.vswitch.del_port(br_name, veth_name_host)

        res = self.vswitch.add_port(br_name, veth_name_host, tag_id)
        logger.debug("Add port {} into {}.".format(veth_name_host, br_name))

        run_cmd("ifconfig " + veth_name_host + " up")

        run_cmd("ip link set dev {} name {} netns {}".format(veth_name_peer, container_veth, nspid))
        logger.debug("Container {}: map ip device (container_out:{}, container_in:{}).".format(container_name, veth_name_peer, container_veth))

        #activate veth in container
        run_cmd("nsenter -t {} -n ip link set dev {} up".format(nspid, container_veth))

        # for ipv6
        run_cmd("docker exec -t -i {} {}".format(container_name, "sysctl net.ipv6.conf.all.disable_ipv6=0"))

        logger.debug("Container {}: create ethnet {} successfully.".format(container_name, container_veth))
    
    def _veth_name_host(self, container_name, veth_name):
        return "-".join([container_name, veth_name])
        
    def _config_ip(self, nspid, veth_name, ip, txoff=False):
        run_cmd("nsenter -t {} -n ip addr add {} dev {}".format(nspid, ip, veth_name))
        if txoff:
            for _ in range(2):
                cmd = "nsenter -t {} -n ethtool -K {} tx off".format(nspid, veth_name)
                run_cmd(cmd)
                time.sleep(1)
        
    def _config_add_route(self, container_name, gw_ip):
        ipv6_flag = "-A inet6" if ":" in gw_ip else ""
        cmd = "docker exec -t -i {} sudo route {} add default gw {}".format(container_name, ipv6_flag, gw_ip)
        run_cmd(cmd)
    