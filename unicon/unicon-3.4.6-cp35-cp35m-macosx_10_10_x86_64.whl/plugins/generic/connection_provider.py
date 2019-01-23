"""
Module:
    unicon.plugins.generic

Authors:
    ATS TEAM (ats-dev@cisco.com, CSG( STEP) - India)

Description:
    This module imports connection provider class which has
    exposes two methods named connect and disconnect. These
    methods are implemented in such a way so that they can
    handle majority of platforms and subclassing is seldom
    required.
"""
from unicon.bases.routers.connection_provider import BaseSingleRpConnectionProvider
from unicon.bases.routers.connection_provider import BaseDualRpConnectionProvider
from unicon.eal.dialogs import Dialog
from .statements import connection_statement_list
from unicon import log


class GenericSingleRpConnectionProvider(BaseSingleRpConnectionProvider):
    """ Implements Generic singleRP Connection Provider,
        This class overrides the base class with the
        additional dialogs and steps required for
        connecting to any device via generic implementation
    """
    def __init__(self, *args, **kwargs):

        """ Initializes the generic connection provider
        """
        super().__init__(*args, **kwargs)

    def get_connection_dialog(self):
        """ creates and returns a Dialog to handle all device prompts
            appearing during initial connection to the device.
            See statements.py for connnection statement lists
        """
        return Dialog(connection_statement_list)


class GenericDualRpConnectionProvider(BaseDualRpConnectionProvider):
    """ Implements Generic dualRP Connection Provider,
        This class overrides the base class with the
        additional dialogs and steps required for
        connecting to any device via generic implementation
    """
    def __init__(self, *args, **kwargs):

        """ Initializes the generic connection provider
        """
        super().__init__(*args, **kwargs)

    def get_connection_dialog(self):
        """ creates and returns a Dialog to handle all device prompts
            appearing during initial connection to the device.
            See statements.py for connnection statement lists
        """
        return Dialog(connection_statement_list)
