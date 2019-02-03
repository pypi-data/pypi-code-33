#!/usr/bin/env python3
"""
Module with custom exceptions.
"""


import signal


def exit_main_menu_ctrlz(signum, frame):
    """Exit to main menu with CTRL+Z."""
    raise MainMenu

class MainMenu(Exception):
    """Exception to exit in main menu of program."""
    pass
