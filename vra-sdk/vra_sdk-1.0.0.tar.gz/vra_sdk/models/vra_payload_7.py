# -*- coding: utf-8 -*-
from vra_sdk.models.vra_object import VraBaseObject
from vra_sdk.vra_config import VraConfig
from vra_sdk.vra_utils import load_payload_file
from vra_sdk.vra_exceptions import VraSdkRequestException, VraSdkPayloadException
import requests
import json


class BasePayload():
    """Base class for CatalogItem and ResourceAction
    """

    def __init__(self):
        self.config = VraConfig()

    def customize_payload(self, payload, **kwargs):
        """base customization payload
        
        Args:
            payload (dict): base payload, without any customization
        
        Returns:
            dict: customized payload
        """

        if kwargs['payload_type'] == 'CatalogItem':
            payload['catalogItemId'] = kwargs['catalog_item_id']
            payload['requestedFor'] = kwargs['requested_for']
            payload['businessGroupId'] = kwargs['business_group_id']
        else:
            payload['actionId'] = kwargs['resource_action_id']
            payload['resourceId'] = kwargs['resource_id']
            if 'description' in kwargs:
                payload['description'] = kwargs['description']

        for key in kwargs.keys():
            if key not in self.config.config_file['not_in_data']:
                payload['data'][key] = kwargs[key]

        return payload


class CatalogItem(BasePayload):

    def __init__(self, customization_func=None, **kwargs):
        """Init ResourceAction object for vRa 7.x payload object
            customization_func ([type], optional): Defaults to None. If not None, this function will add a second customization after the initial one.
        """

        super().__init__()
        self.customized = None
        if not kwargs.get('payload_path'):
            self.base = {
                'type': 'com.vmware.vcac.catalog.domain.request.CatalogItemProvisioningRequest',
                'catalogItemId': '',
                'requestedFor': '',
                'businessGroupId': '',
                'data': {}
            }
        else:
            self.base = load_payload_file(kwargs['payload_path'])

        self.customized = self.customize_payload(self.base, **kwargs)
        if customization_func:
            self.customized = customization_func(self.customized, **kwargs)

    def execute_request(self):
        """Execute the request against the vRa infrastructure
        
        Returns:
            requests.Request: request object
        """

        try:
            req = self.config.session.post(
                f"https://{self.config.vcac_server}/catalog-service/api/consumer/entitledCatalogItems/{self.customized['catalogItemId']}/requests",
                data=json.dumps(self.customized),
                verify=self.config.verify,
                timeout=self.config.timeout)
            req.raise_for_status()
            return req
        except requests.exceptions.RequestException as e:
            raise VraSdkRequestException(
                f'vRa request exception : {e}')
        except Exception as e:
            raise VraSdkPayloadException(
                f'Unmanaged error requesting vRa: {e}')


class ResourceAction(BasePayload):
    def __init__(self, customization_func=None, **kwargs):
        """Init ResourceAction object for vRa 7.x payload object
            customization_func ([type], optional): Defaults to None. If not None, this function will add a second customization after the initial one.
        """

        super().__init__()
        self.customized = None
        if not kwargs.get('payload_path'):
            self.base = {
                'type': 'com.vmware.vcac.catalog.domain.request.CatalogResourceRequest',
                'resourceId': '',
                'actionId': '',
                'description': '',
                'data': {}
            }
        else:
            self.base = load_payload_file(kwargs['payload_path'])

        self.customized = self.customize_payload(self.base, **kwargs)
        if customization_func:
            self.customized = customization_func(self.customized, **kwargs)

    def execute_request(self):
        """Execute the request against the vRa infrastructure
        
        Returns:
            requests.Request: request object
        """

        try:
            req = self.config.session.post(
                f"https://{self.config.vcac_server}/catalog-service/api/consumer/resources/{self.customized['resourceId']}/actions/{self.customized['actionId']}/requests",
                data=json.dumps(self.customized),
                verify=self.config.verify,
                timeout=self.config.timeout)
            req.raise_for_status()
            return req
        except requests.exceptions.RequestException as e:
            raise VraSdkRequestException(
                f'vRa request exception : {e}')
        except Exception as e:
            raise VraSdkPayloadException(
                f'Unmanaged error requesting vRa: {e}')
