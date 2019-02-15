from enum import Enum, auto
from pydotfiles.utils import BijectiveDictionary


"""
Model enums
"""


class FileActionType(Enum):
    """
    Represents what kind of file operation
    this FileAction is
    """
    COPY = auto()
    DELETE = auto()

    SYMLINK = auto()
    UNSYMLINK = auto()

    SCRIPT = auto()
    UNDO_SCRIPT = auto()

    @staticmethod
    def from_string(label):
        if label is None:
            raise KeyError("Enum: No file action was passed in")
        return FileActionType[label.upper()]

    @staticmethod
    def get_reverse(file_action_type):
        file_action_reverse_mapping = BijectiveDictionary({
            FileActionType.COPY: FileActionType.DELETE,
            FileActionType.SYMLINK: FileActionType.UNSYMLINK,
            FileActionType.SCRIPT: FileActionType.UNDO_SCRIPT
        })
        return file_action_reverse_mapping.get(file_action_type)


class OverrideAction(Enum):
    """
    Represents an override action that
    a user can input when deciding what
    to do about certain file actions
    """

    SKIP_FILE = auto()
    SKIP_ALL_FILES = auto()

    OVERWRITE_FILE = auto()
    OVERWRITE_ALL_FILES = auto()

    BACKUP_FILE = auto()
    BACKUP_ALL_FILES = auto()

    @staticmethod
    def from_label(label):
        if label is None:
            raise KeyError("Enum: No override action was passed in")
        return OverrideAction[label.upper()]

    @staticmethod
    def affects_multiple_files(override_action):
        return override_action in {
            OverrideAction.SKIP_ALL_FILES,
            OverrideAction.OVERWRITE_ALL_FILES,
            OverrideAction.BACKUP_ALL_FILES
        }


"""
Exception enums
"""


class PydotfilesErrorReason(Enum):
    """
    Represents a particular reason why
    the pydotfiles failed, enables extraction
    of a potentially useful help message
    as well
    """

    UNKNOWN_ERROR = auto()
    NO_REMOTE_REPO = auto()
    REMOTE_REPO_CLONE_ISSUE = auto()
    UNKNOWN_CLEANING_TARGET = auto()
    UNKNOWN_MODULE_NAME = auto()

    @staticmethod
    def get_help_message(reason):
        help_message_map = {
            PydotfilesErrorReason.UNKNOWN_ERROR: None
        }
        return help_message_map.get(reason)


class ValidationErrorReason(Enum):
    """
    Represents a particular reason why
    the validation of a given dotfiles,
    module, or file failed
    """

    INVALID_TARGET = auto()

    INVALID_EMPTY_FILE = auto()
    INVALID_SYNTAX = auto()
    INVALID_SCHEMA = auto()

    # Specific schema issues
    INVALID_DATA = auto()
    INVALID_SCHEMA_VERSION = auto()
    INVALID_SCHEMA_TYPE = auto()

    @staticmethod
    def get_help_message(reason):
        help_message_map = {
            ValidationErrorReason.INVALID_EMPTY_FILE: "An empty invalid configuration file was detected",
            ValidationErrorReason.INVALID_SCHEMA: "A given configuration file contains an invalid schema"
        }
        return help_message_map.get(reason)
