
import argparse
import unittest
from check_certs.utils import deep_merge
from check_certs.utils import get_args

class TestDeepMerge(unittest.TestCase):
    def test_deep_merge(self):

        # when reaches the max level, it should return b
        max_level = 9
        self.assertEqual(deep_merge({"a": 1}, {"b": 2}, level=max_level), {"b": 2})

        # when a is not a dict
        self.assertEqual(deep_merge(None, {"b": 2}), {"b": 2})

        # when b is not a dict
        self.assertEqual(deep_merge({"a": 1}, None), None)

        # same key overwrites
        self.assertEqual(deep_merge({"a": 1}, {"a": 2}), {"a": 2})
        self.assertEqual(
            deep_merge(
                { "a": { "b": 1, "c": 2, } },
                { "a": { "c": 3, } }
            ),
            { "a": { "b": 1, "c": 3 } }
        )

        # different keys merge
        self.assertEqual(deep_merge({"a": 1}, {"b": 2}), {"a": 1, "b": 2})

        self.assertEqual(
            deep_merge(
                { "a": { "b": 1, "c": 2, } },
                { "a": { "d": 3, } }
            ),
            { "a": { "b": 1, "c": 2, "d": 3, } }
        )

class TestGetArgs(unittest.TestCase):
    def test_get_args(self):

        # default arguments
        args = get_args([])
        self.assertEqual(args, argparse.Namespace(
            sites=[],
            port=443,
            show=False,
            notify_when_expiring_in=35,
        ))

        args = get_args(["--show"])
        self.assertEqual(args.show, True)

        args = get_args("-n 60 --show".split())
        self.assertEqual(args.notify_when_expiring_in, 60)
        self.assertEqual(args.show, True)

        args = get_args("-p 80".split())
        self.assertEqual(args.port , 80)
        self.assertEqual(args.show, False)

        args = get_args("www.google.com www.youtube.com".split())
        self.assertEqual(args.sites, ["www.google.com", "www.youtube.com"])
        self.assertEqual(args.show, False)
