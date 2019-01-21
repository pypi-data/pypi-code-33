"""
Sematic Versioning version class. Data structure and rules of a SemVer version
are obeyed by this class' memebers.
"""


class SemVer(object):
    def __init__(self, major=0, minor=0, patch=0) -> None:
        """
        A SemVer object can be initiallized with its major, minor, and patch
        numbers set, or with none at all (defaults are used instead).
        """
        self.filter_negatives(major, minor, patch)
        self._major, self._minor, self._patch = major, minor, patch
        self._version = f'{major}.{minor}.{patch}'

    def __repr__(self) -> str:
        """
        SemVer version numbers should be represented as strings formatted
        such that they match the following pattern:
        '<non-negative int>.<non-negative int>.<non-negative int>'.
        """
        return self.version

    def __eq__(self, other) -> bool:
        """
        param other

        Two given SemVer objects can be said to be equal if their version
        property matches.
        """
        return self.version == other.version

    def __ne__(self, other) -> bool:
        """
        param other

        Two given SemVer objects can be said to be unequal if their version
        property differs.
        """
        return self.version != other.version

    def __gt__(self, other) -> bool:
        """
        param other

        A given SemVer object can be said to be greater than another if
            1) its major version integer is greater than that of its
            counterpart, failing that and given that the major version integers
            are equal,
            2) its minor version integer is greater than that of its
            counterpart, failing that and given that the minor version integers
            are equal,
            3) its patch version integer is greater than that of its
            counterpart.
        """
        gt = False
        if self.major > other.major:
            gt = True
        elif self.major == other.major and self.minor > other.minor:
            gt = True
        elif self.minor == other.minor and self.patch > other.patch:
            gt = True
        return gt

    def __lt__(self, other) -> bool:
        """
        param other

        A given SemVer object can be said to be less than another if
            1) its major version integer is less than that of its counterpart,
            failing that and given that the major version integers are equal,
            2) its minor version integer is less than that of its counterpart,
            failing that and given that the minor version integers are equal,
            3) its patch version integer is less than that of its counterpart.
        """
        lt = False
        if self.major < other.major:
            lt = True
        elif self.major == other.major and self.minor < other.minor:
            lt = True
        elif self.minor == other.minor and self.patch < other.patch:
            lt = True
        return lt

    @classmethod
    def from_str(cls, version_str: str):
        """
        Alternate constructor that accepts a string SemVer.
        """
        o = cls()
        o.version = version_str
        return o

    @property
    def major(self) -> int:
        """
        Major version number property. Must be a non-negative integer.
        """
        return self._major

    @major.setter
    def major(self, major: int) -> None:
        """
        param major

        Major version number property. Must be a non-negative integer.
        """
        self.filter_negatives(major)
        self._major = major

    @property
    def minor(self) -> int:
        """
        Minor version number property. Must be a non-negative integer.
        """
        return self._minor

    @minor.setter
    def minor(self, minor: int) -> None:
        """
        param minor

        Minor version number property. Must be a non-negative integer.
        """
        self.filter_negatives(minor)
        self._minor = minor

    @property
    def patch(self) -> int:
        """
        Patch version number property. Must be a non-negative integer.
        """
        return self._patch

    @patch.setter
    def patch(self, patch: int) -> None:
        """
        param patch

        Patch version number property. Must be a non-negative integer.
        """
        self.filter_negatives(patch)
        self._patch = patch

    @property
    def version(self) -> str:
        """
        Version version number property. Must be a string consisting of three
        non-negative integers delimited by periods (eg. '1.0.1').
        """
        version: str = (
            str(self._major) + '.' +
            str(self._minor) + '.' +
            str(self._patch)
        )
        return version

    @version.setter
    def version(self, version_str: str) -> None:
        """
        param version

        Version version number property. Must be a string consisting of three
        non-negative integers delimited by periods (eg. '1.0.1').
        """
        ver = []
        for i in version_str.split('.'):
            ver.append(int(i))
            self.filter_negatives(int(i))
        self._major, self._minor, self._patch = ver[0], ver[1], ver[2]

    def bump_major(self):
        return self.__class__(self._major + 1, 0, 0)

    def bump_minor(self):
        return self.__class__(self._major, self._minor + 1, 0)

    def bump_patch(self):
        return self.__class__(self._major, self._minor, self._patch + 1)

    def filter_negatives(self, *num) -> None:
        """
        param *num

        Every integer in a SemVer version must be non-negative. This function
        raises an exception when one or a collection containing a
        non-negative is passed to it.
        """
        for i in num:
            if i < 0:
                raise ValueError(
                    'Every integer in a SemVer version must be non-negative.'
                )
