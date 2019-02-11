


class DeploymentManager:
    """Maintains information about all deployments declared by the
    current Quantum project.
    """

    def __init__(self):
        self._runtimes = {}

    def createruntime(self, name, withenv=True):
        """Creates a new runtime of the application image."""
        assert name not in self._runtimes
        self._runtimes[name] = runtime = Runtime(name)
        return runtime

    def create(self, name, group=None, development=False, image=None, withenv=False):
        """Create a new :class:`Deployment`."""
        if not withenv:
            withenv = image is not None



class Runtime:
    """Represents a runtime instance of the application code with
    a specific environment configuration.
    """

    def __init__(self, name):
        self._name = name
