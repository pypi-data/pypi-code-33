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
import json
import re
from watson_machine_learning_client.utils import print_text_header_h1, print_text_header_h2, TRAINING_RUN_DETAILS_TYPE, STR_TYPE, STR_TYPE_NAME, docstring_parameter, str_type_conv, meta_props_str_conv, group_metrics, StatusLogger
import time
from watson_machine_learning_client.metanames import TrainingConfigurationMetaNames
from watson_machine_learning_client.wml_client_error import WMLClientError
from watson_machine_learning_client.href_definitions import is_uid
from watson_machine_learning_client.wml_resource import WMLResource


class Training(WMLResource):
    """
       Train new models.
    """

    def __init__(self, client):
        WMLResource.__init__(self, __name__, client)
        self.ConfigurationMetaNames = TrainingConfigurationMetaNames()

    @staticmethod
    def _is_training_uid(s):
        res = re.match('training\-[a-zA-Z0-9\-\_]+', s)
        return res is not None

    @staticmethod
    def _is_training_url(s):
        res = re.match('\/v3\/models\/training\-[a-zA-Z0-9\-\_]+', s)
        return res is not None

    def get_frameworks(self):
        """
           Get list of supported frameworks.

           :returns: supported frameworks for training
           :rtype: json

           A way you might use me is:

           >>> model_details = client.training.get_frameworks()
        """
        response_get = requests.get(self._href_definitions.get_repo_models_frameworks_href(), headers=self._client._get_headers())
        if response_get.status_code == 200:
            return response_get.json()
        else:
            error_msg = 'Getting supported frameworks failed.' + '\n' + "Error msg: " + response_get.text
            print(error_msg)
            return None
    
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_status(self, run_uid):
        """
              Get training status.

              :param run_uid: ID of trained model
              :type run_uid: {str_type}

              :returns: training run status
              :rtype: dict

              A way you might use me is:

              >>> training_status = client.training.get_status(run_uid)
        """
        run_uid = str_type_conv(run_uid)
        Training._validate_type(run_uid, 'run_uid', STR_TYPE, True)

        details = self.get_details(run_uid)

        if details is not None:
            return WMLResource._get_required_element_from_dict(details, u'details', [u'entity', u'status'])
        else:
            raise WMLClientError(u'Getting trained model status failed. Unable to get model details for run_uid: \'{}\'.'.format(run_uid))

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_details(self, run_uid=None, limit=None):
        """
              Get training run details.

              :param run_uid: ID of training run (optional, if not provided all runs details are returned)
              :type run_uid: {str_type}

              :param limit: limit number of fetched records (optional)
              :type limit: int

              :returns: training run(s) details
              :rtype: dict

              A way you might use me is:

              >>> training_run_details = client.training.get_details(run_uid)
              >>> training_runs_details = client.training.get_details()
        """
        run_uid = str_type_conv(run_uid)
        Training._validate_type(run_uid, 'run_uid', STR_TYPE, False)

        url = self._href_definitions.get_repo_models_href()

        return self._get_artifact_details(url, run_uid, limit, 'trained models')

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_run_url(run_details):
        """
            Get training run url from training run details.

            :param run_details:  Created training run details
            :type run_details: dict

            :returns: training run URL that is used to manage the training
            :rtype: {str_type}

            A way you might use me is:

            >>> run_url = client.training.get_run_url(run_details)
        """
        Training._validate_type(run_details, u'run_details', object, True)
        Training._validate_type_of_details(run_details, TRAINING_RUN_DETAILS_TYPE)
        return WMLResource._get_required_element_from_dict(run_details, u'run_details', [u'metadata', u'url'])

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_run_uid(run_details):
        """
            Get uid of training run.

            :param run_details:  training run details
            :type run_details: dict

            :returns: uid of training run
            :rtype: {str_type}

            A way you might use me is:

            >>> model_uid = client.training.get_run_uid(run_details)
        """
        Training._validate_type(run_details, u'run_details', object, True)
        Training._validate_type_of_details(run_details, TRAINING_RUN_DETAILS_TYPE)
        return WMLResource._get_required_element_from_dict(run_details, u'run_details', [u'metadata', u'guid'])

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def cancel(self, run_uid):
        """
              Cancel model training.

              :param run_uid: ID of trained model
              :type run_uid: {str_type}

              A way you might use me is:

              >>> client.training.cancel(run_uid)
        """
        run_uid = str_type_conv(run_uid)
        Training._validate_type(run_uid, u'run_uid', STR_TYPE, True)

        patch_endpoint = self._href_definitions.get_repo_model_href(run_uid)
        patch_payload = [
            {
                u'op': u'replace',
                u'path': u'/status/state',
                u'value': u'canceled'
            }
        ]

        response_patch = requests.patch(patch_endpoint, json=patch_payload, headers=self._client._get_headers())

        self._handle_response(204, u'model training cancel', response_patch, False)
        return

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def run(self, definition_uid, meta_props, asynchronous=True):
        """
        Train new model.

        :param definition_uid: uid to saved model_definition/pipeline
        :type definition_uid: {str_type}

        :param meta_props: meta data of the training configuration. To see available meta names use:

            >>> client.training.ConfigurationMetaNames.show()

        :type meta_props: dict

        :param asynchronous: Default `True` means that training job is submitted and progress can be checked later.
               `False` - method will wait till job completion and print training stats.
        :type asynchronous: bool

        :returns: training run details
        :rtype: dict

        A way you might use me is:

        >>> metadata = {
        >>>  client.training.ConfigurationMetaNames.NAME: u'Hand-written Digit Recognition',
        >>>  client.training.ConfigurationMetaNames.TRAINING_DATA_REFERENCE: {
        >>>          u'connection': {
        >>>              u'endpoint_url': u'https://s3-api.us-geo.objectstorage.service.networklayer.com',
        >>>              u'access_key_id': u'***',
        >>>              u'secret_access_key': u'***'
        >>>          },
        >>>          u'source': {
        >>>              u'bucket': u'wml-dev',
        >>>          }
        >>>          u'type': u's3'
        >>>      }
        >>> client.training.ConfigurationMetaNames.TRAINING_RESULTS_REFERENCE: {
        >>>          u'connection': {
        >>>              u'endpoint_url': u'https://s3-api.us-geo.objectstorage.service.networklayer.com',
        >>>              u'access_key_id': u'***',
        >>>              u'secret_access_key': u'***'
        >>>          },
        >>>          u'target': {
        >>>              u'bucket': u'wml-dev-results',
        >>>          }
        >>>          u'type': u's3'
        >>>      },
        >>> client.training.ConfigurationMetaNames.COMPUTE_CONFIGURATION: {'name': 'p100'},
        >>> client.training.ConfigurationMetaNames.EXECUTION_COMMAND: "python3 tensorflow_mnist_softmax.py --trainingIters 20",
        >>> }
        >>> run_details = client.training.run(definition_uid, meta_props=metadata)
        >>> run_uid = client.training.get_run_uid(run_details)
        """
        definition_uid = str_type_conv(definition_uid)
        Training._validate_type(definition_uid, 'definition_uid', STR_TYPE, True)
        Training._validate_type(meta_props, 'meta_props', object, True)
        Training._validate_type(asynchronous, 'asynchronous', bool, True)
        meta_props_str_conv(meta_props)
        self.ConfigurationMetaNames._validate(meta_props)

        if definition_uid is not None and is_uid(definition_uid):
            definition_url = self._href_definitions.get_definition_href(definition_uid)
        elif definition_uid is not None:
            raise WMLClientError(u'Invalid uid: \'{}\'.'.format(definition_uid))
        else:
            raise WMLClientError(u'Both uid and url are empty.')

        details = self._client.repository.get_definition_details(definition_uid)

        # TODO remove when training service starts copying such data on their own
        FRAMEWORK_NAME = details[u'entity'][u'framework'][u'name']
        FRAMEWORK_VERSION = details[u'entity'][u'framework'][u'version']

        if self.ConfigurationMetaNames.EXECUTION_COMMAND not in meta_props:
            meta_props.update(
                {self.ConfigurationMetaNames.EXECUTION_COMMAND: details['entity']['command']})

        training_configuration_metadata = {
            u'model_definition': {
                u'framework': {
                    u'name': FRAMEWORK_NAME,
                    u'version': FRAMEWORK_VERSION
                },
                u'name': meta_props[self.ConfigurationMetaNames.NAME],
                u'author': {
                },
                u'definition_href': definition_url,
                u'execution': {
                    u'command': meta_props[self.ConfigurationMetaNames.EXECUTION_COMMAND],
                    u'compute_configuration': {u'name': self.ConfigurationMetaNames._COMPUTE_CONFIGURATION_DEFAULT}
                }
            },
            u'training_data_reference': meta_props[self.ConfigurationMetaNames.TRAINING_DATA_REFERENCE],
            u'training_results_reference': meta_props[self.ConfigurationMetaNames.TRAINING_RESULTS_REFERENCE]
        }

        if self.ConfigurationMetaNames.DESCRIPTION in meta_props:
            training_configuration_metadata[u'model_definition'].update({u'description': meta_props[self.ConfigurationMetaNames.DESCRIPTION]})

        if self.ConfigurationMetaNames.AUTHOR_NAME in meta_props:
            training_configuration_metadata[u'model_definition'][u'author'].update({u'name': meta_props[self.ConfigurationMetaNames.AUTHOR_NAME]})

        # TODO uncomment if it will be truly optional in service
        # if self.ConfigurationMetaNames.FRAMEWORK_NAME in meta_props or self.ConfigurationMetaNames.FRAMEWORK_VERSION in meta_props:
        #     training_configuration_metadata['model_definition'].update({'framework': {}})
        #     if self.ConfigurationMetaNames.FRAMEWORK_NAME in meta_props:
        #         training_configuration_metadata['model_definition']['framework'].update({'name': meta_props[self.ConfigurationMetaNames.FRAMEWORK_NAME]})
        #     if self.ConfigurationMetaNames.FRAMEWORK_VERSION in meta_props:
        #         training_configuration_metadata['model_definition']['framework'].update({'version': meta_props[self.ConfigurationMetaNames.FRAMEWORK_VERSION]})

        # TODO uncomment if it will be truly optional in service
        # if self.ConfigurationMetaNames.EXECUTION_COMMAND in meta_props or self.ConfigurationMetaNames.EXECUTION_RESOURCE_SIZE in meta_props:
        #     training_configuration_metadata['model_definition'].update({'execution': {}})
        #     if self.ConfigurationMetaNames.EXECUTION_COMMAND in meta_props:
        #         training_configuration_metadata['model_definition']['execution'].update({'command': meta_props[self.ConfigurationMetaNames.EXECUTION_COMMAND]})
        if self.ConfigurationMetaNames.COMPUTE_CONFIGURATION in meta_props:
            training_configuration_metadata[u'model_definition'][u'execution'][u'compute_configuration'].update(meta_props[self.ConfigurationMetaNames.COMPUTE_CONFIGURATION])

        train_endpoint = u'{}/v3/models'.format(self._wml_credentials[u'url'])

        response_train_post = requests.post(train_endpoint, json=training_configuration_metadata,
                                            headers=self._client._get_headers())

        run_details = self._handle_response(202, u'training', response_train_post)

        trained_model_guid = self.get_run_uid(run_details)

        if asynchronous is True:
            return run_details
        else:
            print_text_header_h1(u'Running \'{}\''.format(trained_model_guid))

            status = self.get_status(trained_model_guid)
            state = status[u'state']

            with StatusLogger(state) as status_logger:
                while state not in ['error', 'completed', 'canceled']:
                    time.sleep(5)
                    state = self.get_status(trained_model_guid)['state']
                    status_logger.log_state(state)

            if u'completed' in state:
                print(u'\nTraining of \'{}\' finished successfully.'.format(str(trained_model_guid)))
            else:
                print(u'\nTraining of \'{}\' failed with status: \'{}\'.'.format(trained_model_guid, str(status)))

            self._logger.debug(u'Response({}): {}'.format(state, run_details))
            return self.get_details(trained_model_guid)

    def list(self, limit=None):
        """
           List training runs. If limit is set to None there will be only first 50 records shown.

           A way you might use me is:

           >>> client.training.list()
        """

        details = self.get_details()
        resources = details[u'resources']
        values = [(m[u'metadata'][u'guid'], m[u'entity'][u'model_definition'][u'name'], m[u'entity'][u'status'][u'state'], m[u'metadata'][u'created_at'],
                   m[u'entity'][u'model_definition'][u'framework'][u'name']) for m in resources]

        self._list(values, [u'GUID (training)', u'NAME', u'STATE', u'CREATED', u'FRAMEWORK'], limit, 50)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete(self, run_uid):
        """
            Delete training run.

            :param run_uid: ID of trained model
            :type run_uid: {str_type}

            A way you might use me is:

            >>> client.training.delete(run_uid)
        """
        run_uid = str_type_conv(run_uid)
        Training._validate_type(run_uid, u'run_uid', STR_TYPE, True)

        response_delete = requests.delete(self._href_definitions.get_repo_model_href(run_uid),
                                          headers=self._client._get_headers())

        self._handle_response(204, u'trained model deletion', response_delete, False)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def monitor_logs(self, run_uid):
        """
            Monitor training log file (prints log content to console).

            :param run_uid: ID of trained model
            :type run_uid: {str_type}

            A way you might use me is:

            >>> client.training.monitor_logs(run_uid)
        """
        run_uid = str_type_conv(run_uid)
        Training._validate_type(run_uid, u'run_uid', STR_TYPE, True)

        self._simple_monitor_logs(run_uid, lambda: print_text_header_h1(u'Log monitor started for training run: ' + str(run_uid)))

        print_text_header_h2('Log monitor done.')

    def _simple_monitor_logs(self, run_uid, on_start=lambda: {}):
        from lomond import WebSocket

        monitor_endpoint = self._wml_credentials[u'url'].replace(u'https',
                                                                 u'wss') + u'/v3/models/' + run_uid + u'/monitor'
        websocket = WebSocket(monitor_endpoint)
        try:
            websocket.add_header(bytes("Authorization", "utf-8"), bytes("bearer " + self._client.service_instance._get_token(), "utf-8"))
        except:
            websocket.add_header(bytes("Authorization"), bytes("bearer " + self._client.service_instance._get_token()))

        on_start()

        for event in websocket:
            if event.name == u'text':
                text = json.loads(event.text)

                if 'status' in text:
                    status = text[u'status']

                    if u'message' in status:
                        if len(status[u'message']) > 0:
                            print(status[u'message'])

        websocket.close()

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def monitor_metrics(self, run_uid):
        """
            Monitor metrics log file (prints log content to console).

            :param run_uid: ID of trained model
            :type run_uid: {str_type}

            A way you might use me is:

            >>> client.training.monitor_metrics(run_uid)
        """
        run_uid = str_type_conv(run_uid)
        Training._validate_type(run_uid, u'run_uid', STR_TYPE, True)

        from lomond import WebSocket

        monitor_endpoint = self._wml_credentials[u'url'].replace(u'https',
                                                                 u'wss') + u'/v3/models/' + run_uid + u'/monitor'
        websocket = WebSocket(monitor_endpoint)
        try:
            websocket.add_header(bytes("Authorization", "utf-8"), bytes("bearer " + self._client.service_instance._get_token(), "utf-8"))
        except:
            websocket.add_header(bytes("Authorization"), bytes("bearer " + self._client.service_instance._get_token()))

        print_text_header_h1('Metric monitor started for training run: ' + str(run_uid))

        for event in websocket:
            if event.name == u'text':
                text = json.loads(event.text)
                status = text[u'status']
                if u'metrics' in status:
                    metrics = status[u'metrics']
                    if len(metrics) > 0:
                        metric = metrics[0]
                        values = u''
                        for x in metric[u'values']:
                            values = values + x[u'name'] + ':' + str(x[u'value']) + u' '
                        msg = u'{} iteration:{} phase:{} {}'.format(metric[u'timestamp'], metric[u'iteration'], metric[u'phase'], values)
                        print(msg)

        websocket.close()

        print_text_header_h2('Metric monitor done.')

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_metrics(self, run_uid):
        """
             Get metrics values.

             :param run_uid: ID of trained model
             :type run_uid: {str_type}

             :returns: metric values
             :rtype: list of dicts

             A way you might use me is:

             >>> client.training.get_metrics(run_uid)
         """
        run_uid = str_type_conv(run_uid)
        Training._validate_type(run_uid, u'run_uid', STR_TYPE, True)

        status = self.get_status(run_uid)
        metrics = status['metrics']

        return metrics

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_latest_metrics(self, run_uid):
        """
             Get latest metrics values.

             :param run_uid: ID of trained model
             :type run_uid: {0}

             :returns: metric values
             :rtype: list of dicts

             A way you might use me is:

             >>> client.training.get_latest_metrics(run_uid)
         """
        run_uid = str_type_conv(run_uid)
        Training._validate_type(run_uid, u'run_uid', STR_TYPE, True)

        status = self.get_status(run_uid)
        metrics = status['metrics']
        latest_metrics = []

        if len(metrics) > 0:
            grouped_metrics = group_metrics(metrics)

            for key, value in grouped_metrics.items():
                sorted_value = sorted(value, key=lambda k: k['iteration'])

            latest_metrics.append(sorted_value[-1])

        return latest_metrics

    def list_definitions(self, limit=None):
        """
           List stored definitions. If limit is set to None there will be only first 50 records shown.

           A way you might use me is

           >>> client.training.list_definitions()
        """
        self._client.repository.list_definitions(limit=limit)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_definition_details(self, definition_uid=None, limit=None):
        """
            Get metadata of stored definitions. If definition uid is not specified returns all model definitions metadata.

            :param definition_uid:  stored model definition UID (optional)
            :type definition_uid: {str_type}

            :param limit: limit number of fetched records (optional)
            :type limit: int

            :returns: stored definition(s) metadata
            :rtype: dict

            A way you might use me is:

            >>> definition_details = client.training.get_definition_details(definition_uid)
            >>> definition_details = client.training.get_definition_details()
        """
        return self._client.repository.get_definition_details(definition_uid, limit=limit)

    def get_definition_uid(self, definition_details):
        """
            Get uid of stored definition.

            :param definition_details: stored definition details
            :type definition_details: dict

            :returns: uid of stored model
            :rtype: str

            A way you might use me is:

            >>> definition_uid = client.training.get_definition_uid(definition_details)
        """

        return self._client.repository.get_definition_uid(definition_details)

    def get_definition_url(self, definition_details):
        """
            Get url of stored definition.

            :param definition_details:  stored definition details
            :type definition_details: dict

            :returns: url of stored definition
            :rtype: {str_type}

            A way you might use me is:

            >>> definition_url = client.training.get_definition_url(definition_details)
        """

        return self._client.repository.get_definition_url(definition_details)