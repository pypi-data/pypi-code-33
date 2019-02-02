# -*- coding: utf-8 -*-
from functools import wraps
import json
from vra_sdk.vra_exceptions import VraSdkRequestException, VraSdkEntitlementException, VraSdkDecoratorException
import requests


def check_entitlement(func):
    """Check if the requested action/catalog item is in the catalog
    
    Args:
        func (function): request function to checj
    
    Raises:
        VraSdkEntitlementException: Requested action/catalog item is not in the catalog
    
    Returns:
        func: decorated function
    """


    @wraps(func)
    def wrapper(*args, **kwargs):
        # args[0] is the first argument of the decorated function, so it's the self of the decorated function
        if args[1] in args[0].catalog:
            return func(*args, **kwargs)
        else:
            raise VraSdkEntitlementException(
                'You do not have permissions to perform this request')
    return wrapper


def update_catalog_resource_operation(func):
    """Update the catalog to add the resouce action
    
    Args:
        func (function): decorated function
    
    Raises:
        VraSdkRequestException: Raise if any vRa infrastructure connection error
        VraSdkDecoratorException:  Unmanaged error
    
    Returns:
        function: decorated function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # args[0] is the first argument of the decorated function, so it's the self of the decorated function
        # args[1] is the vRa name of the day2 operation
        # args[2] is the id of the resource
        if args[1] not in args[0].catalog:
            try:
                req = args[0].config.session.get(
                    f'https://{args[0].config.vcac_server}/catalog-service/api/consumer/resources/{args[2]}', verify=args[0].config.verify, timeout=args[0].config.timeout)
                req.raise_for_status()
                response = json.loads(req.text)

                for elt in response['operations']:
                    args[0].catalog[elt["name"]] = elt["id"]
            except requests.exceptions.RequestException as e:
                raise VraSdkException(
                    f'Error retrieving resource operation: {e}')
            except Exception as e:
                raise VraSdkDecoratorException(e)
        return func(*args, **kwargs)
    return wrapper


def singleton(cls):
    """Decorator to make singletonclass 
    This decorator doesn't work for classes that implements the __new__ method.
    To re-enable the init of the class, set the _sealed attribute to False
    """

    class SingleClass(cls):
        """ The real singleton. """
        _instance = None
        __module__ = cls.__module__
        __doc__ = cls.__doc__

        def __new__(cls, *args, **kwargs):
            if SingleClass._instance is None:
                SingleClass._instance = super().__new__(cls)
                SingleClass._instance._sealed = False

            return SingleClass._instance

        def __init__(self, *args, **kwargs):
            if not getattr(self, '_sealed', False):
                super().__init__(*args, **kwargs)
                self._sealed = True

    SingleClass.__name__ = cls.__name__
    return SingleClass
