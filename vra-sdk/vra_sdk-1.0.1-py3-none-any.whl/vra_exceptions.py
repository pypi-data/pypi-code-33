# -*- coding: utf-8 -*-

class VraSdkException(Exception):
    """Main class exception"""
    pass

class VraSdkRequestException(VraSdkException):
    """for requests.exceptions.RequestException"""
    pass

class VraSdkAuthenticateException(VraSdkException):
    """for vra_authenticate"""
    pass

class VraSdkConfigException(VraSdkException):
    """for explicit configuration file issue"""
    pass

class VraSdkMainConfigException(VraSdkException):
    """for vra_config"""
    pass

class VraSdkMainException(VraSdkException):
    """for vra_sdk"""
    pass

class VraSdkFactoryException(VraSdkException):
    """for vra_factory"""
    pass

class VraSdkEntitlementException(VraSdkException):
    """for explicit entitlement"""
    pass

class VraSdkPayloadException(VraSdkException):
    """for vra_payload_*"""
    pass

class VraSdkUtilsException(VraSdkException):
    """for vra_utils"""
    pass

class VraSdkDecoratorException(VraSdkException):
    """for vra_decorator"""
    pass

class VraSdkMainRequestException(VraSdkException):
    """for vra_request"""
    pass