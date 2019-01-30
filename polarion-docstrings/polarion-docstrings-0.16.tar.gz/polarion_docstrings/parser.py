# -*- coding: utf-8 -*-
# pylint: disable=useless-object-inheritance
"""
Parses Polarion docstrings.
"""

from __future__ import absolute_import, unicode_literals

import ast
from collections import namedtuple

FORMATED_KEYS = ("setup", "teardown")

DocstringRecord = namedtuple("DocstringRecord", "lineno column value nodeid")
ValueRecord = namedtuple("ValueRecord", "lineno column value")


def get_section_start(doc_list, section):
    """Finds the line with "section" (e.g. "Polarion", "testSteps", etc.)."""
    section = "{}:".format(section)
    for index, line in enumerate(doc_list):
        if section != line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        return index + 1, indent
    return None, None


# pylint: disable=too-few-public-methods,invalid-name
class DOCSTRING_SECTIONS(object):  # noqa
    """Valid sections in Polarion docstring."""

    polarion = "Polarion"
    steps = "testSteps"
    results = "expectedResults"


class DocstringParser(object):
    """Parser for single docstring."""

    SECTIONS = DOCSTRING_SECTIONS

    def __init__(self, docstring):
        self.docstring = docstring

    @staticmethod
    def _get_key_value(line):
        """Gets the key and value out of docstring line."""
        data = line.split(":")
        if len(data) == 1:
            data.append("")

        key = data[0].strip()

        value = ":".join(data[1:]).strip()
        if value == "None":
            value = None

        return key, value

    # pylint: disable=too-many-locals
    def lines_to_dict(self, lines, start=0, lineno_offset=0, stop=None):
        """Creates dictionary out of docstring lines.

        Includes column and line number info for each record.
        """
        if stop:
            lines = lines[start:stop]
        else:
            lines = lines[start:]

        lines_dict = {}
        indent = len(lines[0]) - len(lines[0].lstrip(" "))
        prev_key = None
        for num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if not line_stripped:
                break

            curr_indent = len(line) - len(line.lstrip(" "))

            if curr_indent < indent:
                break

            # check if the line should be appended to previous key
            first_word = line_stripped.split(" ")[0] or line_stripped
            if prev_key and curr_indent > indent and first_word[-1] != ":":
                sep = "\n" if prev_key in FORMATED_KEYS else " "
                prev_lineno, prev_indent, prev_value = lines_dict[prev_key]
                lines_dict[prev_key] = ValueRecord(
                    prev_lineno, prev_indent, "{}{}{}".format(prev_value, sep, line_stripped)
                )
                continue
            else:
                prev_key = None

            if curr_indent > indent:
                continue

            key, value = self._get_key_value(line)
            lines_dict[key] = ValueRecord(num + lineno_offset, indent, value)
            prev_key = key

        return lines_dict

    @staticmethod
    def lines_to_list(lines, start=0, lineno_offset=0, stop=None):
        """Creates list out of docstring lines.

        Includes column and line number info for each line.
        """
        if stop:
            lines = lines[start:stop]
        else:
            lines = lines[start:]

        lines_list = []
        indent = len(lines[0]) - len(lines[0].lstrip(" "))
        for num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if not line_stripped:
                continue
            curr_indent = len(line) - len(line.lstrip(" "))
            if curr_indent < indent:
                break

            # check if the line should be appended to previous key
            first_word = line_stripped.split(" ")[0] or line_stripped
            if curr_indent > indent and first_word[-1] != ":":
                prev_lineno, prev_indent, prev_value = lines_list.pop()
                lines_list.append(
                    ValueRecord(prev_lineno, prev_indent, "{} {}".format(prev_value, line_stripped))
                )
                continue

            if curr_indent > indent:
                continue
            lines_list.append(ValueRecord(num + lineno_offset, indent, line_stripped))

        return lines_list

    def strip_polarion_data(self):
        """Removes the Polarion section from the docstring."""
        docstring_list = self.docstring.split("\n")
        new_docstring_list = []
        polarion_section = "{}:".format(self.SECTIONS.polarion)
        indent = 0
        in_polarion = False

        for line in docstring_list:
            if line.strip() == polarion_section:
                indent = len(line) - len(line.lstrip(" "))
                in_polarion = True
                continue
            if indent:
                curr_indent = len(line) - len(line.lstrip(" "))
                if curr_indent > indent:
                    continue
                # If this is the next line after Polarion section,
                # don't save blank line.
                if in_polarion:
                    in_polarion = False
                    if not line.strip():
                        continue
            new_docstring_list.append(line)

        new_docstring = "\n".join(new_docstring_list)
        return new_docstring.strip()

    def parse(self):
        """Parses docstring to dictionary. E.g.:

        Polarion:
            assignee: mkourim
            casecomponent: nonexistent
            testSteps:
                1. Step with really long description
                   that doesn't fit into one line
                2. Do that
            expectedResults:
                1. Success outcome with really long description
                   that doesn't fit into one line
                2. 2
            caseimportance: low
            title: Some test with really long description
                   that doesn't fit into one line
            setup: Do this:
                   - first thing
                   - second thing

        This is not included.
        """
        doc_list = self.docstring.split("\n")

        polarion_start, __ = get_section_start(doc_list, self.SECTIONS.polarion)
        if not polarion_start:
            return None

        docstring_dict = self.lines_to_dict(doc_list, start=polarion_start)

        if self.SECTIONS.steps in docstring_dict and docstring_dict[self.SECTIONS.steps].value:
            steps_start, __ = get_section_start(doc_list, self.SECTIONS.steps)
            if steps_start:
                steps_list = self.lines_to_list(
                    doc_list, start=steps_start, lineno_offset=steps_start - polarion_start
                )
                docstring_dict[self.SECTIONS.steps] = steps_list

        if self.SECTIONS.results in docstring_dict and docstring_dict[self.SECTIONS.results].value:
            results_start, __ = get_section_start(doc_list, self.SECTIONS.results)
            if results_start:
                results_list = self.lines_to_list(
                    doc_list, start=results_start, lineno_offset=results_start - polarion_start
                )
                docstring_dict[self.SECTIONS.results] = results_list

        return docstring_dict


class FileParser(object):
    """Parser for whole file."""

    SECTIONS = DOCSTRING_SECTIONS

    def __init__(self, filename, tree=None, tests_only=True):
        self.filename = filename
        self.tests_only = tests_only
        self.tree = tree or self.get_tree()

    def get_tree(self):
        """Returns ast tree."""
        with open(self.filename) as infile:
            source = infile.read()

        tree = ast.parse(source, filename=self.filename)
        return tree

    @staticmethod
    def get_docstring_from_func(func_node):
        """Gets docstring from function definition."""
        docstring = None
        try:
            if (
                func_node.body
                and isinstance(func_node.body[0], ast.Expr)
                and isinstance(func_node.body[0].value, ast.Str)
            ):
                docstring = func_node.body[0].value.s
        # pylint: disable=broad-except
        except Exception:
            return None

        # for Python2
        try:
            docstring = docstring.decode("utf-8")
        except AttributeError:
            pass

        return docstring

    def _get_nodeid(self, node_name, class_name):
        components = [self.filename, class_name, node_name]
        if not class_name:
            components.pop(1)
        nodeid = "::".join(components)
        return nodeid

    def process_func(self, node, class_name):
        """Returns parsed Polarion docstring present in the function."""
        docstring = self.get_docstring_from_func(node)
        nodeid = self._get_nodeid(node.name, class_name)

        # test doesn't have docstring, i.e. it's missing also the Polarion section
        if not docstring:
            return DocstringRecord(
                lineno=node.body[0].lineno - 1, column=node.col_offset, value={}, nodeid=nodeid
            )

        doc_list = docstring.split("\n")
        docstring_start = node.body[0].lineno - len(doc_list)
        polarion_start, polarion_column = get_section_start(doc_list, self.SECTIONS.polarion)

        if not polarion_start:
            # docstring is missing the Polarion section
            return DocstringRecord(
                lineno=docstring_start + 1, column=node.col_offset + 4, value={}, nodeid=nodeid
            )

        polarion_offset = docstring_start + polarion_start
        return DocstringRecord(
            lineno=polarion_offset,
            column=polarion_column,
            value=parse_docstring(docstring),
            nodeid=nodeid,
        )

    def process_ast_body(self, body, class_name=None):
        """Recursively iterates over specified part of ast tree to process functions."""
        docstrings = []
        for node in body:
            if isinstance(node, ast.ClassDef):
                if self.tests_only and not node.name.startswith("Test"):
                    continue
                docstrings.extend(self.process_ast_body(node.body, node.name))

            if not isinstance(node, ast.FunctionDef):
                continue

            if self.tests_only and not node.name.startswith("test_"):
                continue

            docstrings.append(self.process_func(node, class_name))

        return docstrings

    def get_docstrings(self):
        """Returns parsed Polarion docstrings present in the python source file."""
        return self.process_ast_body(self.tree.body)


# convenience functions


def parse_docstring(docstring):
    """Parses docstring to dictionary."""
    return DocstringParser(docstring).parse()


def strip_polarion_data(docstring):
    """Removes the Polarion section from the docstring."""
    return DocstringParser(docstring).strip_polarion_data()


def get_docstrings_in_file(filename, tree=None, tests_only=True):
    """Returns parsed Polarion docstrings present in the python source file."""
    return FileParser(filename, tree=tree, tests_only=tests_only).get_docstrings()
