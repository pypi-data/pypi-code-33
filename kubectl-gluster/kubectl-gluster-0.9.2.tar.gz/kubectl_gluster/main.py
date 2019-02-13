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

from argparse import ArgumentParser

from kubectl_gluster.utils import info, warn, error
from kubectl_gluster.deploy import deploy

import yaml


defaultClusterSize = 3
defaultNamespace = "gcs"


def get_args():
    parser = ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="mode")

    # deploy
    parser_deploy = subparsers.add_parser('deploy')
    parser_deploy.add_argument("config", help="Config File name")
    return parser.parse_args()


def deploy_args_validate(config):
    # Hard coded to 3 for now
    if config.get("cluster-size", 0) != defaultClusterSize:
        error("Invalid cluster-size.",
              actual=config.get("cluster-size", 0),
              required=defaultClusterSize)

    if not config.get("namespace", ""):
        config["namespace"] = defaultNamespace
        warn("Namespace not specified, using default namespace.",
             name=defaultNamespace)

    if len(config.get("nodes", [])) != defaultClusterSize:
        error("Invalid number of nodes provided",
              actual=len(config.get("nodes", [])),
              required=defaultClusterSize)

    for idx, node in enumerate(config["nodes"]):
        if not node.get("address", ""):
            error("Invalid address provided for one or more node")

        if len(node.get("devices", [])) == 0:
            warn("No raw devices provided", address=node["address"])

        info("Node details", address=node["address"],
             devices=",".join(node.get("devices", [])))

    info("Cluster Size", clusterSize=config["cluster-size"])
    info("Namespace", namespace=config["namespace"])


def do_deploy(args):
    try:
        config = yaml.load(open(args.config))
    except FileNotFoundError as err:
        error("Unable to open config file.", error=err)

    if isinstance(config, str):
        error("Unable to parse config file.")

    deploy_args_validate(config)
    deploy(config)


def main():
    try:
        args = get_args()
        if args.mode == "deploy":
            do_deploy(args)
    except KeyboardInterrupt:
        return


if __name__ == "__main__":
    main()
