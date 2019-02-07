import unittest
from looqbox.integration.integration_links import look_tag


class TestSQLIn(unittest.TestCase):

    def test_look_tag(self):
        """
        Test look_tag function
        """
        par = {
            "originalQuestion": "teste",
            "cleanQuestion": "teste",
            "residualQuestion": "",
            "residualWords": [""],
            "entityDictionary": None,
            "userlogin": "user",
            "userId": 666,
            "companyId": 0,
            "userGroupId": 0,
            "language": "pt-br",
            "$date": {
                "content": [
                    {
                        "segment": "ontem",
                        "text": "ontem",
                        "value": [
                            [
                                "2019-01-08",
                                "2019-01-08"
                            ],
                            [
                                "2019-01-02",
                                "2019-01-02"
                            ]
                        ]
                    }
                ]
            },
            "$store": {
                "content": [
                    {
                        "segment": "loja 1",
                        "text": None,
                        "value": [
                            1
                        ]
                    }
                ]
            },
            "apiVersion":[2]
        }

        par2 = {
            "originalQuestion": "teste",
            "cleanQuestion": "teste",
            "residualQuestion": "",
            "residualWords": [""],
            "entityDictionary": None,
            "userlogin": "user",
            "userId": 666,
            "companyId": 0,
            "userGroupId": 0,
            "language": "pt-br",
            "$date": {
                "content": [
                    {
                        "segment": "ontem",
                        "text": "ontem",
                        "value": [
                            [
                                "2019-01-08",
                                "2019-01-08"
                            ]
                        ]
                    }
                ]
            },
            "$datetime": {
                "content": [
                    {
                        "segment": "ontem",
                        "text": "ontem",
                        "value": [
                            [
                                "2019-01-08 00:00:00",
                                "2019-01-08 00:00:00"
                            ]
                        ]
                    }
                ]
            },
            "$store": {
                "content": [
                    {
                        "segment": "loja 1",
                        "text": None,
                        "value": [
                            1
                        ]
                    }
                ]
            },
            "apiVersion": [2]
        }

        par3 = {
            "originalQuestion": "teste",
            "cleanQuestion": "teste",
            "residualQuestion": "",
            "residualWords": [""],
            "entityDictionary": None,
            "userlogin": "user",
            "userId": 666,
            "companyId": 0,
            "userGroupId": 0,
            "language": "pt-br",
            "$date": [
                [
                    "2019-01-08",
                    "2019-01-08"
                ]
            ],
            "$datetime": [
                [
                    "2019-01-08 00:00:00",
                    "2019-01-08 00:00:00"
                ]
            ],
            "$store": [1, 2, 3, 4, 5, 6, 7, 8],
            "apiVersion": [1]
        }

        tag1 = look_tag("$date", par)
        tag2 = look_tag("$store", par)
        tag3 = look_tag("$store", par, only_value=False)
        tag4 = look_tag("$undefined", par)
        tag5 = look_tag("$date", par2)
        tag6 = look_tag(["$date", "$datetime"], par2)
        tag7 = look_tag("$date", par3)
        tag8 = look_tag("$store", par3)
        tag9 = look_tag("$undefined", par3)
        tag10 = look_tag(["$date", "$datetime"], par3)

        self.assertEqual([['2019-01-08', '2019-01-08'], ['2019-01-02', '2019-01-02']], tag1)
        self.assertEqual([1], tag2)
        self.assertEqual({'segment': 'loja 1', 'text': None, 'value': [1]}, tag3)
        self.assertIsNone(tag4)
        self.assertEqual([['2019-01-08', '2019-01-08']], tag5)
        self.assertEqual([['2019-01-08', '2019-01-08'], ['2019-01-08 00:00:00', '2019-01-08 00:00:00']], tag6)
        self.assertEqual([["2019-01-08", "2019-01-08"]], tag7)
        self.assertEqual([1, 2, 3, 4, 5, 6, 7, 8], tag8)
        self.assertIsNone(tag9)
        self.assertEqual([['2019-01-08', '2019-01-08'], ['2019-01-08 00:00:00', '2019-01-08 00:00:00']], tag10)
