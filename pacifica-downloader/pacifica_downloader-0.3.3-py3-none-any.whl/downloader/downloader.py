#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The Downloader internal Module."""
import tarfile
import requests
from .cloudevent import CloudEvent
from .cartapi import CartAPI
from .policy import TransactionInfo


class Downloader(object):
    """
    Downloader Class.

    The constructor takes two arguments `location` and
    `cart_api_url`. The `location` is a download directory to be
    created by a download method. The `cart_api_url` is the endpoint
    for creating carts.

    The other methods in this class are the supported
    download methods. Each method takes appropriate input for that
    method and the method will download the data to the location
    defined in the constructor.
    """

    def __init__(self, location, cart_api_url, **kwargs):
        """Create the downloader given directory location."""
        self.location = location
        self.auth = kwargs.get('auth', {})
        self.cart_api = CartAPI(cart_api_url, auth=self.auth)

    def _download_from_url(self, cart_url, filename):
        """
        Download the cart from the url.

        The cart url is returned from the CartAPI.
        """
        resp = requests.get(
            '{}?filename={}'.format(cart_url, filename),
            stream=True, **self.auth
        )
        cart_tar = tarfile.open(name=None, mode='r|', fileobj=resp.raw)
        cart_tar.extractall(self.location)
        cart_tar.close()

    def transactioninfo(self, transinfo, filename='data'):
        """
        Handle transaction info and download the data in a cart.

        Transaction info objects are pulled from the
        `PolicyAPI <https://pacifica-policy.readthedocs.io/>`_.
        """
        self._download_from_url(
            self.cart_api.wait_for_cart(
                self.cart_api.setup_cart(
                    TransactionInfo.yield_files(transinfo)
                )
            ),
            filename
        )

    def cloudevent(self, cloudevent, filename='data'):
        """
        Handle a cloud event and download the data in a cart.

        `CloudEvents <https://github.com/cloudevents/spec>`_
        is a specification for passing information about
        changes in cloud infrastructure or state. This method
        consumes events produced by the
        `Pacifica Notifications <https://github.com/pacifica/pacifica-notifications>`_
        service.
        """
        self._download_from_url(
            self.cart_api.wait_for_cart(
                self.cart_api.setup_cart(
                    CloudEvent.yield_files(cloudevent)
                )
            ),
            filename
        )
