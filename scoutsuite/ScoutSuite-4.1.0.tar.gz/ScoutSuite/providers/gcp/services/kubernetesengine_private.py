# -*- coding: utf-8 -*-

from ScoutSuite.providers.gcp.configs.base import GCPBaseConfig

from googleapiclient.errors import HttpError
import json
from opinel.utils.console import printException, printError

class KubernetesEngineConfig(GCPBaseConfig):
    """
    From https://googleapis.github.io/google-cloud-python/latest/container/gapic/v1/api.html
    zone (str) – Deprecated. The name of the Google Compute Engine zone in which the cluster resides, or “-” for all
    zones. This field has been deprecated and replaced by the parent field.

    They recommend using "parent" but that doesn't seem to be implemented at this point.
    """
    targets = (
        ('clusters', 'Clusters', 'list_clusters', {'project_id': '{{project_placeholder}}',
                                                   'zone': '-'}, False),
    )

    def __init__(self, thread_config):
        self.library_type = 'cloud_client_library'

        self.clusters = {}
        self.clusters_count = 0

        super(KubernetesEngineConfig, self).__init__(thread_config)

    def parse_clusters(self, cluster, params):

        cluster_dict = {}
        cluster_dict['id'] = self.get_non_provider_id(cluster.name)
        cluster_dict['name'] = cluster.name

        cluster_dict['dashboard_status'] = 'Disabled'
        if hasattr(cluster.addons_config, 'kubernetes_dashboard'):
            cluster_dict['dashboard_status'] = 'Enabled'
            if hasattr(cluster.addons_config.kubernetes_dashboard, 'disabled') and \
                    cluster.addons_config.kubernetes_dashboard.disabled:
                cluster_dict['dashboard_status'] = 'Disabled'

        self.clusters[cluster_dict['id']] = cluster_dict
