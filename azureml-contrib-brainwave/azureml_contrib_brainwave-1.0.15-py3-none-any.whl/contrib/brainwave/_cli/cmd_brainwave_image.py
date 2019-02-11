# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Handle BrainwaveImage CLI commands."""

import json

from azureml._cli_common.cli_workspace import get_workspace
from azureml._cli_common.ml_cli_error import MlCliError
from azureml.core.image import Image
from azureml.core.model import Model
from azureml.contrib.brainwave.brainwave_image import BrainwaveImage
from azureml._model_management._constants import MODEL_METADATA_FILE_ID_KEY, IMAGE_METADATA_FILE_ID_KEY,\
    CLI_METADATA_FILE_WORKSPACE_KEY, CLI_METADATA_FILE_RG_KEY


def image_create_brainwavepackage_container(image_name, image_description, model, model_metadata_file, tags,
                                            properties, output_metadata_file, workspace_name,
                                            resource_group, no_wait_flag, verbose, open_fn=open):
    """
    Create Brainwave image.

    :param image_name:
    :param image_description:
    :param model:
    :param model_metadata_file:
    :param tags:
    :param properties:
    :param output_metadata_file:
    :param workspace_name:
    :param resource_group:
    :param no_wait_flag:
    :param verbose:
    :param open_fn:
    :return:
    """
    workspace = get_workspace(workspace_name, resource_group)
    tags_dict = None
    if tags:
        tags_dict = dict()
        for tag in tags:
            if '=' not in tag:
                raise MlCliError('Error, tags must be entered in the following format: key=value')
            key, value = tag.partition("=")[::2]
            tags_dict[key] = value

    properties_dict = None
    if properties:
        properties_dict = dict()
        for prop in properties:
            if '=' not in prop:
                raise MlCliError('Error, properties must be entered in the following format: key=value')
            key, value = prop.partition("=")[::2]
            properties_dict[key] = value

    if model_metadata_file:
        if model:
            raise MlCliError('Brainwave images only support a single model, please specify either --model or '
                             '--model-metadata-file, not both.')
        with open(model_metadata_file, 'r') as infile:
            model_metadata = json.load(infile)
            if model_metadata[CLI_METADATA_FILE_WORKSPACE_KEY] != workspace.name or \
                    model_metadata[CLI_METADATA_FILE_RG_KEY] != workspace.resource_group:
                raise MlCliError('Model metadata file "{}" contains information for a model in a workspace that '
                                 'does not match the one provided for Image creation. If the model specified in '
                                 'the file is intended to be used, please either register it in the workspace '
                                 'provided to this command, or specify the corresponding workspace to this '
                                 'command.'.format(model_metadata_file))
            model = Model(workspace, model_metadata[MODEL_METADATA_FILE_ID_KEY])

    models = [model] if model else None

    image_config = BrainwaveImage.image_configuration(tags_dict, properties_dict, image_description)
    image = Image.create(workspace, image_name, models, image_config)
    image.wait_for_creation(verbose)

    if output_metadata_file:
        image_metadata = {IMAGE_METADATA_FILE_ID_KEY: image.id, CLI_METADATA_FILE_WORKSPACE_KEY: workspace_name,
                          CLI_METADATA_FILE_RG_KEY: resource_group}

        with open_fn(output_metadata_file, 'w') as outfile:
            json.dump(image_metadata, outfile)

        print("Wrote JSON metadata to {}".format(output_metadata_file))

    if no_wait_flag:
        print('Image may take a few minutes to be created.')
        print('To see if your image is ready to use, run:')
        print('  az ml image show -n {}'.format(image.name))
    else:
        image.wait_for_creation(verbose)

        if image.creation_state.lower() != 'succeeded':
            raise MlCliError('Polling for Image creation ended in "{}" state. More information can be found here: {}\n'
                             'Image ID: {}\n'
                             'Workspace Name: {}\n'
                             'Resource Group: {}'.format(image.creation_state, image.image_build_log_uri, image.id,
                                                         workspace_name, resource_group))

        print('Image ID: {}'.format(image.id))
        print('More details: \'az ml image show -i {}\''.format(image.id))

    return image.serialize(), verbose
