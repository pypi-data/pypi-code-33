# -*- coding: utf8 -*-
from self_update.sdk_version import get_version

package = 'missinglink'


def get_missinglink_cli_version():
    return get_version(package)


def get_missinglink_package():
    return package
