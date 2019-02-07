from ..errors import ExecutorError


class CommandExecutor:
    def __init__(self):
        self._commands = {}

        self.create_command()

    @property
    def commands(self):
        return self._commands

    def create_command(self):
        for method in [f for f in dir(self) if callable(getattr(self, f)) and not f.startswith('__')]:
            self.commands[method] = getattr(self, method)

    def execute_command(self, command, *args, **kwargs):
        if command in self.commands.keys():
            return self.commands[command](*args, **kwargs)
        else:
            raise ExecutorError('Command [{}] not found in possible commands'.format(command))
