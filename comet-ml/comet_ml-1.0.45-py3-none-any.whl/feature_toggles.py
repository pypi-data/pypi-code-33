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

"""
Author: Boris Feld

This module contains feature toggles related code

"""

from .config import get_config


class FeatureToggles(object):
    """ Feature Toggle helper class, avoid getting a feature toggle without
    fallbacking on the default value. Also read environment variables for
    overrides.
    """

    def __init__(self, raw_toggles, config):
        self.raw_toggles = raw_toggles
        self.config = config

    def __eq__(self, other):
        if isinstance(other, FeatureToggles):
            return self.raw_toggles == other.raw_toggles

        return False

    def __getitem__(self, name):
        try:
            override_value = self.config["comet.override_feature.%s" % name]
            if override_value is not None:
                return override_value

        except KeyError:
            pass

        return self.raw_toggles.get(name, False)


def get_feature_toggle_overrides():
    result = {}
    config = get_config()
    for ft in FT_LIST:
        override_value = config["comet.override_feature.%s" % ft]
        if override_value is not None:
            result[ft] = override_value

    return result


# Constants defining feature toggles names to avoid typos disabling a feature

GPU_MONITOR = "sdk_gpu_monitor"
GIT_PATCH = "sdk_git_patch"
HTTP_LOGGING = "sdk_http_logging"

FT_LIST = [GPU_MONITOR, GIT_PATCH, HTTP_LOGGING]
