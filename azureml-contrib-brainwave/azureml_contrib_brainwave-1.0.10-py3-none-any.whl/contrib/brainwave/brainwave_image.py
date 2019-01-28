# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Create a package to accelerate Neural Networks with Project Brainwave."""

import copy
import json
from pkg_resources import resource_string

from azureml._model_management._constants import FPGA_IMAGE_TYPE, FPGA_IMAGE_FLAVOR
from azureml.core.image import Image
from azureml.core.image.image import ImageConfig


realtimeai_image_payload_template = json.loads(resource_string(__name__,
                                                               'data/brainwave_image_payload_template.json')
                                               .decode('ascii'))


class BrainwaveImage(Image):
    """Project Brainwave image representing a package that can be deployed with hardware acceleration."""

    _image_type = FPGA_IMAGE_TYPE
    _image_flavor = FPGA_IMAGE_FLAVOR

    # _expected_payload_keys is inherited from the parent class Image

    def _initialize(self, workspace, obj_dict):
        """Initialize the BrainwaveImage object.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param obj_dict:
        :type obj_dict: dict
        :return:
        :rtype: None
        :raises: None
        """
        super(BrainwaveImage, self)._initialize(workspace, obj_dict)
        self.image_flavor = BrainwaveImage._image_flavor

    @staticmethod
    def image_configuration(tags=None, properties=None, description=None):
        """Create an image configuration object."""
        return BrainwaveImageConfiguration(tags, properties, description)

    def run(self):
        """Test an image locally.

        This does not apply to brainwave images,
        since they require dedicated hardware to accelerate neural networks.

        :raises: NotImplementedError
        """
        raise NotImplementedError("Can't run brainwave images locally.")


class BrainwaveImageConfiguration(ImageConfig):
    """Image configuration object for brainwave services."""

    _can_deploy = True

    def __init__(self, tags=None, properties=None, description=None):
        """Create image configuration object.

        :param tags: Dictionary of key value tags to give this image
        :type tags: dict[str, str]
        :param properties: Dictionary of key value properties to give this image. These properties cannot
            be changed after deployment, however new key value pairs can be added
        :type properties: dict[str, str]
        :param description: A description to give this image
        :type description: str
        :return: A configuration object to use when creating the image
        :rtype: azureml.contrib.brainwave.BrainwaveImageConfiguration
        :raises: azureml.exceptions.WebserviceException
        """
        self.tags = tags
        self.properties = properties
        self.description = description
        self.validate_configuration()

    def validate_configuration(self):
        """Check that the specified configuration values are valid.

        Will raise a WebserviceException if validation fails.
        """
        pass

    def build_create_payload(self, workspace, name, model_ids):
        """Build the creation payload associated with this configuration object.

        :param workspace: The workspace associated with the image
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name of the image
        :type name: str
        :param model_ids: A list of model IDs to be packaged with the image
        :type model_ids: list[str]
        :return: The creation payload to use for Image creation
        :rtype: dict
        """
        if model_ids is None:
            raise ValueError("Cannot create RealtimeAi image without model")
        json_payload = copy.deepcopy(realtimeai_image_payload_template)
        json_payload['name'] = name
        json_payload['kvTags'] = self.tags
        json_payload['properties'] = self.properties
        json_payload['description'] = self.description
        json_payload['modelIds'] = model_ids
        return json_payload
