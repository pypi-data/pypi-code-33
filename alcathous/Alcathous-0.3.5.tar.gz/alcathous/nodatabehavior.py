from enum import Enum


class NoDataBehavior(Enum):
    MUTE = 0, # do nothing
    LAST_VALID = 1, # re-publish last valid result
    EMPTY_MESSAGE = 2 # publish empty message

    @classmethod
    def get_enum(cls, config_str):
        config_str = str(config_str).upper()
        try:
            result = cls.__members__[config_str]
        except KeyError:
            raise ValueError("Unknown value for NoDataBehavior '{}'. Expected {}.".format(config_str, cls.__members__.keys()))
        return result
