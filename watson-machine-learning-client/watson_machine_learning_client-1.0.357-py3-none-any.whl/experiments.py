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
import time
import copy
from watson_machine_learning_client.wml_client_error import MissingValue, WMLClientError, MissingMetaProp
from watson_machine_learning_client.href_definitions import is_uid
from watson_machine_learning_client.wml_resource import WMLResource
from multiprocessing import Pool
from watson_machine_learning_client.utils import print_text_header_h1, print_text_header_h2, EXPERIMENT_DETAILS_TYPE, EXPERIMENT_RUN_DETAILS_TYPE, format_metrics, STR_TYPE, STR_TYPE_NAME, docstring_parameter, group_metrics, str_type_conv, meta_props_str_conv
from watson_machine_learning_client.hpo import HPOParameter, HPOMethodParam
from watson_machine_learning_client.metanames import ExperimentMetaNames


def _get_details_helper(url, headers, setting=None):
    from watson_machine_learning_client.log_util import get_logger
    logger = get_logger(u'experiments._get_details_helper')

    response_get = requests.get(
        url + u'/runs',
        headers=headers)
    if response_get.status_code == 200:
        logger.debug(u'Successfully got runs details ({}): {}'.format(response_get.status_code, response_get.text))
        details = response_get.json()

        if u'resources' in details:
            resources = details[u'resources']
        else:
            resources = [details]

        if setting is not None:
            for r in resources:
                r[u'entity'].update({u'_parent_settings': setting})
        return resources
    else:
        logger.warning(u'Failure during getting runs details ({}): {}'.format(response_get.status_code, response_get.text))
        return []


class Experiments(WMLResource):
    """
       Run new experiment.
    """

    ConfigurationMetaNames = ExperimentMetaNames()
    """MetaNames for experiments creation."""

    @staticmethod
    def HPOParameter(name, values=None, max=None, min=None, step=None):
        return HPOParameter(name, values, max, min, step)

    @staticmethod
    def HPOMethodParam(name=None, value=None):
        return HPOMethodParam(name, value)

    def __init__(self, client):
        WMLResource.__init__(self, __name__, client)
        self._experiments_uids_cache = {}

    def _store(self, meta_props):
        """
           Store experiment.

            :param meta_props: meta data of the experiment configuration. To see available meta names use:

               >>> client.experiments.ConfigurationMetaNames.get()
            :type meta_props: dict

            :returns: stored experiment details
            :rtype: dict

           A way you might use me is:

           >>> metadata = {
           >>>  client.experiments.ConfigurationMetaNames.NAME: 'my_experiment',
           >>>  client.experiments.ConfigurationMetaNames.EVALUATION_METRICS: ['accuracy'],
           >>>  client.experiments.ConfigurationMetaNames.TRAINING_DATA_REFERENCE: {'connection': {'endpoint_url': 'https://s3-api.us-geo.objectstorage.softlayer.net', 'access_key_id': '***', 'secret_access_key': '***'}, 'source': {'bucket': 'train-data'}, 'type': 's3'},
           >>>  client.experiments.ConfigurationMetaNames.TRAINING_RESULTS_REFERENCE: {'connection': {'endpoint_url': 'https://s3-api.us-geo.objectstorage.softlayer.net', 'access_key_id': '***', 'secret_access_key': '***'}, 'target': {'bucket': 'result-data'}, 'type': 's3'},
           >>>  client.experiments.ConfigurationMetaNames.TRAINING_REFERENCES: [
           >>>      {
           >>>        'training_definition_url': definition_url_1
           >>>      },
           >>>      {
           >>>        'training_definition_url': definition_url_2
           >>>      },
           >>>   ],
           >>> }
           >>> experiment_details = client.experiments._store(meta_props=metadata)
           >>> experiment_url = client.experiments.get_url(experiment_details)
        """
        Experiments._validate_type(meta_props, u'meta_props', dict, True)
        meta_props_str_conv(meta_props)
        self.ConfigurationMetaNames._validate(meta_props)

        meta_props = copy.deepcopy(meta_props)

        if any(u'training_definition_url' not in x for x in meta_props[self.ConfigurationMetaNames.TRAINING_REFERENCES]):
            raise MissingMetaProp(u'training_references.training_definition_url')

        for ref in meta_props[self.ConfigurationMetaNames.TRAINING_REFERENCES]:
            if u'name' not in ref or u'command' not in ref:

                training_definition_response = requests.get(ref[u'training_definition_url'].replace(u'/content', u''), headers=self._client._get_headers())
                result = self._handle_response(200, u'getting training definition', training_definition_response)

                if not u'name' in ref:
                    ref.update({u'name': result[u'entity'][u'name']})
                if not u'command' in ref:
                    ref.update({u'command': result[u'entity'][u'command']})

        response_experiment_post = requests.post(
            self._href_definitions.get_experiments_href(),
            json=self.ConfigurationMetaNames._generate_resource_metadata(meta_props),
            headers=self._client._get_headers()
        )

        return self._handle_response(201, u'saving experiment', response_experiment_post)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def _update_experiment(self, experiment_uid, changes):
        """
        Updates existing experiment metadata.

        :param experiment_uid: UID of experiment which definition should be updated
        :type experiment_uid: {str_type}

        :param changes: elements which should be changed, where keys are ConfigurationMetaNames
        :type changes: dict

        :return: metadata of updated experiment
        :rtype: dict
        """
        experiment_uid = str_type_conv(experiment_uid)
        self._validate_type(experiment_uid, u'experiment_uid', STR_TYPE, True)
        self._validate_type(changes, u'changes', dict, True)
        meta_props_str_conv(changes)

        details = self._client.repository.get_experiment_details(experiment_uid)

        patch_payload = self.ConfigurationMetaNames._generate_patch_payload(details['entity'], changes, with_validation=True)

        url = self._href_definitions.get_experiment_href(experiment_uid)
        response = requests.patch(url, json=patch_payload, headers=self._client._get_headers())
        updated_details = self._handle_response(200, u'experiment patch', response)

        return updated_details

    def _get_experiment_uid(self, experiment_run_uid=None, experiment_run_url=None):
        if experiment_run_uid is None and experiment_run_url is None:
            raise MissingValue(u'experiment_run_id/experiment_run_url')

        if experiment_run_uid is not None and experiment_run_uid in self._experiments_uids_cache:
            return self._experiments_uids_cache[experiment_run_uid]

        if experiment_run_url is not None:
            m = re.search(u'.+/v3/experiments/{[^\/]+}/runs/{[^\/]+}', experiment_run_url)
            _experiment_id = m.group(1)
            _experiment_run_id = m.group(2)
            self._experiments_uids_cache.update({_experiment_run_id: _experiment_id})
            return _experiment_id

        details = self.get_details()

        resources = details[u'resources']

        try:
            el = [x for x in resources if x[u'metadata'][u'guid'] == experiment_run_uid][0]
        except:
            raise WMLClientError(u'Cannot find experiment_uid for experiment_run_uid: \'{}\''.format(experiment_run_uid))

        experiment_uid = el[u'experiment'][u'guid']
        self._experiments_uids_cache.update({experiment_run_uid: experiment_uid})
        return experiment_uid

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def run(self, experiment_uid, asynchronous=True):
        """
            Run experiment.

            :param experiment_uid: ID of stored experiment
            :type experiment_uid: {str_type}
            :param asynchronous: Default `True` means that experiment is started and progress can be checked later. `False` - method will wait till experiment end and print experiment stats.
            :type asynchronous: bool

            :return: experiment run details
            :rtype: dict

            A way you might use me is

            >>> experiment_run_status = client.experiments.run(experiment_uid)
            >>> experiment_run_status = client.experiments.run(experiment_uid, asynchronous=False)
        """
        experiment_uid = str_type_conv(experiment_uid)
        Experiments._validate_type(experiment_uid, u'experiment_uid', STR_TYPE, True)
        Experiments._validate_type(asynchronous, u'asynchronous', bool, True)

        run_url = self._href_definitions.get_experiment_runs_href(experiment_uid)

        response = requests.post(run_url, headers=self._client._get_headers())

        # TODO should be 201
        result_details = self._handle_response(200, u'experiment run', response)

        experiment_run_uid = self.get_run_uid(result_details)
        self._experiments_uids_cache.update({experiment_run_uid: experiment_uid})

        if asynchronous:
            return result_details
        else:
            print_text_header_h1(u'Running \'{}\' experiment'.format(experiment_uid))
            print('Experiment run uid: {}\n'.format(experiment_run_uid))

            status = self.get_status(experiment_run_uid)

            tries_no = 10
            error = None
            training_uids = None

            import logging
            root_logger = logging.getLogger("watson_machine_learning_client.wml_client_error")
            root_logger.disabled = True

            while tries_no > 0 and training_uids is None:
                tries_no -= 1
                try:
                    run_details = self.get_run_details(experiment_run_uid)
                    training_uids = self.get_training_uids(run_details)
                except Exception as e:
                    error = e

                time.sleep(1)

            root_logger.disabled = False

            if training_uids is None:
                raise WMLClientError("Getting training uids failed.", error)

            total = 100
            current_progress = 0
            state = "initializing"
            train_state = "initializing"
            last_curr_uid = None

            last_state = state
            last_train_state = train_state

            curr_uid = None

            import math

            training_runs = []
            completed_uids = []

            while state not in ["error", "cancelled", "completed"]:
                run_details = self.get_run_details(experiment_run_uid)
                training_runs = self.get_training_runs(run_details)
                running_uids = [x['training_guid'] for x in training_runs if x['state'] == 'running']
                uncompleted_uids = [x['training_guid'] for x in training_runs if x['state'] not in ["error", "cancelled", "completed"]]
                completed_uids = [x['training_guid'] for x in training_runs if x['state'] in ["error", "cancelled", "completed"]]

                progress = math.floor(total * len(completed_uids)/len(training_runs))

                state = self.get_status(experiment_run_uid)[u'state']

                if (curr_uid is None or curr_uid in completed_uids) and len(uncompleted_uids) > 0:
                    if len(running_uids) > 0:
                        curr_uid = running_uids[0]
                    else:
                        curr_uid = uncompleted_uids[0]

                if curr_uid is not None:
                    train_state = self._client.training.get_status(curr_uid)[u'state']

                if curr_uid is not None and (last_state != state or last_train_state != train_state or last_curr_uid != curr_uid):
                    last_state = state
                    last_train_state = train_state
                    last_curr_uid = curr_uid

                    indent = ' ' * (3 - len(str(progress)))

                    print('{}%{} - Processing {} ({}/{}): experiment_state={}, training_state={}'.format(progress, indent, curr_uid, min(len(completed_uids) + 1, len(training_runs)), len(training_runs), state, train_state))

            print('100% - Finished processing training runs: experiment_state={}'.format(state))

            if u'completed' in state:
                print_text_header_h2(u'Run of \'{}\' finished successfully.'.format(str(experiment_uid)))
            else:
                print_text_header_h2(
                    u'Run of \'{}\' failed with status: \'{}\'.'.format(experiment_uid, str(status)))

            result_details = self.get_run_details(experiment_run_uid)
            self._logger.debug(u'Response({}): {}'.format(state, result_details))
            return result_details

    def get_status(self, experiment_run_uid):
        """
            Get experiment status.

            :param experiment_run_uid: ID of experiment run
            :type experiment_run_uid: bool

            :returns: experiment status
            :rtype: dict

            A way you might use me is

            >>> experiment_status = client.experiments.get_status(experiment_run_uid)
        """
        experiment_run_uid = str_type_conv(experiment_run_uid)
        Experiments._validate_type(experiment_run_uid, u'experiment_run_uid', STR_TYPE, True)
        details = self.get_run_details(experiment_run_uid)

        try:
            status = WMLResource._get_required_element_from_dict(details, u'details', [u'entity', u'experiment_run_status'])
        except Exception as e:
            self._logger.debug('Missing experiment run status in run details:', e)
            raise WMLClientError(u'Missing experiment run status in run details. Probably status wasn\'t updated in time. Try again.')

        return status

    def get_run_details(self, experiment_run_uid):
        """
           Get metadata of particular experiment run.

           :param experiment_run_uid:  experiment run UID
           :type experiment_run_uid: bool

           :returns: experiment run metadata
           :rtype: dict

           A way you might use me is

           >>> experiment_run_details = client.experiments.get_run_details(experiment_run_uid)
        """
        experiment_run_uid = str_type_conv(experiment_run_uid)
        Experiments._validate_type(experiment_run_uid, u'experiment_run_uid', STR_TYPE, True)

        experiment_uid = self._get_experiment_uid(experiment_run_uid)

        url = self._href_definitions.get_experiment_run_href(experiment_uid, experiment_run_uid)

        response_get = requests.get(
            url,
            headers=self._client._get_headers())
        response = self._handle_response(200, u'getting experiment run details', response_get)
        return response

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_details(self, experiment_uid=None, limit=None):
        """
           Get metadata of experiment(s) run(s). If no experiment_uid is provided, runs will be listed for all existing experiments.

           :param experiment_uid:  experiment UID (optional)
           :type experiment_uid: {str_type}

           :param limit: limit number of fetched records (optional)
            :type limit: int

           :returns: experiment(s) run(s) metadata
           :rtype: dict

           A way you might use me is

           >>> experiment_details = client.experiments.get_details(experiment_uid)
           >>> experiment_details = client.experiments.get_details()
        """
        experiment_uid = str_type_conv(experiment_uid)
        return self._get_extended_details(experiment_uid, False)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def _get_uid(experiment_details):
        """
            Get uid of stored experiment.

            :param experiment_details: stored experiment details
            :type experiment_details: dict

            :returns: uid of stored experiment
            :rtype: {str_type}

            A way you might use me is:

            >>> experiment_uid = client.experiments.get_uid(experiment_details)
        """
        Experiments._validate_type(experiment_details, u'experiment_details', object, True)
        Experiments._validate_type_of_details(experiment_details, EXPERIMENT_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(experiment_details, u'experiment_details',
                                                           [u'metadata', u'guid'])

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def _get_url(experiment_details):
        """
            Get url of stored experiment.

            :param experiment_details:  stored experiment details
            :type experiment_details: dict

            :returns: url of stored experiment
            :rtype: {str_type}

            A way you might use me is:

            >>> experiment_url = client.experiments.get_url(experiment_details)
        """
        Experiments._validate_type(experiment_details, u'experiment_details', object, True)
        Experiments._validate_type_of_details(experiment_details, EXPERIMENT_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(experiment_details, u'experiment_details',
                                                           [u'metadata', u'url'])

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_run_url(experiment_run_details):
        """
            Get experiment run url.

            :param experiment_run_details: details of experiment run
            :type experiment_run_details: object

            :returns: experiment run url
            :rtype: {str_type}

            A way you might use me is

            >>> experiment_run_url = client.experiments.get_run_url(experiment_run_details)
        """
        Experiments._validate_type(experiment_run_details, u'experiment_run_details', dict, True)
        Experiments._validate_type_of_details(experiment_run_details, EXPERIMENT_RUN_DETAILS_TYPE)

        try:
            url = WMLResource._get_required_element_from_dict(experiment_run_details, u'experiment_run_details', [u'metadata', u'url'])
        except Exception as e:
            raise WMLClientError(u'Failure during getting experiment run url from details.', e)

        # TODO still, it is not working properly
        #if not is_url(url):
        #     raise WMLClientError('Experiment url: \'{}\' is invalid.'.format(url))

        return url

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_run_uid(experiment_run_details):
        """
            Get experiment run uid.

            :param experiment_run_details: details of experiment run
            :type experiment_run_details: object

            :returns: experiment run uid
            :rtype: {str_type}

            A way you might use me is

            >>> experiment_run_uid = client.experiments.get_run_uid(experiment_run_details)
        """
        Experiments._validate_type(experiment_run_details, u'experiment_run_details', dict, True)
        Experiments._validate_type_of_details(experiment_run_details, EXPERIMENT_RUN_DETAILS_TYPE)

        try:
            uid = WMLResource._get_required_element_from_dict(experiment_run_details, u'experiment_run_details', [u'metadata', u'guid'])
        except Exception as e:
            raise WMLClientError(u'Failure during getting experiment run uid from details.', e)

        if not is_uid(uid):
            raise WMLClientError(u'Experiment run uid: \'{}\' is invalid.'.format(uid))

        return uid

    @staticmethod
    def get_training_runs(experiment_run_details):
        """
            Get experiment training runs details.

            :param experiment_run_details: details of experiment run
            :type: object

            :returns: training runs
            :rtype: array

            A way you might use me is

            >>> training_runs = client.experiments.get_training_runs(experiment_run_details)
        """
        Experiments._validate_type(experiment_run_details, u'experiment_run_details', dict, True)
        Experiments._validate_type_of_details(experiment_run_details, EXPERIMENT_RUN_DETAILS_TYPE)

        try:
            training_runs = WMLResource._get_required_element_from_dict(experiment_run_details, u'experiment_run_details',
                                                              [u'entity', u'training_statuses'])
        except Exception as e:
            raise WMLClientError(u'Failure during getting experiment training runs from details.', e)

        if training_runs is None or len(training_runs) <= 0:
            raise MissingValue(u'training_runs')

        return training_runs

    @staticmethod
    def get_training_uids(experiment_run_details):
        """
            Get experiment training uids.

            :param experiment_run_details: details of experiment run
            :type experiment_run_details: object

            :returns: training uids
            :rtype: array

            A way you might use me is

            >>> training_uids = client.experiments.get_training_uids(experiment_run_details)
        """
        Experiments._validate_type(experiment_run_details, u'experiment_run_details', dict, True)
        Experiments._validate_type_of_details(experiment_run_details, EXPERIMENT_RUN_DETAILS_TYPE)

        try:
            training_uids = [x[u'training_guid'] for x in WMLResource._get_required_element_from_dict(experiment_run_details,
                                                                         u'experiment_run_details',
                                                                        [u'entity', u'training_statuses'])]
        except Exception as e:
            raise WMLClientError(u'Failure during getting experiment training runs from details.', e)

        if training_uids is None or len(training_uids) <= 0:
            raise MissingValue(u'training_uids')

        return training_uids

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete(self, experiment_run_uid):
        """
            Delete experiment run.

            :param experiment_run_uid:  experiment run UID
            :type experiment_run_uid: {str_type}

            A way you might use me is

            >>> client.experiments.delete(experiment_run_uid)

            .. hint::

                This function is only for deleting experiment runs. To delete whole experiment use:

                >>> client.repository.delete(experiment_uid)
        """
        experiment_run_uid = str_type_conv(experiment_run_uid)
        Experiments._validate_type(experiment_run_uid, u'experiment_run_uid', STR_TYPE, True)

        experiment_uid = self._get_experiment_uid(experiment_run_uid)

        run_url = self._href_definitions.get_experiment_run_href(experiment_uid, experiment_run_uid)

        response = requests.delete(run_url, headers=self._client._get_headers())

        self._handle_response(204, u'experiment deletion', response, False)

    def _get_extended_details(self, experiment_uid=None, extended=True):
        experiment_uid = str_type_conv(experiment_uid)
        Experiments._validate_type(experiment_uid, u'experiment_uid', STR_TYPE, False)

        if experiment_uid is None:
            experiments = self._client.repository.get_experiment_details()

            try:
                urls_and_settings = [(experiment[u'metadata'][u'url'], experiment[u'entity'][u'settings'] if extended else None) for experiment in
                                     experiments[u'resources']]

                self._logger.debug(u'Preparing details for urls and settings: {}'.format(urls_and_settings))

                res = []

                pool = Pool(processes=4)
                tasks = []
                for url_and_setting in urls_and_settings:
                    url = url_and_setting[0]
                    setting = url_and_setting[1]
                    tasks.append(pool.apply_async(_get_details_helper,
                                                  (url, self._client._get_headers(), setting)))

                for task in tasks:
                    res.extend(task.get())

                pool.close()

            except Exception as e:
                raise WMLClientError(u'Error during getting all experiments details.', e)
            return {u'resources': res}
        else:
            url = self._href_definitions.get_experiment_runs_href(experiment_uid)

            response_get = requests.get(
                url,
                headers=self._client._get_headers())

            result = self._handle_response(200, u'getting experiment details', response_get)

            if extended:
                setting = self._client.repository.get_experiment_details(experiment_uid)[u'entity'][u'settings']
                for r in result[u'resources']:
                    r[u'entity'].update({u'_parent_settings': setting})

            return result

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def list_runs(self, experiment_uid=None, limit=None):
        """
            List experiment runs. If experiment_uid set to None and limit set to None only 50 first records will be displayed.

            :param experiment_uid: experiment UID (optional)
            :type experiment_uid: {str_type}

            :param limit: limit number of fetched records (optional)
            :type limit: int

            A way you might use me is

            >>> client.experiments.list_runs()
            >>> client.experiments.list_runs(experiment_uid)
        """
        experiment_uid = str_type_conv(experiment_uid)
        Experiments._validate_type(experiment_uid, u'experiment_uid', STR_TYPE, False)

        from tabulate import tabulate

        details = self._get_extended_details(experiment_uid)

        resources = details['resources']

        values = [(m[u'experiment'][u'guid'], m[u'metadata'][u'guid'], m[u'entity'][u'_parent_settings'][u'name'], m[u'entity'][u'experiment_run_status'][u'state'], m[u'metadata'][u'created_at']) for m in resources]

        if experiment_uid is not None:
            table = tabulate([[u'GUID (experiment)', u'GUID (run)', u'NAME (experiment)', u'STATE', u'CREATED']] + values)
            print(table)
        else:
            self._list(values, [u'GUID (experiment)', u'GUID (run)', u'NAME (experiment)', u'STATE', u'CREATED'], limit, 50)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def list_training_runs(self, experiment_run_uid):
        """
             List training runs triggered by experiment run.

             :param experiment_run_uid: experiment run UID
             :type experiment_run_uid: {str_type}

             A way you might use me is

             >>> client.experiments.list_training_runs(experiment_run_uid)
        """
        experiment_run_uid = str_type_conv(experiment_run_uid)
        Experiments._validate_type(experiment_run_uid, 'experiment_run_uid', STR_TYPE, True)

        from tabulate import tabulate
        details = self._client.experiments.get_run_details(experiment_run_uid)
        training_statuses = details[u'entity'][u'training_statuses']

        values = [(m[u'training_guid'], m[u'training_reference_name'], m[u'state'], m[u'submitted_at'], m[u'finished_at'] if u'finished_at' in m else u'-',
                   format_metrics(self._client.training.get_latest_metrics(m[u'training_guid'])) if len(self._client.training.get_latest_metrics(m[u'training_guid'])) > 0 else u'-') for m in training_statuses]

        table = tabulate([[u'GUID (training)', u'NAME', u'STATE', u'SUBMITTED', u'FINISHED', u'PERFORMANCE']] + values)

        print(table)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def monitor_logs(self, experiment_run_uid):
        """
            Monitor experiment run log files (prints log content to console).

            :param experiment_run_uid: ID of experiment run
            :type experiment_run_uid: {str_type}

            A way you might use me is

            >>> client.experiments.monitor_logs(experiment_run_uid)
        """
        experiment_run_uid = str_type_conv(experiment_run_uid)
        Experiments._validate_type(experiment_run_uid, u'experiment_run_uid', STR_TYPE, True)

        print_text_header_h1(u'Monitor started for experiment run: ' + str(experiment_run_uid))

        # TODO More correct but not as nice working version
        # try:
        #     experiment_uid = self.get_run_details(experiment_run_uid)[u'experiment'][u'guid']
        # except Exception as e:
        #     raise WMLClientError(u'Failure during getting experiment uid from experiment run details.', e)
        #
        # from lomond import WebSocket
        # experiment_monitor_endpoint = self._wml_credentials[u'url'].replace(u'https',
        #                                                                     u'wss') + u'/v3/experiments/' + experiment_uid + u'/runs/' + experiment_run_uid + '/monitor'
        # websocket = WebSocket(experiment_monitor_endpoint)
        # try:
        #     websocket.add_header(bytes('Authorization', 'utf-8'), bytes('bearer ' + self._client.service_instance._get_token(), 'utf-8'))
        # except:
        #     websocket.add_header(bytes('Authorization'), bytes('bearer ' + self._client.service_instance._get_token()))
        #
        # previous_guid = ''
        #
        # for event in websocket:
        #     if event.name == u'text':
        #         text = json.loads(event.text)
        #         if (u'entity' in str(text)) and (u'training_statuses' in str(text)):
        #             training_statuses = text[u'entity'][u'training_statuses']
        #             for i in training_statuses:
        #                 if (u'training_guid' in i) and (u'message' in i):
        #                     msg = i[u'message'].strip()
        #                     guid = i[u'training_guid'].strip()
        #                     if msg != '':
        #                         if guid == previous_guid:
        #                             print(msg)
        #                         else:
        #                             if 'training_reference_name' in str(i):
        #                                 name = i['training_reference_name']
        #                                 if name != '':
        #                                     h2_text = guid + " (" + name + ")"
        #                                 else:
        #                                     h2_text = guid
        #                             else:
        #                                 h2_text = guid
        #                             print_text_header_h2(h2_text)
        #                             print(msg)
        #                         previous_guid = guid

        state = "initialized"

        import logging
        root_logger = logging.getLogger("watson_machine_learning_client.wml_client_error")
        root_logger.disabled = True

        uids_get_tries = 10
        training_run_uids = None
        error = None

        while uids_get_tries > 0 and training_run_uids is None:
            uids_get_tries -= 1
            try:
                run_details = self.get_run_details(experiment_run_uid)
                training_run_uids = self.get_training_uids(run_details)
            except Exception as e:
                error = e

            time.sleep(1)

        root_logger.disabled = False

        if training_run_uids is None:
            raise WMLClientError("Training run uids couldn't be retrieved.", error)

        training_run_uids = [x for x in training_run_uids if "_" not in x]

        finished = []

        while state not in ("error", "cancelled", "completed"):
            run_details = self.get_run_details(experiment_run_uid)
            training_runs = self.get_training_runs(run_details)
            running_uids = [x['training_guid'] for x in training_runs if x['state'] == 'running' and x['training_guid'] not in finished]
            for running_uid in running_uids:
                self._client.training._simple_monitor_logs(running_uid, lambda: print_text_header_h2(u'Log monitor started for training run: ' + str(running_uid)))
                finished.append(running_uid)
            status = self.get_status(experiment_run_uid)
            state = status['state']

        for training_uid in training_run_uids:
            if training_uid not in finished:
                self._client.training._simple_monitor_logs(training_uid, lambda: print_text_header_h2(u'Log monitor started for training run: ' + str(training_uid)))

        print_text_header_h2(u'Log monitor done.')

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def monitor_metrics(self, experiment_run_uid):
        """
            Monitor metrics log file (prints metrics to console).

            :param experiment_run_uid: ID of experiment run
            :type run_uid: {str_type}

            A way you might use me is:

            >>> client.experiments.monitor_metrics(experiment_run_uid)
        """
        experiment_run_uid = str_type_conv(experiment_run_uid)

        try:
            experiment_uid = self.get_run_details(experiment_run_uid)[u'experiment'][u'guid']
        except Exception as e:
            raise WMLClientError(u'Failure during getting experiment uid from experiment run details.', e)

        print_text_header_h1(u'Metric monitor started for experiment run: ' + str(experiment_run_uid))

        from lomond import WebSocket
        experiment_monitor_endpoint = self._wml_credentials[u'url'].replace(u'https',
                                                                     u'wss') + u'/v3/experiments/' + experiment_uid + u'/runs/' + experiment_run_uid + '/monitor'
        websocket = WebSocket(experiment_monitor_endpoint)
        try:
            websocket.add_header(bytes('Authorization', 'utf-8'), bytes('bearer ' + self._client.service_instance._get_token(), 'utf-8'))
        except:
            websocket.add_header(bytes('Authorization'), bytes('bearer ' + self._client.service_instance._get_token()))

        previous_guid = u''

        for event in websocket:
            if event.name == u'text':
                text = json.loads(event.text)
                if (u'entity' in str(text)) and (u'training_statuses' in str(text)):
                    training_statuses = text[u'entity'][u'training_statuses']

                    for i in training_statuses:
                        if u'training_guid' in i:
                            guid = i[u'training_guid'].strip()

                            if u'metrics' in i:
                                metrics = i[u'metrics']
                                if len(metrics) > 0:
                                    metric = metrics[0]
                                    values = u' '.join([x[u'name'] + ':' + str(x[u'value']) for x in metric[u'values']])

                                    metric_msg = u'{} iteration:{} phase:{} {}'.format(metric[u'timestamp'], metric[u'iteration'], metric[u'phase'], values)

                                    if metric_msg != u'':
                                        if guid == previous_guid:
                                            print(metric_msg)
                                        else:
                                            if 'training_reference_name' in str(i):
                                                name = i['training_reference_name']
                                                if name != '':
                                                    h2_text = guid + " (" + name + ")"
                                                else:
                                                    h2_text = guid
                                            else:
                                                h2_text = guid

                                            print_text_header_h2(h2_text)
                                            print(metric_msg)

                                        previous_guid = guid

        websocket.close()

        print_text_header_h2(u'Metric monitor done.')

    def get_latest_metrics(self, experiment_run_uid):
        """
             Get latest metrics values for experiment run.

             :param experiment_run_uid: ID of training run
             :type experiment_run_uid: str

             :returns: metric values
             :rtype: list of dicts

             A way you might use me is:

             >>> client.experiments.get_latest_metrics(experiment_run_uid)
         """
        experiment_run_uid = str_type_conv(experiment_run_uid)
        Experiments._validate_type(experiment_run_uid, 'experiment_run_uid', str, True)

        training_statuses = self.get_run_details(experiment_run_uid)['entity']['training_statuses']

        metrics = []

        for status in training_statuses:
            training_guid_metrics = status['metrics']

            if len(training_guid_metrics) > 0:
                grouped_metrics = group_metrics(training_guid_metrics)

                for key, value in grouped_metrics.items():
                    sorted_value = sorted(value, key=lambda k: k['iteration'])

                metrics.append({"training_guid": status['training_guid'], "training_reference_name": status['training_reference_name'], "metrics": sorted_value[-1]})

        return metrics

    def get_metrics(self, experiment_run_uid):
        """
              Get all metrics values for experiment run.

              :param experiment_run_uid: ID of training run
              :type experiment_run_uid: str

              :returns: metric values
              :rtype: list of dicts

              A way you might use me is:

              >>> client.experiments.get_metrics(experiment_run_uid)
        """
        experiment_run_uid = str_type_conv(experiment_run_uid)
        Experiments._validate_type(experiment_run_uid, 'experiment_run_uid', STR_TYPE, True)

        training_statuses = self.get_run_details(experiment_run_uid)['entity']['training_statuses']

        metrics = []

        for status in training_statuses:
            training_guid_metrics = status['metrics']

            if len(training_guid_metrics) > 0:
                metrics.append({"training_guid": status['training_guid'], "training_reference_name": status['training_reference_name'], "metrics": training_guid_metrics})

        return metrics

    def list_definitions(self, limit=None):
        """
           List stored experiments. If limit is set to None there will be only first 50 records shown.

           A way you might use me is

           >>> client.experiments.list_definitions()
        """

        self._client.repository.list_experiments(limit=limit)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_definition_details(self, experiment_uid=None, limit=None):
        """
            Get metadata of stored experiments. If neither experiment uid nor url is specified all experiments metadata is returned.

            :param experiment_uid: stored experiment UID (optional)
            :type experiment_uid: {str_type}

            :param limit: limit number of fetched records (optional)
            :type limit: int

            :returns: stored experiment(s) metadata
            :rtype: dict

            A way you might use me is:

            >>> experiment_details = client.experiments.get_definition_details(experiment_uid)
            >>> experiment_details = client.experiments.get_definition_details()
         """

        return self._client.repository.get_experiment_details(experiment_uid, limit=limit)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_definition_uid(self, experiment_details):
        """
            Get uid of stored experiment.

            :param experiment_details: stored experiment details
            :type experiment_details: dict

            :returns: uid of stored experiment
            :rtype: {str_type}

            A way you might use me is:

            >>> experiment_uid = client.experiments.get_definition_uid(experiment_details)
        """
        return self._client.repository.get_experiment_uid(experiment_details)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_definition_url(self, experiment_details):
        """
            Get url of stored experiment.

            :param experiment_details:  stored experiment details
            :type experiment_details: dict

            :returns: url of stored experiment
            :rtype: {str_type}

            A way you might use me is:

            >>> experiment_url = client.experiments.get_definition_url(experiment_details)
        """
        return self._client.repository.get_experiment_url(experiment_details)
