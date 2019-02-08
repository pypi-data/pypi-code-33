# -*- coding: utf-8 -*-
"""
module flow_layer.py
--------------------
Base flow layer class.
"""
import tensorflow as tf
layers = tf.keras.layers


class FlowLayer(layers.Layer):
    """
    A base class used to define layers for neural network.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialization function.
        :param *args: `tf.keras.Layer` args;
        :param **kwargs: `tf.keras.Layer` kwargs;
        """
        super(FlowLayer, self).__init__(*args, **kwargs)

    def build(self, input_shape):
        """Creates the variables of the layer."""
        # a list of all object attributes
        property_names = dir(self)
        # foreach attribute name
        for p_name in property_names:
            # filter the public attributes
            if not p_name.startswith('_'):
                try:
                    prop = getattr(self, p_name)
                    # filters sub layers objects
                    if isinstance(prop, layers.Layer):
                        for variable in prop.weights:
                            if variable.trainable:
                                self._trainable_weights.append(variable)
                            else:
                                self._non_trainable_weights.append(variable)
                except AttributeError:
                    pass

        super(FlowLayer,self).build(input_shape)

    def __call__(self, *args, **kwargs):
        outputs = super().__call__(*args, **kwargs)

        if isinstance(outputs, (tuple, list,)):
            for out in outputs:
                out.__dict__["_connectivity"] = self
        else:
            outputs.__dict__["_connectivity"] = self
        return outputs