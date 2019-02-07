import unittest
from osem.general.enerapi.base.base import Base


class TestBase(unittest.TestCase):
    def test_has_default_args_should_work_without_default_args(self):
        args = {"abc": 123}
        Base._apply_default(args, {})
        self.assertDictEqual({"abc": 123}, args)

    def test_has_default_args_should_apply_a_default_arg_when_missing(self):
        args = {"abc": 123}
        Base._apply_default(args, {"def": 345})
        self.assertDictEqual({"abc": 123, "def": 345}, args)

    def test_has_default_args_should_not_override_given_args(self):
        args = {"abc": 123}
        Base._apply_default(args, {"abc": 345})
        self.assertDictEqual({"abc": 123}, args)

    def test_when_subclassing_base_without_default_args_has_default_args_should_work_correctly(self):
        self.assertDictEqual(ChildWithoutDefaultArgs({"abc": 123}).args, {"abc": 123})

    def test_when_subclassing_base_with_default_args_has_default_args_should_work_correctly(self):
        self.assertDictEqual(ChildWithDefaultArgs({"abc": 123}).args, {"abc": 123, "def": 345})


class ChildWithoutDefaultArgs(Base):

    def __init__(self, args):
        # This calls hasDefaultArgs
        super(ChildWithoutDefaultArgs, self).__init__(args)

        self.args = args


class ChildWithDefaultArgs(Base):

    _default_parameter_value = {"def": 345}

    def __init__(self, args):
        # This calls hasDefaultArgs
        super(ChildWithDefaultArgs, self).__init__(args)

        self.args = args
