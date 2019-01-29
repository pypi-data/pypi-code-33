# -*- coding: utf-8 -*-
"""Send email alerts.

This module contains classes that create objects for sending email alerts.

Attributes:
    settings (_settings_accessor.SettingsAccessor): Interfaces with various
        module settings.

    logger (logging.Logger): Logger set to DEBUG level and configured using
        logging.json, if such file exists.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.

Todo:
    =

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
import email
import logging.config
import os
import smtplib

import word_neo4j.settings_accessor  # pylint: disable=import-error

SETTINGS = word_neo4j.settings_accessor.SettingsAccessor()
if SETTINGS.logging_config:
    logging.config.dictConfig(SETTINGS.logging_config)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class EmailHandler(logging.StreamHandler):
    """Email handler for logging.

    Custom logging handler for sending emails.

    Written because of issues with logging.handlers.SMTPHandler class.

    """

    def emit(self, record):
        has_all_email_settings = True
        if not SETTINGS.email_address:
            has_all_email_settings = False
            package_name = os.path.basename(os.path.dirname(__file__))
            _LOGGER.info("Missing email address so you won't receive any "
                         "alerts from package %s", package_name)

        if not SETTINGS.admin_addresses:
            has_all_email_settings = False
            package_name = os.path.basename(os.path.dirname(__file__))
            _LOGGER.info("Missing admin addresses so you won't receive any "
                         "alerts from package %s", package_name)

        if not SETTINGS.email_host:
            has_all_email_settings = False
            package_name = os.path.basename(os.path.dirname(__file__))
            _LOGGER.info("Missing email server host so you won't receive any "
                         "alerts from package %s", package_name)

        if has_all_email_settings:
            message = self.format(record)
            msg = email.message.EmailMessage()
            msg['From'] = SETTINGS.email_address
            msg['To'] = ', '.join(SETTINGS.admin_addresses)
            msg['Subject'] = 'Hello'
            msg.set_content(message)
            try:
                smtp = smtplib.SMTP(SETTINGS.email_host)
                smtp.ehlo()
                smtp.starttls()
                smtp.login(SETTINGS.email_address, SETTINGS.email_password)
                smtp.send_message(msg)
                smtp.quit()
                _LOGGER.info('email message sent')
            except smtplib.SMTPServerDisconnected as error_message:
                _LOGGER.debug(error_message)
            except smtplib.SMTPAuthenticationError as error_message:
                _LOGGER.debug(error_message)
            except OSError as error_message:
                _LOGGER.debug(error_message)
                _LOGGER.debug('Poorly formed port number in email credentials')
