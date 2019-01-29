# -*- coding: utf-8 -*-
"""Settings accessor.

This module contains classes for accessing settings for module. Used to
abstract settings so they can be read from a variety of sources.

Attributes:
    logger (logging.Logger): Logger set to DEBUG level.

    logging config JSON path (str): String of location of config file for
        logging.

    logging config file name (str): String of file name of config file for
        logging.

    logging config place (str): Full path of config file for logging.

    email config JSON path (str): String of location of config file for
        email notifications.

    email config file name (str): String of file name of config file for
        email notifications.

    email config place (str): Full path of config file for email notifications.

Todo:

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
import json
import logging.handlers
import os


_LOGGER = logging.getLogger(__name__)
_HANDLER = logging.StreamHandler()
_LOGGER.addHandler(_HANDLER)
_LOGGER.setLevel(logging.DEBUG)

_LOGGING_CONFIG_JSON_PATH = os.path.join(os.path.dirname(__file__), 'settings')
_LOGGING_CONFIG_FILE_NAME = 'logging.json'
_LOGGING_CONFIG_PLACE = os.path.join(_LOGGING_CONFIG_JSON_PATH,
                                     _LOGGING_CONFIG_FILE_NAME)
_EMAIL_CONFIG_JSON_PATH = os.path.join(os.path.dirname(__file__), 'settings')
_EMAIL_CONFIG_JSON_FILE_NAME = 'email.json'
_EMAIL_CONFIG_PLACE = os.path.join(_EMAIL_CONFIG_JSON_PATH,
                                   _EMAIL_CONFIG_JSON_FILE_NAME)


def _attempt_read_json_file(file_place, file_not_found_message):
    """Attempt to read JSON file.

    That's it.

    Args:
        file place (str): Where file is found.
        file not found message (str): Message to go along with notification if
            is not found.

    Returns:
        Python object of contents of file | None

    """
    try:
        with open(file_place) as file:
            return json.load(file)
    except FileNotFoundError:
        should_print = False
        if should_print:
            _LOGGER.info(file_not_found_message)


_EMAIL_CONFIG = _attempt_read_json_file(_EMAIL_CONFIG_PLACE,
                                        'No email config file found. This means '
                                        'WARNING and ERROR email will not be '
                                        'sent to you.')
_LOGGING_CONFIG = _attempt_read_json_file(_LOGGING_CONFIG_PLACE,
                                          'No logging config file found. This '
                                          'means no logging will be '
                                          'configured for this module.')


def email_config_exists():
    """Check if email config file exists.

    Returns:
        bool: The return value. True for success, False otherwise.
    """
    return bool(_EMAIL_CONFIG)


class SettingsAccessor:
    """Settings accessor

    Used to access configuration settings.
    """

    def __init__(self):
        pass

    def __str__(self):
        return '\n'.join([
            'Email Address: {address}'.format(address=self.email_address),
            'Email Password: {password}'.format(password=self.email_password),
        ])

    @property
    def email_address(self):
        """str: string of email address of Admin."""
        return _EMAIL_CONFIG.get('address', None) if _EMAIL_CONFIG else None

    @property
    def email_password(self):
        """str: string of email password of Admin."""
        return _EMAIL_CONFIG.get('password', None) if _EMAIL_CONFIG else None

    @property
    def credentials(self):
        """str: string of email password of Admin."""
        return self.email_address, self.email_password

    @property
    def admin_addresses(self):
        """list: list of email password of Admins."""
        if _EMAIL_CONFIG:
            out = _EMAIL_CONFIG.get('admin_addresses', None)
        else:
            out = None
        return out

    @property
    def email_host(self):
        """list: list of email password of Admins."""
        return _EMAIL_CONFIG.get('host', None) if _EMAIL_CONFIG else None

    @property
    def logging_config(self):
        """dict: dict of configuration settings for logging module"""
        return _LOGGING_CONFIG
