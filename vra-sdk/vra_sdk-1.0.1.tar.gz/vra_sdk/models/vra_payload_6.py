# -*- coding: utf-8 -*-
from vra_sdk.models.vra_object import VraBaseObject
from vra_sdk.vra_config import VraConfig
from vra_sdk.vra_exceptions import VraSdkRequestException, VraSdkPayloadException
from vra_sdk.vra_utils import load_payload_file
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
            payload['catalogItemRef']['id'] = kwargs['catalog_item_id']
            payload['requestedFor'] = kwargs['requested_for']
        else:
            payload['resourceRef']['id'] = kwargs['resource_id']
            payload['resourceActionRef']['id'] = kwargs['resource_action_id']

        payload['organization']['tenantRef'] = kwargs['tenant_name']
        payload['organization']['tenantLabel'] = kwargs['tenant_name']
        payload['organization']['subtenantRef'] = kwargs['business_group_id']
        payload['organization']['subtenantLabel'] = kwargs['business_group_name']

        for k, v in kwargs.items():
            if k not in self.config.config_file['not_in_data']:
                provider_k = k
                if not k.startswith('provider-'):
                    provider_k = 'provider-' + provider_k
                if isinstance(v, str):
                    payload['requestData']['entries'].append(
                        {"key": provider_k, "value": {"type": "string", "value": v}})
                elif isinstance(v, (int, float)):
                    payload['requestData']['entries'].append(
                        {"key": provider_k, "value": {"type": "decimal", "value": v}})
        return payload


class CatalogItem(BasePayload):

    def __init__(self, customization_func=None, **kwargs):
        """Init the CatalogItem for vRa 6.x payload object
            customization_func ([type], optional): Defaults to None. If not None, this function will add a second customization after the initial one.
        """

        super().__init__()
        self.customized = None
        if not kwargs.get('payload_path'):
            self.base = {
                "@type": "CatalogItemRequest",
                "catalogItemRef": {
                    "id": ""
                },
                "organization": {
                    "tenantRef": "",
                    "subtenantRef": ""
                },
                "requestedFor": "",
                "state": "SUBMITTED",
                "requestNumber": 0,
                "requestData": {
                    "entries": [
                    ]
                }
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
                f"https://{self.config.vcac_server}/catalog-service/api/consumer/requests",
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
        """Init ResourceAction object for vRa 6.x payload object
            customization_func ([type], optional): Defaults to None. If not None, this function will add a second customization after the initial one.
        """

        super().__init__()
        self.customized = None
        if not kwargs.get('payload_path'):
            self.base = {
                "@type": "ResourceActionRequest",
                "resourceRef": {
                    "id": ""
                },
                "resourceActionRef": {
                    "id": ""
                },
                "organization": {
                    "tenantRef": "",
                    "tenantLabel": "",
                    "subtenantRef": "",
                    "subtenantLabel": ""
                },
                "state": "SUBMITTED",
                "requestNumber": 0,
                "requestData": {
                    "entries": [
                    ]
                }
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
                f"https://{self.config.vcac_server}/catalog-service/api/consumer/requests",
                data=json.dumps(self.customized),
                verify=self.config.verify,
                timeout=self.config.timeout)
            req.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise VraSdkRequestException(
                f'vRa request exception : {e}')
        except Exception as e:
            raise VraSdkPayloadException(
                f'Unmanaged error requesting vRa: {e}')
