from functools import reduce
from time import sleep

from openstack import connect
from openstack.config import OpenStackConfig
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY


# metrics
# openstack_limit_max{project_id="", limit="cores"}
# openstack_limit_used{project_id="", limit="cores"}

LIMITS = {
    'max': {
        'cores': 'max_total_cores',
        'floating_ips': 'properties.maxTotalFloatingIps',
        'instances': 'max_total_instances',
        'ram': 'max_total_ram_size',
        'security_groups': 'properties.maxSecurityGroups',
        'server_groups': 'max_server_groups'
    },
    'used': {
        'cores': 'total_cores_used',
        'floating_ips': 'properties.totalFloatingIpsUsed',
        'instances': 'total_instances_used',
        'ram': 'total_ram_used',
        'security_groups': 'properties.totalSecurityGroupsUsed',
        'server_groups': 'total_server_groups_used'
    }
}

def rget(obj, key, *args):
    def _get(obj, key):
        return obj.get(key, *args)
    return reduce(_get, [obj] + key.split('.'))

class Connection():
    conn = None
    limits = None

    def __init__(self, name):
        self.conn = connect(cloud=name)
        self.new_compute_limits()

    def get_compute_limits(self):
        return self.limits

    def new_compute_limits(self):
        self.limits = self.conn.get_compute_limits().toDict()


class LimitCollector():
    conns = {}
    name = ""

    def __init__(self, conns, name, limits):
        self.conns = conns
        self.name = name
        self.limits = limits

    def collect(self):
        metric = GaugeMetricFamily(
            "openstack_limit_%s" % self.name,
            "openstack limits %s in project" % self.name,
            labels=["project_id", "limit"]
        )

        for conn in self.conns:
            compute = conn.get_compute_limits()

            for limit in self.limits:
                metric.add_metric(
                    [rget(compute, 'location.project.id'), limit],
                    rget(compute, self.limits[limit])
                )

        yield metric


def start_server(port, interval, cloud_names):
    clouds = []
    if cloud_names is None:
        for cloud in OpenStackConfig().get_all():
            clouds.append(cloud.name)
    else:
        clouds = cloud_names.split(",")

    conns = []
    for cloud in clouds:
        conns.append(Connection(cloud))

    collector_max = LimitCollector(conns, 'max', LIMITS['max'])
    collector_used = LimitCollector(conns, 'used', LIMITS['used'])
    REGISTRY.register(collector_max)
    REGISTRY.register(collector_used)

    start_http_server(port)

    while True:
        for conn in conns:
            conn.new_compute_limits()
        sleep(interval)
