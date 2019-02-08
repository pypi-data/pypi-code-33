# coding=utf-8
from __future__ import print_function
import json as json_import
import time
import logging
import requests
from retry import retry
from ibm_ai_openscale_cli.utility_classes.utils import get_error_message

DEFAULT_RESOURCE_GROUP_URL = 'https://resource-manager.bluemix.net'
DEFAULT_URL = 'https://resource-controller.bluemix.net'
ROLE_WRITER = 'Writer'
REGION_ID = 'us-south'

logger = logging.getLogger(__name__)
class ResourceController(object):
    def __init__(self, access_token, url=DEFAULT_URL, resourceGroupUrl=DEFAULT_RESOURCE_GROUP_URL):
        self.access_token = access_token
        self.url = url
        self.resourceGroupUrl = resourceGroupUrl

    def _request(self, method, url, headers=None, params=None, data=None, json_data=None, accept_json=True, **kwargs):
        full_url = self.url + url if url.startswith('/') else url

        headers = {} if headers is None else headers
        headers.update({
            'Authorization': 'Bearer {0}'.format(self.access_token)
        })
        if accept_json:
            headers['accept'] = 'application/json'

        if not data and json_data is not None:
            data = json_import.dumps(json_data)
            headers.update({'content-type': 'application/json'})

        response = requests.request(method=method, url=full_url,
                                    headers=headers, params=params,
                                    data=data, **kwargs)

        if 200 <= response.status_code <= 299:
            return response.json() if accept_json else response.text

        raise Exception(get_error_message(response))

    def list_resource_group(self, account_id=None):
        logger.debug('ResourceController.list_resource_group()')
        params = {'account_id': account_id} if account_id else {}
        response = self._request(
            method='GET',
            url='{0}/v2/resource_groups'.format(self.resourceGroupUrl),
            params=params)

        return response['resources']

    def get_default_resource_group(self, account_id=None):
        logger.debug('ResourceController.get_default_resource_group()')
        resource_groups = self.list_resource_group(account_id=account_id)
        resource_groups = [r['id'] for r in resource_groups if r['default']]
        return resource_groups[0] if resource_groups else None

    def get_resource_group_by_name(self, name):
        logger.debug('ResourceController.get_resource_group_by_name()')
        resource_groups = self.list_resource_group()
        resource_groups = [r['id'] for r in resource_groups if r['name'] == name]
        return resource_groups[0] if resource_groups else None

    def create_instance(self, name, target, resource_group, resource_plan_id):
        logger.debug('ResourceController.create_instance()')
        data = {
            'name': name,
            'target': target,
            'resource_group': resource_group,
            'resource_plan_id': resource_plan_id,
            'tags': ['self-created']
        }
        response = self._request(
            method='POST',
            url='/v2/resource_instances',
            json_data=data)

        return response

    def list_instances(self, resource_id=None):
        logger.debug('ResourceController.list_instances()')
        params = {'resource_id': resource_id} if resource_id else {}
        response = self._request(
            method='GET',
            url='/v2/resource_instances',
            params=params)

        return response

    def delete_instance(self, guid, recursive=True):
        logger.debug('ResourceController.delete_instance()')
        response = self._request(
            method='DELETE',
            accept_json=False,
            params={'recursive': recursive},
            url='/v2/resource_instances/{0}'.format(guid))

        return response

    def create_instance_key(self, source, role):
        logger.debug('ResourceController.create_instance_key()')
        data = {
            'name': 'aios-fastpath-credentials',
            'source': source,
            'role': role
        }
        response = self._request(
            method='POST',
            url='/v2/resource_keys',
            json_data=data)

        return response

    def list_instance_keys(self, guid):
        logger.debug('ResourceController.list_instance_keys()')
        response = self._request(
            method='GET',
            url='/v2/resource_instances/{0}/resource_keys'.format(guid))

        return response

    def delete_instance_key(self, guid):
        logger.debug('ResourceController.delete_instance_key()')
        response = self._request(
            method='DELETE',
            url=self.url + '/v2/resource_keys/{0}'.format(guid),
            accept_json=False)

        return response

    @retry(tries=5, delay=1, backoff=2)
    def get_or_create_instance(self, resource_id, resource_name=None, resource_plan_id=None, resource_group=None, resource_group_name=None, create_credentials=True, target='us-south'):
        """Returns a service instance.
        If there is no instance available, a new one is provisioned.
        If there is no existing service key, a new one is created.

        Arguments:
            resource_id {string} -- The resource_id that identifies the service in the global catalog
            resource_plan_id {string} -- resource plan id. spark and compose-for-postgres plans are constants in this module
            resource_group {string} -- resource group id.
            resource_group_name {string} -- resource group name.
            create_credentials {boolean} -- If True, credentials will be created if they don't exist
        Returns:
            dict -- The service instance with valid credentials, dictionary with: id, name, created_at and credentials
        """
        logger.debug('ResourceController.get_or_create_instance()')
        instances = self.list_instances(resource_id=resource_id)
        instance = instances['resources'][0] if instances['resources'] else None

        if not instance:
            if resource_group_name:
                resource_group = self.get_resource_group_by_name(resource_group_name)
            if not resource_group:
                resource_group = self.get_default_resource_group()

            name = resource_name if resource_name else 'aios-{0}-{1}'.format(resource_id, time.time())
            instance = self.create_instance(
                name=name,
                target=target,
                resource_group=resource_group,
                resource_plan_id=resource_plan_id)

        if create_credentials:
            keys = self.list_instance_keys(instance['guid'])
            key = None
            if keys['resources']:
                for resource in keys['resources']:
                    if resource['name'] == 'aios-fastpath-credentials':
                        key = resource
                        break

            if not key:
                key = self.create_instance_key(
                    source=instance['guid'],
                    role=ROLE_WRITER
                )
            instance['credentials'] = key['credentials']
        else:
            instance['credentials'] = None

        return {
            'id': instance['guid'],
            'crn': instance['id'],
            'name': instance['name'],
            'created_at': instance['created_at'],
            'credentials': instance['credentials']
        }

    def __str__(self):
        return 'ResourceController: url: {1}, access_token: {0}'.format(self.url, self.access_token[:5])
