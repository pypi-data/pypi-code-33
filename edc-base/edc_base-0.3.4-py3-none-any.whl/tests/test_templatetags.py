from django.test import TestCase, tag
from ..templatetags.edc_base_extras import age_in_years, human
from edc_base.utils import get_utcnow
from dateutil.relativedelta import relativedelta
from uuid import uuid4


class TestTemplateTags(TestCase):
    def test_age(self):
        context = {"reference_datetime": None}
        born = get_utcnow() - relativedelta(years=25)
        self.assertEqual(25, age_in_years(context, born))

        reference_datetime = get_utcnow() - relativedelta(years=25)
        context = {"reference_datetime": reference_datetime}
        born = reference_datetime - relativedelta(years=5)
        self.assertEqual(5, age_in_years(context, born))

        reference_datetime = get_utcnow() - relativedelta(years=25)
        context = {"reference_datetime": reference_datetime}
        born = get_utcnow()
        self.assertEqual(born, age_in_years(context, born))

    def test_human(self):
        self.assertEqual(human(11112222333344445555), "1111-2222-3333-4444-5555")
