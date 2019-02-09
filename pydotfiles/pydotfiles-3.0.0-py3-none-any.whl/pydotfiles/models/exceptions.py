from .enums import PydotfilesErrorReason, ValidationErrorReason


class PydotfilesError(Exception):

    def __init__(self, reason, help_message_override=None):
        super().__init__()
        self.reason = reason
        self.help_message_override = help_message_override

    @property
    def help_message(self):
        return PydotfilesErrorReason.get_help_message(self.reason) if self.help_message_override is None else self.help_message_override


class ValidationError(Exception):

    def __init__(self, reason, help_message_override=None, context_map=None):
        super().__init__()
        self.reason = reason
        self.help_message_override = help_message_override
        if context_map is None:
            context_map = {
                "help": "If you need additional context like a stack trace, please run in verbose mode (with the -v flag)"
            }
        self.context_map = context_map

    @property
    def help_message(self):
        undecorated_original_help_message = ValidationErrorReason.get_help_message(self.reason) if self.help_message_override is None else self.help_message_override

        if len(self.context_map) == 0:
            serialized_context_decoration = ""
        else:
            serialized_context_decoration = '\n'.join([f"\t{context_type}: {context_reason}" for context_type, context_reason in self.context_map.items()])

        decorated_error_message = f"{undecorated_original_help_message} [\n{serialized_context_decoration}\n]"
        return decorated_error_message
