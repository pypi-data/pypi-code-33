# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains automated machine learning modules.

Included classes provide resources for configuring, managing pipelines, and examining run output
for Automated Machine Learning experiments.
"""
import os
import sys

vendor_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "_vendor"))
sys.path.append(vendor_folder)

from automl.client.core.common.utilities import extract_user_data, get_sdk_dependencies

from .automl import fit_pipeline
from .automlconfig import AutoMLConfig

__all__ = [
    'AutoMLConfig',
    'fit_pipeline',
    'extract_user_data',
    'get_sdk_dependencies']

try:
    from ._version import ver as VERSION
    __version__ = VERSION
except ImportError:
    VERSION = '0.0.0+dev'
    __version__ = VERSION
