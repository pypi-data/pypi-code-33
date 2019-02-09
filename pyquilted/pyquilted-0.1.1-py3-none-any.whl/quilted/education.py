from pyquilted.quilted.section import Section


class Education(Section):
    def __init__(self, education, icon=None):
        self.label = 'Education'
        self.value = education
        self.icon = icon or "fa-graduation-cap"
