# -*- coding: utf-8 -*-
class AbstractException(Exception):
    """
        Abstract class to create exceptions.

        Parameters
        ----------
        message: str
            Message to be displayed when the exception rises.
            Default: Campo não pode ser branco.

        status_code: integer
            HTTP response status code.
            Default: 500

        payload: dict
            Payload data to be send with in the exception response.
    """
    def __init__(self, message='Excecao abstrata.', status_code=500, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """
            Method class to create a dictionary for exception object.

            Returns
            ----------
            dict
                { 'error_message': self.message } + self.payload
        """
        return_value = dict(self.payload or ())
        return_value['error_message'] = self.message
        return return_value
