# -*- coding: utf-8 -*-
from ct_api_gateway_deployer.src.common.abstract_exception import AbstractException


class GenericException(AbstractException):

    def __init__(self, message='Ocorreu um comportamento inesperado.', status_code=500, payload=None):
        """
            Exception to warn for generic purpose when there is not specific exception to be used. Accusing an internal
            server error.

            Parameters
            ----------
            message: str
                Message to be displayed when the exception rises.
                Default: Ocorreu um comportamento inesperado.

            status_code: integer
                HTTP response status code.
                Default: 500

            payload: dict
                Payload data to be send with in the exception response.
        """
        super().__init__(message, status_code, payload)
