##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import re
import unittest
import doctest
from zope.publisher.browser import TestRequest
from zope.interface.verify import verifyObject

from zope.testing.renormalizing import RENormalizing

from z3c.batching.batch import Batch
from z3c.table import testing
from z3c.table import interfaces
from z3c.table import table
from z3c.table import column
from z3c.table import batch


class FakeContainer(object):
    def values(self):
        pass


marker_pos = object()
marker_kws = object()


class InterfaceBaseTest(object):
    """Base test for IContainer including interface test."""

    iface = None
    klass = None
    pos = marker_pos
    kws = marker_kws

    def getTestPos(self):
        return self.pos

    def getTestKws(self):
        return self.kws

    def makeTestObject(self, object=None, *pos, **kws):
        # provide default positional or keyword arguments
        ourpos = self.getTestPos()
        if ourpos is not marker_pos and not pos:
            pos = ourpos

        ourkws = self.getTestKws()
        if ourkws is not marker_kws and not kws:
            kws = ourkws

        testclass = self.getTestClass()

        if object is None:
            # a class instance itself is the object to be tested.
            return testclass(*pos, **kws)
        else:
            # an adapted instance is the object to be tested.
            return testclass(object, *pos, **kws)

    def test_verifyObject(self):
        # object test
        self.assertTrue(
            verifyObject(self.getTestInterface(), self.makeTestObject())
        )


# table
class TestTable(InterfaceBaseTest, unittest.TestCase):
    def setUp(test):
        testing.setUpAdapters()

    def getTestInterface(self):
        return interfaces.ITable

    def getTestClass(self):
        return table.Table

    def getTestPos(self):
        return (FakeContainer(), TestRequest())


class TestSequenceTable(InterfaceBaseTest, unittest.TestCase):
    def setUp(test):
        testing.setUpAdapters()

    def getTestInterface(self):
        return interfaces.ITable

    def getTestClass(self):
        return table.SequenceTable

    def getTestPos(self):
        return (None, TestRequest())


# column
class TestColumn(InterfaceBaseTest, unittest.TestCase):
    def getTestInterface(self):
        return interfaces.IColumn

    def getTestClass(self):
        return column.Column

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)


class TestNoneCell(InterfaceBaseTest, unittest.TestCase):
    def getTestInterface(self):
        return interfaces.INoneCell

    def getTestClass(self):
        return column.NoneCell

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)


class TestNameColumn(InterfaceBaseTest, unittest.TestCase):
    def getTestInterface(self):
        return interfaces.IColumn

    def getTestClass(self):
        return column.NameColumn

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)


class TestRadioColumn(InterfaceBaseTest, unittest.TestCase):
    def getTestInterface(self):
        return interfaces.IColumn

    def getTestClass(self):
        return column.RadioColumn

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)


class TestCheckBoxColumn(InterfaceBaseTest, unittest.TestCase):
    def getTestInterface(self):
        return interfaces.IColumn

    def getTestClass(self):
        return column.CheckBoxColumn

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)


# batch
class TestBatchProvider(InterfaceBaseTest, unittest.TestCase):
    def getTestInterface(self):
        return interfaces.IBatchProvider

    def getTestClass(self):
        return batch.BatchProvider

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        t.rows = Batch([])
        return ({}, TestRequest(), t)


def test_suite():
    checker = RENormalizing(
        (
            (re.compile("u'(.*)'"), "'\\1'"),
            (re.compile('u"(.*)"'), '"\\1"'),
            (
                re.compile("zope.security.interfaces.Unauthorized"),
                "Unauthorized",
            ),
        )
    )

    return unittest.TestSuite(
        (
            doctest.DocFileSuite(
                "README.rst",
                setUp=testing.setUp,
                tearDown=testing.tearDown,
                checker=checker,
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            ),
            doctest.DocFileSuite(
                "sequence.rst",
                setUp=testing.setUp,
                tearDown=testing.tearDown,
                checker=checker,
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            ),
            doctest.DocFileSuite(
                "sort.rst",
                setUp=testing.setUp,
                tearDown=testing.tearDown,
                checker=checker,
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            ),
            doctest.DocFileSuite(
                "batch.rst",
                setUp=testing.setUp,
                tearDown=testing.tearDown,
                checker=checker,
                optionflags=doctest.NORMALIZE_WHITESPACE
                | doctest.ELLIPSIS
                | doctest.REPORT_UDIFF,
            ),
            doctest.DocFileSuite(
                "miscellaneous.rst",
                setUp=testing.setUp,
                tearDown=testing.tearDown,
                checker=checker,
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            ),
            doctest.DocFileSuite(
                "column.rst",
                setUp=testing.setUp,
                tearDown=testing.tearDown,
                checker=checker,
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            ),
            unittest.defaultTestLoader.loadTestsFromName(__name__),
        )
    )
