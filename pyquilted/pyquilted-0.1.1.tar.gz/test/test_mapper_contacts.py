import unittest
from pyquilted.mapper.contacts import ContactsMapper
from pyquilted.yaml_loader import YamlLoader


class TestMapperContacts(unittest.TestCase):
    def test_mapper_contacts(self):
        with open('tests/validations/contacts.yml') as f:
            data = YamlLoader.ordered_load(f)
        mapper = ContactsMapper(data['contacts'])
        contacts = mapper.deserialize()

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
                    'value': '@jonsnowEGOT',
                    'icons': ['fa-twitter', 'fa-instagram']
                }
                ]
        self.assertEqual(contacts.serialize(), valid)


if __name__ == '__main__':
    unittest.main()
