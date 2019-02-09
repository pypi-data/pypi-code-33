"""
Helpers for making Flask error response.
"""

from http import HTTPStatus

from flask import jsonify


class ErrorCodes:
    """
    Datasource service error codes,
    """
    INVALID_REQUEST = 'INVALID_REQUEST'
    NOT_AUTHORIZED = 'NOT_AUTHORIZED'
    FETCH_DATA_ERROR = 'FETCH_DATA_ERROR'


def error_response(status, code, message):
    """
    Makes a customized error response.

    Args:
        status (int): HTTP status code
        code (str): error code
        message (str): error message

    Returns:
        object: Flask json response
    """

    return jsonify({'code': code, 'message': message}), status


def invalid_request(message):
    """
    Makes a customized error response (with
    HTTP 400 status code).

    Args:
        status (int): HTTP status code
        code (str): error code
        message (str): error message

    Returns:
        object: Flask json response
    """
    return error_response(HTTPStatus.BAD_REQUEST, code=ErrorCodes.INVALID_REQUEST, message=message)


def not_authorized(message):
    """
    Makes an unauthorized error response (with
    HTTP 401 status code).

    Args:
        message (str): error message

    Returns:
        object: Flask json response
    """
    return error_response(HTTPStatus.UNAUTHORIZED, code=ErrorCodes.NOT_AUTHORIZED, message=message)


def fetch_data_error(message):
    """
    Makes a fetch-data error response (with
    HTTP 400 status code).

    Args:
        message (str): error message

    Returns:
        object: Flask json response
    """
    return error_response(HTTPStatus.BAD_REQUEST, code=ErrorCodes.FETCH_DATA_ERROR, message=message)


class ServiceErrorBase(Exception):
    """Base error type"""


class ServiceBadRequestError(ServiceErrorBase):
    """Error representing a bad request"""


class ServiceAuthError(ServiceErrorBase):
    """Error representing an authorization failure"""


class ServiceFetchDataError(ServiceErrorBase):
    """Error representing data fetching failure"""
