from enum import Enum
from enum import IntEnum


class Enforcement(Enum):
    NONE = 1
    IGNORE = 2
    STRICT = 3

    @classmethod
    def get_enum(cls, text):
        text = text.upper()
        if text == "NONE":
            return Enforcement.NONE
        elif text == "IGNORE":
            return Enforcement.IGNORE
        elif text == "STRICT":
            return Enforcement.STRICT
        else:
            raise ValueError("dont know how to convert '{}' to enum Enforcement.".format(text))


class Necessity(Enum):
    OPTIONAL = 1  # predefined in config, but if inactive/stopped, the combined group health is still green
    REQUIRED = 2  # predefiend in config, if inactive/stopped, the combined group health is red
    SPONTANEOUS = 3  # not predefined. if configured, occurence of a spontaneous agent onboarding will result in a red group health

    @classmethod
    def get_enum(cls, text):
        text = text.upper()
        if text == "OPTIONAL":
            return Necessity.OPTIONAL
        elif text == "REQUIRED":
            return Necessity.REQUIRED
        elif text == "SPONTANEOUS":
            return Necessity.SPONTANEOUS
        else:
            raise ValueError("dont know how to convert '{}' to Necessity".format(text))


class StatType(Enum):
    ALL = 1
    GENERAL = 2
    PROPERTIES = 3
    PING = 4
    RUNTIME = 5
    CONFIG = 6
    LOGGER = 7
    REQUEST = 8

    @classmethod
    def get_enum(cls, text):
        text = str(text).upper()
        for name, member in StatType.__members__.items():
            if text == name:
                return member
        raise ValueError("StatType: dont know how to convert '{}' to enum".format(text))

    @classmethod
    def get_members(cls):
        return StatType.__members__.keys()


class Health(IntEnum):
    GREEN = 0
    YELLOW = 1
    RED = 2


class ViewDetails(IntEnum):
    NONE = 0
    HEALTH = 1
    STATE = 2
    GID = 4
    FULL = NONE+HEALTH+STATE+GID
