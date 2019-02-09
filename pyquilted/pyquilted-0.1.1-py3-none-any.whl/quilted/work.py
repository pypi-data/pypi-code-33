from pyquilted.quilted.section import Section


class Work(Section):
    def __init__(self, blocks=None, slugs=None, icon=None):
        self.label = 'Work'
        self.icon = icon or 'fa-briefcase'
        self.blocks = blocks or []

    def add_job(self, job):
        self.blocks.append(vars(job))

    def add_slugs(self, slugs):
        self.slugs = slugs


class Job:
    def __init__(self, dates=None, location=None, company=None, title=None,
                 slugs=None, **kwargs):
        self.dates = dates
        self.location = location
        self.company = company
        self.title = title
        self.slugs = slugs


class Slugs():
    def __init__(self, slugs=None):
        self.blocks = slugs
