#
# Copyright (c) 2019 Red Hat, Inc.
#
# This file is part of gluster-health-report project which is a
# subproject of GlusterFS ( www.gluster.org)
#
# This file is licensed to you under your choice of the GNU Lesser
# General Public License, version 3 or any later version (LGPLv3 or
# later), or the GNU General Public License, version 2 (GPLv2), in all
# cases as published by the Free Software Foundation.

import tempfile
import uuid
import json

from glustercsctl.utils import kubectl_get, template_kube_apply, \
    GlusterCSException, error, info, kubectl_exec

# Manifest files
ManifestGcsNamespace = "gcs-namespace.yml"
ManifestEtcdOperator = "gcs-etcd-operator.yml"
ManifestEtcdCluster = "gcs-etcd-cluster.yml"
ManifestGd2Services = "gcs-gd2-services.yml"
ManifestGd2Node = "gcs-gd2.yml"
ManifestFsCSI = "gcs-fs-csi.yml"
ManifestVirtBlockCSI = "gcs-virtblock-csi.yml"
ManifestPromethesOperator = "gcs-prometheus-operator.yml"
ManifestPrometheusBundle = "gcs-prometheus-bundle.yml"
ManifestPrometheusKubeStateMetrics = "gcs-prometheus-kube-state-metrics.yml"
ManifestPrometheusKubeMetrics = "gcs-prometheus-kube-metrics.yml"
ManifestPrometheusEtcdMetrics = "gcs-prometheus-etcd.yml"
ManifestPrometheusNodeMetrics = "gcs-prometheus-node-exporter.yml"
ManifestPrometheusOperatorMetrics = "gcs-prometheus-operator-metrics.yml"
ManifestGrafanaMixins = "gcs-mixins.yml"
ManifestGrafanaDashboard = "gcs-grafana.yml"
ManifestPrometheusAlertManager = "gcs-prometheus-alertmanager-cluster.yml"
ManifestVirtBlockCSIStorageClass = "gcs-storage-virtblock.yml"
ManifestStorageSnapshot = "gcs-storage-snapshot.yml"


def gcs_namespace_setup(config):
    template_kube_apply(config, ManifestGcsNamespace)
    info("GCS Namespace created")


def etcd_setup(config):
    template_kube_apply(config, ManifestEtcdOperator)
    info("Etcd Operator created")

    kubectl_get(
        namespace=config["namespace"],
        jsonpath="status.availableReplicas",
        gettype="deployment",
        name="etcd-operator",
        retries=50,
        delay=10,
        out_expect="1",
        label="Checking etcd operator status"
    )

    info("Etcd Operator is ready")

    template_kube_apply(
        config,
        ManifestEtcdCluster,
        retries=5,
        delay=5,
        label="Checking Etcd Operator status"
    )
    info("Etcd cluster created")

    etcd_client_endpoint = kubectl_get(
        namespace=config["namespace"],
        jsonpath="spec.clusterIP",
        gettype="service",
        name="etcd-client",
        retries=5,
        delay=5,
        label="Fetch etcd Cluster IP"
    )

    def check_num_etcd_running(out):
        # 3 etcd pods + one header line in CLI
        return len(out.split("\n")) == 4

    etcd_client_endpoint = "http://%s:2379" % etcd_client_endpoint
    config["template-args"]["etcd_client_endpoint"] = etcd_client_endpoint
    info("Etcd Service IP is available", endpoint=etcd_client_endpoint)
    kubectl_get(
        namespace=config["namespace"],
        jsonpath="",
        gettype="pods",
        name="",
        extra_args=["-l", "etcd_cluster=etcd",
                    "--field-selector=status.phase=Running"],
        out_expect_fn=check_num_etcd_running,
        retries=50,
        delay=10,
        label="Check for Etcd cluster status"
    )

    info("Etcd cluster is UP")


def glusterd2_setup(config):
    template_kube_apply(config, ManifestGd2Services)
    info("Glusterd2 services created")

    for node in config["nodes"]:
        config["template-args"]["kube_hostname"] = node["address"]
        node_manifest_file = ManifestGd2Node.replace(
            ".yml", "-" + node["address"] + ".yml")
        template_kube_apply(
            config,
            node_manifest_file,
            template_file=ManifestGd2Node
        )
        info("Glusterd2 pod created", address=node["address"])

    gd2_client_endpoint = kubectl_get(
        namespace=config["namespace"],
        jsonpath="spec.clusterIP",
        gettype="service",
        name="glusterd2-client",
        retries=5,
        delay=5,
        label="Fetching Glusterd2 Cluster IP"
    )
    gd2_client_endpoint = "http://%s:24007" % gd2_client_endpoint
    info("Fetched Glusterd2 ClusterIP", ip=gd2_client_endpoint)

    def check_num_peers(cmdout):
        peers = json.loads(cmdout.strip())
        return len(peers) == len(config["nodes"])

    curl_cmd = "curl %s/v1/peers" % gd2_client_endpoint
    peers = kubectl_exec(
        config["namespace"],
        "gluster-%s-0" % config["nodes"][0]["address"],
        curl_cmd,
        out_expect_fn=check_num_peers,
        retries=50,
        delay=10,
        label="Fetching the Gluster Peer info"
    )

    info("Glusterd2 cluster is ready")

    peers_json = json.loads(peers)

    for peer in peers_json:
        kube_hostname = peer["name"].split('-')[1]
        config["template-args"]["kube_hostname"] = kube_hostname
        devices = []
        for node in config["nodes"]:
            if node["address"] == kube_hostname:
                devices = node["devices"]
                break

        for device in devices:
            cmd = "glustercli device add %s %s" % (peer["id"], device)
            kubectl_exec(
                config["namespace"],
                "gluster-%s-0" % config["nodes"][0]["address"],
                cmd,
                retries=5,
                delay=5,
                label="Adding device to peer"
            )
            info("Added device", peer=kube_hostname, device=device)


def fs_csi_setup(config):
    template_kube_apply(config, ManifestFsCSI)
    info("GlusterCS FS CSI driver pods created")

    kubectl_get(
        namespace=config["namespace"],
        jsonpath="status.readyReplicas",
        gettype="statefulset",
        name="csi-provisioner-glusterfsplugin",
        retries=50,
        delay=10,
        out_expect="1",
        label="Checking FS CSI Provisioner state"
    )
    info("FS CSI provisioner is Ready")

    kubectl_get(
        namespace=config["namespace"],
        jsonpath="status.readyReplicas",
        gettype="statefulset",
        name="csi-attacher-glusterfsplugin",
        retries=50,
        delay=10,
        out_expect="1",
        label="Checking FS CSI attacher status"
    )
    info("FS CSI attacher is Ready")

    kubectl_get(
        namespace=config["namespace"],
        jsonpath="status.numberAvailable",
        gettype="daemonset",
        name="csi-nodeplugin-glusterfsplugin",
        retries=50,
        delay=10,
        out_expect="%s" % config["cluster-size"],
        label="Checking CSI node plugins"
    )
    info("FS CSI node plugins are Ready")

    template_kube_apply(config, ManifestStorageSnapshot)
    info("FS Storage and Snapshot class created")


def virtblock_csi_setup(config):
    template_kube_apply(config, ManifestVirtBlockCSI)
    info("GlusterCS Virtblock CSI driver pods created")

    kubectl_get(
        namespace=config["namespace"],
        jsonpath="status.readyReplicas",
        gettype="statefulset",
        name="csi-glustervirtblock-provisioner",
        retries=50,
        delay=10,
        out_expect="1",
        label="Checking Virtblock CSI Provisioner state"
    )
    info("CSI Virtblock provisioner is Ready")

    kubectl_get(
        namespace=config["namespace"],
        jsonpath="status.readyReplicas",
        gettype="statefulset",
        name="csi-glustervirtblock-attacher",
        retries=50,
        delay=10,
        out_expect="1",
        label="Checking Virtblock CSI attacher status"
    )
    info("CSI Virtblock attacher is Ready")

    kubectl_get(
        namespace=config["namespace"],
        jsonpath="status.numberAvailable",
        gettype="daemonset",
        name="csi-glustervirtblock-nodeplugin",
        retries=50,
        delay=10,
        out_expect="%s" % config["cluster-size"],
        label="Checking Virtblock CSI node plugins"
    )
    info("Virtblock CSI node plugins are Ready")

    template_kube_apply(config, ManifestVirtBlockCSIStorageClass)
    info("Virtblock Storage class created")


def monitoring_setup(config):
    template_kube_apply(config, ManifestPromethesOperator)
    info("Prometheus operator created")

    kubectl_get(
        namespace=config["namespace"],
        jsonpath="status.availableReplicas",
        gettype="deployment",
        name="prometheus-operator",
        retries=50,
        delay=10,
        out_expect="1",
        label="Checking Prometheus Operator"
    )
    info("Prometheus operator is Ready")

    kubectl_get(
        namespace="",
        jsonpath="",
        gettype="customresourcedefinitions",
        name="servicemonitors.monitoring.coreos.com",
        retries=30,
        delay=10,
        label="Checking Prometheus CRD"
    )
    info("Prometheus CRD check successful")

    kubectl_get(
        namespace=config["namespace"],
        jsonpath="",
        gettype="servicemonitors",
        name="",
        retries=30,
        delay=10
    )
    info("Prometheus service monitor CRD check successful")

    kubectl_get(
        namespace=config["namespace"],
        jsonpath="",
        gettype="Prometheus",
        name="",
        retries=30,
        delay=10
    )
    info("Prometheus namespace check successful")

    monitoring_extra = (
        (
            "Prometheus services, ServiceMonitor and Prometheus Objects",
            ManifestPrometheusBundle
        ),
        (
            "Kube-State-Metrics Exporter",
            ManifestPrometheusKubeStateMetrics
        ),
        (
            "Kubelet, APIServer and CoreDNS",
            ManifestPrometheusKubeMetrics
        ),
        (
            "Etcd Operator and the etcd cluster Exporters",
            ManifestPrometheusEtcdMetrics
        ),
        (
            "Node exporter",
            ManifestPrometheusNodeMetrics
        ),
        (
            "Prometheus Operator Exporter",
            ManifestPrometheusOperatorMetrics
        ),
        (
            "Alert manager Cluster",
            ManifestPrometheusAlertManager
        ),
        (
            "Grafana mixins",
            ManifestGrafanaMixins
        ),
        (
            "Grafana dashboard",
            ManifestGrafanaDashboard
        )
    )

    for msg, filename in monitoring_extra:
        template_kube_apply(config, filename, retries=2, delay=10,
                            label="Checking status of %s" % msg)
        info(msg + " deployed")


def deploy(config):
    config["template-args"] = {}
    config["template-args"]["gcs_namespace"] = config["namespace"]

    config["template-args"]["gcs_gd2_clusterid"] = str(uuid.uuid1())

    if not config.get("manifests-dir", ""):
        config["manifests-dir"] = (
            "https://raw.githubusercontent.com/gluster/"
            "gcs/master/deploy/templates/gcs-manifests/"
        )

    # Create working directory
    config["workdir"] = tempfile.mkdtemp(prefix="glustercs-")

    try:
        # GCS namespace create
        gcs_namespace_setup(config)

        # Etcd Operator and Etcd Cluster create
        etcd_setup(config)

        # Glusterd2 and devices setup
        glusterd2_setup(config)

        # FS CSI drivers setup
        fs_csi_setup(config)

        # Virtblock CSI drivers setup
        virtblock_csi_setup(config)

        # Monitoring setup
        monitoring_setup(config)

    except GlusterCSException as err:
        error(err)
