import requests
import json
import datetime
import pytz
import itertools

from prometheus_client import CollectorRegistry, generate_latest
from prometheus_client.core import GaugeMetricFamily

from .defer import parallelize

requests.packages.urllib3.disable_warnings()

class VacTenantCollector(object):

    def __init__(self, connection, host, ignore_ssl):
        self.host = host
        self.token = connection.token
        self.ignore_ssl = ignore_ssl
        self.tenants = connection.tenants

    def _create_metric_containers(self):
        metric_list = {}
        metric_list['tenant'] = {
                'tenant_vms_backedup': GaugeMetricFamily(
                    'teant_vms_backedup',
                    'Number of protected vms of tenant',
                    labels=['tenant_name','tenant_id']),
                'tenant_vms_replicated': GaugeMetricFamily(
                    'tenant_vms_replicated',
                    'Number of replicated vms of tenant',
                    labels=['tenant_name','tenant_id']),
                'tenant_vms_backed_cloud': GaugeMetricFamily(
                    'tenant_vms_backed_cloud',
                    'Number of tenat vms backed up to cloud',
                    labels=['tenat_name','tenant_id'])
                }

        metrics = {}
        for key in metric_list.keys():
            metrics.update(metric_list[key])

        return metrics

    def collect(self):
        """
        Get Tenant information
        """
        start = datetime.datetime.utcnow()
        metrics = self._create_metric_containers()
        log("Starting Tenat metrics collection")

        for tenant in self.tenants:
            labels = [str(tenant['id']), str(tenant['name'])]

            metrics['tenant_vms_backedup'].add_metric(labels, tenant['vMsBackedUp'])
            metrics['tenant_vms_replicated'].add_metric(labels, tenant['vMsReplicated'])
            metrics['tenant_vms_backed_cloud'].add_metric(labels, tenant['vMsBackedUpToCloud'])

        log("Finished tenant metrics collection (%s)", datetime.datetime.utcnow() - start)

        return list(metrics.values())

class VacJobCollector(object):

    def __init__(self, connection, host, ignore_ssl):
        self.host = host
        self.token = connection.token
        self.ignore_ssl = ignore_ssl

    def _create_metric_containers(self):
        metric_list = {}
        metric_list['job'] = {
                'job_processing_rate': GaugeMetricFamily(
                    'job_processing_rate',
                    'Rate of job processing',
                    labels=['job_id','job_name','tenant_id','units']),
                'job_transfer_data': GaugeMetricFamily(
                    'job_transfer_data',
                    'Amount of data transferred in job',
                    labels=['job_id','job_name','tenant_id','units']),
                'job_protected_vms': GaugeMetricFamily(
                    'job_protected_vms',
                    'Protected vms in job',
                    labels=['job_id','job_name','tenant_id'])
                }

        metrics = {}
        for key in metric_list.keys():
            metrics.update(metric_list[key])

        return metrics


    def collect(self):
        metrics = self._create_metric_containers()
        """
        Invoke Rest Call for Jobs
        """
        log("Gathering VAC Jobs")
        start = datetime.datetime.utcnow()
        headers = {'Authorization': self.token}
        url = "https://" + self.host + ":1281/v2/jobs"
        try:
            if self.ignore_ssl:
                r = requests.get(url, headers=headers, verify=False)
                log("Fetched Jobs (%s)",datetime.datetime.utcnow() - start)
                jobs = json.loads(r.content)
            else:
                r = requests.get(url, headers=headers)
                log("Fetched Jobs (%s)",datetime.datetime.utcnow() - start)
                jobs = json.loads(r.content)
        except Exception as error:
            log("Unable to gather jobs: " + error)


        """
        Get Job information
        """
        log("Starting Job metrics collection")
        start = datetime.datetime.utcnow()

        labels = {}
        for job in jobs:
            tenant_id = job['_links']['tenants']['href'].split("/")
            labels_processing = [str(job['id']),str(job['name']),str(tenant_id[(len(tenant_id)-1)]),str(job['processingRateUnits'])]
            labels_transferred = [str(job['id']),str(job['name']),str(tenant_id[(len(tenant_id)-1)]),str(job['transferredDataUnits'])]
            labels = [str(job['id']),str(job['name']),str(tenant_id[(len(tenant_id)-1)])]

            metrics['job_processing_rate'].add_metric(labels_processing, job['processingRate'])
            metrics['job_transfer_data'].add_metric(labels_transferred, job['transferredData'])
            metrics['job_protected_vms'].add_metric(labels, job['protectedVMs'])

        log("Finished job metrics collection (%s)", datetime.datetime.utcnow() - start)


        return list(metrics.values())


class VacResourceCollector(object):

    def __init__(self, connection, host, ignore_ssl):
        self.host = host
        self.token = connection.token
        self.ignore_ssl = ignore_ssl
        self.tenants = connection.tenants

    def _create_metric_containers(self):
        metric_list = {}
        metric_list['resources'] = {
                'resources_storage_quota': GaugeMetricFamily(
                    'resources_storage_quota',
                    'Storage quota for tenant resources',
                    labels=['resource_id','tenant_id','tenant_name','units']),
                'resources_vms_quota': GaugeMetricFamily(
                    'resources_vms_quota',
                    'VM quota for tenant resources',
                    labels=['resource_id','tenant_id','tenant_name','units']),
                'resources_traffic_quota': GaugeMetricFamily(
                    'resources_traffic_quota',
                    'Network traffic quota for tenant resources',
                    labels=['resource_id','tenant_id','tenant_name','units']),
                'resources_used_storage': GaugeMetricFamily(
                    'resources_used_storage',
                    'Used storage for tenant resources',
                    labels=['resource_id', 'tenant_id','tenant_name','units']),
                'resources_used_traffic': GaugeMetricFamily(
                    'resources_used_traffic',
                    'Used network traffic for tenant resources',
                    labels=['resource_id','tenant_id','tenant_name','units'])
                }
        metrics = {}
        for key in metric_list.keys():
            metrics.update(metric_list[key])

        return metrics

    def collect(self):
        metrics = self._create_metric_containers()

        """
        Get Tenant Resource information
        """
        log("Starting Resource collection")
        start = datetime.datetime.utcnow()

        labels = {}
        for tenant in self.tenants:
            try:
                resources = self.tenant_resources(tenant['id'])
                vm_labels = [str(resources[0]['id']),str(tenant['id']),str(tenant['name'])]
                storage_quota_labels = [str(resources[0]['id']),str(tenant['id']),str(tenant['name']),str(resources[0]['storageQuotaUnits'])]
                storage_labels = [str(resources[0]['id']),str(tenant['id']),str(tenant['name']),str(resources[0]['usedStorageQuotaUnits'])]
                traffic_quota_labels = [str(resources[0]['id']),str(tenant['id']),str(tenant['name']),str(resources[0]['trafficQuotaUnits'])]
                traffic_labels = [str(resources[0]['id']),str(tenant['id']),str(tenant['name']),str(resources[0]['usedTrafficQuotaUnits'])]
                
                metrics['resources_storage_quota'].add_metric(storage_quota_labels, resources[0]['storageQuota'])
                metrics['resources_vms_quota'].add_metric(vm_labels, resources[0]['vMsQuota'])
                metrics['resources_traffic_quota'].add_metric(traffic_quota_labels, resources[0]['trafficQuota'])
                metrics['resources_used_storage'].add_metric(storage_labels, resources[0]['usedStorageQuota'])
                metrics['resources_used_traffic'].add_metric(traffic_labels, resources[0]['usedTrafficQuota'])
            except Exception as error:
                log("Unable to gather resources for (%s): (%s)", tenant['id'], error)
                continue

        return list(metrics.values()) 

    def tenant_resources(self, tenant_id):
        """
        Invoke Rest call for Tenant Resources
        """
        log("Gathering resources for tenant {}".format(tenant_id))
        start = datetime.datetime.utcnow()
        headers = {'Authorization': self.token}
        url = "https://" + self.host + ":1281/v2/tenants/" + str(tenant_id) + "/backupResources"
        try:
            if self.ignore_ssl:
                r = requests.get(url, headers=headers, verify=False)
                log("Fetched Tenant resources (%s)", datetime.datetime.utcnow() - start)
                return json.loads(r.content)
            else:
                r = requests.get(url, headers=headers)
                log("Fetched Tenant resources (%s)", datetime.datetime.utcnow() - start)
                return json.loads(r.content)
        except Exception as error:
            log("Unable to gather tenant resoucres: " + error)


class VacConnection(object):
    def __init__(self, host, username, password, ignore_ssl):
        self.host = host
        self.username = username
        self.password = password
        self.ignore_ssl = ignore_ssl
        self.token = ''
        self.tenants = {}
        self.configure()

    def configure(self):
        """
        Connect to VAC and get connection
        """
        body = "grant_type=password&username=" + self.username + "&password=" + self.password
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer'}
        url = "https://" + self.host + ":1281/token"
        try:
            if self.ignore_ssl:
                # Request api key with sslverify = false
                r = requests.post(url, data=body, headers=headers, verify=False)
                response = json.loads(r.content)
                self.token = "Bearer " + response['access_token']
            else:
                r = requests.post(url, data=body, headers=headers)
                response = json.loads(r.content)
                self.token = "Bearer " + response['access_token']
        except Exception as error:
            log("Unable to gather token: " + str(error))

        """
        Invoke Rest call for Tenants
        """
        log("Gathering VAC Tenants")
        start = datetime.datetime.utcnow()
        headers = {'Authorization': self.token}
        url = "https://" + self.host + ":1281/v2/tenants"
        try:
            if self.ignore_ssl:
                r = requests.get(url, headers=headers, verify=False)
                log("Fetched Tenants (%s)", datetime.datetime.utcnow() - start)
                self.tenants = json.loads(r.content)
            else:
                r = requests.get(url, headers=headers)
                log("Fetched Tenants (%s)", datetime.datetime.utcnow() - start)
                self.tenants = json.loads(r.content)
        except Exception as error:
            log("Unable to gather tenants: " + str(error))


def log(data, *args):
    """
    Log any message in a uniform format
    """
    print("[{0}] {1}".format(datetime.datetime.utcnow().replace(tzinfo=pytz.utc), data % args))


def collect_vac(host, username, password, ignore_ssl):
    """
    Scrape and return metrics 
    """
    connection = VacConnection(host, username, password, ignore_ssl)
    
    registry = CollectorRegistry()
    registry.register(VacTenantCollector(connection, host, ignore_ssl))
    registry.register(VacJobCollector(connection, host, ignore_ssl))
    registry.register(VacResourceCollector(connection, host, ignore_ssl))
    return generate_latest(registry)
