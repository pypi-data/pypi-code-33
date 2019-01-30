# encoding: utf-8
# pylint: disable=missing-docstring

from __future__ import unicode_literals

from polarion_docstrings.parser import DocstringRecord, ValueRecord, get_docstrings_in_file

RESULTS = [
    DocstringRecord(
        lineno=10,
        column=4,
        value={},
        nodeid="tests/data/polarion_docstrings.py::TestClassFoo::test_in_class_no_docstring",
    ),
    DocstringRecord(
        lineno=14,
        column=8,
        value={},
        nodeid="tests/data/polarion_docstrings.py::TestClassFoo::test_in_class_no_polarion",
    ),
    DocstringRecord(
        lineno=20,
        column=8,
        value={
            "assignee": ValueRecord(lineno=1, column=12, value="mkourim"),
            "casecomponent": ValueRecord(lineno=2, column=12, value="nonexistent"),
            "testSteps": [
                ValueRecord(
                    lineno=4,
                    column=16,
                    value="1. Step with really long description that doesn't fit into one line",
                ),
                ValueRecord(lineno=6, column=16, value="2. Do that"),
            ],
            "expectedResults": [
                ValueRecord(
                    lineno=8,
                    column=16,
                    value=(
                        "1. Success outcome with really long description "
                        "that doesn't fit into one line"
                    ),
                ),
                ValueRecord(lineno=10, column=16, value="2. second"),
            ],
            "caseimportance": ValueRecord(lineno=11, column=12, value="low"),
            "title": ValueRecord(
                lineno=12,
                column=12,
                value="Some test with really long description that doesn't fit into one line",
            ),
            "setup": ValueRecord(
                lineno=14, column=12, value="Do this:\n- first thing\n- second thing"
            ),
            "teardown": ValueRecord(lineno=17, column=12, value="Tear it down"),
            "caselevel": ValueRecord(lineno=18, column=12, value="level1"),
            "caseautomation": ValueRecord(lineno=19, column=12, value="automated"),
            "linkedWorkItems": ValueRecord(lineno=20, column=12, value="FOO, BAR"),
            "foo": ValueRecord(lineno=21, column=12, value="this is an unknown field"),
            "description": ValueRecord(lineno=22, column=12, value="ignored"),
        },
        nodeid="tests/data/polarion_docstrings.py::TestClassFoo::test_in_class_polarion",
    ),
    DocstringRecord(
        lineno=49,
        column=0,
        value={},
        nodeid="tests/data/polarion_docstrings.py::test_annotated_no_docstring",
    ),
    DocstringRecord(
        lineno=53,
        column=0,
        value={},
        nodeid="tests/data/polarion_docstrings.py::test_standalone_no_docstring",
    ),
    DocstringRecord(
        lineno=59,
        column=4,
        value={},
        nodeid="tests/data/polarion_docstrings.py::test_annotated_no_polarion",
    ),
    DocstringRecord(
        lineno=67,
        column=4,
        value={
            "assignee": ValueRecord(lineno=1, column=8, value="mkourim"),
            "initialEstimate": ValueRecord(lineno=2, column=8, value="1/4"),
            "testSteps": ValueRecord(lineno=3, column=8, value="wrong"),
            "expectedResults": ValueRecord(lineno=4, column=8, value=""),
        },
        nodeid="tests/data/polarion_docstrings.py::test_annotated_polarion",
    ),
    DocstringRecord(
        lineno=78,
        column=4,
        value={"initialEstimate": ValueRecord(lineno=1, column=8, value="1/4")},
        nodeid="tests/data/polarion_docstrings.py::test_blacklisted",
    ),
    DocstringRecord(
        lineno=86,
        column=4,
        value={"initialEstimate": ValueRecord(lineno=1, column=8, value="1/4")},
        nodeid="tests/data/polarion_docstrings.py::test_blacklisted_and_whitelisted",
    ),
]


def test_parser(source_file):
    docstrings = get_docstrings_in_file(source_file)
    assert len(docstrings) == len(RESULTS)
    assert docstrings == RESULTS
