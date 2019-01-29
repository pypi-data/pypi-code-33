# Copyright 2015, Radware LTD. All rights reserved
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

import copy
import netaddr
import time
import threading

from neutron.api.v2 import attributes
from neutron import context
from neutron.plugins.common import constants
from oslo_config import cfg
from oslo_log import helpers as log_helpers
from oslo_log import log as logging
from oslo_utils import excutils
from six.moves import queue as Queue

from neutron_lbaas._i18n import _LE, _LW, _LI
import neutron_lbaas.common.cert_manager
import neutron_lbaas.extensions.loadbalancerv2 as lb_ext
import neutron_lbaas.db.loadbalancer.models as dbm

import base_driver
import exceptions as r_exc
import rest_client as rc
import config as rad_config
import monitoring

CERT_MANAGER_PLUGIN = neutron_lbaas.common.cert_manager.get_backend()

PROPERTY_DEFAULTS = {'type': 'none',
                     'cookie_name': 'none',
                     'url_path': '/',
                     'http_method': 'GET',
                     'expected_codes': '200',
                     'subnet': '255.255.255.255',
                     'mask': '255.255.255.255',
                     'gw': '255.255.255.255',
                     }
LOADBALANCER_PROPERTIES = ['vip_address', 'admin_state_up']
LISTENER_PROPERTIES = ['id', 'protocol_port', 'protocol',
                       'connection_limit', 'admin_state_up']
DEFAULT_CERT_PROPERTIES = ['id', 'certificate', 'intermediates',
                           'private_key', 'passphrase']
SNI_CERT_PROPERTIES = DEFAULT_CERT_PROPERTIES + ['position']
L7_RULE_PROPERTIES = ['id', 'type', 'compare_type',
                      'key', 'value', 'admin_state_up']
L7_POLICY_PROPERTIES = ['id', 'action', 'redirect_pool_id',
                        'redirect_url', 'position', 'admin_state_up']
DEFAULT_POOL_PROPERTIES = ['id']
POOL_PROPERTIES = ['id', 'protocol', 'lb_algorithm', 'admin_state_up']
MEMBER_PROPERTIES = ['id', 'address', 'protocol_port', 'weight',
                     'admin_state_up', 'subnet', 'mask', 'gw']
SESSION_PERSISTENCY_PROPERTIES = ['type', 'cookie_name']
HEALTH_MONITOR_PROPERTIES = ['type', 'delay', 'timeout', 'max_retries',
                             'admin_state_up', 'url_path', 'http_method',
                             'expected_codes', 'id']

LOG = logging.getLogger(__name__)


class RadwareLBaaSV2Driver(base_driver.RadwareLBaaSBaseV2Driver):
    #
    # Assumptions:
    # 1) We have only one worflow that takes care of l2-l4 and service creation
    # 2) The workflow template exists on the vDirect server
    # 3) The workflow expose one operation named 'update' (plus ctor and dtor)
    # 4) The 'update' operation gets the loadbalancer object graph as input
    # 5) The object graph is enehanced by our code before it is sent to the
    #    workflow
    # 6) Async operations are handled by a different thread
    #

    queue = Queue.Queue()
    queuelock = threading.Lock()

    def __init__(self, plugin, module_fqn=None):
        if not module_fqn:
            module_fqn = __name__
        module_name = module_fqn.split('.')[-1]

        base_driver.RadwareLBaaSBaseV2Driver.__init__(self, plugin, module_name)

        self.config = rad_config.RadwareDirectConfig(module_name)
        if self.config.missing():
            self.config = rad_config.RadwareOsloConfig(module_name)
        if self.config.missing():
            raise lb_ext.DriverError(msg='No service provider configuration found.')

        self.plugin = plugin
        self.service = {
            "name": "_REPLACE_",
            "tenantId": "_REPLACE_",
            "haPair": self.config.service_ha_pair,
            "sessionMirroringEnabled": self.config.service_session_mirroring_enabled,
            "primary": {
                "capacity": {
                    "throughput": self.config.service_throughput,
                    "sslThroughput": self.config.service_ssl_throughput,
                    "compressionThroughput":
                    self.config.service_compression_throughput,
                    "cache": self.config.service_cache
                },
                "network": {
                    "type": "portgroup",
                    "portgroups": '_REPLACE_'
                },
                "adcType": self.config.service_adc_type,
                "acceptableAdc": "Exact"
            }
        }
        if self.config.service_resource_pool_ids:
            ids = self.config.service_resource_pool_ids
            self.service['resourcePoolIds'] = [
                {'id': iid} for iid in ids
            ]
        else:
            self.service['resourcePoolIds'] = []

        if self.config.service_isl_vlan:
            self.service['islVlan'] = self.config.service_isl_vlan
        self.workflow_template_name = self.config.workflow_template_name
        self.workflow_instance_prefix = self.config.workflow_instance_prefix
        self.child_workflow_template_names = self.config.child_workflow_template_names
        self.workflow_params = self.config.workflow_params
        self.workflow_action_name = self.config.workflow_action_name
        self.stats_action_name = self.config.stats_action_name
        self.status_action_name = self.config.status_action_name
        self.monitoring_pace = self.config.monitoring_pace
        vdirect_address = self.config.vdirect_address
        sec_server = self.config.ha_secondary_address
        self.rest_client = rc.vDirectRESTClient(
            server=vdirect_address,
            secondary_server=sec_server,
            user=self.config.vdirect_user,
            password=self.config.vdirect_password,
            port=self.config.port,
            ssl=self.config.ssl,
            ssl_verify_context=self.config.ssl_verify_context,
            timeout=self.config.timeout,
            base_uri=self.config.base_uri)
        self.workflow_params['provision_service'] = self.config.provision_service
        self.workflow_params['configure_l3'] = self.config.configure_l3
        self.workflow_params['configure_l4'] = self.config.configure_l4
        self.configure_allowed_address_pairs =\
            self.config.configure_allowed_address_pairs

        self.completion_monitor = monitoring.CompletionMonitor(
            self.rest_client, plugin)
        self.completion_monitor.daemon = True
        self.completion_monitor.start()

        self.monitor = monitoring.StatusMonitor(
            self.rest_client, self.monitoring_pace,
            self.status_action_name, self.stats_action_name,
            status_feedback = self._update_operational_status)
        self.monitor.daemon = True
        self.monitor.start()

        self.workflow_templates_exists = False

    def _get_wf_name(self, lb):
        return self.workflow_instance_prefix + lb.id

    @log_helpers.log_method_call
    def _verify_workflow_templates(self):
        """Verify the existence of workflows on vDirect server."""
        resource = '/api/runnable/WorkflowTemplate/'
        workflow_templates = [self.workflow_template_name]
        workflow_templates.extend(self.child_workflow_template_names)
        response = rc.rest_wrapper(
            self.rest_client.call('GET', resource, None, None), [200])

        template_names = response['names']
        for required_template in workflow_templates:
            if required_template not in template_names:
                raise r_exc.WorkflowTemplateMissing(
                    workflow_template=required_template)

    @log_helpers.log_method_call
    def workflow_exists(self, lb):
        wf_resource = '/api/runnable/Workflow/'
        response = rc.rest_wrapper(
            self.rest_client.call('GET', wf_resource, None, None), [200])
        LOG.info('Workflow exist response:' + repr(response))
        if 'names' not in response:
            return False
        workflow_names = response['names']
        return self._get_wf_name(lb) in workflow_names

    @log_helpers.log_method_call
    def _create_workflow(self, lb, lb_network_id, proxy_network_id):
        self._verify_workflow_templates()

        wf_name = self._get_wf_name(lb)
        service = copy.deepcopy(self.service)
        service['tenantId'] = lb.tenant_id
        service['name'] = 'srv_' + lb_network_id

        self.workflow_params["loadbalancer_id"] = lb.id
        if lb_network_id != proxy_network_id:
            self.workflow_params["twoleg_enabled"] = True
            service['primary']['network']['portgroups'] = [
                lb_network_id, proxy_network_id]
        else:
            self.workflow_params["twoleg_enabled"] = False
            service['primary']['network']['portgroups'] = [lb_network_id]

        tenants = [lb.tenant_id] if lb.tenant_id else []
        parameters = dict(self.workflow_params, service_params=service,
                          workflowName=wf_name,
                          __tenants=tenants)
        resource = '/api/runnable/WorkflowTemplate/%s/%s' % (
            self.workflow_template_name, 'createWorkflow')
        rc.rest_wrapper(self.rest_client.call(
            'POST', resource, parameters, rc.JSON_HEADER))

    @log_helpers.log_method_call
    def execute_workflow(self, ctx, manager, data_model,
                         old_data_model=None, delete=False):
        lb = data_model.root_loadbalancer

        # Get possible proxy subnet.
        # Proxy subnet equals to LB subnet if no proxy
        # is necessary.
        # Get subnet id of any member located on different than
        # loadbalancer's network. If returned subnet id is the subnet id
        # of loadbalancer - all members are accessible from loadbalancer's
        # network, meaning no second leg or static routes are required.
        # Otherwise, create proxy port on found member's subnet and get its
        # address as a proxy address for loadbalancer instance
        lb_subnet = self.plugin.db._core_plugin.get_subnet(
            ctx, lb.vip_subnet_id)
        proxy_subnet = lb_subnet
        proxy_port_address = lb.vip_address

        if not self.workflow_exists(lb):
            # Create proxy port if needed
            proxy_port_subnet_id = self._get_proxy_port_subnet_id(lb)
            if proxy_port_subnet_id != lb.vip_subnet_id:
                proxy_port = self._create_proxy_port(
                    ctx, lb, proxy_port_subnet_id)
                proxy_subnet = self.plugin.db._core_plugin.get_subnet(
                    ctx, proxy_port['subnet_id'])
                proxy_port_address = proxy_port['ip_address']

            self._create_workflow(lb,
                                  lb_subnet['network_id'],
                                  proxy_subnet['network_id'])
        else:
            # Check if proxy port exists
            proxy_port = self._get_proxy_port(ctx, lb)
            if proxy_port:
                proxy_subnet = self.plugin.db._core_plugin.get_subnet(
                    ctx, proxy_port['subnet_id'])
                proxy_port_address = proxy_port['ip_address']

        # Build objects graph
        objects_graph = self._build_objects_graph(ctx, lb, data_model,
                                                  proxy_port_address,
                                                  proxy_subnet,
                                                  delete)
        LOG.debug("Radware vDirect LB object graph is " + str(objects_graph))

        wf_name = self._get_wf_name(lb)
        resource = '/api/runnable/Workflow/%s/%s' % (
            wf_name, self.workflow_action_name)
        response = rc.rest_wrapper(
            self.rest_client.call(
                #'POST', resource, {'parameters': objects_graph}, rc.JSON_HEADER),
                'POST', resource, objects_graph, rc.JSON_HEADER),
            success_codes=[202])
        LOG.debug('_update_workflow response: %s ', response)

        oper = monitoring.CRUDOperationAttributes(
            ctx, manager, response['uri'], lb,
            data_model, old_data_model,
            delete=delete,
            post_operation_function=self._feedback_operation_completion)

        RadwareLBaaSV2Driver.queuelock.acquire()
        RadwareLBaaSV2Driver.queue.put(oper)
        RadwareLBaaSV2Driver.queuelock.release()

    @log_helpers.log_method_call
    def get_stats(self, ctx, lb):

        wf_name = self._get_wf_name(lb)
        resource = '/api/runnable/Workflow/%s/%s' % (
            wf_name, self.stats_action_name)
        response = rc.rest_wrapper(
            self.rest_client.call(
                'POST', resource, {}, rc.JSON_HEADER))
        LOG.debug('stats_action  response: %s ', response)

        completed = False
        while not completed:
            result = self.rest_client.call('GET', response['uri'], None, None)
            res_data = result[rc.RESP_DATA]
            completed = res_data['complete']
            if not completed:
                time.sleep(3)
                continue
            stats = res_data['parameters']['stats']['stats']
            return stats

    def remove_workflow(self, ctx, manager, lb):
        wf_name = self._get_wf_name(lb)
        LOG.debug('Remove the workflow %s', wf_name)
        resource = '/api/runnable/Workflow/%s/%s' % (wf_name, 'deleteWorkflow')
        rest_return = self.rest_client.call('POST', resource, {}, rc.JSON_HEADER)
        response = rc.rest_wrapper(rest_return, [204, 202, 404])

        if rest_return[rc.RESP_STATUS] in [404]:
            try:
                self._feedback_lb_deletion(manager, lb, n_constants.ACTIVE, True)
            except Exception:
                with excutils.save_and_reraise_exception():
                    LOG.error('Proxy port deletion for LB %s failed', lb.id)
        else:
            oper = monitoring.CRUDOperationAttributes(
                ctx, manager, response['uri'], lb,
                lb, old_data_model=None,
                delete=True,
                post_operation_function=self._feedback_lb_deletion)

            RadwareLBaaSV2Driver.queuelock.acquire()
            RadwareLBaaSV2Driver.queue.put_nowait(oper)
            RadwareLBaaSV2Driver.queuelock.release()

    def _build_objects_graph(self, ctx, lb, data_model,
                             proxy_port_address, proxy_subnet,
                             deleted):
        """Iterate over the LB model starting from root lb entity
        and build its JSON representtaion for vDirect
        """
        deleted_ids = []
        if deleted:
            deleted_ids.append(data_model.id)

        graph = {}
        for prop in LOADBALANCER_PROPERTIES:
            graph[prop] = getattr(lb, prop, PROPERTY_DEFAULTS.get(prop))

        graph['pip_address'] = proxy_port_address
        graph['configure_allowed_address_pairs'] =\
            self.configure_allowed_address_pairs

        graph['listeners'] = []
        listeners = [
            listener for listener in lb.listeners
            if listener.provisioning_status != constants.PENDING_DELETE and
            (listener.default_pool and
             listener.default_pool.provisioning_status !=
             constants.PENDING_DELETE and
             listener.default_pool.id not in deleted_ids and
             listener.default_pool.members)]
        for listener in listeners:
            listener_dict = {}
            for prop in LISTENER_PROPERTIES:
                listener_dict[prop] = getattr(
                    listener, prop, PROPERTY_DEFAULTS.get(prop))

            cert_mgr = CERT_MANAGER_PLUGIN.CertManager()

            if listener.default_tls_container_id:
                default_cert = cert_mgr.get_cert(
                    project_id=listener.tenant_id,
                    cert_ref=listener.default_tls_container_id,
                    resource_ref=cert_mgr.get_service_url(
                        listener.loadbalancer_id),
                    service_name='Neutron LBaaS v2 Radware provider')
                def_cert_dict = {
                    'id': listener.default_tls_container_id,
                    'certificate': default_cert.get_certificate(),
                    'intermediates': default_cert.get_intermediates(),
                    'private_key': default_cert.get_private_key(),
                    'passphrase': default_cert.get_private_key_passphrase()}
                listener_dict['default_tls_certificate'] = def_cert_dict

            if listener.sni_containers:
                listener_dict['sni_tls_certificates'] = []
                for sni_container in listener.sni_containers:
                    sni_cert = cert_mgr.get_cert(
                        project_id=listener.tenant_id,
                        cert_ref=sni_container.tls_container_id,
                        resource_ref=cert_mgr.get_service_url(
                            listener.loadbalancer_id),
                        service_name='Neutron LBaaS v2 Radware provider')
                    listener_dict['sni_tls_certificates'].append(
                        {'id': sni_container.tls_container_id,
                         'position': sni_container.position,
                         'certificate': sni_cert.get_certificate(),
                         'intermediates': sni_cert.get_intermediates(),
                         'private_key': sni_cert.get_private_key(),
                         'passphrase': sni_cert.get_private_key_passphrase()})

            listener_dict['l7_policies'] = []
            policies = [
                policy for policy in listener.l7_policies
                if policy.provisioning_status != constants.PENDING_DELETE and
	            policy.id not in deleted_ids]
            for policy in policies:
                policy_dict = {}
                for prop in L7_POLICY_PROPERTIES:
                    policy_dict[prop] = getattr(
                        policy, prop, PROPERTY_DEFAULTS.get(prop))
                policy_dict['rules'] = []
                rules = [
                    rule for rule in policy.rules
                    if rule.provisioning_status != constants.PENDING_DELETE and
                    rule.id not in deleted_ids]
                for rule in rules:
                    rule_dict = {}
                    for prop in L7_RULE_PROPERTIES:
                        rule_dict[prop] = getattr(
                            rule, prop, PROPERTY_DEFAULTS.get(prop))
                    policy_dict['rules'].append(rule_dict)
                if policy_dict['rules']:
                    listener_dict['l7_policies'].append(policy_dict)

            def_pool_dict = {'id': listener.default_pool.id}

            if listener.default_pool.session_persistence:
                sess_pers_dict = {}
                for prop in SESSION_PERSISTENCY_PROPERTIES:
                    sess_pers_dict[prop] = getattr(
                        listener.default_pool.session_persistence, prop,
                        PROPERTY_DEFAULTS.get(prop))
                def_pool_dict['sessionpersistence'] = sess_pers_dict
            listener_dict['default_pool'] = def_pool_dict

            graph['listeners'].append(listener_dict)

        graph['pools'] = []
        pools = [
            pool for pool in lb.pools
            if pool.provisioning_status != constants.PENDING_DELETE and
            pool.id not in deleted_ids]
        for pool in pools:
            pool_dict = {}
            for prop in POOL_PROPERTIES:
                pool_dict[prop] = getattr(
                    pool, prop,
                    PROPERTY_DEFAULTS.get(prop))

            if (pool.healthmonitor and
                pool.healthmonitor.provisioning_status !=
                constants.PENDING_DELETE and
                pool.healthmonitor.id not in deleted_ids):
                hm_dict = {}
                for prop in HEALTH_MONITOR_PROPERTIES:
                    hm_dict[prop] = getattr(
                        pool.healthmonitor, prop,
                        PROPERTY_DEFAULTS.get(prop))
                pool_dict['healthmonitor'] = hm_dict

            pool_dict['members'] = []
            members = [
                member for member in pool.members
                if member.provisioning_status != constants.PENDING_DELETE and
                member.id not in deleted_ids]
            for member in members:
                member_dict = {}
                for prop in MEMBER_PROPERTIES:
                    member_dict[prop] = getattr(
                        member, prop,
                        PROPERTY_DEFAULTS.get(prop))
                if (proxy_port_address != lb.vip_address and
                    netaddr.IPAddress(member.address)
                    not in netaddr.IPNetwork(proxy_subnet['cidr'])):
                    self._accomplish_member_static_route_data(
                        ctx, member, member_dict,
                        proxy_subnet['gateway_ip'])
                pool_dict['members'].append(member_dict)
            graph['pools'].append(pool_dict)

        return graph

    def _get_proxy_port_subnet_id(self, lb):
        """Look for at least one member of any listener's pool
        that is located on subnet different than loabalancer's subnet.
        If such member found, return its subnet id.
        Otherwise, return loadbalancer's subnet id
        """
        for listener in lb.listeners:
            if listener.default_pool:
                for member in listener.default_pool.members:
                    if lb.vip_subnet_id != member.subnet_id:
                        return member.subnet_id
        return lb.vip_subnet_id

    def _create_proxy_port(self,
        ctx, lb, proxy_port_subnet_id):
        """Check if proxy port was created earlier.
        If not, create a new port on proxy subnet and return its ip address.
        Returns port IP address
        """
        proxy_port = self._get_proxy_port(ctx, lb)
        if proxy_port:
            LOG.info(_LI('LB %(lb_id)s proxy port exists on subnet \
                     %(subnet_id)s with ip address %(ip_address)s') %
                     {'lb_id': lb.id, 'subnet_id': proxy_port['subnet_id'],
                      'ip_address': proxy_port['ip_address']})
            return proxy_port

        proxy_port_name = 'proxy_' + lb.id
        proxy_port_subnet = self.plugin.db._core_plugin.get_subnet(
            ctx, proxy_port_subnet_id)
        proxy_port_data = {
            'tenant_id': lb.tenant_id,
            'name': proxy_port_name,
            'network_id': proxy_port_subnet['network_id'],
            'mac_address': attributes.ATTR_NOT_SPECIFIED,
            'admin_state_up': False,
            'device_id': '',
            'device_owner': 'neutron:' + constants.LOADBALANCERV2,
            'fixed_ips': [{'subnet_id': proxy_port_subnet_id}]
        }
        proxy_port = self.plugin.db._core_plugin.create_port(
            ctx, {'port': proxy_port_data})
        proxy_port_ip_data = proxy_port['fixed_ips'][0]

        LOG.info(_LI('LB %(lb_id)s proxy port created on subnet %(subnet_id)s \
                 with ip address %(ip_address)s') %
                 {'lb_id': lb.id, 'subnet_id': proxy_port_ip_data['subnet_id'],
                  'ip_address': proxy_port_ip_data['ip_address']})

        return proxy_port_ip_data

    def _get_proxy_port(self, ctx, lb):
        ports = self.plugin.db._core_plugin.get_ports(
            ctx, filters={'name': ['proxy_' + lb.id], })
        if not ports:
            return None

        proxy_port = ports[0]
        return proxy_port['fixed_ips'][0]

    def _delete_proxy_port(self, ctx, lb):
        port_filter = {
            'name': ['proxy_' + lb.id],
        }
        ports = self.plugin.db._core_plugin.get_ports(
            ctx, filters=port_filter)
        if ports:
            proxy_port = ports[0]
            proxy_port_ip_data = proxy_port['fixed_ips'][0]
            try:
                LOG.info(_LI('Deleting LB %(lb_id)s proxy port on subnet  \
                             %(subnet_id)s with ip address %(ip_address)s') %
                         {'lb_id': lb.id,
                          'subnet_id': proxy_port_ip_data['subnet_id'],
                          'ip_address': proxy_port_ip_data['ip_address']})
                self.plugin.db._core_plugin.delete_port(
                    ctx, proxy_port['id'])

            except Exception as exception:
                # stop exception propagation, nport may have
                # been deleted by other means
                LOG.warning(_LW('Proxy port deletion failed: %r'),
                            exception)

    def _accomplish_member_static_route_data(self,
        ctx, member, member_data, proxy_gateway_ip):
        member_ports = self.plugin.db._core_plugin.get_ports(
            ctx,
            filters={'fixed_ips': {'ip_address': [member.address]},
                     'tenant_id': [member.tenant_id]})
        if len(member_ports) == 1:
            member_port = member_ports[0]
            member_port_ip_data = member_port['fixed_ips'][0]
            LOG.debug('member_port_ip_data:' + repr(member_port_ip_data))
            member_subnet = self.plugin.db._core_plugin.get_subnet(
                ctx,
                member_port_ip_data['subnet_id'])
            LOG.debug('member_subnet:' + repr(member_subnet))
            member_network = netaddr.IPNetwork(member_subnet['cidr'])
            member_data['subnet'] = str(member_network.network)
            member_data['mask'] = str(member_network.netmask)
        else:
            member_data['subnet'] = member_data['address']
        member_data['gw'] = proxy_gateway_ip

    def _feedback_operation_completion(self, oper):
        try:
            if oper.result['success']:
                oper.manager.successful_completion(
                    oper.ctx, oper.data_model, delete=oper.delete)
            else:
                oper.manager.failed_completion(oper.ctx, oper.data_model)
        except Exception:
            with excutils.save_and_reraise_exception():
                LOG.error('Provisioning status update failed '
                          'for data model id %s',
                          repr(oper.data_model.id))

    def _feedback_lb_deletion(self, oper):
        port_filter = {
            'name': ['proxy_' + oper.lb.id],
        }
        ports = self.plugin.db._core_plugin.get_ports(
            oper.ctx, filters=port_filter)
        if ports:
            proxy_port = ports[0]
            proxy_port_ip_data = proxy_port['fixed_ips'][0]
            try:
                LOG.info('Deleting LB %(lb_id)s proxy port on subnet  '
                         '%(subnet_id)s with ip address %(ip_address)s' %
                         {'lb_id': oper.lb.id,
                          'subnet_id': proxy_port_ip_data['subnet_id'],
                          'ip_address': proxy_port_ip_data['ip_address']})
                self.plugin.db._core_plugin.delete_port(
                    oper.ctx, proxy_port['id'])

            except Exception as exception:
                # stop exception propagation, nport may have
                # been deleted by other means
                LOG.warning('Proxy port deletion failed: %r',
                            exception)

        self._feedback_operation_completion(oper)

    def _update_operational_status(self, oper):
        if not oper.result['success']:
            LOG.error('Failed to get loadbalancer status')
            return

        statuses = oper.result['parameters']['status']
        LOG.info('Status received:' + repr(statuses))
        ctx = context.get_admin_context()

        self.plugin.db.update_status(
            ctx, dbm.LoadBalancer,
            statuses['id'],
            operating_status=statuses['status'])

        if 'listeners' in statuses:
            listeners_status = [l for l in statuses['listeners']]
            for l in listeners_status:
                self.plugin.db.update_status(
                    ctx, dbm.Listener,
                    RadwareLBaaSV2Driver._dash_uuid(l['id']),
                    operating_status=l['status'])
        if 'pools' in statuses:
            pools_status = [l for l in statuses['pools']]
            for p in pools_status:
                self.plugin.db.update_status(
                    ctx, dbm.PoolV2,
                    RadwareLBaaSV2Driver._dash_uuid(p['id']),
                    operating_status=p['status'])
            if 'members' in p:
                members_status = [m for m in p['members']]
                for m in members_status:
                    self.plugin.db.update_status(
                        ctx, dbm.MemberV2,
                        RadwareLBaaSV2Driver._dash_uuid(m['id']),
                        operating_status=m['status'])

    def _update_statistics(self, oper):
        pass

    @staticmethod
    def _dash_uuid(uuid):
        return uuid[:8] + "-" + uuid[8:12] + "-" + uuid[12:16] + "-" + uuid[16:20]+ "-" + uuid[20:32]
