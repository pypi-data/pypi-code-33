# -*- coding: utf-8 -*-

"""
This file contains custom Exceptions that are used within the CloudCIX API library
"""


class ImproperlyConfiguredException(Exception):
    """
    This exception is raised when the CloudCIX library has not been properly configured.

    This can usually happen in the following ways:

        - The ``settings`` file has not been specified in the environment variables
        - The ``settings`` file is missing a required setting
          (see `Required Settings <https://cloudcix.github.io/python-cloudcix/readme.html#required-settings>`_)
    """
    pass


class MissingClientKeywordArgumentException(Exception):
    """
    This exception is raised when a method is called on a service that requires one or more keyword arguments that were
    not supplied by the user.

    For example: if a service's URL is ``address/{address_id}/link/``, the call to ``Membership.address_link.list`` must
    include an ``address_id`` keyword argument, or else this exception will be thrown.

    The message for the exception will look like this;
    ``The "address_id" keyword argument is required by <Client [{.../address/{address_id}/link/}]>``.
    """

    def __init__(self, name, cli):
        """
        Initialize an instance of the exception

        :param name: The name of the keyword argument that is missing
        :type name: str
        :param cli: The Client instance that is missing the keyword argument
        :type cli: cloudcix.client.Client
        """
        self.name = name
        self.message = 'The "{}" keyword argument is required by {}'.format(name, cli)

    def __str__(self):
        return self.message

    def __repr__(self):
        return '<MissingClientKeywordArgument [{}]>'.format(self.name)
