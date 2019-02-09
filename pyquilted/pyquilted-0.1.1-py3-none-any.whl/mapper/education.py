from pyquilted.quilted.education import Education


class EducationMapper:
    def __init__(self, odict):
        self.odict = odict

    def deserialize(self):
        education_section = Education(self.odict)
        return education_section
