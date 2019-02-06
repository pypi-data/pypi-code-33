"""
semvermanager
=================
`semvermamager` exports a single class Version which implements
a restricted subset of the  SEMVER_ standard.

.. _SEMVER: http://semver.org/

Version defines a Semantic version using the following field
structure:

.. code-block:: python

    # MAJOR.MINOR.PATCH-TAG

    int MAJOR  # 0 to N
    int MINOR  # 0 to N
    int PATCH  # 0 to N
    str TAG    # one of "alpha", "beta".
    int TAG_VERSION # appended to the tag if the tag is alpha or beta.

Versions may be bumped by a single increment using any of the
`bump` functions. Bumping a PATCH value simply increments it.
Bumping a MINOR value zeros the PATCH value and bumping a MAJOR
zeros the MINOR and the PATCH value.

`semvermanager` only supports Python 3.6 and greater.
"""

import os
import re

from typing import List


class VersionError(ValueError):
    """Exception for handling errors in Version Class"""
    pass


class Version:
    """
    Handle creation and storage of SEMVER version numbers. In this case
    SEMVERs must be of the form a.b.c-tag, Where a,b and c are integers
    in the range 0-n and tag is one of `Version.TAGS`.

    Version numbers may be bumped by using the various bump functions.
    Bumping minor zeros patch, bumping major zeros minor.

    """

    TAGS = {0: "alpha", 1: "beta", 2: ""}
    FIELDS = ["major", "minor", "patch", "tag", "tag_version"]
    FILENAME = "VERSION"

    def __init__(self, major=0, minor=0, patch=0, tag="alpha", tag_version=0, lhs="VERSION", separator="="):
        """
        :param major: 0-n
        :param minor: 0-n
        :param patch: 0-n
        :param tag: member of Version.TAGs.values()
        :param tag_version: The version of the tag value (e.g. alpha0, alpha1 etc.)
        :param lhs : str The candidate str for the lhs of a VERSION line
        :param separator: str the seperator string between the field name and the version
        """
        if isinstance(lhs, str):
            self._lhs = lhs
        else:
            raise VersionError(f"{lhs} is not a str type")

        if isinstance(major, int) and major >= 0:

            self._major = major
        else:
            raise VersionError(f"{major} is not an int type or is a negative int")

        if isinstance(minor, int) and minor >= 0:
            self._minor = minor
        else:
            raise VersionError(f"{minor} is not an int type or is a negative int")

        if isinstance(patch, int) and patch >= 0:
            self._patch = patch
        else:
            raise VersionError(f"{patch} is not an int type or is a negative int")

        self._separator = separator
        self._tag_index = None
        self._tag = None
        for k, v in Version.TAGS.items():
            if tag == v:
                self._tag = v
                self._tag_index = k

        if isinstance(tag_version, int) and tag_version >= 0 :
            self._tag_version = tag_version
        else:
            raise VersionError(f"{tag_version} is not an int or is negative")

        if self._tag_index is None:
            raise VersionError(f"'{tag}' is not a valid version tag")

    def bump(self, field):
        self.bump_map()[field]()

    def bump_major(self):
        self._patch = 0
        self._minor = 0
        self._major += 1

    def bump_minor(self):
        self._patch = 0
        self._minor += 1

    def bump_patch(self):
        self._patch += 1

    def bump_tag(self):
        if self._tag_index == len(Version.TAGS) - 1:
            self._tag_index = 0
        else:
            self._tag_index += 1
        self._tag = Version.TAGS[self._tag_index]
        if self._tag == "":  # prod
            self._tag_version = 0

    def bump_tag_version(self):
        if self._tag != "":
            self.tag_version = self.tag_version + 1
        else:
            raise VersionError("tag is not 'alpha' or 'beta' no bumping allowed for tag_version")
        return self._tag_version

    @property
    def lhs(self):
        self._lhs

    @property
    def major(self):
        return self._major

    @major.setter
    def major(self, value):
        assert isinstance(value, int) and value >= 0
        self._major = value

    @property
    def minor(self):
        return self._minor

    @minor.setter
    def minor(self, value):
        assert isinstance(value, int) and value >= 0
        self._minor = value

    @property
    def patch(self):
        return self._patch

    @patch.setter
    def patch(self, value):
        assert isinstance(value, int) and value >= 0
        self._patch = value

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        assert self._tag in self.TAGs.values()
        self._tag = value

    @property
    def tag_version(self):
        return self._tag_version

    @tag_version.setter
    def tag_version(self, value):
        assert isinstance(value, int) and value >= 0
        self._tag_version = value


    def bump_map(self):
        """
        a mapping of field names to corresponding bump methods
        :return: a dict of field names to bump methods
        """
        return {"major": self.bump_major,
                "minor": self.bump_minor,
                "patch": self.bump_patch,
                "tag": self.bump_tag,
                "tag_version": self.bump_tag_version}

    def field_map(self):
        """
        Mapping of field names to field values.
        :return: A dict of field names to their properties.
        """
        return {"major": self.major,
                "minor": self.minor,
                "patch": self.patch,
                "tag": self.tag,
                "tag_version": self._tag_version}

    def field(self, field):
        """
        Return the mapping from a field to its corresponding
        property.
        :param field: str in Version.FIELDS
        :return:
        """

        if field not in self.FIELDS:
            raise VersionError(f"No such field name'{field}'")
        return self.field_map()[field]

    @staticmethod
    def update(filename, version, lhs="VERSION", seperator="="):
        """
        Find any line starting with "VERSION" and replace that line with
        the new `version`.

        :param filename: A path to a file containing at least one VERSION line
        :param version: The new version object
        :return: A tuple (number of lines updated, list(line_numbers))
        """

        count = 0 # Number of replacements
        lines: List[int] = [] # line numbers of replacement lines
        with open(filename, "r") as input_file:
            with open(filename+".temp", "w") as output_file:
                for i, line in enumerate(input_file, 1):
                    candidate = line.strip()
                    if candidate.startswith(lhs):
                        try:
                            v = Version.parse_version(line, lhs, separator=seperator)
                            if v:
                                output_file.write(f"{str(version)}\n")
                                lines.append(i)
                                count = count + 1
                        except VersionError:
                            output_file.write(line)

                    else:
                        output_file.write(line)

        os.rename(filename, filename+".old")
        os.rename(filename+".temp", filename)

        return count, lines

    def write(self, filename):
        """
        Write a single line containing the version object to filename.
        This will overwrite the existing file if it exists.

        :param filename: The file to create with the new version object
        :param version: a valid version object.
        :return: A tuple of the filename and the version object
        """

        with open(filename, "w") as file:
            file.write(f"{str(self)}\n")

        return filename, self

    @staticmethod
    def find(filename, lhs="VERSION", separator="="):
        """Look for the first instance of a VERSION definition in a file
        and try and parse it as a `Version`"""

        version = None
        with open(filename, "r") as file:
            for line in file:
                line = line.strip()
                if line.startswith(lhs):
                    version = Version.parse_version(line, lhs=lhs, separator=separator)
                    break

        return version

    def read(self, filename, lhs=None, separator=None):
        """
        Read a single line from filename and parse it as version string.

        :param filename: a file containing a single line VERSION string.
        :param lhs : override the class field string
        :param separator: the character seperating the VERSION label from the value
        :return: a Version object

        :raises VersionError if it fails to parse the file.
        """

        with open(filename, "r") as file:
            line = file.readline()
            line.rstrip()

        if not lhs:
            lhs = self._lhs

        if not separator:
            separator = self._separator

        return self.parse_version(line, lhs, separator)
        # try:
        #     _, rhs = line.split(self._separator)
        # except ValueError as e:
        #     raise VersionError(e)
        #
        # try:
        #     version, tag = rhs.split("-")
        #     tag = tag.strip()
        #     tag = tag.strip("\"\'")
        #     version = version.strip()  # whitespace
        #     version = version.strip("\"\'")  # quotes
        # except ValueError as e:
        #     raise VersionError(e)
        #
        # try:
        #     major, minor, patch = [int(x) for x in version.split('.')]
        # except ValueError as e:
        #     raise VersionError(e)
        #
        # return Version(major, minor, patch, tag, tag_version=t separator=separator)

    @staticmethod
    def parse_version(line: str, lhs: str = "VERSION", separator="=") -> object:
        tag_version = 0
        line = line.strip()

        if line.startswith(lhs):
            try:
                version_label, rhs = line.split(separator)
                version_label = version_label.strip()
                rhs = rhs.strip()
                if version_label != lhs:
                    raise VersionError(f"{line} has wrong left hand side {version_label}")
            except ValueError as e:
                raise VersionError(f"{e} : in '{line}'")
        else:
            rhs = line

        try:
            if "-" in rhs:
                version, tag = rhs.split("-")
                tag = tag.strip()
                tag = tag.strip("\"\'")
                match = re.match(r"([a-z]+)([0-9]+)", tag, re.I)
                if match:
                    tag,tag_version = match.groups()
                    tag_version = int(tag_version)
                version = version.strip()
                version = version.strip("\"\'")
            else:
                version = rhs.strip()
                version = version.strip("\"\'")

                tag = ""
                tag_version=0

        except ValueError as e:
            raise VersionError(f"{e} : in '{rhs}'")

        try:
            major, minor, patch = [int(x) for x in version.split('.')]
        except ValueError as e:
            raise VersionError(f"{e} : in {lhs} '{version}'")

        return Version(major, minor, patch, tag, tag_version, lhs=lhs, separator=separator)

    def __eq__(self, other):
        return self.major == other.major and \
               self.minor == other.minor and \
               self.patch == other.patch and \
               self.tag == other.tag and \
               self.tag_version == other.tag_version

    def __str__(self):
        if self.tag == "":
            return f"{self._lhs} {self._separator} '{self._major}.{self._minor}.{self._patch}'"
        else:
            return f"{self._lhs} {self._separator} '{self._major}.{self._minor}.{self._patch}-{self._tag}{self._tag_version}'"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.major}, {self.minor}, {self.patch}, '{self.tag}', {self.tag_version}, '{self._lhs}', '{self._separator}')"

    def bare_version(self):
        if self.tag == "":
            return f'{self._major}.{self._minor}.{self._patch}'
        else:
            return f'{self._major}.{self._minor}.{self._patch}-{self._tag}{self.tag_version}'


