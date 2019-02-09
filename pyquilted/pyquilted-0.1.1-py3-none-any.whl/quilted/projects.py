from pyquilted.quilted.section import Section


class Projects(Section):
    def __init__(self, blocks=None, icon=None):
        self.label = 'Projects'
        self.icon = icon or "fa-code"
        self.blocks = blocks or []

    def add_activity(self, activity):
        self.blocks.append(vars(activity))


class Activity:
    def __init__(self, name=None, description=None, slugs=None, flair=None,
                 flair_icon=None, **kwargs):
        self.name = name
        self.flair = flair
        self.flair_icon = flair_icon
        self.description = description
        self.slugs = slugs
