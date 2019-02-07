#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
***
Module:
***

 Copyright (C) Smart Arcs Ltd, registered in the United Kingdom.
 This file is owned exclusively by Smart Arcs Ltd.
 Unauthorized copying of this file, via any medium is strictly prohibited
 Proprietary and confidential
 Written by Smart Arcs <support@smartarchitects.co.uk>, May 2018
"""
from foxyproxy.csp.base_csp import BaseCryptoService

__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'


class CryptoTestSmartcard(BaseCryptoService):
    def init(self, config=None):
        pass

    def sign(self, alias, fingerprint, password=None, hash_alg=None, sign_alg=None):
        pass

    def aliases(self):
        pass

    def chain(self, alias, sign_alg=None):
        pass

    def reset(self, token):
        # test response, send instead of the CloudFoxy
        response_data = "621A82013883023F008404524F4F5485030079AD8A0105A1038B01019000"
        return response_data

    def apdu(self, token, command):
        response_data = "102030409000"

        return response_data