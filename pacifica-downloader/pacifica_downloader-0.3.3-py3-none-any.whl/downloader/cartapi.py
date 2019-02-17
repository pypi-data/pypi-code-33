#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Cart API module for interacting with carts."""
import logging
from uuid import uuid4 as uuid
import time
from json import dumps
import requests


class CartAPI(object):
    """
    Cart api object for manipulating carts.

    This class has two methods used for setting up a cart and waiting
    for completion.
    """

    def __init__(self, cart_api_url, **kwargs):
        """
        Constructor for cart api.

        The constructor takes a required URL to the Cart API.
        Optionally, there can be passed a
        `requests <https://docs.python-requests.org>`_ session via
        keyword arguments. Also, an optional requests authentication
        dictionary can be passed via keyword arguments.
        """
        self.cart_api_url = cart_api_url
        adapter = requests.adapters.HTTPAdapter(max_retries=5)
        session = requests.Session()
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        self.session = kwargs.get('session', session)
        self.auth = kwargs.get('auth', {})

    def setup_cart(self, yield_files):
        """
        Setup a cart from the method and return url to the download.

        This method takes a callable argument that returns an iterator.
        The iterator is used to generate a list that is directly sent to
        the `Cartd API <https://github.com/pacifica/pacifica-cartd>`_.
        This method returns the full url to the cart created.
        """
        cart_url = '{}/{}'.format(self.cart_api_url, uuid())
        resp = self.session.post(
            cart_url,
            data=dumps({
                'fileids': [file_obj for file_obj in yield_files()]
            }),
            headers={'Content-Type': 'application/json'},
            **self.auth
        )
        assert resp.status_code == 201
        return cart_url

    def wait_for_cart(self, cart_url, timeout=120):
        """
        Wait for cart completion to finish.

        This method takes a cart url returned from the
        `setup_cart()` method and polls the endpoint until the cart is
        ready to download.
        """
        while timeout > 0:
            resp = self.session.head(cart_url, **self.auth)
            resp_status = resp.headers['X-Pacifica-Status']
            resp_message = resp.headers['X-Pacifica-Message']
            resp_code = resp.status_code
            if resp_code == 204 and resp_status != 'staging':
                break
            if resp_code == 500:  # pragma: no cover
                logging.error(resp_message)
                break
            time.sleep(1)
            timeout -= 1
        assert resp_status == 'ready'
        assert resp_code == 204
        return cart_url
