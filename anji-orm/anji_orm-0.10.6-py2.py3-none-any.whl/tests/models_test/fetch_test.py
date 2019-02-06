from anji_orm.rethinkdb.executor import fetch

from .base_models import BaseModel
from ..base import BaseTestCase


class FetchTest(BaseTestCase):

    def test_base_fetch(self):
        base_record = BaseModel(id='55', test_field_1='5', test_field_2='8')
        fetch_dict = base_record.to_dict()
        self.assertEqual(
            base_record.to_dict(),
            fetch(fetch_dict).to_dict()
        )

    def test_fetch_dict(self):
        some_dict = {5: 6, 7: 8}
        self.assertEqual(some_dict, fetch(some_dict))
