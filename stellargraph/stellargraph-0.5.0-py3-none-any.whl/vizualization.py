from keras import models
from keras import Model, optimizers, losses
from keras import backend as K, Input
from keras.layers import (
    Layer,
    Lambda,
    Dropout,
    Reshape,
    Dense,
    Concatenate,
    AveragePooling1D,
)
from keras.models import Sequential
import pydot


def keras_model_to_dot(model, show_shapes=False, show_layer_names=True, rankdir="TB"):
    """Convert a Keras model to dot format.

    # Arguments
        model: A Keras model instance.
        show_shapes: whether to display shape information.
        show_layer_names: whether to display layer names.
        rankdir: `rankdir` argument passed to PyDot,
            a string specifying the format of the plot:
            'TB' creates a vertical plot;
            'LR' creates a horizontal plot.

    # Returns
        A `pydot.Dot` instance representing the Keras model.
    """

    dot = pydot.Dot()
    dot.set("rankdir", rankdir)
    dot.set("concentrate", True)
    dot.set_node_defaults(shape="record")

    if isinstance(model, Sequential):
        if not model.built:
            model.build()
    layers = model.layers

    # Create graph nodes.
    for layer in layers:
        layer_id = str(id(layer))

        for i, node in enumerate(layer._inbound_nodes):
            node_key = layer.name + "-" + str(i)

        # Append a wrapped layer's label to node's label, if it exists.
        layer_name = layer.name
        class_name = layer.__class__.__name__
        layer_label = "{}: {}".format(layer_name, class_name)

        # Use inbound nodes as real nodes
        prev_node_key = None
        for i, node in enumerate(layer._inbound_nodes):
            node_key = layer.name + "-" + str(i)

            outputlabels = ", ".join([str(s[1:]) for s in node.output_shapes])
            inputlabels = ", ".join([str(s[1:]) for s in node.input_shapes])
            label = "%s|{input:|output:}|{{%s}|{%s}}" % (
                node_key,
                inputlabels,
                outputlabels,
            )
            print(node_key, label)
            node = pydot.Node(node_key, label=label)
            dot.add_node(node)

            # Add edge between node sub-layers
            if prev_node_key:
                dot.add_edge(
                    pydot.Edge(node_key, prev_node_key, style="dashed", arrowhead="dot")
                )
            prev_node_key = node_key

    # Connect nodes with edges.
    for layer in layers:
        layer_id = str(id(layer))
        for i, node in enumerate(layer._inbound_nodes):
            node_key_ob = layer.name + "-" + str(i)
            config = node.get_config()
            if isinstance(config, dict):
                config = [config]
            for c in config:
                layer_ob = c["outbound_layer"]
                layers_ib = c["inbound_layers"]
                indices_ib = c["node_indices"]

                for l_ib, i_ib in zip(layers_ib, indices_ib):
                    node_key_in = l_ib + "-" + str(i_ib)
                    dot.add_edge(pydot.Edge(node_key_in, node_key_ob))
    return dot
