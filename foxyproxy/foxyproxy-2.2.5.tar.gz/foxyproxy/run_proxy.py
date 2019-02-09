# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
***
Module: foxyproxy - TCP proxy for flexible access to CloudFoxy RESTful API
***

Copyright (C) 2018 Smart Arcs Ltd, registered in the United Kingdom.

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from foxyproxy.upstream import GlobalPlatformProConfig, GlobalPlatformPro

__author__ = "Petr Svenda"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@enigmabridge.com'
__status__ = 'Development'

from foxyproxy.beacon_thread import BeaconThread
from foxyproxy import FoxyProxyTCP


def proxy_remote_mypc():
    """
    A test upstream connection definition - GPPro
    """
    server_config = GlobalPlatformProConfig()
    proxy_cfg = GlobalPlatformPro(server_config)
    proxy_cfg.test_simulated_card = False
    proxy_cfg.test_with_local_reader = True
    # proxy_cfg.test_local_reader = 'OMNIKEY AG Smart Card Reader USB 0'

    new_beacon = BeaconThread(proxy_cfg)
    FoxyProxyTCP.start_server(0, new_beacon)


def main():
    """
    Only for testing
    """
    proxy_remote_mypc()
    # proxy_local()  # 'OMNIKEY AG 3121 USB'
    # proxy_remote_single_card()
    # proxy_simulated()
    # proxy_remote_simona()


if __name__ == "__main__":
    main()
