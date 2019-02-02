# -*- coding: utf-8 -*-
import requests
import urllib3
import re
import json
import time
import importlib
from vra_sdk.vra_formatter import format_result
from vra_sdk.vra_utils import get_module_class
from vra_sdk.vra_authenticate import VraConfig
from vra_sdk.vra_factory import VraFactory
from vra_sdk.vra_exceptions import VraSdkConfigException, VraSdkRequestException, VraSdkMainRequestException


class VraRequest():
    """Handle getting data from vRa infrastructure as well as catalog item/resource action request

    Attributes:
        config (VraConfig): VraConfig object
        Payload (vra_payload_x.CatalogItem or vra_payload_x.ResourceAction): Payload object
        status_url (string): url to get the status of the current request
        response (requests.Response): request response
    """

    def __init__(self, payload, **kwargs):
        """Init the VraRequest object
        
        Args:
            payload (CatalogItem or ResourceAction): payload object
        """

        urllib3.disable_warnings()
        self.config = VraConfig()
        self.payload = payload
        self.status_url = 'not set'
        self.response = None

    def format_filters(self, object_type, key, value, resource_type=None):
        """Handle generation of OData url filter
        
        Args:
            object_type (string): type of object ot create filter for
            key (string): field to filter from
            value (string): value of the field to filter
            resource_type (string, optional): Defaults to None. Use only for get_raw_definitions(), use to create a filter without defintions
        
        Returns:
            string: Odata filter
        """

        filters_array = []
        computed = []

        if resource_type is None:

            if object_type not in self.config.config_file["business_models"]:
                raise VraSdkConfigException(
                    "Cannot retrieve resource type associated with your object type, have you declared it in config.json map_resource_type array?")

            try:
                my_module, _ = get_module_class(
                    self.config.config_file["business_models"][object_type]["path"])
            except Exception as e:
                raise VraSdkMainRequestException(f"Error importing module.class {self.config.config_file['business_models'][object_type]} Error:{e}")

            for ref in getattr(my_module, 'RESOURCE_TYPE'):
                computed.append(f"(resourceType/name+eq+'{ref}')")
        else:
            computed.append(f"(resourceType/name+eq+'{resource_type}')")

        if computed:
            filters_array.append("(" + "+or+".join(computed) + ")")

        if key and value:
            filters_array.append("(" + key + "+eq+'" + value + "')")

        result = "$filter=" + \
            "(" + "+and+".join(filters_array) + ")" if filters_array else None
        return result

    def get_status(self):
        """Use the status_url attribute to get the status of the request against the vRa infrastructure
        
        Returns:
            dict: vRa status state
        """

        try:
            req = self.config.session.get(
                self.status_url, verify=self.config.verify, timeout=self.config.timeout)
            res = json.loads(req.text)['state']
            return res
        except requests.exceptions.RequestException as e:
            raise VraSdkRequestException(
                f'Error requesting status url {self.status_url}: {e}')
        except Exception as e:
            raise VraSdkMainRequestException(
                f'Unmanaged error requesting status url {self.status_url}: {e}')

    def execute_async(self):
        """Execute the self.payload object execute_request() method. Set the status_url if there's one in the vRa answer.
        
        Returns:
            self: VraRequest
        """

        self.response = self.payload.execute_request()
        if hasattr(self.response, 'headers'):
            self.status_url = self.response.headers.get(
                'Location', 'NoLocationFound')

        return self

    def execute_sync(self):
        """wrapper of execute_async and retry it until the result if successful or failed
        
        Returns:
            self: VraRequest
        """

        self.execute_async()
        while self.get_status() != 'SUCCESSFUL' and self.get_status() != 'PROVIDER_FAILED':
            time.sleep(3)
        if self.get_status() != 'SUCCESSFUL':
            raise VraSdkMainRequestException('Request failed')
        else:
            return self

    def get_object_raw(self, object_type, key, value, limit, page, full=False, resource_type=None):
        """Get raw catalog resource information from vRa infrastructure
        
        Args:
            object_type (string): type of vRa resource to get data on
            key (string): field to search for
            value (string): value of the field
            limit (int): maximum result per page
            page (int): page to get from result.
            full (bool): If True return the full result
            resource_type (string, optional): Defaults to None. Only used for get_raw_definitions()
        
        Returns:
            dict: raw vRa data
        """

        
        #url_array = [f"limit={str(limit)}",f'page={str(page)}']
        url_array = ["limit=" + str(limit), "page=" + str(page)]
        filters = self.format_filters(object_type, key, value, resource_type)
        if filters:
            url_array.append(filters)
        amp = "&"
        url = f"https://{self.config.vcac_server}/catalog-service/api/consumer/resources/?{amp.join(url_array)}"
        try:
            req = self.config.session.get(
                url, verify=self.config.verify, timeout=self.config.timeout)
            req.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise VraSdkRequestException(
                f'vRa request exception : {e}')
        except Exception as e:
            raise VraSdkMainRequestException(
                f'Unmanaged error requesting vRa: {e}')

        res = req.json()

        if (not object_type and resource_type) or full:
            ids = []
            if key != 'id':
                for elt in res["content"]:
                    ids.append(elt["id"])
            else:
                ids.append(value)

            result = []
            for id in ids:
                url = f"https://{self.config.vcac_server}/catalog-service/api/consumer/resources/{id}"
                try:
                    req = self.config.session.get(
                        url, verify=self.config.verify, timeout=self.config.timeout)
                    req.raise_for_status()
                except requests.exceptions.RequestException as e:
                    raise VraSdkRequestException(
                        f'vRa request exception : {e}')
                except Exception as e:
                    raise VraSdkMainRequestException(
                        f'Unmanaged error requesting vRa: {e}')

                res = req.json()
                result.append(res)
                print(result)
            return result
        else:
            return res['content'] if 'content' in res else []

    def get_object(self, object_type, key, value, limit, page, full=False, resource_type=None):
        """Get raw_data from get_raw_object() and prettify it to then create a list of object using the factory and these data.
        
        Args:
            object_type (string): type of vRa resource to get data on
            key (string): field to search for
            value (string): value of the field
            limit (int): maximum result per page
            page (int): page to get from result.
            resource_type (string, optional): Defaults to None. Only used for get_raw_definitions()
        
        Returns:
            list: list of object type as defined in the business_models configuration section 
        """

        result = []
        object_result = []
        raw_data = self.get_object_raw(object_type, key, value, limit, page, full, resource_type)
        # Contruct dict of result without raw_data
        if raw_data is not None:
            for elt in raw_data:
                result.append(format_result(elt))
            if key and value:
                result = [obj for obj in result if re.match(
                    value, obj.get(key, ""))]
        if resource_type is not None:
            return result

        # Adding raw_data and contruct object array
        if result:
            for i, elt in enumerate(result):
                elt['raw_data'] = raw_data[i]
                object_result.append(VraFactory.factory(object_type, **elt))
            return object_result

    def get_request_result_raw(self):
        """Request vRa to get the status of a specific request based on the status_url
        
        Returns:
            dict: vRa raw data
        """

        try:
            req = self.config.session.get(f"{self.status_url}/resources", verify=self.config.verify, timeout=self.config.timeout)
            req.raise_for_status()
            data = json.loads(req.text)
        except requests.exceptions.RequestException as e:
            raise VraSdkRequestException(
                f'vRa request exception : {e}')
        except Exception as e:
            raise VraSdkMainRequestException(
                f'Unmanaged error requesting vRa: {e}')

        if data.get("content"):
            return data['content'][0]
        else:
            try:
                req = self.config.session.get(f"{self.status_url}/forms/details", verify=self.config.verify, timeout=self.config.timeout)
                req.raise_for_status()
            except requests.exceptions.RequestException as e:
                raise VraSdkRequestException(
                    f'vRa request exception : {e}')
            except Exception as e:
                raise VraSdkMainRequestException(
                    f'Unmanaged error requesting vRa: {e}')
            data = json.loads(req.text)
            return data

    def get_request_result(self):
        """wrapper of get_request_result_raw(). Return the beautify result
        
        Returns:
            dict: vRa beautify result
        """

        return format_result(self.get_request_result_raw())
