import unittest

import pytest

from oc_wrapper.api import Oc
from oc_wrapper.policy import Policy


class TestOc(unittest.TestCase):
    def test_init(self):
        assert Oc()
        assert Oc().ci_mode
        assert isinstance(Oc().policy, Policy)


if __name__ == '__main__':
    pytest.main()
