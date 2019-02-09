import unittest
from pyquilted.quilted.contacts import *


class TestContacts(unittest.TestCase):
    def test_email_contact(self):
        email = EmailContact('jon.snow@winterfell.got')
        valid = {
                'label': 'email',
                'value': 'jon.snow@winterfell.got',
                'icons': ['fa-envelope']
                }
        self.assertEqual(vars(email), valid)

    def test_phone_contact(self):
        phone = PhoneContact('555-123-4567')
        valid = {
                'label': 'phone',
                'value': '555-123-4567',
                'icons': ['fa-phone']
                }
        self.assertEqual(vars(phone), valid)

    def test_social_contact(self):
        social_dict = {"handle": "@jonsnow", "sites": ['twitter', 'instagram']}
        social = SocialContact(**social_dict)
        valid = {
                'label': 'social',
                'value': '@jonsnow',
                'icons': ['fa-twitter', 'fa-instagram']
                }
        self.assertEqual(vars(social), valid)


if __name__ == '__main__':
    unittest.main()
