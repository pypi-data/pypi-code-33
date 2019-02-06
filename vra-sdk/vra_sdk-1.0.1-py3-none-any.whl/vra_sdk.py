# -*- coding: utf-8 -*-
import json
import requests
import re
import os
import os.path
import time
import urllib3
from vra_sdk.vra_request import VraRequest
from vra_sdk import vra_decorator, vra_utils
from vra_sdk.vra_config import VraConfig
from vra_sdk.vra_exceptions import VraSdkMainException, VraSdkRequestException
from vra_sdk.vra_factory import VraFactory


class VraSdk():
    """Core class of the library.

    Attributes:
        config (VraConfig): VraConfig object
        business_group (string): current business group name
        business_group_id (string): current business group id
        catalog (dict): map of catalog item/resource action to related vRa id
    """

    def __init__(self, authentication_object, business_group, **kwargs):
        """Init the VraSdk object
        
        Args:
            authentication_object (VraAuthenticate): authentication object
            business_group (string): business group to work on
        """

        urllib3.disable_warnings()
        self.authentication_object = authentication_object
        self.config = VraConfig()
        self.business_group_id = ''
        self.business_group = business_group
        self.catalog = self.get_catalog()

    @property
    def business_group(self):
        """property to get business group name"""
        return self._business_group

    @business_group.setter
    def business_group(self, value):
        """property to set business group name and update the business group id
        
        Args:
            value (string): business group name to set
        """

        self.business_group_id = self.get_bg_id(value)
        self._business_group = value

    def get_bg_id(self, business_group, force_refresh=False):
        """get business group id against vRa infrastructure
        
        Args:
            business_group (string): business group name
            force_refresh (bool, optional): Defaults to False. force the refresh of the business group id
        
        """

        if not self.business_group_id or force_refresh:
            try:
                req = self.config.session.get(
                    f"https://{self.config.vcac_server}/catalog-service/api/consumer/entitledCatalogItems?limit=998",
                    verify=self.config.verify, timeout=self.config.timeout)
                req.raise_for_status()
                response = json.loads(req.text)
            except requests.exceptions.RequestException as e:
                raise VraSdkRequestException(
                    f"Error getting business group id for bg {self.business_group}: {e}")
            except Exception as e:
                raise VraSdkMainException(e)

            if 'content' in response:
                for catalog_item in response['content']:
                    for elt in catalog_item['entitledOrganizations']:
                        if elt["subtenantLabel"] == business_group:
                            return elt['subtenantRef']
                raise VraSdkMainException(
                    f'No entitlement for the account {self.authentication_object.login} in business group {business_group}')
            else:
                raise VraSdkMainException(
                    f'Unable get bg id list. No entitled catalog item for account {self.authentication_object.login}')

    def get_catalog(self):
        """Get the catalog item list from the vRa infrastructure
        
        Returns:
            dict: map of catalog item to vRa id
        """

        catalog = {}
        try:
            req = self.config.session.get(
                f"https://{self.config.vcac_server}/catalog-service/api/consumer/entitledCatalogItems?limit=9999",
                verify=self.config.verify,
                timeout=self.config.timeout)
            req.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise VraSdkRequestException(
                f'Error during retrieving catalog item: {e}')
        except Exception as e:
            raise VraSdkMainException(
                f'Unmanaged error during catalog retrieving: {e}')

        try:
            for elt in json.loads(req.text)['content']:
                catalog[elt['catalogItem']['name']] = elt['catalogItem']['id']
        except Exception as e:
            raise VraSdkMainException(
                f'Error updating the catalog attribute {e}')

        return catalog

    @vra_decorator.check_entitlement
    def request_catalog_item(self, item_name, customization_func=None, **kwargs):
        """create a ready to use Request object to request a catalog item
        
        Args:
            item_name (string): catalog item name
            customization_func (function, optional): Defaults to None. payload customization function
        
        Returns:
            VraRequest: object with the payload attribute well customized
        """

        if not kwargs.get('payload_version'):
            kwargs['payload_version'] = self.config.config_file['payload_default_version']
        payload = self.format_payload(
            'catalog_item', item_name, customization_func, **kwargs)
        return VraRequest(payload)

    @vra_decorator.update_catalog_resource_operation
    @vra_decorator.check_entitlement
    def request_resource_action(self, action_name, resource_id, customization_func=None, **kwargs):
        """create a ready to use Request object to request a resource action
        
        Args:
            action_name (string): resource action name
            resource_id (string): resource id to perform action on
            customization_func (function, optional): Defaults to None. payload customization function
        
        Returns:
            VraRequest: object with the payload attribute well customized
        """
        if not kwargs.get('payload_version'):
            kwargs['payload_version'] = self.config.config_file['payload_default_version']
        payload = self.format_payload(
            'resource_action', action_name, resource_id, customization_func, **kwargs)
        return VraRequest(payload)

    def format_payload(self, origin, *args, **kwargs):
        """Customized request kwargs before using it in the VraFactory class to create a payload object
        
        Args:
            origin (string): origin of the request. 'catalog_item' or 'resource_action'
        
        Returns:
            object: CatalogItem or ResourceAction object from one of the vra_payload_x modulme
        """

        kwargs['requested_for'] = self.authentication_object.requestedFor
        kwargs['business_group_name'] = self.business_group
        kwargs['business_group_id'] = self.business_group_id
        kwargs['tenant_name'] = self.authentication_object.tenant

        if args[0] in self.config.config_file[origin] and self.config.config_file[origin][args[0]].get('payload'):
            kwargs['payload_path'] = self.config.config_file[origin][args[0]].get(
                'payload')

        if origin == 'catalog_item':
            kwargs['catalog_item_name'] = args[0]
            kwargs['catalog_item_id'] = self.catalog[args[0]]
            kwargs['payload_type'] = 'CatalogItem'
            customization_func = args[1]
        elif origin == 'resource_action':
            kwargs['resource_id'] = args[1]
            kwargs['resource_action_name'] = args[0]
            kwargs['resource_action_id'] = self.catalog[args[0]]
            kwargs['payload_type'] = 'ResourceAction'
            customization_func = args[2]

        return VraFactory.factory('payload', customization_func, **kwargs)

    def get_data(self, object_type, key, value):
        """Get data about one catalog resource in vRa. Get detailed info about your object
        
        Args:
            object_type (string): object type as described in the 'business_models' section of the configuration fiel
            key (string): field to filter on
            value (string): value of the field
        
        Returns:
            object: business models object type as described in you configuration file
        """

        data = VraRequest({}).get_object(object_type, key, value, 1,1, True)

        if not data:
            raise VraSdkMainException(
                f'No {object_type} exist with {key}={value}')

        return data[0]

    def list_data(self, object_type, key, value, limit=None, page=1, full=False, recursive=False):
        """Get info about a list of object. Get less details than get_data(), but you still get the id
        
        Args:
            object_type (string): object typre
            key (string): field to filter on
            value (string): value of the field to search on
            limit (int, optional): Defaults to None. maximum result
            page (int, optional): Defaults to 1. vRa result page to get data from
            recursive (bool, optional): Defaults to False. If True, will call itself recursively until there's no more page to get from
        
        Raises:
            VraSdkMainException: [description]
        
        Returns:
            list: list of business models object type as described in you configuration file
        """
        if not limit:
            limit = self.config.config_file['max_vra_result_per_page']

        data = VraRequest({}).get_object(object_type, key, value, limit, page, full)
        if not data:
            raise VraSdkMainException(f'No {object_type} exist with {key}={value}')

        if recursive and (len(data) == limit):
            page = page+1
            data_to_add = self.list_data(object_type, key, value, limit, page, full, recursive)
            data = data + data_to_add
        return data

    def get_raw_definition(self, key, value, resource_type):
        """Return dict used to create object inside the VraFactory

        This methods is a helper. You should use only at the beginning to help you build the object definitions needed for the factrory

        Args:
            key (string): key to search data from
            value (string): value of the key
            resource_type (string): vRa resource type

        Returns:
            dict: dict of user friendly vRa formatted data
        """
        
        return VraRequest({}).get_object(None, key, value, 1, 1, True, resource_type)[0]

