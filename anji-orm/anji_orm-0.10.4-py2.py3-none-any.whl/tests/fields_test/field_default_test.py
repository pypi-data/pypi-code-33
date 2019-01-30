import typing

from parameterized import parameterized

from anji_orm import Model, Field
from ..base import BaseTestCase


class T1(Model):

    _table = 'non_table'

    c1: str = '5'
    c2: int = 0
    c3: str = ''
    c4: typing.Optional[str] = Field(default_factory=lambda: None)
    c5: str = Field(default_factory=lambda: '')


class FieldValidationTest(BaseTestCase):

    @parameterized.expand([
        ('c1', '5'),
        ('c2', 0),
        ('c3', ''),
        ('c4', None),
        ('c5', '')
    ])
    def test_simple_default(self, attribute, value) -> None:
        test_record = T1()
        self.assertEqual(getattr(test_record, attribute), value)
