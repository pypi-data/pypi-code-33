import unittest
from pyquilted.mapper.skills import SkillsMapper
from pyquilted.yaml_loader import YamlLoader


class TestMapperSkills(unittest.TestCase):
    def test_mapper_skills(self):
        with open('tests/validations/skills.yml') as f:
            data = YamlLoader.ordered_load(f)
        mapper = SkillsMapper(data['skills'])
        skills= mapper.deserialize()

        valid = {
                "skills": {
                    "label": "Skills",
                    "value": "Bravery, Leadership, Swordsmanship, Brooding, Knowing-nothing, HTML",
                    "icon": "fa-wrench"
                    }
                }
        self.assertEqual(skills.serialize(), valid)


if __name__ == '__main__':
    unittest.main()
