# Copyright 2018, Radware LTD. All rights reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_log import helpers as log_helpers
from neutron_lbaas.drivers import driver_base
import neutron_lbaas.extensions.loadbalancerv2 as lb_ext


VERSION = "M4.5.0"

# Alteon strict application type port numbers
# with automatic protocol selection
ALTEON_STRICT_APPLICATION_TYPE_PORTS_LIST_AUTO_PROTOCOL = [
    20, 21, 22, 23, 25, 43, 69, 79,
    109, 110, 161, 179, 194, 554, 1985
]

# Alteon strict application type port numbers
# with possible (tcp/udp/stateless) protocol selection
ALTEON_STRICT_APPLICATION_TYPE_PORTS_LIST_VARIOUS_PROTOCOL = [
    37, 42, 53, 119, 123, 143, 144, 162,
    389, 520, 1812, 1813, 5060
]

# Alteon strict application type port numbers
ALTEON_STRICT_APPLICATION_PORTS_LIST = \
    ALTEON_STRICT_APPLICATION_TYPE_PORTS_LIST_AUTO_PROTOCOL + \
    ALTEON_STRICT_APPLICATION_TYPE_PORTS_LIST_VARIOUS_PROTOCOL

# Alteon encrypted application type (https/ssl)
# with automatic protocol selection
ALTEON_HTTP_PORT = 80

# Alteon encrypted application type (https/ssl)
# with automatic protocol selection
ALTEON_ENCRYPTED_PORT = 443

class RadwareLBaaSBaseV2Driver(driver_base.LoadBalancerBaseDriver):

    def __init__(self, plugin, provider_name):
        super(RadwareLBaaSBaseV2Driver, self).__init__(plugin)

        self.load_balancer = LoadBalancerManager(self)
        self.listener = ListenerManager(self)
        self.l7policy = L7PolicyManager(self)
        self.l7rule = L7RuleManager(self)
        self.pool = PoolManager(self)
        self.member = MemberManager(self)
        self.health_monitor = HealthMonitorManager(self)


class LoadBalancerManager(driver_base.BaseLoadBalancerManager):

    @log_helpers.log_method_call
    def create(self, context, lb):
        self.successful_completion(context, lb)

    @log_helpers.log_method_call
    def update(self, context, old_lb, lb):
        if self.driver.workflow_exists(old_lb):
            self.driver.execute_workflow(
                context, self, lb, old_data_model=old_lb)
        else:
            self.successful_completion(context, lb)

    @log_helpers.log_method_call
    def delete(self, context, lb):
        if self.driver.workflow_exists(lb):
            self.driver.remove_workflow(
                context, self, lb)
        else:
            self.successful_completion(context, lb, delete=True)

    @log_helpers.log_method_call
    def refresh(self, context, lb):
        if lb.listeners and any(listener.default_pool and
            listener.default_pool.members for listener in lb.listeners):
            self.driver.execute_workflow(
                context, self, lb)
        else:
            self.successful_completion(context, lb)

    @log_helpers.log_method_call
    def stats(self, context, lb):
        if self.driver.workflow_exists(lb):
            return self.driver.get_stats(context, lb)
        else:
            self.successful_completion(context, lb)


class ListenerManager(driver_base.BaseListenerManager):

    def _validate_listener(self, listener):
        if not listener.protocol == 'TCP' and \
            not listener.protocol == 'UDP' and \
            listener.protocol_port in ALTEON_STRICT_APPLICATION_PORTS_LIST:
            raise lb_ext.DriverError(msg='Listener with %(protocol)s '
            'protocol may not use '
            'port %(port)s. This port is reserved for certain application '
            'type and only may use TCP or UDP protocols. '
            'Following is a list of ports allowed for using with TCP or UDP '
            'protocols only %(ports_list)s' %
            {'protocol': listener.protocol, 'port': listener.protocol_port,
            'ports_list': ALTEON_STRICT_APPLICATION_PORTS_LIST})

        if not listener.protocol == 'HTTPS' and \
            not listener.protocol == 'TCP' and \
            not listener.protocol == 'TERMINATED_HTTPS' and \
            listener.protocol_port == ALTEON_ENCRYPTED_PORT:
            raise lb_ext.DriverError(msg='Listener with %(protocol)s '
                'protocol may not use '
                'port number %(port)s. This port number is reserved '
                'for TCP, HTTPS or TERMINATED_HTTPS protocols.' %
                {'protocol': listener.protocol, 'port': ALTEON_ENCRYPTED_PORT})

        if not listener.protocol == 'HTTP' and \
            not listener.protocol == 'TCP' and \
            listener.protocol_port == ALTEON_HTTP_PORT:
            raise lb_ext.DriverError(msg='Listener with %(protocol)s '
                'protocol may not use '
                'port number %(port)s. This port number is reserved '
                'for TCP or HTTP  protocols.' %
                {'protocol': listener.protocol, 'port': ALTEON_HTTP_PORT})

    @log_helpers.log_method_call
    def create(self, context, listener):
        self._validate_listener(listener)
        if self.driver.workflow_exists(listener.root_loadbalancer):
            self.driver.execute_workflow(
                context, self, listener)
        else:
            self.successful_completion(context, listener)

    @log_helpers.log_method_call
    def update(self, context, old_listener, listener):
        if self.driver.workflow_exists(old_listener.root_loadbalancer):
            self.driver.execute_workflow(
                context, self, listener, old_data_model=old_listener)
        else:
            self.successful_completion(context, listener)

    @log_helpers.log_method_call
    def delete(self, context, listener):
        if self.driver.workflow_exists(listener.root_loadbalancer):
            self.driver.execute_workflow(
                context, self, listener, delete=True)
        else:
            self.successful_completion(context, listener, delete=True)


class L7PolicyManager(driver_base.BaseL7PolicyManager):

    @log_helpers.log_method_call
    def create(self, context, policy):
        if self.driver.workflow_exists(policy.root_loadbalancer):
            self.driver.execute_workflow(
                context, self, policy)
        else:
            self.successful_completion(context, policy)

    @log_helpers.log_method_call
    def update(self, context, old_policy, policy):
        if self.driver.workflow_exists(old_policy.root_loadbalancer):
            self.driver.execute_workflow(
                context, self, policy, old_data_model=old_policy)
        else:
            self.successful_completion(context, policy)

    @log_helpers.log_method_call
    def delete(self, context, policy):
        if self.driver.workflow_exists(policy.root_loadbalancer):
            self.driver.execute_workflow(
                context, self, policy, delete=True)
        else:
            self.successful_completion(context, policy, delete=True)


class L7RuleManager(driver_base.BaseL7RuleManager):

    @log_helpers.log_method_call
    def create(self, context, rule):
        if self.driver.workflow_exists(rule.root_loadbalancer):
            self.driver.execute_workflow(
                context, self, rule)
        else:
            self.successful_completion(context, rule)

    @log_helpers.log_method_call
    def update(self, context, old_rule, rule):
        if self.driver.workflow_exists(old_rule.root_loadbalancer):
            self.driver.execute_workflow(
                context, self, rule, old_data_model=old_rule)
        else:
            self.successful_completion(context, rule)

    @log_helpers.log_method_call
    def delete(self, context, rule):
        if self.driver.workflow_exists(rule.root_loadbalancer):
            self.driver.execute_workflow(
                context, self, rule, delete=True)
        else:
            self.successful_completion(context, rule, delete=True)


class PoolManager(driver_base.BasePoolManager):

    @log_helpers.log_method_call
    def create(self, context, pool):
        if self.driver.workflow_exists(pool.root_loadbalancer):
            self.driver.execute_workflow(
                context, self, pool)
        else:
            self.successful_completion(context, pool)

    @log_helpers.log_method_call
    def update(self, context, old_pool, pool):
        if self.driver.workflow_exists(old_pool.root_loadbalancer):
            self.driver.execute_workflow(
                context, self, pool, old_data_model=old_pool)
        else:
            self.successful_completion(context, pool)

    @log_helpers.log_method_call
    def delete(self, context, pool):
        if self.driver.workflow_exists(pool.root_loadbalancer):
            self.driver.execute_workflow(
                context, self, pool, delete=True)
        else:
            self.successful_completion(context, pool,
                                       delete=True)


class MemberManager(driver_base.BaseMemberManager):

    @log_helpers.log_method_call
    def create(self, context, member):
        self.driver.execute_workflow(
            context, self, member)

    @log_helpers.log_method_call
    def update(self, context, old_member, member):
        self.driver.execute_workflow(
            context, self, member, old_data_model=old_member)

    @log_helpers.log_method_call
    def delete(self, context, member):
        self.driver.execute_workflow(
            context, self, member,
            delete=True)


class HealthMonitorManager(driver_base.BaseHealthMonitorManager):

    @log_helpers.log_method_call
    def create(self, context, hm):
        if self.driver.workflow_exists(hm.root_loadbalancer):
            self.driver.execute_workflow(
                context, self, hm)
        else:
            self.successful_completion(context, hm)

    @log_helpers.log_method_call
    def update(self, context, old_hm, hm):
        if self.driver.workflow_exists(old_hm.root_loadbalancer):
            self.driver.execute_workflow(
                context, self, hm, old_data_model=old_hm)
        else:
            self.successful_completion(context, hm)

    @log_helpers.log_method_call
    def delete(self, context, hm):
        if self.driver.workflow_exists(hm.root_loadbalancer):
            self.driver.execute_workflow(
                context, self, hm, delete=True)
        else:
            self.successful_completion(context, hm,
                                       delete=True)