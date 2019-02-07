#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test ingest with good uploads of good and bad data."""
from __future__ import print_function, absolute_import
from common_methods_test import try_good_move


def test_good_move():
    """Test the good move."""
    try_good_move('move-md', 'OK', 'ingest metadata', 100)


def test_bad_file_move():
    """Test the bad file path move."""
    try_good_move('bad-move-md', 'FAILED', 'move files', 0)
