from ethronsoft.gcspypi.utilities.version import complete_version
from ethronsoft.gcspypi.exceptions import InvalidState, InvalidParameter
import os


class Package(object):

    def __init__(self, name, version="", requirements=None, type=""):
        if requirements is None:
            requirements = set([])
        self.name = name.replace("_", "-")
        self.version = complete_version(version) if version else None
        self.requirements = set([])
        self.type = type
        for r in requirements:
            self.requirements.add(r.replace("_", "-"))

    @staticmethod
    def repo_name(pkg, filename):
        if not pkg.version:
            raise InvalidState("cannot formulate package repository-name for a package without version")
        return "{name}/{version}/{filename}".format(
            name=pkg.name,
            version=pkg.version,
            filename=os.path.split(filename)[1]
        )

    @staticmethod
    def from_text(text):
        if ">" in text or "<" in text:
            raise InvalidParameter("Cannot create a package with non deterministic version")
        if "==" in text:
            name, version = text.split("==")
            return Package(name.strip(), version.strip())
        else:
            return Package(text)

    def __str__(self):
        return self.full_name

    def __repr__(self):  # pragma: no cover
        return "<Package {}>".format(str(self))

    def __eq__(self, o):
        if not o:
            return False

        return (self.name, self.version, self.type) == (o.name, o.version, o.type)

    def __ne__(self, o):
        return not self.__eq__(o)

    def __hash__(self):
        return hash((self.name, str(self.version), self.type))

    @property
    def full_name(self):
        return self.name + ":" + self.version if self.version else self.name
