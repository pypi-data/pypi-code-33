# -*- coding: utf-8 -*-
from vra_sdk.vra_utils import get_module_class, clean_kwargs_key
from vra_sdk.vra_config import VraConfig
import inspect
from vra_sdk.vra_exceptions import VraSdkFactoryException, VraSdkConfigException


class VraFactory(object):
    """Factory to create specific object class
    """

    
    

    @staticmethod
    def factory(object_type, customization_func=None, **kwargs):
        """Factory to create specific type object
        
        Args:
            object_type (string): Object type to create as defined in the business_models section of the configuration file
            customization_func (func, optional): Defaults to None. For 'payload' type only. Post customization payload processing function
        
        Returns:
            object: object of the 'object_type' type specified in args
        """

        config = VraConfig().config_file
        enforce_id = None

        if object_type == 'payload':
            if all(k in kwargs for k in ("payload_version", "payload_type")):
                str_version = str(kwargs['payload_version'])
                payload_type = kwargs['payload_type']
                object_path = f'vra_sdk.models.vra_payload_{str_version}.{payload_type}'
            else:
                raise VraSdkFactoryException(
                    "Error creating payload object. Missing required parameters")
        elif object_type in config['business_models']:
            object_path = config.get(
                'business_models').get(object_type).get('path')
            if not object_path:
                raise VraSdkFactoryException(
                    f"Error retrieving module_class for {object_type} object type.")
            enforce_id = config['business_models'][object_type].get('enforce_id')
        else:
            raise VraSdkConfigException(
                'Error building vraObject, unknown type')

        _, object_class = get_module_class(object_path)
        id_cards = inspect.signature(object_class).parameters
        cleaned_kwargs = clean_kwargs_key(**kwargs)

        if enforce_id:
            for kwarg in cleaned_kwargs:
                if kwarg not in id_cards:
                    raise VraSdkConfigException(
                        f"Error creating vraObject {object_type}, {kwarg} not authorized by the id card of {object_path}")

        if object_type == 'payload':
            to_return = object_class(customization_func, **cleaned_kwargs)
        else:
            to_return = object_class(**cleaned_kwargs)
        return to_return
