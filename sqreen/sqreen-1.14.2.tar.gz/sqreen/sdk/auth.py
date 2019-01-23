# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Authentication sdk functions
"""

import logging
from datetime import datetime

from . import events
from ..actions import ACTION_STORE
from ..exceptions import ActionBlock
from ..runtime_storage import runtime

LOGGER = logging.getLogger(__name__)


def _check_block_user(user_dict):
    """Block user when required."""
    action = ACTION_STORE.get_for_user(user_dict)
    if action is None:  # User is not blocked, abort.
        return
    LOGGER.info("User blocked: %r", user_dict)
    events.track_action(action, {"user": user_dict})
    raise ActionBlock(action.iden)


def auth_track(success, **user_identifiers):
    """ Register a successfull or failed authentication attempt (based on
    success boolean) for an user identified by the keyword-arguments.
    For example:

    auth_track(True, email="foobar@example.com") register a successfull
    authentication attempt for user with email "foobar@example.com".

    auth_track(False, user_id=42) register a failed authentication
    attempt for user with id 42.
    """
    _check_block_user(user_identifiers)


def signup_track(**user_identifiers):
    """ Register a new account signup identified by the keyword-arguments.
    For example:

    auth_track(email="foobar@example.com", user_id=42) register
    a new account signup for user identifed by email "foobar@example.com" or
    bu user id 42.
    """
    pass


def identify(auth_keys, traits=None, storage=runtime):
    if traits is None:
        traits = {}
    storage.observe(
        "sdk", ["identify", datetime.utcnow(), auth_keys, traits], report=False
    )
    _check_block_user(auth_keys)
