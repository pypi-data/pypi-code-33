################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from __future__ import print_function
import requests
from watson_machine_learning_client.utils import DEFINITION_DETAILS_TYPE, INSTANCE_DETAILS_TYPE, STR_TYPE, STR_TYPE_NAME, docstring_parameter, meta_props_str_conv, str_type_conv, get_file_from_cos
from watson_machine_learning_client.metanames import ModelDefinitionMetaNames
from watson_machine_learning_client.wml_resource import WMLResource

_DEFAULT_LIST_LENGTH = 50


class Definitions(WMLResource):
    """
    Store and manage your definitions.
    """
    ConfigurationMetaNames = ModelDefinitionMetaNames()
    """MetaNames for definitions creation."""

    def __init__(self, client):
        WMLResource.__init__(self, __name__, client)
        if not client.ICP:
            Definitions._validate_type(client.service_instance.details, u'instance_details', dict, True)
            Definitions._validate_type_of_details(client.service_instance.details, INSTANCE_DETAILS_TYPE)
        self._ICP = client.ICP

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def store(self, training_definition, meta_props):
        """
            Store training definition.

            :param training_definition:  path to zipped model_definition
            :type training_definition: {str_type}

            :param meta_props: meta data of the training definition. To see available meta names use:

               >>> client.definitions.ConfigurationMetaNames.get()
            :type meta_props: dict


            :returns: stored training definition details
            :rtype: dict

            A way you might use me is:

            >>> metadata = {
            >>>  client.definitions.ConfigurationMetaNames.NAME: 'my_training_definition',
            >>>  client.definitions.ConfigurationMetaNames.FRAMEWORK_NAME: 'tensorflow',
            >>>  client.definitions.ConfigurationMetaNames.FRAMEWORK_VERSION: '1.5',
            >>>  client.definitions.ConfigurationMetaNames.RUNTIME_NAME: 'python',
            >>>  client.definitions.ConfigurationMetaNames.RUNTIME_VERSION: '3.5',
            >>>  client.definitions.ConfigurationMetaNames.EXECUTION_COMMAND: 'python3 tensorflow_mnist_softmax.py --trainingIters 20'
            >>> }
            >>> definition_details = client.definitions.store(training_definition_filepath, meta_props=metadata)
            >>> definition_url = client.definitions.get_url(definition_details)
        """

        # quick support for COS credentials instead of local path
        # TODO add error handling and cleaning (remove the file)
        if type(training_definition) is dict:
            training_definition = get_file_from_cos(training_definition)

        training_definition = str_type_conv(training_definition)
        Definitions._validate_type(training_definition, u'training_definition', STR_TYPE, True)
        Definitions._validate_type(meta_props, u'meta_props', dict, True)
        meta_props_str_conv(meta_props)

        # TODO to be replaced with repository client

        if not self._ICP:
            response_definition_post = requests.post(
                self._href_definitions.get_definitions_href(),
                json=self.ConfigurationMetaNames._generate_resource_metadata(meta_props, with_validation=True),
                headers=self._client._get_headers()
            )
        else:
            response_definition_post = requests.post(
                self._href_definitions.get_definitions_href(),
                json=self.ConfigurationMetaNames._generate_resource_metadata(meta_props, with_validation=True),
                headers=self._client._get_headers(),
                verify=False
            )

        details = self._handle_response(201, u'saving model definition', response_definition_post)

        definition_version_content_url = details[u'entity'][u'training_definition_version'][u'content_url']

        # save model definition content
        put_header = self._client._get_headers(no_content_type=True)
        with open(training_definition, 'rb') as data:
            if not self._ICP:
                response_definition_put = requests.put(definition_version_content_url, data=data, headers=put_header)
            else:
                response_definition_put = requests.put(definition_version_content_url, data=data, headers=put_header, verify=False)
        self._handle_response(200, u'saving model definition content', response_definition_put)

        return details

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete(self, definition_uid):
        """
            Delete definition.

            :param definition_uid: definition UID
            :type definition_uid: {str_type}

            A way you might use me is:

            >>> client.definitions.delete(definition_uid)
        """
        definition_uid = str_type_conv(definition_uid)
        Definitions._validate_type(definition_uid, u'definition_uid', STR_TYPE, True)

        definition_endpoint = self._href_definitions.get_definition_href(definition_uid)
        if not self._ICP:
            response_delete = requests.delete(definition_endpoint, headers=self._client._get_headers())
        else:
            response_delete = requests.delete(definition_endpoint, headers=self._client._get_headers(), verify=False)

        self._handle_response(204, u'model definition deletion', response_delete, False)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_details(self, definition_uid=None, limit=None):
        """
            Get metadata of stored definitions. If definition uid is not specified returns all model definitions metadata.

            :param definition_uid:  stored model definition UID (optional)
            :type definition_uid: {str_type}

            :param limit: limit number of fetched records (optional)
            :type limit: int

            :returns: stored definition(s) metadata
            :rtype: dict

            A way you might use me is:

            >>> definition_details = client.definitions.get_details(definition_uid)
            >>> definition_details = client.definitions.get_details()
         """
        definition_uid = str_type_conv(definition_uid)
        Definitions._validate_type(definition_uid, u'definition_uid', STR_TYPE, False)
        Definitions._validate_type(limit, u'limit', int, False)

        url = self._href_definitions.get_definitions_href()

        return self._get_artifact_details(url, definition_uid, limit, 'definitions')

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_url(definition_details):
        """
            Get url of stored definition.

            :param definition_details:  stored definition details
            :type definition_details: dict

            :returns: url of stored definition
            :rtype: {str_type}

            A way you might use me is:

            >>> definition_url = client.definitions.get_url(definition_details)
        """
        Definitions._validate_type(definition_details, u'definition_details', object, True)
        Definitions._validate_type_of_details(definition_details, DEFINITION_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(definition_details, u'definition_details', [u'metadata', u'url'])

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def _get_version_url(definition_details):
        """
            Get url of stored definition version.

            :param definition_details:  stored definition details
            :type definition_details: dict

            :returns: url of stored definition version
            :rtype: {str_type}

            A way you might use me is:

            >>> definition_version_url = client.definitions.get_version_url(definition_details)
        """
        Definitions._validate_type(definition_details, u'definition_details', object, True)
        Definitions._validate_type_of_details(definition_details, DEFINITION_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(definition_details, 'definition_details', ['entity', 'training_definition_version', 'url'])

    @staticmethod
    def get_uid(definition_details):
        """
            Get uid of stored definition.

            :param definition_details: stored definition details
            :type definition_details: dict

            :returns: uid of stored model
            :rtype: str

            A way you might use me is:

            >>> definition_uid = client.definitions.get_uid(definition_details)
        """
        Definitions._validate_type(definition_details, u'definition_details', object, True)
        Definitions._validate_type_of_details(definition_details, DEFINITION_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(definition_details, u'definition_details', [u'metadata', u'guid'])

    def list(self, limit=None):
        """
           List stored definitions. If limit is set to None there will be only first 50 records shown.

           :param limit: limit number of fetched records (optional)
           :type limit: int

           A way you might use me is

           >>> client.definitions.list()
        """
        definition_resources = self.get_details(limit=limit)[u'resources']
        definition_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'],m[u'entity'][u'framework'][u'name']) for m in definition_resources]

        self._list(definition_values, [u'GUID', u'NAME', u'CREATED', u'FRAMEWORK'], limit, _DEFAULT_LIST_LENGTH)