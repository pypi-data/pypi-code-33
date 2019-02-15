class Enum:
    OPTIONS = None

    @classmethod
    def label(cls, value):
        return cls._members()[value]

    @classmethod
    def choices(cls):
        return cls.OPTIONS

    # private

    members = None

    @classmethod
    def _members(cls):
        if not cls.members:
            cls.members = dict(cls.OPTIONS)

        return cls.members

class ResponseType(Enum):
    USER_RESPONSE = 0
    SUPPORT_RESPONSE = 1

    OPTIONS = [
        (USER_RESPONSE, 'Awaiting response'),
        (SUPPORT_RESPONSE, 'Support responded'),
    ]

class Status(Enum):
    OPEN = 0
    CLOSE = 1
    ARCHIVE = 2

    OPTIONS = [
        (OPEN, 'Open'),
        (CLOSE, 'Closed'),
        (ARCHIVE, 'Archived'),
    ]

class Priority(Enum):
    NORMAL = 0
    MODERATE = 1
    HIGH = 2

    OPTIONS = [
        (NORMAL, 'Normal priority'),
        (MODERATE, 'Moderate priority'),
        (HIGH, 'High priority'),
    ]
