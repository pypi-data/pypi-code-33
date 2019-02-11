# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Accelerate deep neural networks on FPGAs with Project Brainwave."""
from .brainwave_image import BrainwaveImage
from .brainwave_webservice import BrainwaveWebservice
from azureml._base_sdk_common import __version__ as VERSION

try:
    import tensorflow as tf

    tf_version = str.split(tf.VERSION, '.')
    tf_version_ints = [int(x) for x in tf_version]
    assert tf_version_ints[0] == 1
    assert 6 <= tf_version_ints[1]
except ImportError as e:
    raise Exception("azureml-contrib-brainwave {} requires tensorflow>=1.6<=1.10 - install it".format(VERSION))
except AssertionError as e:
    raise Exception("azureml-contrib-brainwave {} requires tensorflow>=1.6<=1.10 and you have {}"
                    .format(VERSION, tf.VERSION))


__all__ = ["BrainwaveWebservice", "BrainwaveImage"]
