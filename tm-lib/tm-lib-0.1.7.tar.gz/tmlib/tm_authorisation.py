#!/usr/bin/env python3
import logging

from tmlib.settings import Settings


def token_auth(api_key_admin, *args, **kwargs):
    logging.debug("In authenticate_admin")
    logging.debug("**** BYPASSING API_KEY CHECK ******")
    if api_key_admin == Settings.ADMIN_API_KEY:
        return {'sub': 'admin'}
    logging.debug("api_key_admin=" + api_key_admin)
    return None
