from .base_test import BaseTestClass
from rossby import Rossby

rossby = Rossby()


class SpecialCaseTestClass(BaseTestClass):
    data = rossby.alerts.get_all()

    def test_default_pagination_limit(self):
        params = {'limit': 10}
        test_against = self.plain_request('/alerts', params)

        self.assertIsNotNone(self.data)
        self.assertDictEqual(self.data.response.json(), test_against)

    def test_custom_limit(self):
        data = self.rossby.alerts.get_all(limit=50)

        params = {'limit': 50}
        test_against = self.plain_request('/alerts', params)

        self.assertDictEqual(data.response.json(), test_against)

    def test_pagination(self):
        test_against = [x for x in self.data.paginate()]
        self.assertIsNotNone(test_against)
        self.assertIs(type(test_against), list)

    def test_early_stop_pagination(self):
        data = self.rossby.alerts.get_all()

        test_against = []

        for index, item in enumerate(data.paginate()):
            if index == 2:
                break

            test_against.append(item)

        self.assertIs(len(test_against), 2)
