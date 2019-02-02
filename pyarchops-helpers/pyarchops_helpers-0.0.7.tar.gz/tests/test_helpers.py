#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `pyarchops_helpers` package."""

from suitable import Api
from pyarchops_helpers import helpers


def test_helpers_using_docker():
    """Test the helpers."""

    with helpers.ephemeral_docker_container(
            image='registry.gitlab.com/pyarchops/pyarchops-base'
    ) as container:
        connection_string = "{}:{}".format(
            container['ip'], container['port']
        )
        print('connection strings is ' + connection_string)
        api = Api(connection_string,
                  connection='smart',
                  remote_user=container['user'],
                  private_key_file=container['pkey'],
                  become=True,
                  become_user='root',
                  sudo=True,
                  ssh_extra_args='-o StrictHostKeyChecking=no')

        try:
            result = api.setup()['contacted'][connection_string]
        except Exception as error:
            raise error

        assert result['ansible_facts']
