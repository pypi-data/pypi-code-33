__copyright__ = "# Copyright (c) 2016 by cisco Systems, Inc. All rights reserved."
__author__ = "Syed Raza <syedraza@cisco.com>"

from unicon.plugins.generic.statements import GenericStatements, password_handler
from unicon.plugins.iosxr.patterns import IOSXRPatterns
from unicon.eal.dialogs import Statement, Dialog
from unicon.eal.helpers import sendline

patterns = IOSXRPatterns()


class IOSXRStatements(GenericStatements):

    def __init__(self):
        super().__init__()
        self.password_stmt = Statement(pattern=patterns.password_prompt,
                                       action=password_handler,
                                       args=None,
                                       loop_continue=True,
                                       continue_timer=False)
        self.commit_replace_stmt = Statement(pattern=patterns.commit_replace_prompt,
                                     action=sendline,
                                     args={'command': 'yes'},
                                     loop_continue=True,
                                     continue_timer=False)
        self.confirm_y_prompt_stmt = Statement(
                                        pattern=patterns.confirm_y_prompt,
                                        action=sendline,
                                        args={'command': 'y'},
                                        loop_continue=True,
                                        continue_timer=False)

iosxr_statements = IOSXRStatements()


pre_connection_statement_list = [
    iosxr_statements.escape_char_stmt,
    iosxr_statements.press_return_stmt,
    iosxr_statements.continue_connect_stmt,
    iosxr_statements.connection_refused_stmt,
    iosxr_statements.disconnect_error_stmt ]
authentication_statement_list = [iosxr_statements.bad_password_stmt,
    iosxr_statements.login_incorrect,
    iosxr_statements.login_stmt,
    iosxr_statements.useraccess_stmt,
    iosxr_statements.password_stmt]
