# -*- coding: utf-8 -*-

import json
import requests
import os
from vra_sdk.vra_decorator import singleton
from vra_sdk.vra_utils import resolve_path
from vra_sdk.vra_exceptions import VraSdkConfigException, VraSdkMainConfigException


@singleton
class VraConfig():
    """Handle configuration loading

    Warning: This class is a singleton created through the vra_sdk.vra_decorator singleton method
     
    Attributes:
        config_file (dict): Serialization of the configuration file
        verify (boolean): Requests verify option behavior
        session (requests.sessions): Requests session object
        vcac_server (string): vRa server
    """

    def __init__(self, config_path=None):
        """Init VraConfig
            config_path (string, optional): Defaults to None. Path to the config file. Relative to the python execution path
        
        Raises:
            VraSdkConfigException: Config file not found
            VraSdkMainConfigException: Unmanaged error
        """

        self.config_file={}
        if config_path:
            try:
                final_config_path = resolve_path(config_path)
                with open(final_config_path, 'r') as f:
                    self.config_file = json.load(f)
            except FileNotFoundError as e:
                raise VraSdkConfigException(f'Config file {final_config_path} not found {e}')
            except Exception as e:
                raise VraSdkMainConfigException(e)

        self.verify = self.config_file.get('verify', True)
        self.timeout = self.config_file.get('timeout', 30)
        self.session = requests.Session()
        self.session.trust_env = False
        self.vcac_server = None
