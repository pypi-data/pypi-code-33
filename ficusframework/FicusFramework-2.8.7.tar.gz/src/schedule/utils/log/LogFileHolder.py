from depocs import Scoped


class LogFileHolder(Scoped):
    class ScopedOptions:
        # If True, instances will share the stack of their parent class.
        # If False, this class will have its own stack independent of any
        # ancestors. The default is to inherit the stack, unless subclassing
        # Scoped directly. This option is NOT inherited by subclasses.
        inherit_stack = True

    def __init__(self, filePath):
        self.filePath = filePath