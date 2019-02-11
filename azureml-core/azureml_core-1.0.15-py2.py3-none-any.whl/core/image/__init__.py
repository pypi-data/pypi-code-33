# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""This package is used for managing the images you create with Azure Machine Learning service."""

from azureml._base_sdk_common import __version__ as VERSION
from .image import Image
from .container import ContainerImage
from .unknown_image import UnknownImage


__version__ = VERSION

__all__ = [
    'Image',
    'ContainerImage',
    'UnknownImage'
]
