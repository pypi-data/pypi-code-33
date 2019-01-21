# coding: utf-8

import requests
import json
try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

from .tools import is_string_type
from .eikonError import *
import eikon.Profile
import sys
import logging


def send_json_request(entity, payload, debug=False):
    """
    Returns the JSON response.
    This function can be used for advanced usage or early access to new features.

    Parameters
    ----------
    entity: string
        A string containing a service name

    payload: string
        A string containing a JSON request

    debug: bool, optional
        When set to True, the json request and response are printed.
        Default: False

    Returns
    -------
    string
        The JSON response as a string

    Raises
    ------
        EikonError
            If daemon is disconnected

        requests.Timeout
            If request times out

        Exception
            If request fails (HTTP code other than 200)

        EikonError
            If daemon is disconnected
    """
    profile = eikon.Profile.get_profile()
    if profile:
        logger = profile.logger
        logger.trace('entity: {}'.format(entity))
        logger.trace('payload:', payload)

        if not is_string_type(entity):
            error_msg = 'entity must be a string identifying an UDF endpoint'
            logger.error(error_msg)
            raise ValueError(error_msg)
        try:
            if is_string_type(payload):
                data = json.loads(payload)
            elif type(payload) is dict:
                data = payload
            else:
                error_msg = 'payload must be a string or a dictionary'
                logger.error(error_msg)
                raise ValueError(error_msg)
        except JSONDecodeError as e:
            error_msg = 'payload must be json well formed.\n'
            error_msg += str(e)
            logger.error(error_msg)
            raise e

        try:
            # build the request
            udf_request = {'Entity': {'E': entity, 'W': data} }
            logger.debug('Request:{}'.format(udf_request))
            response = profile.get_session().post(profile.get_url(),
                                     json = udf_request,
                                     headers={'Content-Type': 'application/json',
                                              'x-tr-applicationid': profile.get_app_key()},
                                     timeout=60)

            try:
                logger.debug('HTTP Response code: {}'.format(response.status_code))
                logger.debug('HTTP Response: {}'.format(response.text))
            except UnicodeEncodeError:
                logger.error('HTTP Response: cannot decode error message')

            if response.status_code == 200:
                result = response.json()
                logger.trace('Response size: {}'.format(sys.getsizeof(json.dumps(result))))
                check_server_error(result)
                return result
            else:
                raise_for_status(response)

        except requests.exceptions.ConnectionError as connectionError:
             network_error = True
        if network_error:
            error_msg = 'Eikon Proxy not installed or not running. Please read the documentation to know how to install and run the proxy'
            logger.error(error_msg)
            raise EikonError(401, error_msg)


def check_server_error(server_response):
    """
    Check server response.

    Check is the server response contains an HTPP error or a server error.

    :param server_response: request's response
    :type server_response: requests.Response
    :return: nothing

    :raises: Exception('HTTP error : <error_message>) if response contains HTTP response
              ex: '<500 Server error>'
          or Exception('Server error (<error code>) : <server_response>') if UDF returns an error
              ex: {u'ErrorCode': 500, u'ErrorMessage': u'Requested datapoint was not found: News_Headlines', u'Id': u''}

    """
    logger = eikon.Profile.get_profile().logger
    str_response = str(server_response)

    # check HTTP response (server response is an object that can contain ErrorCode attribute)
    if hasattr(server_response, 'ErrorCode'):
        logger.error(getattr(server_response, 'ErrorMessage'))
        raise requests.HTTPError(response=server_response)

    # check HTTPError on proxy request
    if str_response.startswith('<') and str_response.endswith('>'):
        logger.error(str_response)
        raise requests.HTTPError(response=server_response)

    # check UDF response (server response is JSON and it can contain ErrorCode + ErrorMessage keys)
    if 'ErrorCode' in server_response and 'ErrorMessage' in server_response:
        error_message = server_response['ErrorMessage']
        if len(error_message.split(',')) > 4:
            status, reason_phrase, version, content, headers = error_message.split(',')[:5]
        logger.error(error_message)
        raise EikonError(int(server_response['ErrorCode']), error_message)

    # check DataGrid response (server response is JSON and it can contain error + transactionId keys)
    if 'error' in server_response and 'transactionId' in server_response:
        error_message = '{} (transactionId:{}'.format(server_response['error'],server_response['transactionId'])
        logger.error(error_message)
        raise EikonError(400, error_message)


def raise_for_status(response):
    """Raises stored :class:`HTTPError`, if one occurred."""

    error_msg = ''
    if isinstance(response.reason, bytes):
        # We attempt to decode utf-8 first because some servers
        # choose to localize their reason strings. If the string
        # isn't utf-8, we fall back to iso-8859-1 for all other
        # encodings. (See PR #3538)
        try:
            reason = response.reason.decode('utf-8')
        except UnicodeDecodeError:
            reason = response.reason.decode('iso-8859-1')
    else:
        reason = response.reason

    logger = eikon.Profile.get_profile().logger

    if eikon.Profile.get_profile().get_log_level() < logging.INFO:
        # Check if retry-after is in headers
        rate_limit = response.headers.get('x-ratelimit-limit')
        rate_remaining = response.headers.get('x-ratelimit-remaining')
        volume_limit = response.headers.get('x-volumelimit-limit')
        volume_remaining = response.headers.get('x-volumelimit-remaining')

        retry_after = response.headers.get('retry-after')
        logger.trace('Headers: x_ratelimit_limit={} / x_ratelimit_remaining={} '.format(rate_limit, rate_remaining))
        logger.trace('         x_volumelimit_limit={} / x_volumelimit_remaining={}'.format(volume_limit, volume_remaining))
        logger.trace('         retry_after {}'.format(retry_after))

    if 400 <= response.status_code < 500:
        error_msg = u'Client Error: %s - %s' % (reason, response.text)
    elif 500 <= response.status_code < 600:
        error_msg = u'Server Error: %s - %s' % (reason, response.text)

    if error_msg:
        logger.error(u'Error code {} | {}'.format(response.status_code, error_msg))
        raise EikonError(response.status_code, error_msg)
