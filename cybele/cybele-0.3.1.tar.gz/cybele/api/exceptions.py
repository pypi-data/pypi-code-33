class DBNotFoundError(FileNotFoundError):
    """Raise when DB is not reachable"""


class EntryNotFoundError(KeyError):
    """Raise when trying to set entry_name and its not free"""


class EntryNameNotAvailableError(KeyError):
    """Raise when trying to set entry_name and its not free"""


class EntryFormatError(ValueError):
    """Raise when core keys are missing in a record"""
