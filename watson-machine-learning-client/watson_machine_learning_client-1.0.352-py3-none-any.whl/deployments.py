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
from watson_machine_learning_client.utils import DEPLOYMENT_DETAILS_TYPE, INSTANCE_DETAILS_TYPE, print_text_header_h1, print_text_header_h2, STR_TYPE, STR_TYPE_NAME, docstring_parameter, str_type_conv, meta_props_str_conv, StatusLogger, convert_metadata_to_parameters
from watson_machine_learning_client.wml_client_error import WMLClientError, MissingValue, NoVirtualDeploymentSupportedForICP
from watson_machine_learning_client.href_definitions import is_uid
from watson_machine_learning_client.wml_resource import WMLResource
from watson_machine_learning_client.metanames import PayloadLoggingMetaNames


class Deployments(WMLResource):
    """
        Deploy and score published artifacts (models and functions).
    """
    def __init__(self, client):
        WMLResource.__init__(self, __name__, client)
        if not client.ICP:
            Deployments._validate_type(client.service_instance.details, u'instance_details', dict, True)
            Deployments._validate_type_of_details(client.service_instance.details, INSTANCE_DETAILS_TYPE)
        self.session = requests.Session()
        self._ICP = client.ICP
        if not client.ICP:
            self.PayloadLoggingMetaNames = PayloadLoggingMetaNames()

    def _deployment_status_errors_handling(self, deployment_details, operation_name):
        try:
            if 'status_details' in deployment_details['entity']:
                errors = deployment_details[u'entity'][u'status_details'][u'failure'][u'errors']
                for error in errors:
                    if type(error) == str:
                        try:
                            error_obj = json.loads(error)
                            print(error_obj[u'message'])
                        except:
                            print(error)
                    elif type(error) == dict:
                        print(error['message'])
                    else:
                        print(error)
                raise WMLClientError('Deployment ' + operation_name + ' failed. Errors: ' + str(errors))
            else:
                print(deployment_details['entity']['status_message'])
                raise WMLClientError('Deployment ' + operation_name + ' failed. Error: ' + str(deployment_details['entity']['status_message']))
        except WMLClientError as e:
            raise e
        except Exception as e:
            self._logger.debug('Deployment ' + operation_name + ' failed: ' + str(e))
            raise WMLClientError('Deployment ' + operation_name + ' failed.')

    def update(self, deployment_uid, name=None, description=None, asynchronous=False, meta_props=None):
        """
            Update model used in deployment to the latest version. The scoring_url remains.
            Name and description change will not work for online deployment.
            For virtual deployments the file will be updated under the same download_url.

            :param deployment_uid:  Deployment UID
            :type deployment_uid: str

            :param name: new name for deployment
            :type name: str

            :param description: new description for deployment
            :type description: str

            :param meta_props: dictionary with parameters used for virtual deployment (Core ML format)
            :type meta_props: dict

            :returns: updated metadata of deployment
            :rtype: dict

            A way you might use me is:

            >>> deployment_details = client.deployments.update(deployment_uid)
            >>> deployment_details = client.deployments.update(deployment_uid, meta_props_names=new_CoreML_parameters)
        """
        if not self._ICP:
            deployment_uid = str_type_conv(deployment_uid)
            Deployments._validate_type(deployment_uid, 'deployment_uid', STR_TYPE, True)

            deployment_details = self.get_details(deployment_uid)
            asset_uid = self._get_required_element_from_dict(deployment_details, 'deployment_details', ['entity', 'deployable_asset', 'guid'])

            response = None

            if name is not None or description is not None:
                patch_payload = []

                if name is not None:
                    patch_payload.append({
                        'op': 'replace',
                        'path': '/name',
                        'value': name
                    })

                if description is not None:
                    patch_payload.append({
                        'op': 'replace',
                        'path': '/description',
                        'value': description
                    })

                url = self._href_definitions.get_deployment_href(deployment_uid)
                if not self._ICP:
                    response = requests.patch(url, json=patch_payload, headers=self._client._get_headers())
                else:
                    response = requests.patch(url, json=patch_payload, headers=self._client._get_headers(), verify=False)

                updated_details = self._handle_response(200, u'deployment patch', response)

                return updated_details

            deployment_type = str(self._get_required_element_from_dict(deployment_details, 'deployment_details', ['entity', 'type'])).lower()

            if 'virtual' in deployment_type:
                deployment_format = str(self._get_required_element_from_dict(deployment_details, 'deployment_details', ['entity', 'format'])).lower()

                if not self._ICP:
                    response = requests.patch(
                        self._href_definitions.get_deployment_href(deployment_uid),
                        headers=self._client._get_headers(),
                        json=[
                            {
                                "op": "replace",
                                "path": "/parameters",
                                "value": convert_metadata_to_parameters(meta_props)
                            }
                        ]
                    )
                else:
                    response = requests.patch(
                        self._href_definitions.get_deployment_href(deployment_uid),
                        headers=self._client._get_headers(),
                        json=[
                            {
                                "op": "replace",
                                "path": "/parameters",
                                "value": convert_metadata_to_parameters(meta_props)
                            }
                        ],
                        verify=False
                    )

                self._handle_response(200, 'updating Core ML version in virtual deployment', response, False)
            else:
                asset_details = self._client.repository.get_details(asset_uid)

                asset_type = self._client.repository._check_artifact_type(asset_uid)
                if asset_type['model']:
                    latest_version_url = self._get_required_element_from_dict(asset_details, 'model_details', ['entity', 'latest_version', 'url'])

                    if not self._ICP:
                         response = requests.patch(
                            self._href_definitions.get_published_model_href(asset_uid),
                            headers=self._client._get_headers(),
                            json=[
                                {
                                    "op": "replace",
                                    "path": "/deployed_version/url",
                                    "value": latest_version_url
                                }
                            ]
                        )
                    else:
                        response = requests.patch(
                            self._href_definitions.get_published_model_href(asset_uid),
                            headers=self._client._get_headers(),
                            json=[
                                {
                                    "op": "replace",
                                    "path": "/deployed_version/url",
                                    "value": latest_version_url
                                }
                            ],
                            verify=False
                        )

                    self._handle_response(200, 'updating artifact version in deployment', response, False)
                elif asset_type['function']:
                    latest_version_url = self._get_required_element_from_dict(asset_details, 'function_details', ['entity', 'function_revision', 'url'])

                    # TODO how to update function version in deployment..?
                else:
                    raise WMLClientError('Error during update of deployment, unexpected artifact type: \'{}\'.'.format(asset_type))

            if not asynchronous:
                if response is not None:
                    if response.status_code == 200:
                        deployment_details = self.get_details(deployment_uid)

                        import time
                        print_text_header_h1(u'Synchronous deployment update for uid: \'{}\' started'.format(asset_uid))

                        status = deployment_details[u'entity'][u'status']

                        with StatusLogger(status) as status_logger:
                            while True:
                                time.sleep(5)
                                deployment_details = self.get_details(deployment_uid)
                                status = deployment_details[u'entity'][u'status']
                                status_logger.log_state(status)

                                if status != u'DEPLOY_IN_PROGRESS' and status != u'UPDATE_IN_PROGRESS':
                                    break

                        if status == u'DEPLOY_SUCCESS' or status == u'UPDATE_SUCCESS':
                            print(u'')
                            print_text_header_h2(
                                u'Successfully finished deployment update, deployment_uid=\'{}\''.format(deployment_uid))
                            return deployment_details
                        else:
                            print_text_header_h2(u'Deployment update failed')
                            self._deployment_status_errors_handling(deployment_details, 'update')
                    else:
                        error_msg = u'Deployment update failed'
                        reason = response.text
                        print(reason)
                        print_text_header_h2(error_msg)
                        raise WMLClientError(error_msg + u'. Error: ' + str(response.status_code) + '. ' + reason)

            return self.get_details()
        else:
            deployment_uid = str_type_conv(deployment_uid)
            Deployments._validate_type(deployment_uid, 'deployment_uid', STR_TYPE, True)

            deployment_details = self.get_details(deployment_uid)
            asset_uid = self._get_required_element_from_dict(deployment_details, 'deployment_details', ['entity', 'deployable_asset', 'guid'])

            response = None

            if name is not None or description is not None:
                patch_payload = []

                if name is not None:
                    patch_payload.append({
                        'op': 'replace',
                        'path': '/name',
                        'value': name
                    })

                if description is not None:
                    patch_payload.append({
                        'op': 'replace',
                        'path': '/description',
                        'value': description
                    })

                url = self._href_definitions.get_deployment_href(deployment_uid)
                if not self._ICP:
                    response = requests.patch(url, json=patch_payload, headers=self._client._get_headers())
                else:
                    response = requests.patch(url, json=patch_payload, headers=self._client._get_headers(), verify=False)

                updated_details = self._handle_response(200, u'deployment patch', response)

                return updated_details

            deployment_type = str(self._get_required_element_from_dict(deployment_details, 'deployment_details', ['entity', 'type'])).lower()

            if 'virtual' in deployment_type:
                raise NoVirtualDeploymentSupportedForICP()
            else:
                asset_details = self._client.repository.get_details(asset_uid)

                asset_type = self._client.repository._check_artifact_type(asset_uid)
                if asset_type['model']:
                    latest_version_url = self._get_required_element_from_dict(asset_details, 'model_details', ['entity', 'latest_version', 'url'])

                    if not self._ICP:
                        response = requests.patch(
                            self._href_definitions.get_published_model_href(asset_uid),
                            headers=self._client._get_headers(),
                            json=[
                                {
                                    "op": "replace",
                                    "path": "/deployed_version/url",
                                    "value": latest_version_url
                                }
                            ]
                        )
                    else:
                        response = requests.patch(
                            self._href_definitions.get_published_model_href(asset_uid),
                            headers=self._client._get_headers(),
                            json=[
                                {
                                    "op": "replace",
                                    "path": "/deployed_version/url",
                                    "value": latest_version_url
                                }
                            ],
                            verify=False
                        )

                    self._handle_response(200, 'updating artifact version in deployment', response, False)
                elif asset_type['function']:
                    latest_version_url = self._get_required_element_from_dict(asset_details, 'function_details', ['entity', 'function_revision', 'url'])

                    # TODO how to update function version in deployment..?
                else:
                    raise WMLClientError('Error during update of deployment, unexpected artifact type: \'{}\'.'.format(asset_type))

            if not asynchronous:
                if response is not None:
                    if response.status_code == 200:
                        deployment_details = self.get_details(deployment_uid)

                        import time
                        print_text_header_h1(u'Synchronous deployment update for uid: \'{}\' started'.format(asset_uid))

                        status = deployment_details[u'entity'][u'status']

                        with StatusLogger(status) as status_logger:
                            while True:
                                time.sleep(5)
                                deployment_details = self.get_details(deployment_uid)
                                status = deployment_details[u'entity'][u'status']
                                status_logger.log_state(status)

                                if status != u'DEPLOY_IN_PROGRESS' and status != u'UPDATE_IN_PROGRESS':
                                    break

                        if status == u'DEPLOY_SUCCESS' or status == u'UPDATE_SUCCESS':
                            print(u'')
                            print_text_header_h2(
                                u'Successfully finished deployment update, deployment_uid=\'{}\''.format(deployment_uid))
                            return deployment_details
                        else:
                            print_text_header_h2(u'Deployment update failed')
                            self._deployment_status_errors_handling(deployment_details, 'update')
                    else:
                        error_msg = u'Deployment update failed'
                        reason = response.text
                        print(reason)
                        print_text_header_h2(error_msg)
                        raise WMLClientError(error_msg + u'. Error: ' + str(response.status_code) + '. ' + reason)

            return self.get_details()


    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_details(self, deployment_uid=None, limit=None):
        """
           Get information about your deployment(s).

           :param deployment_uid:  Deployment UID (optional)
           :type deployment_uid: {str_type}

           :param limit: limit number of fetched records (optional)
           :type limit: int

           :returns: metadata of deployment(s)
           :rtype: dict

           A way you might use me is:

            >>> deployment_details = client.deployments.get_details(deployment_uid)
            >>> deployment_details = client.deployments.get_details(deployment_uid=deployment_uid)
            >>> deployments_details = client.deployments.get_details()
        """
        deployment_uid = str_type_conv(deployment_uid)
        Deployments._validate_type(deployment_uid, u'deployment_uid', STR_TYPE, False)

        if deployment_uid is not None and not is_uid(deployment_uid):
            raise WMLClientError(u'\'deployment_uid\' is not an uid: \'{}\''.format(deployment_uid))

        url = self._href_definitions.get_deployments_href()

        return self._get_artifact_details(url, deployment_uid, limit, 'deployments')

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_status(self, deployment_uid):
        """
            Get status of deployment creation.

            :param deployment_uid: Guid of deployment
            :type deployment_uid: {str_type}

            :returns: status of deployment creation
            :rtype: {str_type}

            A way you might use me is:

             >>> status = client.deployments.get_status(deployment_uid)
        """
        deployment_uid = str_type_conv(deployment_uid)
        Deployments._validate_type(deployment_uid, u'deployment_uid', STR_TYPE, True)

        details = self.get_details(deployment_uid)
        return self._get_required_element_from_dict(details, u'deployment_details', [u'entity', u'status'])

    @docstring_parameter({'str_type': STR_TYPE_NAME}) # TODO model_uid and artifact_uid should be changed to artifact_uid only
    def create(self, artifact_uid=None, name=u'Artifact deployment', description=u'Description of deployment', asynchronous=False, deployment_type=u'online', deployment_format='Core ML', meta_props=None, **kwargs):
        """
            Create deployment (online) from artifact. As artifact we understand model or function which may be deployed.

            :param artifact_uid:  Published artifact UID (model or function UID)
            :type artifact_uid: {str_type}
            :param name: Deployment name
            :type name: {str_type}
            :param description: Deployment description
            :type description: {str_type}
            :param asynchronous: if `False` then will wait until deployment will be fully created before returning
            :type asynchronous: bool
            :param deployment_type: type of deployment ('online', 'virtual'). Default one is 'online'
            :type deployment_type: {str_type}
            :param deployment_format: file format of virtual deployment. Currently supported is 'Core ML' only (default value)
            :type deployment_format: {str_type}
            :param meta_props: dictionary with parameters used for virtual deployment (Core ML format)
            :type meta_props: dict

            :returns: details of created deployment
            :rtype: dict

            A way you might use me is:

             >>> online_deployment = client.deployments.create(model_uid, 'Deployment X', 'Online deployment of XYZ model.')
             >>> virtual_deployment = client.deployments.create(model_uid, 'Deployment A', 'Virtual deployment of XYZ model.', deployment_type='virtual')
         """
        artifact_uid = str_type_conv(artifact_uid) if artifact_uid is not None else (str_type_conv(kwargs['model_uid'] if 'model_uid' in kwargs else None))
        Deployments._validate_type(artifact_uid, u'artifact_uid', STR_TYPE, True)
        name = str_type_conv(name)
        Deployments._validate_type(name, u'name', STR_TYPE, True)
        description = str_type_conv(description)
        Deployments._validate_type(description, u'description', STR_TYPE, True)

        if self._ICP:
            predictionUrl = self._wml_credentials[u'url'].replace('31002','32006')

        artifact_type = self._client.repository._check_artifact_type(artifact_uid)

        if not self._ICP:
            if artifact_type["model"]:
                if 'online'.lower() in str(deployment_type).lower():
                    response = self._create_online(model_uid=artifact_uid, name=name, description=description)
                elif 'virtual'.lower() in str(deployment_type).lower() and ('Core ML'.lower() in str(deployment_format).lower()):
                    response = self._create_virtual(model_uid=artifact_uid, name=name, description=description, deployment_format=deployment_format, meta_props=meta_props)
                else:
                    raise WMLClientError(u'Deployment creation failed. Unsupported deployment type/format:' + str(deployment_type) + u'/' + str(deployment_format))
            elif artifact_type["function"]:
                response = self._create_function_deployment(function_uid=artifact_uid, name=name, description=description)
            else:
                raise WMLClientError('Invalid set artifact_type: {}'.format(artifact_type))
        else:
            if artifact_type["model"]:
                if 'online'.lower() in str(deployment_type).lower():
                    response = self._create_online(model_uid=artifact_uid, name=name, description=description)
                #elif 'virtual'.lower() in str(deployment_type).lower() and ('Core ML'.lower() in str(deployment_format).lower()):
                    #response = self._create_virtual(model_uid=artifact_uid, name=name, description=description, deployment_format=deployment_format, meta_props=meta_props)
                else:
                    raise WMLClientError(u'Deployment creation failed. Unsupported deployment type/format:' + str(deployment_type) + u'/' + str(deployment_format))
            elif artifact_type["function"]:
                response = self._create_function_deployment(function_uid=artifact_uid, name=name, description=description)
            else:
                raise WMLClientError('Invalid set artifact_type: {}'.format(artifact_type))

        if asynchronous:
            if response.status_code == 202:
                deployment_details = response.json()
                if self._ICP:
                    scoringUrl = deployment_details.get(u'entity').get(u'scoring_url').replace('https://wml-os-envoy:16600', predictionUrl)
                    deployment_details[u'entity'][u'scoring_url'] = scoringUrl
                deployment_uid = self.get_uid(deployment_details)
                print_text_header_h1(u'Asynchronous deployment creation for uid: \'{}\' started'.format(artifact_uid))
                print(u'To monitor status of your deployment use: client.deployments.get_status(\"{}\")'.format(deployment_uid))
                print(u'Scoring url for this deployment: \"{}\"'.format(self.get_scoring_url(deployment_details)))
                return deployment_details
            else:
                response = response.json()
                if self._ICP:
                    scoringUrl = response.get(u'entity').get(u'scoring_url').replace('https://wml-os-envoy:16600', predictionUrl)
                    response[u'entity'][u'scoring_url'] = scoringUrl
                return self._handle_response(201, u'deployment creation', response)
        else:
            if response.status_code == 202:
                deployment_details = response.json()
                if self._ICP:
                    scoringUrl = deployment_details.get(u'entity').get(u'scoring_url').replace('https://wml-os-envoy:16600', predictionUrl)
                    deployment_details[u'entity'][u'scoring_url'] = scoringUrl
                deployment_uid = self.get_uid(deployment_details)

                import time
                print_text_header_h1(u'Synchronous deployment creation for uid: \'{}\' started'.format(artifact_uid))

                status = deployment_details[u'entity'][u'status']

                with StatusLogger(status) as status_logger:
                    while True:
                        time.sleep(5)
                        deployment_details = self._client.deployments.get_details(deployment_uid)
                        if self._ICP:
                            scoringUrl = deployment_details.get(u'entity').get(u'scoring_url').replace('https://wml-os-envoy:16600', predictionUrl)
                            deployment_details[u'entity'][u'scoring_url'] = scoringUrl
                        status = deployment_details[u'entity'][u'status']
                        status_logger.log_state(status)

                        if status != u'DEPLOY_IN_PROGRESS':
                            break

                if status == u'DEPLOY_SUCCESS':
                    print(u'')
                    print_text_header_h2(u'Successfully finished deployment creation, deployment_uid=\'{}\''.format(deployment_uid))
                    return deployment_details
                else:
                    print_text_header_h2(u'Deployment creation failed')
                    self._deployment_status_errors_handling(deployment_details, 'creation')
            elif response.status_code == 201:
                deployment_details = response.json()
                if self._ICP:
                    scoringUrl = deployment_details.get(u'entity').get(u'scoring_url').replace('https://wml-os-envoy:16600', predictionUrl)
                    deployment_details[u'entity'][u'scoring_url'] = scoringUrl
                deployment_uid = self.get_uid(deployment_details)
                print_text_header_h1(u'Synchronous deployment creation for uid: \'{}\' started'.format(artifact_uid))
                print(u'DEPLOY_SUCCESS')
                print_text_header_h2(u'Successfully finished deployment creation, deployment_uid=\'{}\''.format(deployment_uid))
                return deployment_details
            elif response.status_code == 303:
                deployment_details = response.json()
                if self._ICP:
                    scoringUrl = deployment_details.get(u'entity').get(u'scoring_url').replace('https://wml-os-envoy:16600', predictionUrl)
                    deployment_details[u'entity'][u'scoring_url'] = scoringUrl
                deployment_uid = self.get_uid(deployment_details)
                print_text_header_h2(
                    u'Deployment already exists, deployment_uid=\'{}\''.format(deployment_uid))
                return deployment_details
            elif response.status_code == 200:
                # TODO it should be 303 but 200 is returned ... this elif should be removed when 303
                deployment_details = response.json()
                if self._ICP:
                    scoringUrl = deployment_details.get(u'entity').get(u'scoring_url').replace('https://wml-os-envoy:16600', predictionUrl)
                    deployment_details[u'entity'][u'scoring_url'] = scoringUrl
                deployment_uid = self.get_uid(deployment_details)
                print_text_header_h2(
                    u'Deployment already exists, deployment_uid=\'{}\''.format(deployment_uid))
                return deployment_details
            else:
                error_msg = u'Deployment creation failed'
                reason = response.text
                print(reason)
                print_text_header_h2(error_msg)
                raise WMLClientError(error_msg + '. Error: ' + str(response.status_code) + '. ' + reason)

    def _create_online(self, model_uid, name, description):
        """
            Create online deployment.
        """
        url = self._href_definitions.get_deployments_href() + '?sync=false'

        if not self._ICP:
            response = requests.post(
                url,
                json={
                    u'name': name,
                    u'description': description,
                    u'type': u'online',
                    u'deployable_asset_url': self._href_definitions.get_published_model_href(model_uid)
                },
                headers=self._client._get_headers())
        else:
            response = requests.post(
                url,
                json={
                    u'name': name,
                    u'description': description,
                    u'type': u'online',
                    u'deployable_asset_url': self._href_definitions.get_published_model_href(model_uid)
                },
                headers=self._client._get_headers(),
                verify=False)

        return response

    def _create_virtual(self, model_uid, name='Virtual deployment', description='Virtual deployment description', deployment_format='Core ML', meta_props=None):
        """
            Creates virtual deployment.
        """

        url = self._href_definitions.get_deployments_href() + '?sync=false'

        if not self._ICP:
            response = requests.post(
                url,
                json={
                    u'name': name,
                    u'description': description,
                    u'type': u'virtual',
                    u'format': deployment_format,
                    u'parameters': convert_metadata_to_parameters(meta_props),
                    u'deployable_asset_url': self._href_definitions.get_published_model_href(model_uid)
                },
                headers=self._client._get_headers())
        else:
            response = requests.post(
                url,
                json={
                    u'name': name,
                    u'description': description,
                    u'type': u'virtual',
                    u'format': deployment_format,
                    u'parameters': convert_metadata_to_parameters(meta_props),
                    u'deployable_asset_url': self._href_definitions.get_published_model_href(model_uid)
                },
                headers=self._client._get_headers(),
                verify=False)


        return response

    def _create_function_deployment(self, function_uid, name='function deployment', description='function deployment description'):
        """
            Creates function deployment.
        """

        url = self._href_definitions.get_deployments_href() + '?sync=false'

        if not self._ICP:
            response = requests.post(
                url,
                json={
                    u'name': name,
                    u'description': description,
                    u'type': u'online',
                    u'deployable_asset_url': self._href_definitions.get_function_href(function_uid)
                },
                headers=self._client._get_headers())
        else:
            response = requests.post(
                url,
                json={
                    u'name': name,
                    u'description': description,
                    u'type': u'online',
                    u'deployable_asset_url': self._href_definitions.get_function_href(function_uid)
                },
                headers=self._client._get_headers(),
                verify=False)

        return response

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_scoring_url(deployment):
        """
            Get scoring_url from deployment details.

            :param deployment: Created deployment details
            :type deployment: dict

            :returns: scoring endpoint URL that is used for making scoring requests
            :rtype: {str_type}

            A way you might use me is:

             >>> scoring_url = client.deployments.get_scoring_url(deployment)
        """
        Deployments._validate_type(deployment, u'deployment', dict, True)
        Deployments._validate_type_of_details(deployment, DEPLOYMENT_DETAILS_TYPE)

        try:
            url = deployment.get(u'entity').get(u'scoring_url')
        except Exception as e:
            raise WMLClientError(u'Getting scoring url for deployment failed.', e)

        if url is None:
            raise MissingValue(u'entity.scoring_url')

        return url

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_uid(deployment_details):
        """
            Get deployment_uid from deployment details.

            :param deployment_details: Created deployment details
            :type deployment_details: dict

            :returns: deployment UID that is used to manage the deployment
            :rtype: {str_type}

            A way you might use me is:

            >>> deployment_uid = client.deployments.get_uid(deployment)
        """
        Deployments._validate_type(deployment_details, u'deployment_details', dict, True)
        Deployments._validate_type_of_details(deployment_details, DEPLOYMENT_DETAILS_TYPE)

        try:
            uid = deployment_details.get(u'metadata').get(u'guid')
        except Exception as e:
            raise WMLClientError(u'Getting deployment uid from deployment details failed.', e)

        if uid is None:
            raise MissingValue(u'deployment_details.metadata.guid')

        return uid

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_url(deployment_details):
        """
            Get deployment_url from deployment details.

            :param deployment_details:  Created deployment details
            :type deployment_details: dict

            :returns: deployment URL that is used to manage the deployment
            :rtype: {str_type}

            A way you might use me is:

            >>> deployment_url = client.deployments.get_url(deployment)
        """
        Deployments._validate_type(deployment_details, u'deployment_details', dict, True)
        Deployments._validate_type_of_details(deployment_details, DEPLOYMENT_DETAILS_TYPE)

        try:
            url = deployment_details.get(u'metadata').get(u'url')
        except Exception as e:
            raise WMLClientError(u'Getting deployment url from deployment details failed.', e)

        if url is None:
            raise MissingValue(u'deployment_details.metadata.url')

        return url

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_download_url(deployment_details):
        """
            Get deployment_download_url from deployment details.

            :param deployment_details:  Created deployment details
            :type deployment_details: dict

            :returns: deployment download URL that is used to get file deployment (for example: Core ML)
            :rtype: {str_type}

            A way you might use me is:

            >>> deployment_url = client.deployments.get_download_url(deployment)
        """
        Deployments._validate_type(deployment_details, u'deployment_details', dict, True)
        Deployments._validate_type_of_details(deployment_details, DEPLOYMENT_DETAILS_TYPE)

        try:
            url = deployment_details.get(u'entity').get(u'download_details').get(u'url')
        except Exception as e:
            raise WMLClientError(u'Getting download url from deployment details failed.', e)

        if url is None:
            raise MissingValue(u'deployment_details.entity.download_details.url')

        return url

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete(self, deployment_uid):
        """
            Delete deployment.

            :param deployment_uid: Deployment UID
            :type deployment_uid: {str_type}

            A way you might use me is:

            >>> client.deployments.delete(deployment_uid)
        """
        deployment_uid = str_type_conv(deployment_uid)
        Deployments._validate_type(deployment_uid, u'deployment_uid', STR_TYPE, True)

        if deployment_uid is not None and not is_uid(deployment_uid):
            raise WMLClientError(u'\'deployment_uid\' is not an uid: \'{}\''.format(deployment_uid))

        deployment_url = self._href_definitions.get_deployment_href(deployment_uid)

        if not self._ICP:
            response_delete = requests.delete(
                deployment_url,
                headers=self._client._get_headers())
        else:
            response_delete = requests.delete(
                deployment_url,
                headers=self._client._get_headers(),
                verify=False)

        self._handle_response(204, u'deployment deletion', response_delete, False)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def score(self, scoring_url, payload, transaction_id=None):
        """
            Make scoring requests against deployed artifact.

            :param scoring_url:  scoring endpoint URL
            :type scoring_url: {str_type}
            :param payload: records to score
            :type payload: dict
            :param transaction_id: transaction id to be passed with records during payload logging (optional)
            :type transaction_id: {str_type}

            :returns: scoring result containing prediction and probability
            :rtype: dict

            A way you might use me is:

            >>> scoring_payload = {'fields': ['GENDER','AGE','MARITAL_STATUS','PROFESSION'], 'values': [['M',23,'Single','Student'],['M',55,'Single','Executive']]}
            >>> predictions = client.deployments.score(scoring_url, scoring_payload)
        """
        scoring_url = str_type_conv(scoring_url)
        Deployments._validate_type(scoring_url, u'scoring_url', STR_TYPE, True)
        Deployments._validate_type(payload, u'payload', dict, True)

        headers = self._client._get_headers()

        if transaction_id is not None:
            headers.update({'x-global-transaction-id': transaction_id})
        # making change - connection keep alive

        if not self._ICP:
            response_scoring = self.session.post(
                scoring_url,
                json=payload,
                headers=headers)
        else:
            response_scoring = self.session.post(
                scoring_url,
                json=payload,
                headers=headers,
                verify=False)

        return self._handle_response(200, u'scoring', response_scoring)

    def _get_deployable_asset_type(self, details):
        url = details[u'entity'][u'deployable_asset']['url']
        if 'model' in url:
            return 'model'
        elif 'function' in url:
            return 'function'
        else:
            return 'unknown'

    def list(self, limit=None):
        """
           List deployments. If limit is set to None there will be only first 50 records shown.

           :param limit: limit number of fetched records (optional)
           :type limit: int

           A way you might use me is:

           >>> client.deployments.list()
        """
        details = self.get_details()
        resources = details[u'resources']
        values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'entity'][u'type'], m[u'entity'][u'status'],
                   m[u'metadata'][u'created_at'], m[u'entity'][u'model_type'],
                   self._get_deployable_asset_type(m)) for m in resources]

        self._list(values, [u'GUID', u'NAME', u'TYPE', u'STATE', u'CREATED', u'FRAMEWORK', u'ARTIFACT TYPE'], limit, 50)

    def get_uids(self):
        """
            Get all deployments uids.

            :returns: list of uids
            :rtype: list of strings

            A way you might use me is:

            >>> deployments_uids = client.deployments.get_uids()
        """
        details = self.get_details()
        resources = details[u'resources']
        uids = []

        for x in resources:
            uids.append(x['metadata']['guid'])

        return uids

    def download(self, virtual_deployment_uid, filename=None):
        """
            Downloads file deployment of specified UID. Currently supported format is Core ML.

            :param virtual_deployment_uid:  UID of virtual deployment
            :type virtual_deployment_uid: {str_type}
            :param filename: filename of downloaded archive (optional)
            :type filename: {str_type}

            :returns: path to downloaded file
            :rtype: {str_type}
        """

        if not self._ICP:
            virtual_deployment_uid = str_type_conv(virtual_deployment_uid)
            Deployments._validate_type(virtual_deployment_uid, u'deployment_uid', STR_TYPE, False)

            if virtual_deployment_uid is not None and not is_uid(virtual_deployment_uid):
                raise WMLClientError(u'\'deployment_uid\' is not an uid: \'{}\''.format(virtual_deployment_uid))

            details = self.get_details(virtual_deployment_uid)
            download_url = self.get_download_url(details)

            if not self._ICP:
                response_get = requests.get(
                    download_url,
                    headers=self._client._get_headers())
            else:
                response_get = requests.get(
                    download_url,
                    headers=self._client._get_headers(),
                    verify=False)

            if filename is None:
                filename = 'mlartifact.tar.gz'

            if response_get.status_code == 200:
                with open(filename, "wb") as new_file:
                    new_file.write(response_get.content)
                    new_file.close()

                    print_text_header_h2(
                        u'Successfully downloaded deployment file: ' + str(filename))

                    return filename
            else:
                raise WMLClientError(u'Unable to download deployment content: ' + response_get.text)
        else:
            raise NoVirtualDeploymentSupportedForICP()
