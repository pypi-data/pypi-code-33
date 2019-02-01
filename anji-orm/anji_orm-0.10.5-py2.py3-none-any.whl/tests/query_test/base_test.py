from typing import Optional

from anji_orm import Model

from ..base import BaseTestCase


class T1(Model):

    _table = 'non_table'

    c1: Optional[str]
    c2: Optional[str]


class BaseTest(BaseTestCase):

    def test_id_search(self):
        self.assertIs(T1.id.eq('5').model_ref, T1)
