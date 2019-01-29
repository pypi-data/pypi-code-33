# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

import calendar
import logging
import time
import os
from datetime import datetime

import six

LOGGER = logging.getLogger(__name__)


def is_iterable(value):
    try:
        iter(value)
        return True

    except TypeError:
        return False


def is_list_like(value):
    """ Check if the value is a list-like
    """
    if is_iterable(value) and not isinstance(value, six.string_types):
        return True

    else:
        return False


def to_utf8(str_or_bytes):
    if hasattr(str_or_bytes, "decode"):
        return str_or_bytes.decode("utf-8", errors="replace")

    return str_or_bytes


def local_timestamp():
    """ Return a timestamp in a format expected by the backend (milliseconds)
    """
    now = datetime.utcnow()
    timestamp_in_seconds = calendar.timegm(now.timetuple()) + (now.microsecond / 1e6)
    timestamp_in_milliseconds = int(timestamp_in_seconds * 1000)
    return timestamp_in_milliseconds


def wait_for_empty(check_function, timeout, verbose=False, sleep_time=1):
    """ Wait up to TIMEOUT seconds for the messages queue to be empty
    """
    end_time = time.time() + timeout

    while check_function() is False and time.time() < end_time:
        if verbose is True:
            LOGGER.info("Still uploading")
        time.sleep(sleep_time)

def read_unix_packages():
    package_status_file = "/var/lib/dpkg/status"
    if os.path.isfile(package_status_file):
        with open(package_status_file, "r") as f:
            status = f.read()
        package = None
        os_packages = []
        for line in status.split("\n"):
            if line.startswith("Package: "):
                package = line[9:]
            if line.startswith("Version: "):
                version = line[9:]
                if package is not None:
                    os_packages.append((package, version))
                package = None
        os_packages_list = sorted(
            [("%s=%s" % (package, version))
             for (package, version) in os_packages]
        )
        return os_packages_list
    else:
        return None
