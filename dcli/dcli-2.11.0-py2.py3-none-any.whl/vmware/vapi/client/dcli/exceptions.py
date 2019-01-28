"""
dcli exception handling functions and Exception classes
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright (c) 2015-2018 VMware, Inc.  All rights reserved. '
__license__ = 'SPDX-License-Identifier: MIT'
__docformat__ = 'epytext en'

import traceback
import sys
import logging

import six

from vmware.vapi.lib.converter import Converter
from vmware.vapi.data.value import ErrorValue
from com.vmware.vapi.std.errors_client import Error


logger = logging.getLogger(__name__)
ignore_error = False


class CommandCollision(Exception):
    """
    Class used for throwing cli specific expection when conflicting commands in expanding
    short command are found
    """
    def __init__(self, conflicting_commands, msg):
        Exception.__init__(self, msg)
        self.msg = msg
        self.conflicting_commands = conflicting_commands


class CliArgumentException(Exception):
    """
    Class used for throwing cli specific expection when argument mismatch occurs
    """
    def __init__(self, msg, status_code, print_error=True):
        Exception.__init__(self, msg)
        self.msg = msg
        self.status_code = status_code
        self.print_error = print_error


class ParsingExit(Exception):
    """
    Class to extend Exception class
    """
    def __init__(self, status, msg):
        Exception.__init__(self, msg)
        self.msg = msg
        self.status = status


class ParsingError(RuntimeError):
    """
    Class to extend RuntimeError class
    """
    def __init__(self, msg):
        RuntimeError.__init__(self, msg)
        self.msg = msg


class InvalidCSPToken(Exception):
    """
    Exception which stores information of csp generate auth token response
    """
    def __init__(self, msg, csp_response):
        Exception.__init__(self, msg)
        self.msg = msg
        self.csp_response = csp_response


def extract_error_msg(err):
    """
    Extract error message from an exception

    :type  err: :class:`Exception`
    :param err: Exception object

    :rtype:  :class:`str`
    :return: Error message
    """
    msg = ''
    try:
        msg = str(err)
    except UnicodeError:
        msg = repr(err)

    if msg == 'None':
        return None
    return msg


def handle_error(msg, print_error=True, print_usage=False, prefix_message='Error: ', exception=None):
    """
    Prints a friendly error message for given exception
    Logs stack trace.

    :type msg: :class:`str`
    :param msg: Error message
    """
    if ignore_error:
        return

    if msg:
        logger.error('%s%s', prefix_message, msg)
        if print_error:
            print("{}{}".format(prefix_message, msg), file=sys.stderr)
        if print_usage:
            print("For usage type: dcli --help", file=sys.stderr)

    if exception:
        logger.exception(exception)
    else:
        # output stack trace info to log file
        formatted_stack = traceback.format_stack()
        stackMsg = '\n' + ''.join(formatted_stack)
        logger.error('Error stack trace: %s', stackMsg)


def handle_server_error(error):
    """
    Prints a friendly error message for given exception
    using server error information
    Logs stack trace.

    :type error: :class:`vmware.vapi.data.value.ErrorValue`
    :param error: Server error
    """
    error_name = get_server_error_name(error.name)
    handle_error(error_name, prefix_message='Server error: ')

    msg_list = get_error_messages(error)

    if msg_list:
        prefix = 'Error messages:' if len(msg_list) > 1 else 'Error message:'
        indent = ' ' * 4
        logger.error(prefix)
        print(prefix, file=sys.stderr)
        for msg in msg_list:
            logger.error('%s%s', indent, msg)
            print('{}{}'.format(indent, msg), file=sys.stderr)


def handle_ssl_error(e):
    """f
    handles ssl exceptions by giving adequate message and logs in the logger

    :type error: :class:`requests.exceptions.SSLError`
    :param error: Server SSL error
    """
    error_msg = 'SSL error occurred while trying to communicate with server.\n'
    error_msg += 'Please provide valid trust store file through '
    error_msg += 'either +cacert-file option or DCLI_CA_BUNDLE environment '
    error_msg += 'variable to verify against the server'
    msg = extract_error_msg(e)
    if msg:
        logger.error('Error: %s', msg)
    raise Exception(error_msg)


def handle_connection_error(e):
    """
    common handling of connection errors

    :type error: :class:`requests.exceptions.ConnectionError`
    :param error: Server connection error
    """
    error_msg = 'Unable to connect to the server.\n'
    error_msg += 'Please provide correct +server option value.'
    msg = extract_error_msg(e)
    if msg:
        logger.error('Error: %s', msg)
    raise Exception(error_msg)


def get_server_error_name(name):
    """
    Get vapi error full name from python error name

    :type  name: :class:`str`
    :param name: Error name

    :rtype:  :class:`str`
    :return: Error string
    """
    tmp_err_name = name.rsplit('.', 1)
    error_str = ''
    if len(tmp_err_name) > 1:
        error_str = '%s.' % tmp_err_name[0]
    error_str = '%s%s' % (error_str, Converter.underscore_to_capwords(tmp_err_name[-1]))
    return error_str


def get_error_messages(error):
    """
    From Vapi error or Python Exception extract error
    messages into list and return the result

    :type  name: :class:`com.vmware.vapi.std.errors_client.Error` or
                 :class:`Exception` or
                 :class:`vmware.vapi.data.value.ErrorValue`
    :param name: Error or exception object

    :rtype:  :class:`list` of :class:`str`
    :return: List of error messages
    """
    assert isinstance(error, (ErrorValue, Exception))
    try:
        if isinstance(error, (Error, ErrorValue)):
            msg_list = error.get_field('messages')
        else:
            return [str(error)]
    except Exception:
        msg_list = []

    result = []
    for msg in msg_list:
        default_message = msg.get_field('default_message')
        if not isinstance(default_message, six.string_types):
            result.append(default_message.value)
        else:
            result.append(default_message)

    return result
