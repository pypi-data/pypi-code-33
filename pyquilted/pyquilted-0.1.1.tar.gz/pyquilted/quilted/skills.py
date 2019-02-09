from pyquilted.quilted.section import Section


class Skills(Section):
    def __init__(self, skills, icon=None):
        self.label = 'Skills'
        self.value = ", ".join(skills)
        self.icon = icon or "fa-wrench"
