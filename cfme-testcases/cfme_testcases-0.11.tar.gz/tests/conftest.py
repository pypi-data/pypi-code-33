# encoding: utf-8
# pylint: disable=missing-docstring,no-self-use

from __future__ import unicode_literals

import copy
import io
import logging
import os
from collections import OrderedDict

import pytest
import yaml

from tests import conf


# pylint: disable=invalid-name
def ordered_load(stream, Loader=yaml.Loader):  # noqa: N803
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return OrderedDict(loader.construct_pairs(node))

    OrderedLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)

    return yaml.load(stream, OrderedLoader)


def get_config():
    conf_file = os.path.join(conf.DATA_PATH, "polarion_tools.yaml")
    with io.open(conf_file, encoding="utf-8") as input_file:
        return ordered_load(input_file)


_config = get_config()


@pytest.fixture(scope="function")
def config():
    return copy.deepcopy(_config)


@pytest.fixture(scope="module")
def config_modulescope():
    return copy.deepcopy(_config)


class SimpleFormatter(object):
    def format(self, record):
        message = record.getMessage()
        if isinstance(message, bytes):
            message = message.decode("utf-8")
        return message


@pytest.yield_fixture
def captured_log():
    buff = io.StringIO()
    handler = logging.StreamHandler(buff)
    handler.setFormatter(SimpleFormatter())

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    yield buff

    logger.handlers.remove(handler)
