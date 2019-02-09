from pyquilted.quilted.resume import Resume
from pyquilted.quilted.style import Style
from pyquilted.mapper.section import SectionMapper
from pyquilted.yaml_loader import YamlLoader


class ResumeBuilder:
    def __init__(self, resume_odict, style=None, options=None):
        self.resume_odict = resume_odict
        self.resume = Resume(style=style)

    def load_yaml(self, path):
        with open(path) as f:
            ordered_dict = YamlLoader.ordered_load(f)
        return ordered_dict

    def build_resume(self):
        for key, val in self.resume_odict.items():
            mapper = SectionMapper(key, val)
            self.resume.add_section(mapper.create_section())
        return self.resume
