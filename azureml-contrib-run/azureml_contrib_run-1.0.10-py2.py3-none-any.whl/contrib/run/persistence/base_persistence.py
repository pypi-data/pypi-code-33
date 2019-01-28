# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""generic persistence functions."""
import os

AML_MODELDATA_EXTENSION = ".modeldata.aml"


def save_model_generic(model, model_path, model_handlers):
    """Extensible function to run save model operation and other operations such as saving modeldata.

    :param model:
    :param model_path: path is inside outputs/ directory
    :param model_handlers: list of functions with signature (model, model_path) -> output
    :return: list of outputs
    """
    outputs = []
    for handler in model_handlers:
        # possible to add exception logic
        output = handler(model, model_path)
        outputs.append(output)

    return outputs


def create_default_modeldata_path(model_path):
    """Add modeldata extension."""
    modeldata_path = "{0}{1}".format(model_path, AML_MODELDATA_EXTENSION)
    return modeldata_path


def check_has_path(path, description, additional_description=None):
    """Check path exists."""
    if not os.path.exists(path):
        message = "{} does not exist: {}".format(
            description, os.path.abspath(path))
        if additional_description:
            message += "\n{}".format(additional_description)
        raise Exception(message)
