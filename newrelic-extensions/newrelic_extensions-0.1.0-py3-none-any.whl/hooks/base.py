class BasePatch(object):
    required_modules = []

    def instrument(self, project_packages=None):
        pass
