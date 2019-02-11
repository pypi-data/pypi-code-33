# Copyright (C) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in project root for information.
"""Init for standard AutoML modules."""

from automl.client.core.common.datasets import ClientDatasets
__all__ = []

try:
    from ._version import ver
    __version__ = ver
except ImportError:
    __version__ = '0.0.0+dev'
