# -*- coding: utf-8 -*-

"""Fixtures for working with shadow"""


import pytest

from shadow.shadow import Shadow


@pytest.fixture
def tmpl_file(tmpdir):
    return tmpdir.join("test.txt.tpl")


@pytest.fixture
def tmpl_dir(tmpdir):
    return tmpdir.mkdir("test.tpl")


@pytest.fixture
def shadow():
    return Shadow
