#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `search_in_api` package."""

import pytest

from search_in_api.search_in_api import is_in_structure


@pytest.fixture
def structure():
    """
    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return {
        'one': 1,
        'two': [
            {'deeper': {'ok': 'This is OK'}},
            {'not ok': 'Not OK'},
        ],
        'three': {
            'four': 4,
        }
    }


def test_deep_successful_structure(structure):
    """Test is_in_structure() with a deep structure"""
    result = is_in_structure(
        key_to_search="ok",
        value_to_search="ok",
        structure=structure,
    )
    assert result is True


def test_deep_failing_structure(structure):
    """Test is_in_structure() with a deep structure"""
    """Test is_in_structure() with a deep structure"""
    result = is_in_structure(
        key_to_search="ok",
        value_to_search="!ok",
        structure=structure,
    )
    assert result is False
