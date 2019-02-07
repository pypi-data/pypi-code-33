from unittest import TestCase

from pkg_resources import resource_string
from pyhocon import ConfigFactory

from aiconf import MalformattedConfigException, get_constructor_and_args, load_class, construct_from_config, \
    ConfigReader, safe_construct
import nose.tools as nt

cfg = """
x = {
 class = DummyClass
 args = {
    arg1 = 3
    arg2 = false
 }
}
y = {
 "()" = DummyClass
 arg1 = 3
 arg2 = false
}
z = {
 class = DummyClass
 arg1 = 3
 arg2 = false
}
u = {
 arg1 = 3
 arg2 = false
}
v = DummyClass

"""


class DummyClass:
    def __init__(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2


class OtherDummyClass:
    pass


# noinspection PyMethodMayBeStatic
class ConfigTester(TestCase):

    @classmethod
    def setup_class(cls):
        cls.cfg = ConfigFactory.parse_string(cfg)
        cls.config_path = "tests/resources/test.conf"

    def test_successful_config_reader_no_path(self):
        c = ConfigReader(default=cfg)
        nt.assert_equal(c.read_config(), self.cfg)

    def test_successful_config_reader_no_default(self):
        c = ConfigReader(path=self.config_path)
        nt.assert_equal(c.read_config(), self.cfg)

    @nt.raises(ValueError)
    def fail_to_parse_with_no_arguments(self):
        ConfigReader()

    def test_successful_read_resource(self):
        default = resource_string(__name__, "resources/test.conf")
        c = ConfigReader(default=default)
        nt.assert_equal(c.read_config(), self.cfg)

    def test_successful_merge(self):
        c = ConfigReader(path=self.config_path, default="r=[1,2,3]")
        new_cfg = dict(self.cfg.as_plain_ordered_dict())
        new_cfg['r'] = [1, 2, 3]
        cfg = dict(c.read_config().as_plain_ordered_dict())

        nt.assert_equal(cfg, new_cfg)

    def test_successful_get_constructor_args_oldstyle(self):
        c, args = get_constructor_and_args(self.cfg['x'])
        nt.assert_equal(c, "DummyClass")
        nt.assert_equal(args['arg1'], 3)
        nt.assert_false(args['arg2'])

    def test_successful_get_constructor_args_newstyle(self):
        c, args = get_constructor_and_args(self.cfg['y'])
        nt.assert_equal(c, "DummyClass")
        nt.assert_equal(args['arg1'], 3)
        nt.assert_false(args['arg2'])

        c, args = get_constructor_and_args(self.cfg['z'])
        nt.assert_equal(c, "DummyClass")
        nt.assert_equal(args['arg1'], 3)
        nt.assert_false(args['arg2'])

    def test_successful_when_only_class_name(self):
        c, args = get_constructor_and_args(self.cfg['v'])
        nt.assert_equal(c, "DummyClass")
        nt.assert_equal(args, dict())

    def test_fail_when_whether_new_nor_old_style_config(self):
        nt.assert_raises(
            MalformattedConfigException, get_constructor_and_args, self.cfg['u']
        )

    def test_successful_load_class_with_relative_import(self):
        cls = load_class("DummyClass", relative_import="tests.test_config")
        nt.assert_equal(cls, DummyClass)

    def test_successful_load_class_with_no_relative_import(self):
        cls = load_class("tests.test_config.DummyClass")
        nt.assert_equal(cls, DummyClass)  #

    def test_successful_load_class_with_partial_relative_import(self):
        cls = load_class("test_config.DummyClass", relative_import="tests")
        nt.assert_equal(cls, DummyClass)

    def test_successful_load_class_with_wrong_relative_import_but_absolute_path(self):
        cls = load_class("tests.test_config.DummyClass", relative_import="tests.test_config")
        nt.assert_equal(cls, DummyClass)

    def test_successful_class_check(self):
        cls = load_class("tests.test_config.DummyClass", restrict_to=DummyClass)
        nt.assert_equal(cls, DummyClass)

    def test_fail_when_restricted_to_wrong_class(self):
        nt.assert_raises(ValueError, load_class, "tests.test_config.DummyClass", OtherDummyClass)

    def test_successful_construct(self):
        instance = construct_from_config(self.cfg['x'], restrict_to=DummyClass,
                                         relative_import="tests.test_config")
        nt.assert_is_instance(instance, DummyClass)
        nt.assert_equal(instance.arg1, 3)
        nt.assert_equal(instance.arg2, False)
        instance = construct_from_config(self.cfg['y'], restrict_to=DummyClass,
                                         relative_import="tests.test_config")
        nt.assert_is_instance(instance, DummyClass)
        nt.assert_equal(instance.arg1, 3)
        nt.assert_equal(instance.arg2, False)

    def test_successful_safe_construct(self):
        instance = safe_construct(DummyClass(1, 2), restrict_to=DummyClass,
                                  relative_import="tests.test_config")
        nt.assert_is_instance(instance, DummyClass)
        nt.assert_equal(instance.arg1, 1)
        nt.assert_equal(instance.arg2, 2)
