# encoding: utf-8
# pylint: disable=missing-docstring

from __future__ import unicode_literals

import io
import os

import yaml

from polarion_docstrings import checker

CONFIG_TEMPLATE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir, "polarion_tools.yaml.template"
)

RESULTS = [
    (10, 4, 'P665 Missing "Polarion" section'),
    (14, 8, 'P665 Missing "Polarion" section'),
    (20, 8, 'P669 Missing required field "initialEstimate"'),
    (22, 12, 'P667 Invalid value "nonexistent" of the "casecomponent" field'),
    (38, 12, 'P667 Invalid value "level1" of the "caselevel" field'),
    (38, 12, 'P668 Field "caselevel" should be handled by the "@pytest.mark.tier" marker'),
    (39, 12, 'P668 Field "caseautomation" should be handled by the "@pytest.mark.manual" marker'),
    (
        40,
        12,
        'P668 Field "linkedWorkItems" should be handled by the "@pytest.mark.requirements" marker',
    ),
    (41, 12, 'P666 Unknown field "foo"'),
    (42, 12, 'P664 Ignoring field "description": use test docstring instead'),
    (49, 0, 'P665 Missing "Polarion" section'),
    (53, 0, 'P665 Missing "Polarion" section'),
    (59, 4, 'P665 Missing "Polarion" section'),
    (70, 8, 'P667 Invalid value "wrong" of the "testSteps" field'),
    (71, 8, 'P667 Invalid value "" of the "expectedResults" field'),
    (86, 4, 'P669 Missing required field "assignee"'),
]


def _strip_func(errors):
    return [(lineno, col, msg) for lineno, col, msg, __ in errors]


def test_checker(source_file):
    with io.open(CONFIG_TEMPLATE, encoding="utf-8") as config_file:
        config = yaml.load(config_file)
    errors = checker.DocstringsChecker(None, source_file, config, "TestChecker").run_checks()
    errors = _strip_func(errors)
    assert len(errors) == len(RESULTS)
    assert errors == RESULTS
