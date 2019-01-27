import unittest

from zope.pagetemplate.tests import test_htmltests as reference


class HTMLTests(reference.HTMLTests):
    def setUp(self):
        import z3c.ptcompat
        import zope.component.testing
        import zope.configuration.xmlconfig

        zope.component.testing.setUp(self)
        zope.configuration.xmlconfig.XMLConfig(
            "configure.zcml", z3c.ptcompat
        )()

        super(HTMLTests, self).setUp()


class TestProgram(unittest.TestCase):
    def _makeOne(self, *args):
        from z3c.ptcompat.engine import Program

        return Program.cook(*args)

    def test_call_with_no_tal_returns_template_body(self):
        body = "<html />"
        program, _ = self._makeOne(None, body, None, None)

        result = program(None, None, tal=False)
        self.assertEqual(result, body)
