import unittest
from pyquilted.mapper.education import EducationMapper
from pyquilted.yaml_loader import YamlLoader


class TestMapperEducation(unittest.TestCase):
    def test_mapper_education(self):
        with open('tests/validations/education.yml') as f:
            odata = YamlLoader.ordered_load(f)
        mapper = EducationMapper(odata['education'])
        education = mapper.deserialize()

        valid = {
                "education": {
                    "label": "Education",
                    "value": "The Night's Watch",
                    "icon": "fa-graduation-cap"
                    }
                }
        self.assertEqual(education.serialize(), valid)


if __name__ == '__main__':
    unittest.main()
