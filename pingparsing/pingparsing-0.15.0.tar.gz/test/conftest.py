# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


def pytest_addoption(parser):
    parser.addoption("--device", default=None)
