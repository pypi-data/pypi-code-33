import unittest
from pyquilted.quilted.contacts import *
from pyquilted.quilted.contacts_list import ContactsList


class TestContacts(unittest.TestCase):
    def test_contact_list(self):
        contacts = ContactsList()
        email = EmailContact('jon.snow@winterfell.got')
        phone = PhoneContact('555-123-4567')
        social_dict = {"handle": "@jonsnow", "sites": ['twitter', 'instagram']}
        social = SocialContact(**social_dict)

        contacts.append(email)
        contacts.append(phone)
        contacts.append(social)

        valid = [
                {
                    'label': 'email',
                    'value': 'jon.snow@winterfell.got',
                    'icons': ['fa-envelope']
                },
                {
                    'label': 'phone',
                    'value': '555-123-4567',
                    'icons': ['fa-phone']
                },
                {
                    'label': 'social',
                    'value': '@jonsnow',
                    'icons': ['fa-twitter', 'fa-instagram']
                }
                ]
        self.assertEqual(contacts.serialize(), valid)


if __name__ == '__main__':
    unittest.main()
