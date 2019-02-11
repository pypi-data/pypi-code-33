# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deploy GRPC web services accelerated with Project Brainwave."""

import requests
from azureml.contrib.brainwave import BrainwaveImage
from azureml._model_management._constants import MMS_WORKSPACE_API_VERSION
from azureml._model_management._constants import MMS_SYNC_TIMEOUT_SECONDS
from azureml.core.webservice import Webservice
from azureml.core.webservice.webservice import WebserviceDeploymentConfiguration
from azureml.exceptions import WebserviceException
import json
from pkg_resources import resource_string
from re import findall
import warnings
import numpy as np
import os

realtimeai_service_payload_template = json.loads(resource_string(__name__,
                                                                 'data/brainwave_service_payload_template.json')
                                                 .decode('ascii'))
try:
    from .client import PredictionClient
except ImportError:
    warnings.warn("Tensorflow not imported, can't use Run", ImportWarning)


class BrainwaveWebservice(Webservice):
    """Class for AzureML RealTimeAI Webservices."""

    _expected_payload_keys = Webservice._expected_payload_keys + ['ipAddress', 'numReplicas', 'port', 'sslEnabled']
    _webservice_type = 'FPGA'

    def _initialize(self, workspace, obj_dict):
        """
        Initialize Webservice.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param obj_dict:
        :type obj_dict: dict
        :return:
        :rtype: None
        """
        # Validate obj_dict with _expected_payload_keys
        BrainwaveWebservice._validate_get_payload(obj_dict)

        # Initialize common Webservice attributes
        super(BrainwaveWebservice, self)._initialize(workspace, obj_dict)

        # Initialize expected BrainwaveWebservice specific attributes
        self.ip_address = obj_dict['ipAddress']
        self.num_replicas = obj_dict['numReplicas']
        self.port = obj_dict['port']
        self.scoring_uri = "{}:{}".format(self.ip_address, self.port)
        self.ssl = obj_dict['sslEnabled']

        # Initialize other Brainwave utility attributes
        self.client = None

    @staticmethod
    def deploy_configuration(num_replicas=None,
                             tags=None,
                             properties=None,
                             description=None,
                             ssl_enabled=False,
                             ssl_cert_pem_file=None,
                             ssl_key_pem_file=None):
        """
        Create deployment configuration for BrainwaveWebservices.

        :param properties:
        :param ssl_enabled:
        :type ssn_enabled: bool
        :param ssl_cert_pem_file:
        :type ssl_cert_pem_file: str | Path
        :param ssl_key_pem_file:
        :type ssl_key_pem_file: str | Path
        :param num_replicas:
        :type num_replicas: int
        :param tags:
        :type tags: list[str]
        :param description:
        :type description: str
        """
        config = RealTimeAIWebserviceDeploymentConfiguration(num_replicas=num_replicas,
                                                             tags=tags,
                                                             properties=properties,
                                                             description=description,
                                                             ssl_enabled=ssl_enabled,
                                                             ssl_cert_pem_file=ssl_cert_pem_file,
                                                             ssl_key_pem_file=ssl_key_pem_file)
        return config

    @staticmethod
    def _deploy(workspace, name, image, deployment_config):
        """
        Deploy the webservice.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param name:
        :type name: str
        :param image:
        :type image: azureml.core.image.Image
        :param deployment_config:
        :type deployment_config: RealTimeAIWebserviceDeploymentConfiguration
        :return:
        :rtype: BrainwaveWebservice
        """
        if not deployment_config:
            raise ValueError('deployment_config')
        if not image:
            raise ValueError('image not defined')
        deployment_config.validate_image(image)
        create_payload = BrainwaveWebservice._build_create_payload(name, deployment_config, image)
        try:
            return Webservice._deploy_webservice(workspace, name, create_payload, BrainwaveWebservice)
        except WebserviceException as e:
            error_message = ""
            if hasattr(e, "status_code") and e.status_code == 412:
                error_message = "This workspace does not have enough quota for FPGA service creation." + \
                                "To request quota for the first time or request additional quota, follow this link" + \
                                " (https://aka.ms/aml-real-time-ai-request). "
            # If the request ID was found, add it to the error message
            request_id = findall(r"'x-ms-client-request-id': '([a-zA-Z\d]*)'", e.message)
            if len(request_id) > 0:
                error_message = "{0}For more information on this error, contact Microsoft Support or get help on the" \
                                " Azure ML forum (https://aka.ms/aml-forum) with the request ID <{1}>." \
                    .format(error_message, request_id[0])
            if error_message:
                raise WebserviceException(e.message + "\n\n" + error_message)
            raise

    @staticmethod
    def _build_create_payload(name, deploy_config, image):
        """
         Create the payload.

        :param name:
        :type name: str
        :param deploy_config:
        :type deploy_config: RealTimeAIWebserviceDeploymentConfiguration
        :param image:
        :type image: azureml.core.Image
        :return:
        :rtype: dict
        """
        import copy
        json_payload = copy.deepcopy(realtimeai_service_payload_template)
        json_payload['name'] = name
        json_payload['kvTags'] = deploy_config.tags
        json_payload['properties'] = deploy_config.properties
        json_payload['description'] = deploy_config.description
        json_payload['numReplicas'] = deploy_config.num_replicas
        json_payload['sslEnabled'] = deploy_config.ssl_enabled
        if deploy_config.ssl_enabled:
            with open(deploy_config.ssl_cert_pem_file, 'r') as cert_file:
                cert_data = cert_file.read()
            json_payload['sslCertificate'] = cert_data
            with open(deploy_config.ssl_key_pem_file, 'r') as key_file:
                key_data = key_file.read()
            json_payload['sslKey'] = key_data
        else:
            del (json_payload['sslCertificate'])
            del (json_payload['sslKey'])
        json_payload['imageId'] = image.id
        return json_payload

    def run(self, input_data):
        """
        Run the webservice.

        :param input_data:
        :type input_data: File | np.array | Path to image
        :return:
        """
        if self.ssl:
            raise NotImplementedError("Use azureml.contrib.brainwave.client.PredictionClient directly with the"
                                      "FullyQualified domain name of the service")
        if self.client is None:
            self.client = PredictionClient(self.ip_address, self.port, False, "")
        if isinstance(input_data, str):
            return self.client.score_image(input_data)
        if isinstance(input_data, np.ndarray):
            return self.client.score_numpy_array(input_data)
        return self.client.score_file(input_data.read())

    def update(self, image=None, num_replicas=None, tags=None, description=None, ssl_enabled=None,
               ssl_certificate=None, ssl_key=None):
        """
        Update the webservice.

        :param num_replicas:
        :type num_replicas: int
        :param ssl_key:
        :type ssl_key: str
        :param ssl_certificate:
        :type ssl_certificate: str
        :param ssl_enabled:
        :type ssl_enabled: bool | None
        :param image:
        :type image: BrainwaveImage
        :param tags:
        :type tags: list[str]
        :param description:
        :type description: str
        :return:
        :rtype: None
        """
        if tags is None and not description and not image and ssl_enabled is None and not num_replicas:
            raise WebserviceException('No parameters provided to update.')

        if ssl_enabled and (ssl_certificate is None or ssl_key is None):
            raise ValueError("Must provide certificate and key if SSL is enabled")

        headers = {'Content-Type': 'application/json-patch+json'}
        headers.update(self._auth.get_authentication_header())
        params = {'api-version': MMS_WORKSPACE_API_VERSION}

        patch_list = []
        if image:
            patch_list.append({'op': 'replace', 'path': '/imageId', 'value': image.id})
        if num_replicas:
            patch_list.append({'op': 'replace', 'path': '/numReplicas', 'value': num_replicas})
        if tags is not None:
            patch_list.append({'op': 'replace', 'path': '/kvTags', 'value': tags})
        if description:
            patch_list.append({'op': 'replace', 'path': '/description', 'value': description})

        if ssl_enabled:
            patch_list.append({'op': 'replace', 'path': '/sslEnabled', 'value': True})
            patch_list.append({'op': 'replace', 'path': '/sslCertificate', 'value': ssl_certificate})
            patch_list.append({'op': 'replace', 'path': '/sslKey', 'value': ssl_key})
        if ssl_enabled is False:
            patch_list.append({'op': 'replace', 'path': '/sslEnabled', 'value': False})
            patch_list.append({'op': 'remove', 'path': '/sslCertificate'})
            patch_list.append({'op': 'remove', 'path': '/sslKey'})

        resp = requests.patch(self._mms_endpoint, headers=headers, params=params, json=patch_list,
                              timeout=MMS_SYNC_TIMEOUT_SECONDS)

        if resp.status_code == 200:
            self.update_deployment_state()
        else:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content))

    def serialize(self):
        """Convert this Webservice into a json serialized dictionary.

        :return: The json representation of this Webservice
        :rtype: dict
        """
        properties = super(BrainwaveWebservice, self).serialize()
        rt_properties = {'numReplicas': self.num_replicas}
        properties.update(rt_properties)
        return properties


class RealTimeAIWebserviceDeploymentConfiguration(WebserviceDeploymentConfiguration):
    """Service deployment configuration object for Brainwave services."""

    def __init__(self, num_replicas=None, tags=None, properties=None, description=None, ssl_enabled=False,
                 ssl_cert_pem_file=None, ssl_key_pem_file=None):
        """
        Create deployment configuration.

        :param num_replicas:
        :type num_replicas: int
        :param tags:
        :type tags: list[str]
        :param properties:
        :type properties: list[str]
        :param description:
        :type description: str
        :param ssl_enabled:
        :type ssl_enabled: boolean
        :param ssl_cert_pem_file:
        :type ssl_cert_pem_file: str
        :param ssl_key_pem_file:
        :type ssl_key_pem_file: str
        """
        super(RealTimeAIWebserviceDeploymentConfiguration, self).__init__(BrainwaveWebservice)
        self.num_replicas = num_replicas if num_replicas is not None else 1
        self.tags = tags
        self.description = description
        self.ssl_enabled = ssl_enabled
        self.ssl_cert_pem_file = ssl_cert_pem_file
        self.ssl_key_pem_file = ssl_key_pem_file
        self.properties = properties
        self.validate_configuration()

    def validate_configuration(self):
        """Check that the specified configuration values are valid.

        Will raise a WebserviceException if validation fails.

        :raises: WebserviceException
        """
        if self.num_replicas and self.num_replicas <= 0:
            raise WebserviceException('Invalid configuration, num_replicas must be positive.')
        if (self.ssl_key_pem_file or self.ssl_cert_pem_file) and not self.ssl_enabled:
            raise WebserviceException('Invalid configuration, can only pass certificate and key if ssl is enabled')
        if self.ssl_enabled and not (self.ssl_key_pem_file and self.ssl_cert_pem_file):
            raise WebserviceException('Invalid configuration, cannot enable SSL without certificate and key')
        if self.ssl_enabled and \
                (not os.path.isfile(self.ssl_key_pem_file) or not os.path.isfile(self.ssl_cert_pem_file)):
            raise FileNotFoundError("SSL cert or key don't exist")

    @classmethod
    def validate_image(cls, image):
        """Check that the image that is being deployed to the webservice is valid.

        Will raise a WebserviceException if validation fails.

        :param image: The image that will be deployed to the webservice.
        :raises: WebserviceException
        """
        if not isinstance(image, BrainwaveImage):
            raise WebserviceException("Can only deploy Brainwave web service from a BrainwaveImage")
        if image.creation_state != 'Succeeded':
            raise WebserviceException('Unable to create service with image {} in non "Succeeded" state'
                                      .format(image.id))
