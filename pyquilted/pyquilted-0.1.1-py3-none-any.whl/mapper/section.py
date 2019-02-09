from pyquilted.mapper.contacts import ContactsMapper
from pyquilted.mapper.education import EducationMapper
from pyquilted.mapper.heading import HeadingMapper
from pyquilted.mapper.projects import ProjectsMapper
from pyquilted.mapper.skills import SkillsMapper
from pyquilted.mapper.work import WorkMapper


class SectionMapper:
    def __init__(self, key, section_odict):
        self.key = key
        self.section_odict = section_odict
        self.mapper = None
        self.section = None

    def create_section(self):
        self._create_mapper()
        self.section = self.mapper.deserialize()
        return self.section

    def _create_mapper(self):
        if self.key in 'contacts':
            self.mapper = ContactsMapper(self.section_odict)
        elif self.key in 'education':
            self.mapper = EducationMapper(self.section_odict)
        elif self.key in 'heading':
            self.mapper = HeadingMapper(self.section_odict)
        elif self.key in 'projects':
            self.mapper = ProjectsMapper(self.section_odict)
        elif self.key in 'skills':
            self.mapper = SkillsMapper(self.section_odict)
        elif self.key in 'work':
            self.mapper = WorkMapper(self.section_odict)
