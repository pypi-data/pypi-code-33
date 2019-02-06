import os.path

tags = (
    'auth', 'beacons', 'cache', 'engines', 'executor', 'fileserver', 'grains',
    'log_handlers', 'module', 'pillar', 'render', 'returner', 'runner',
    'serializers', 'states', 'tokens', 'top', 'utils', 'wheel',
)


class Loader:
    def __init__(self, dirname):
        self.dirname = dirname
        self.root = os.path.dirname(os.path.abspath(__file__))

    def __call__(self):
        fullpath = os.path.join(self.root, self.dirname)
        if os.path.isdir(fullpath):
            yield fullpath


for tag in tags:
    globals()[tag] = Loader(tag)
