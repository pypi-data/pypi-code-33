# -*- coding: utf-8 -*-
"""
module model.py
--------------------
Definition of the machine learning model for the task.
"""
import tensorflow as tf
import numpy as np
from blinker import signal

class Inputs(object):
    def __init__(self):
        pass


class Outputs(object):
    def __init__(self):
        pass

class Model(object):
    """ Project main class.
    """
    def __init__(self, inputs, outputs=None):
        """Main module initialization."""

        self.inputs = inputs
        # set in _ get_model
        if outputs is None:
            self.outputs = Outputs()
        else:
            self.outputs = outputs

        # outputs and model initialization
        self.get_model_spec()

    def get_model_spec(self, *args, **kwargs):
        """
        Layers and model definition
        :return: a compiled model
        """
        pass