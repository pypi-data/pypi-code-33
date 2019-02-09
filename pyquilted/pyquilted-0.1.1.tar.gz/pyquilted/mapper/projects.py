from pyquilted.quilted.projects import *


class ProjectsMapper:
    def __init__(self, projects_odict):
        self.projects = Projects()
        self.odict = projects_odict

    def deserialize(self):
        for key, val in self.odict.items():
            activity = self._create_activity(key, val)
            self.projects.add_activity(activity)
        return self.projects

    def _create_activity(self, key, data):
        self._add_name_to_data(key, data)
        activity = Activity(**data)
        return activity

    def _add_name_to_data(self, name, data):
        data['name'] = name
