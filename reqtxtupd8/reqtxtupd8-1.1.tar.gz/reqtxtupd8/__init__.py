#!/usr/bin/env python

"""
usage: in terminal run requpd8
"""

import os


def run():
    """
    writes python package list to requirements.txt
    """
    os.system("pip freeze > requirements.txt")
