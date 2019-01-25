#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""sim_db command line tool entry points"""
# Copyright (C) 2019 Håkon Austlid Taskén <hakon.tasken@gmail.com>
# Licenced under the MIT License.

import os.path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sim_db.src_command_line_tool.command_line_tool as command_line_tool

def sim_db():
    """sim_db command line tool"""
    command_line_tool.command_line_tool("sim_db", sys.argv[1:])

def sdb():
    """sdb command line tool"""
    command_line_tool.command_line_tool("sdb", sys.argv[1:])

if __name__ == '__main__':
    sim_db()
