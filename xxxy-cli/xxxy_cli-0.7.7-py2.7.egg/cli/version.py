#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       version
   Description:
   Author:          huangzhen
   date:            2018/3/26
-------------------------------------------------
   Change Activity:
                   2018/3/26:
-------------------------------------------------
"""
import click
from distutils.version import LooseVersion
import pkg_resources
import subprocess
from russell.client.version import VersionClient
from russell.client.service import ServiceClient
from russell.exceptions import RussellException
from russell.log import logger as russell_logger


def check_cli_version():
    """
    Check if the current cli version satisfies the server requirements
    """
    server_version = VersionClient().get_cli_version()
    current_version = pkg_resources.require("russell-cli")[0].version
    if LooseVersion(current_version) < LooseVersion(server_version.min_version):
        raise RussellException("""
Your version of CLI ({}) is no longer compatible with server. Run:
    pip install -U russell-cli
to upgrade to the latest version ({})
            """.format(current_version, server_version.latest_version))
    if LooseVersion(current_version) < LooseVersion(server_version.latest_version):
        click.echo("""
New version of CLI ({}) is now available. To upgrade run:
    pip install -U russell-cli
            """.format(server_version.latest_version))


def print_version():
    server_version = VersionClient().get_cli_version()
    current_version = pkg_resources.require("russell-cli")[0].version
    click.echo('Version: {}'.format(current_version))
    click.echo('Remote latest version: {}'.format(server_version.latest_version))
    if LooseVersion(current_version) < LooseVersion(server_version.min_version):
        raise RussellException("""
    Your version of CLI ({}) is no longer compatible with server. Run:
        pip install -U russell-cli
    to upgrade to the latest version ({})
                """.format(current_version, server_version.latest_version))
    if LooseVersion(current_version) < LooseVersion(server_version.latest_version):
        click.echo("""
    New version of CLI ({}) is now available. To upgrade run:
        pip install -U russell-cli
                """.format(server_version.latest_version))


def check_server_status():
    """
    Check if russell cloud service status now
    """
    service = ServiceClient().get_service_status()
    if service.service_status <= 0:
        raise RussellException("""
            System is being maintained. Please wait until the end. 
        """)


@click.command()
def version():
    """
    Check current version of the local client and the latest version of remote.
    """
    check_cli_version()
    print_version()


@click.command()
@click.option('-v', '--version', default=None, help='Upgrade to the specified version')
def upgrade(version):
    """
    Upgrade local client.
    """
    if version is None:
        cli_v = "-U", "russell-cli"
    else:
        cli_v = "russell-cli=={}".format(version),
    russell_logger.info("Upgrade to version {}...".format(version or "latest"))
    popenargs = ["pip", "install"]
    popenargs.extend(cli_v)
    subprocess.call(popenargs)
