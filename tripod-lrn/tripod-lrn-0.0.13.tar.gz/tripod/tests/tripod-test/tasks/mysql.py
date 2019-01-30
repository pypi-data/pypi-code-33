# -*- coding: utf-8 -*-
"""
module mysql.py:
---------------
Automates mysql commands via a single application command.
"""
from invoke import task
import subprocess
import json


# tasks definitions

@task
def print_line(context):
    """A tasks that creates tables on the mysql database.
    """
    print(">>>>>passei aquii<<<<<<")
